#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mqtt

# python 3.11


from paho.mqtt import client as mqtt_client
from pytz import utc, timezone
import gps.tracker.models as tracker
from datetime import datetime,timedelta
from django.contrib.gis.geos import Point


#broker = 'test.mosquitto.org'
broker = 'condor3582.startdedicated.com'
port = 1883
topic = "BNR/#"
# Generate a Client ID with the subscribe prefix.
client_id = 'subscribe-11243'

log_name = '/home/django13/mqtt.log'

def connect_mqtt(log):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print >> log, "Connected to MQTT Broker!"
            print "Connected to MQTT Broker!"
        else:
            print >> log, "Failed to connect, return code", rc
            print("Failed to connect, return code", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.username_pw_set(username="transmetro", password="trans001")
    client.connect(broker, port)
    return client


def subscribe(client, log):
    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        print >>  log, "MQTT:", msg.topic, ":", payload
        print "MQTT:",  msg.topic, ":", payload
        xy = payload.split(',')
        topics = msg.topic.split('/')
        if not tracker.SGAvl.objects.filter(imei = topics[1]):
            # Create device
            h = tracker.SGHarness.objects.all()[0]
            dev = tracker.SGAvl(imei = topics[1], name = topics[1], harness =h)
            dev.save()
        dev = tracker.SGAvl.objects.get(imei = topics[1])
        try: #if len(xy)==2 and len(topics) ==3:
            yct = xy[1].split("@")  #if len(yct)==2 :
            x = xy[0]
            y = yct[0]
            ct = yct[1]
            tstamp = datetime.fromtimestamp(int(ct),utc)
            coord = Point(float(x), float(y))
            dev.position = coord
            dev.date = tstamp
            dev.lastLog = datetime.now(tz=utc)
            dev.save()
            tev = tracker.Event.objects.filter(imei=dev, type = 'TRACK', date = tstamp)
            if not tev: # No duplicates
                ev = tracker.Event(imei = dev, type = 'TRACK', position = coord, date = tstamp)
                ev.save()
                print "Saved TRACK for device ", dev.name
        except Exception as e:
            raise e
            pass
        print "Received Message ", msg.payload.decode()," Topic = ", msg.topic

    client.subscribe(topic)
    client.on_message = on_message


def run():
    with open(log_name,"a") as log:
        client = connect_mqtt(log)
        subscribe(client, log)
        client.loop_forever()

