#!/usr/bin/python
# -*- coding: utf-8 -*-
# SGAvl server

import socket
import struct
import SocketServer
import string
import time
import threading
import sys
import types
import errno
from datetime import datetime,timedelta
from pytz import utc, timezone
import os,io
import subprocess

import decimal
from geopy.point import Point as gPoint
from geopy.distance import distance as geoLen


os.environ['DJANGO_SETTINGS_MODULE'] = 'sites.www.settings'
path = '/home/django13/skyguard'
if path not in sys.path:
    sys.path.append(path)

from django.db import transaction, DatabaseError, IntegrityError, connection
from django.contrib.gis.geos import Point
from django.conf import settings
#import gps.tracker.models as tracker
from gps.tracker.models import SGAvl, Event
import gps.gprs.models as gprs

settings.DEBUG = False


class SATRequestHandler(SocketServer.BaseRequestHandler ):
	def setup(self):
		print "*"*80
		print datetime.now().ctime(), self.client_address, 'connected!'

	def handle(self):
		self.imei = None

		data = self.request.recv(2048)
		nBytes = len(data)
		if nBytes <38:
			raise ValueError("Invalid Length %d"%len(data))
		
		self.imei = int(data[10:25])
		packN, = struct.unpack("<H",data[26:28])
		print "IMEI:",self.imei
		print "Seq", packN
		log = open('satlog_%d'%packN,"w")
		log.write(data)
		log.close() 
		data = data[38:]
		avl = SGAvl.objects.get(imei= self.imei)
		while data:
			print "Payloadlen :", len(data)
			ym,tm = struct.unpack("<BH",data[0:3])
			lat,lon = struct.unpack("<ff",data[3:11])
			year = (ym>>4)+2007
			month = ym & 0x0F
			day = (tm>>11) & 0x1F
			hour = (tm>>6) & 0x1F
			minute = tm & 0x3F
			dt = datetime(year,month,day,hour,minute,tzinfo=utc)
			print "Date:",dt
			print "Lat,Lon: ", lat,lon
			pos = Point(lon,lat)		
			avl.position = pos
			avl.lastLog = avl.date = dt
			track = Event(imei = avl,type = "TRACK",position = pos, date = dt, speed = 0, course = 0, altitude = 0, odom =0)
			avl.save()
			track.save()		
			data = data[12:]
		

			
	def finish(self):
		pass

if __name__ == "__main__":
	try:
		server = SocketServer.ThreadingTCPServer(('', 15557), SATRequestHandler)
		#server = SocketServer.UDPServer(('', 15557), CFERequestHandler)
		print "_"*80
		print "Server Started."
		print "-"*80
		sys.stdout.flush()
		server.serve_forever()
	except KeyboardInterrupt:
		print "_"*80
		print "Server received signal, exiting."
		print "-"*80
		sys.stdout.flush()
