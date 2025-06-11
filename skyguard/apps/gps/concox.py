#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket,sys,io,traceback
import SocketServer
import datetime,pytz
import crcmod,struct
import time,os

CrcFun = crcmod.predefined.mkPredefinedCrcFun("x-25")
DATE_FORMAT = "%d/%m/%y %H:%M:%S"
KillThreads = False
RECV_TMOUT = 2
SOCK_TMOUT = 360
log = None

os.environ['DJANGO_SETTINGS_MODULE'] = 'sites.www.settings'
path = '/home/django13/skyguard'
if path not in sys.path:
	sys.path.append(path)

from django.db import transaction, DatabaseError, IntegrityError, connection
from django.contrib.gis.geos import Point
from django.conf import settings
import gps.tracker.models as tracker
import gps.gprs.models as gprs

DefaultHarness = tracker.SGHarness.objects.get(name = "default")

def bcdDigits(chars):
    for char in chars:
        char = ord(char)
        for val in (char >> 4, char & 0xF):
            yield val
            
def decodeImei(data):
    imei = 0
    for i in bcdDigits(data):
        imei *=10
        imei +=i
    return imei
    
class Server(SocketServer.BaseRequestHandler ):

    def FindDev(self,imei):
        # find device or create it
        try:
            self.dev = tracker.SGAvl.objects.get(imei = imei)
        except tracker.SGAvl.DoesNotExist:
            if self.imei < 10000000000000 or imei >899999999999999:
                print >> self.stdout, "Invalid device imei. Not creating..."
                self.dev = None
            else:
                self.dev = tracker.SGAvl(imei=self.imei,name = "%015d"%self.imei, 
                    harness = DefaultHarness, comments ="", icon = "jettaicon.png")
                self.dev.save()
                print >> self.stdout, "Created device %s"%self.dev.name
    
    def GetMccMnc(self,data):
        mcc,mnc = struct.unpack(">HH",data[:4])
        if mcc &0x8000:
            data = data[4:]
        else:
            data = data[3:]
            mnc = mnc >>8
        return mcc,mnc,data
        
    def GetLacID(self,data,f4g):
        if f4g:
            lac,ci = struct.unpack(">IQ",data[:12])
            return lac,ci,data[12:]
        else:
            lac,ci1,ci2 = struct.unpack(">HBH",data[:5])
            ci = (ci1<<16) | ci2
            return lac,ci,data[5:]

    def GetLacIDrssi(self,data,f4g):
        if f4g:
            lac,ci,rssi = struct.unpack(">IQB",data[:13])
            return lac,ci,rssi,data[13:]
        else:
            lac,ci1,ci2,rssi = struct.unpack(">HBHB",data[:6])
            ci = (ci1<<16) | ci2
            return lac,ci,rssi,data[6:]

    def GetUTC(self,data):
        utc = struct.unpack("BBBBBB",data)
        return datetime.datetime(2000+utc[0], *utc[1:], tzinfo = pytz.UTC)

    def UpdateLastLog(self):
        self.dev.lastLog = datetime.datetime.now(tz=pytz.UTC)
        self.dev.save()

    def handleGps(self):
        utc = self.GetUTC(self.payload[:6])
        ns,lat,lon,speed,cs = struct.unpack(">BIIBH",self.payload[6:18])
        lat /= 1800000.0
        lon /= 1800000.0
        mcc,mnc,rest = self.GetMccMnc(self.payload[18:])
        course = cs & 0x03FF
        if cs &0x0400 == 0: lat = -lat
        if cs &0x0800: lon = -lon
        lac,ci,rest = self.GetLacID(rest,self.proto == 0xA0)
        acc,dum,drl = struct.unpack(">BBB",rest[:3])
        if rest[3:]: ms, = struct.unpack(">I",rest[3:7])
        else:        ms = 0
        if self.proto == 0x2D:
            self.SendPacket(0x2D,"")
        if cs & 0x1000:
            print >> self.stdout, "=== GPS FIX ({:02X})===".format(self.proto)
            print >> self.stdout , "{} GPS Position {:10.7} , {:10.7} @{} Sats Course={} speed={} ACC={}".format(utc.isoformat(),lat, lon, ns&0x0f, course, speed, acc)
            print >> self.stdout , "  from cell {}.{}:{}-{}. dum={} drl={} ms={}".format(mcc,mnc,lac,ci,dum,drl,ms)
            # Create track event and update
            ev = tracker.Event(type="TRACK", imei=self.dev, position = Point(lon,lat),
                date = utc,	speed = speed, course = course, altitude = 0, odom = self.dev.odom)
            ev.save()
            self.dev.position = ev.position
            self.dev.date = utc
            self.dev.speed = speed
            self.dev.course = course
            self.UpdateLastLog()
        else:
            print >> self.stdout, "=== GPS NOT FIXED ({:02X})===".format(self.proto)
            print >> self.stdout , "{} GPS Position {:10.7} , {:10.7} @{} Sats Course={} speed={} ACC={}".format(utc.strftime(DATE_FORMAT),lat, lon, ns&0x0f, course, speed, acc)
            print >> self.stdout , "  from cell {}.{}:{}-{}. dum={} drl={} ms={}".format(mcc,mnc,lac,ci,dum,drl,ms)
            print >> self.stdout , "DISCARDED ******"

    def handleWifi(self):
        utc = self.GetUTC(self.payload[:6])
        mcc,mnc,rest = self.GetMccMnc(self.payload[6:])
        cells = []
        for i in range(7):
            lac,ci,rssi,rest = self.GetLacIDrssi(rest,self.proto == 0xA2)
            cells.append((lac, ci, rssi))
        ta = ord(rest[0])
        nWifi = ord(rest[1])
        mac1 = rest[2:8]
        wifi1 = ord(rest[8])
        mac2 = rest[9:15]
        wifi2 = ord(rest[15])
        print >> self.stdout, "UTC: ", utc.isoformat()
        print >> self.stdout, "MCC/MNC {}-{}".format(mcc,mnc)
        for i in range(7):
            print >> self.stdout, "LAC {} CI {} RSSI {}".format(*cells[i])
        print >> self.stdout, "WiFis: ",nWifi
        print >> self.stdout, "Wifi {}-{}".format(mac1.encode("hex"),wifi1)
        print >> self.stdout, "Wifi {}-{}".format(mac2.encode("hex"),wifi2)
    
    def handleAlarm(self):
        mcc,mnc,rest = self.GetMccMnc(self.payload)
        lac,ci,rest = self.GetLacID(rest,self.proto == 0xA5)
        ti, vl, ss, alert, lang = struct.unpack(">BBBBB",rest)
        print >> self.stdout, "ALERT from cell {}.{} {}-{}: TI={} {}/{} #{:02X} Lang:{}".format(mcc,mnc,lac,ci,ti,vl,ss,alert,lang)
        if self.proto == 0xA5:
            self.SendPacket(0x26,"")
        self.UpdateLastLog()


    def SendPacket(self,proto,payload):
        plen = len(payload)+5
        packet = struct.pack(">HBB",0x7878, plen, proto)+payload+struct.pack(">H",self.isn)
        crc = CrcFun(packet[2:])
        packet += struct.pack(">HH",crc,0x0D0A)
        self.request.send(packet)
        print >> self.stdout, "SENT: ",packet.encode("hex")

    def GetPacket(self,data):
        if len(data) < 10:
            raise ValueError("Invalid short packet")
        self.head, = struct.unpack(">H",data[:2])
        if self.head == 0x7878:
            self.len = ord(data[2])
            if len(data) < self.len+5:
                raise ValueError("Invalid len {} < {}".format(len(data),self.len+5))
            crc = CrcFun(data[2:1+self.len]) 
            self.proto = ord(data[3])
            self.payload = data[4:self.len-1]
            self.tail, = struct.unpack(">H",data[3+self.len:5+self.len])
            self.packet = data[:5+self.len]
            print >> self.stdout, "RECV: ",data[:5+self.len].encode("hex")
            data = data[5+self.len:]
        elif self.head == 0x7979:
            self.len, = struct.unpack(">H",data[2:4])
            if len(data) < self.len+6:
                raise ValueError("Invalid len {} < {}".format(len(data),self.len+6))
            crc = CrcFun(data[2:2+self.len]) 
            self.proto = ord(data[4])
            self.payload = data[5:self.len]
            self.tail, = struct.unpack(">H",data[4+self.len:6+self.len])
            self.packet = data[:6+self.len]
            print >> self.stdout, "RECV: ",data[:6+self.len].encode("hex")
            data = data[6+self.len:]
        else:
            raise ValueError("Invalid HEAD {:04X}".format(self.head))
        if self.tail != 0x0D0A:
            raise ValueError("Invalid TAIL {:04X}".format(self.tail))
        self.isn, pcrc = struct.unpack(">HH",self.packet[-6:-2]);
        if pcrc != crc:
            raise ValueError("Invalid CRC {:04X} != {:04X}".format(pcrc,crc))
        return data
    
    def handlePackets(self,data):
        while data:
            data = self.GetPacket(data)
            if self.proto == 0x01: # Login Packet
                self.imei = decodeImei(self.payload[:8])
                self.FindDev(self.imei)
                ti,tz = struct.unpack(">HH",self.payload[8:12])
                print >> self.stdout,"Login from {} TI={:04X} TZ={:04X}".format(self.imei,ti,tz)
                self.SendPacket(0x01,"")
                self.UpdateLastLog()
            elif self.proto == 0x19 or self.proto == 0xA5: # Alarm packet
                self.handleAlarm()
            elif self.proto == 0x22 or self.proto == 0x2D or self.proto == 0xA0: #GPS Location
                self.handleGps()
            elif self.proto == 0x23: #Heartbeat packet
                tic,volts,gsmss,pad = struct.unpack(">BHBH", self.payload)
                print >> self.stdout, "Heartbeat {:02X}-{:3.2}-{}-{:04X}".format(tic,volts/100.0,gsmss,pad)
                self.SendPacket(0x23,"")
                self.UpdateLastLog()
            elif self.proto == 0x2C or self.proto == 0xA2: #WIFI Info over 2G
                self.handleWifi()
                self.UpdateLastLog()
            elif self.proto == 0x8A: #Time calibration
                dt = datetime.datetime.now(pytz.UTC)
                payload = struct.pack(">BBBBBB",dt.year%100,dt.month,dt.day,dt.hour,dt.minute,dt.second)
                self.SendPacket(0x8A,payload)
                print >> self.stdout, "Time calibrated to: ", dt.strftime(DATE_FORMAT)
            elif self.proto == 0x94: # General Info Packet
                self.UpdateLastLog()
                if ord(self.payload[0]) == 0:
                    print >> self.stdout, "External Voltage: ",struct.unpack(">H",self.payload[1:3])[0]/100.0
                elif ord(self.payload[0]) == 4:
                    print >> self.stdout, "Info: ",self.payload[1:]
                elif ord(self.payload[0]) == 10:
                    print >> self.stdout, "IMEI:  ",decodeImei(self.payload[1:9])
                    print >> self.stdout, "IMSI:  ",decodeImei(self.payload[9:17])
                    print >> self.stdout, "ICCID: ",decodeImei(self.payload[17:27])
                else:
                    print >> self.stdout, "**** :", self.payload.encode("hex")
            else: 
                raise ValueError("Invalid packet protocol {:02X}".format(self.proto))
    
    def flushOutput(self):
        sys.stdout.write(self.stdout.getvalue())
        sys.stdout.flush()
        if log:
            log.write(self.stdout.getvalue())
        self.stdout.close()
        self.stdout = io.BytesIO()
    
    def handle(self):
        tmouts = 0
        self.packet = ""
        self.data = ""
        while True:
            try:
                self.data += self.request.recv(2048)
            except socket.timeout:
                nRecv = len(self.data)
                if KillThreads: 
                    return
                if nRecv:
                    self.handlePackets(self.data)    ## Process packets first
                    print >> self.stdout, '{}:{} processed {} bytes ==============='.format(self.client_address[0],self.client_address[1],nRecv)
                    self.packet = self.data = "" 
                    tmouts = 0
                    self.flushOutput()
                else:
                    tmouts += 1
                    if tmouts >= (SOCK_TMOUT/RECV_TMOUT):
                        print >> self.stdout, self.client_address, '** Socket timed out ***'
                        return                
            except:
                print >> self.stdout,"**** Error processing data: *****"
                print >> self.stdout,"**** Received: ", self.data.encode("hex")            
                print >> self.stdout,"**** Packet: ", self.packet.encode("hex")            
                print >> self.stdout,traceback.format_exc()
                self.request.close()       

    def setup(self):
        self.request.settimeout(RECV_TMOUT)
        self.timeck = datetime.datetime.now()
        self.stdout = io.BytesIO()
        print >> self.stdout, "*"*80
        print >> self.stdout, datetime.datetime.now().ctime(), self.client_address, 'connected!'
        self.request.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,1)
        self.login = True

    #@transaction.commit_manually()
    def finish(self):
        print >> self.stdout, datetime.datetime.now().ctime(),self.client_address, 'disconnected!'
        print >> self.stdout, "*"*80
        self.flushOutput()

if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            log = open(sys.argv[1],"w")
            print "Opened log file ",sys.argv[1]
        server = SocketServer.ThreadingTCPServer(('', 55300), Server)
        print "_"*80
        print "Server Started. ",datetime.datetime.now().isoformat()
        print "-"*80
        if log:
            print >> log, "_"*80
            print >> log, "Server Started. ",datetime.datetime.now().isoformat()
            print >> log, "-"*80
            log.flush()
        sys.stdout.flush()
        server.serve_forever()
    except KeyboardInterrupt, SystemExit:
        KillThreads = True
        time.sleep(RECV_TMOUT*2)
        print "_"*80
        print "Server received signal, exiting."
        print "-"*80
        sys.stdout.flush()
        log.close()
