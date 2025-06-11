#!/usr/bin/python
# -*- coding: utf-8 -*-
# Meiligao server

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
import crcmod

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
from gps.tracker.models import SGAvl, Event, SGHarness
import gps.gprs.models as gprs

settings.DEBUG = False

def nmea2deg(str):
	return float(str[:-7])+float(str[-7:])/60.0
	
def nmea2date(hms,mdy):
	h = int(hms[:2])
	m = int(hms[2:4])
	s = int(hms[4:6])
	d = int(mdy[:2])
	mn = int(mdy[2:4])
	y = int(mdy[4:])+2000
	dt = datetime(y,mn,d,h,m,s,tzinfo=utc)
	return dt

class MeiligaoRequestHandler(SocketServer.BaseRequestHandler ):
	def FindOrCreateDev(self):
		# find device or create it
		try:
			self.dev = SGAvl.objects.get(imei = self.imei)
			self.harness = self.dev.harness
		except SGAvl.DoesNotExist:
			try:
				self.harness = SGHarness.objects.get(name = "default")
			except tracker.SGHarness.DoesNotExist:
				print >> self.stdout, ">>>> Creating default harness"
				self.harness = SGHarness(name = "default",
					in00 = 'Pánico', in01 = 'Ignición', in02 ='i02', in03 = 'i03',
					in04 ='i04', in05 = 'i05', in06 ='BAT_DOK', in07 = 'BAT_CHG',
					in08 ='BAT_FLT', in09 = 'i09', in10 ='i10', in11 = 'i11',
					in12 ='i12', in13 = 'i13', in14 ='i14', in15 = 'i15',
					out00 = 'Motor', out01 = '', out02 = '', out03 = '',
					out04 = '', out05 = '', out06 = '', out07 = '',
					out08 = '', out09 = '', out10 = '', out11 = '',
					out12 = '', out13 = '', out14 = '', out15 = '',
					inputCfg = '03070000000007000700000000000000') #	{3,7,0,0,0,0,7,0,7}
				self.harness.save()
			self.dev = SGAvl(imei=self.imei,name = "%015d"%self.imei, harness = self.harness, comments ="")
			self.dev.save()
			print ">>>> Created device %s"%self.dev.name

	def setup(self):
		print "*"*80
		print datetime.now().ctime(), self.client_address, 'connected!'

	def handle(self):
		self.imei = None
		data = self.request[0]
		socket = self.request[1]
		nBytes = len(data)
		# Sanity Check
		if data[:2] != '$$' and data[-2:] !='\r\n':
			print "Invalid packet from", self.client_address
			return
		# Check crc
		crc = crcmod.mkCrcFun(0x11021,initCrc=0xFFFF, rev=False)
		pcrc, = struct.unpack(">H",data[-4:-2])
		dlen, = struct.unpack(">H",data[2:4])
		ecrc = crc(data[:-4])
		if pcrc != ecrc:
			print "Invalid CRC from", self.client_address
			print "Expected %04x, got %04x"%(ecrc,pcrc)
			return
		if dlen != nBytes:
			print "Invalid data length from", self.client_address
			print "Expected %04x, got %04x"%(dlen,nBytes)
			return
		idhex = data[4:11]
		self.imei = self.getId(idhex)
		command, = struct.unpack(">H",data[11:13])
		payload = data[13:-4]
		print "Received command %04x"%command
		print "Payload: ",len(payload),payload
		print "ID: ", self.imei
		self.FindOrCreateDev()
		# Parse Command
		if command == 0x9955:
			fields = payload.split('|')
			gprmc = fields[0].split(',')
			lon = nmea2deg(gprmc[4])
			if gprmc[5] == "W":
				lon = -lon
			lat = nmea2deg(gprmc[2])
			if gprmc[3] == 'S':
				lat = -lat
			dt = nmea2date(gprmc[0],gprmc[8])
			pos = Point(lon,lat)
			self.dev.position = pos
			self.dev.latLog = self.dev.date = dt
			track = Event(imei = self.dev,type = "TRACK",position = pos, date = dt, speed = 0, course = 0, altitude = 0, odom =0)
			self.dev.save()
			track.save()
		elif command == 0x5000:
			pass
		else :
			print "Invalid command received from ID %d: 0x%04x"%(self.imei,command)
			
	def finish(self):
		pass
		
	def getId(self,data):
		hexs = []
		for i in data:
			hexs.append(ord(i)>>4)
			hexs.append(ord(i)&15)
		id = 0
		for i in hexs:
			if (i!=15):
				id = id *10 +i
		return id

if __name__ == "__main__":
	try:
		server = SocketServer.UDPServer(('', 62000), MeiligaoRequestHandler)
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
