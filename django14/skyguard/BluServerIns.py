#!/usr/bin/python
# -*- coding: utf-8 -*-
# Bluetooth AVL server

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
from PyCRC.CRCCCITT import CRCCCITT

PKTID_LOGIN    =0x01
PKTID_PING     =0x02
PKTID_DEVINFO  =0x03
PKTID_DATA     =0x04

RSPID_SESSION  =0x10
RSPID_LOGIN    =0x11

CMDID_DEVINFO  =0x20
CMDID_DATA     =0x21
CMDID_ACK      =0x22

RECID_TRACKS   =0x30
RECID_PEOPLE   =0x31

MOTORio     =(1<<0)
IGNio       =(1<<1)
PANICio     =(1<<2)
CHRGio      =(1<<3)
PWRio       =(1<<4)

crc = CRCCCITT('1D0F')

os.environ['DJANGO_SETTINGS_MODULE'] = 'sites.www.settings'
path = '/home/django13/skyguard'
if path not in sys.path:
    sys.path.append(path)

from django.db import transaction, DatabaseError, IntegrityError, connection
from django.contrib.gis.geos import Point
from django.conf import settings
import gps.tracker.models as tracker
import gps.udp.models as udp

settings.DEBUG = False
SESSION_EXPIRE = timedelta(hours = 10)

class BLURequestHandler(SocketServer.BaseRequestHandler ):
	def UnpackPos(self,data):
		"""
		Unpack a gps position record
		"""
		ct,lat,lon,speed,inputs = struct.unpack("<IiiBB",data)
		dt = datetime.fromtimestamp(ct,utc)
		if abs(dt-datetime.now(utc)>timedelta(days=20)):
			dt = datetime.now(utc)
			print >> self.stdout, "Invalid time in position"
			
		return {'date': dt,'pos': Point(lon/10000000.0,lat/10000000.0),'speed': speed, 'inputs': inputs}

	def Login(self):
		if self.nBytes != 15:
			print >> self.stdout, "Invalid LOGIN size: {0}".format(self.nBytes)
		imei, = struct.unpack("<Q",self.data[1:9])
		mac, = struct.unpack("<Q", self.data[9:15]+'\x00\x00')
		print >> self.stdout, "Session request from IMEI: {0:015d} MAC ID: {1:012X}".format(imei,mac)
		try:
			avl = tracker.SGAvl.objects.get(imei = imei)
		except tracker.SGAvl.DoesNotExist:
			print >> self.stdout, "Device not found. Creating..."
			harness = tracker.SGHarness.objects.get(name = "default")
			avl = tracker.SGAvl(imei=imei,name = "{:015d}".format(imei), harness = harness, comments ="")
			avl.save()
		#delete old sessions
		sessions = udp.UdpSession.objects.filter(imei = avl)
		if sessions:
			sessions.delete()
		expires = self.timeck + SESSION_EXPIRE
		session = udp.UdpSession(imei = avl, expires = expires, host = self.host, port = self.port)
		session.save()
		if not avl.comments:
			response = struct.pack("<BLB",RSPID_SESSION,session.session,CMDID_DEVINFO)	# Refresh dev info
		else:
			response = struct.pack("<BLB",RSPID_SESSION,session.session,CMDID_DATA)
		self.socket.sendto(response, self.client_address)
		print >> self.stdout, "Sent login response"

	def FindSession(self):
		self.sessionNo, = struct.unpack("<L",self.data[1:5])
		self.session = None
		try:
			self.session = udp.UdpSession.objects.get(session = self.sessionNo)
			self.session.expires = self.timeck + SESSION_EXPIRE
			self.session.host = self.host
			self.session.port = self.port
			self.avl = tracker.SGAvl.objects.get(imei = self.session.imei.imei)
			print >> self.stdout, "AVL:", self.avl
			self.session.save()
		except udp.UdpSession.DoesNotExist: 
			print >> self.stdout, "Unknown session #", self.sessionNo
		except: 
			raise
		
	def SendLogin(self):
		self.socket.sendto(chr(RSPID_LOGIN), self.client_address)
		print >> self.stdout, "Sent login request."
	
	def Ping(self):
		pos = self.UnpackPos(self.data[5:19])
		print >> self.stdout ," Inputs: " , pos['inputs']
		self.avl.position = pos["pos"]
		self.avl.speed = pos["speed"]
		self.avl.lastLog = self.avl.date = pos["date"]
		if pos['inputs']&MOTORio:
                    self.avl.outputs = 0  #MOTOR ON
                else:
                    self.avl.outputs = 15
                if pos['inputs']&IGNio:
                    self.avl.inputs = 4
                else:
                    self.avl.inputs = 0
                if pos['inputs' ]&PWRio:
                    self.avl.alarms = 0
                else:
                    self.avl.alarms = 1
		self.avl.save()
		response = struct.pack("<BLBB",RSPID_SESSION,self.session.session,CMDID_ACK,0)
		#response = struct.pack("<BLB",RSPID_SESSION,self.session.session,CMDID_DATA)
		self.socket.sendto(response, self.client_address)
		print >> self.stdout, "Got PING w/position from ", self.avl.imei," Position: ",self.avl.position
		
	def DevInfo(self):
		print >> self.stdout, "Got DevInfo response from", self.avl.imei
		self.avl.comments = "INFO OK"
		self.avl.save()
		response = struct.pack("<BLBB",RSPID_SESSION,self.session.session,CMDID_ACK,0)
		self.socket.sendto(response, self.client_address)
	
	def UnpackTracks(self,data):
		positions = []
		while len(data)>=14:
			pos = self.UnpackPos(data[:14])
			data = data[14:]
			positions.append(pos)
		print >> self.stdout, "Unpacked {0} positions.".format(len(positions))
		evs = tracker.Event.objects.filter(imei = self.avl, date__range = (positions[0]["date"],positions[-1]["date"]))
		if positions and evs:
			print >> self.stdout, "Duplicate track records found"
		elif positions:
			query = 'INSERT INTO tracker_event (imei_id , type, position, speed, course, date, odom, altitude ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) '
			values = []
			for pos in positions:
				p = "SRID=4326; POINT({0} {1})".format(pos['pos'].x,pos['pos'].y)
				values.append((self.avl.imei, "TRACK", p, pos['speed'], 0, pos['date'], 0,0))
			self.queries.append((query,values))
			self.lastPos = positions[-1]

	def UnpackTof(self,data):
		"""
		Unpack a tof counter record
		"""
		ct,countIn,countOut,mac1,mac2= struct.unpack("<IIIIH",data)
		dt = datetime.fromtimestamp(ct,utc)
		mac = "{:012X}".format((mac2 << 32) | mac1)
		if abs(dt-datetime.now(utc)>timedelta(days=20)):
			dt = datetime.now(utc)
			print >> self.stdout, "Invalid time in people"
		return {'date': dt, 'in': countIn, 'out': countOut, 'id': mac}
	
	def UnpackPeople(self,data):
		people = []
		while len(data) >= 18:
			people.append(self.UnpackTof(data[:18]))
			data = data[18:]
		print >> self.stdout, "Unpacked {0} tof records.".format(len(people))
		query = '''INSERT INTO tracker_psiweightlog (imei_id , sensor, date, psi1, psi2 ) VALUES (%s, %s, %s, %s, %s) '''
		values = []
		for i in people:
			#last = tracker.PsiWeightLog.objects.filter(sensor = i["id"], date__gte = i["date"])[:1]
			dupe = tracker.PsiWeightLog.objects.filter(sensor = i["id"], date = i["date"])
			if not dupe:
				values.append((self.avl.imei, i["id"], i["date"], i["in"], i["out"]))
		if values:
			self.queries.append((query,values))
		if len(values) != len(people):
			print >> self.stdout, "Dropped {0} TOF duplicates.".format(len(people)-len(values))
		
	def RxData(self):
		if crc.calculate(self.data) != 0:
			print >> self.stdout, "CRC Failiure. Discarding packet"
			return
		self.lastPos = None
		data = self.data[5:-2]
		records = []
		id0 = id1 = 0
		while data:
			if len(data)<=8:
				print >> self.stdout, "Invalid record header, len=", len(data)
				data =''
			else:
				id,size = struct.unpack("<II",data[:8])
				if size>248:
					print >> self.stdout, "Invalid record size =", size
					data =''
				else:
					id1 = id
					if not id0:
						id0 = id
					rec = data[8:8+size]
					data = data[8+size:]
					records.append(rec)
		if id0:
			print >> self.stdout, "Extracted {0} records.".format(len(records))
			response = struct.pack("<BIBBII",RSPID_SESSION,self.session.session,CMDID_ACK,len(records),id0,id1)
			self.socket.sendto(response, self.client_address)
			self.queries = []
			for rec in records:
				id = ord(rec[0])
				if id == RECID_TRACKS:
				    self.UnpackTracks(rec[1:])
				elif id == RECID_PEOPLE:
					self.UnpackPeople(rec[1:])
				else:
					print >> self.stdout, "Invalid RECID: {0:02X}".format(id)
			if self.lastPos:
				self.avl.position = self.lastPos["pos"]
				self.avl.speed = self.lastPos["speed"]
				self.avl.date = self.lastPos["date"]
                                if self.lastPos['inputs']&MOTORio:
                                    self.avl.outputs = 0  #MOTOR ON
                                else:
                                    self.avl.outputs = 15
                                if self.lastPos['inputs']&IGNio:
                                    self.avl.inputs = 0
                                else:
                                    self.avl.inputs = 1
                                if self.lastPos['inputs' ]&PWRio:
                                    self.avl.alarms = 0
                                else:
                                    self.avl.alarms = 1
			self.avl.lastLog = self.timeck
			self.avl.save()
			cursor = connection.cursor()
			for i in self.queries:
				cursor.executemany(i[0],i[1])
			transaction.commit_unless_managed()
			connection.close()
						
	def setup(self):
		self.timeck = datetime.now(utc)
		self.localtime = datetime.now(timezone(settings.TIME_ZONE))
		self.stdout = io.BytesIO()
		print >> self.stdout, "*"*80
		print >> self.stdout, self.localtime.ctime(), self.client_address, 'connected!'

	def handle(self):
		self.imei = None
		self.socket = self.request[1]
		self.data = self.request[0]
		self.nBytes = len(self.data)
		self.host = self.client_address[0]
		self.port = self.client_address[1]
		print >> self.stdout, "RX len = {0} from {1}:{2}".format(len(self.data), self.host, self.port)
		try: 
			id = ord(self.data[0])
			if id == PKTID_LOGIN:
				self.Login()
			else:
				self.FindSession()
				if not self.session:
					self.SendLogin()
				else:					
					if id == PKTID_PING:
						self.Ping()
					elif id == PKTID_DEVINFO:
						self.DevInfo()
					elif id == PKTID_DATA:
						self.RxData()
					else:
						print >> self.stdout,"Invalid token {0}".format(id)
						#socket.sendto(response,self.client_address)
		finally: 
			pass
			
	def finish(self):
		dt = datetime.now(utc)-self.timeck
		print >> self.stdout, "Finished processing packet in {0.seconds}.{0.microseconds:06d} seconds".format(dt)
		sys.stdout.write(self.stdout.getvalue())
		sys.stdout.flush()

if __name__ == "__main__":
	try:
		server = SocketServer.ThreadingUDPServer(('', 61000), BLURequestHandler)
		#server = SocketServer.UDPServer(('', 50100), BLURequestHandler)
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
