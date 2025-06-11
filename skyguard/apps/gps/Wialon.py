#!/usr/bin/python
# -*- coding: utf-8 -*-
# Bluetooth AVL server

import socket
import struct
import SocketServer
import string
import time
import threading
import queue
import sys
import types
import errno
from datetime import datetime,timedelta
from pytz import utc, timezone
import os,io
import subprocess
import cyacd

import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

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
CMDID_MOTORON  =0x23
CMDID_MOTOROFF =0x24
CMDID_RESET    =0x25

BTLID_ENTER    =0x28
BTLID_DATA     =0x29
BTLID_EXIT     =0x2A

RECID_TRACKS   =0x30
RECID_PEOPLE   =0x31

MOTORio     =(1<<0)
IGNio       =(1<<1)
PANICio     =(1<<2)
CHRGio      =(1<<3)
PWRio       =(1<<4)
DELTAio     =(1<<7)

SENDDELAY  = 0.15

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

#from __future__ import with_statement

settings.DEBUG = False
SESSION_EXPIRE = timedelta(hours = 10)

def nmeaDegrees(deg):
	d1 = abs(int(deg))
	d2 = abs(deg - int(deg))*60
	return "{}{:08.5f}".format(d1,d2)
	
def nmeaLat(deg):
	if deg<0: 
		return ';S;'
	else:
		return ';N;'

def nmeaLon(deg):
	if deg<0: 
		return ';W;'
	else:
		return ';E;'
		
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
		if not avl.comments or (not 'INFO OK' in avl.comments):
			response = struct.pack("<BLB",RSPID_SESSION,session.session,CMDID_DEVINFO)	# Refresh dev info
			print >> self.stdout, "Sent login response w/DevInfo"
		else:
			response = struct.pack("<BLB",RSPID_SESSION,session.session,CMDID_DATA)
			print >> self.stdout, "Sent login response"
		time.sleep(SENDDELAY)
		self.socket.sendto(response, self.client_address)
		self.avl = avl

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
		time.sleep(SENDDELAY)
		self.socket.sendto(chr(RSPID_LOGIN), self.client_address)
		print >> self.stdout, "Sent login request."
	
	def SetPos(self,pos):
		if pos['inputs']&MOTORio:
			self.avl.outputs = 0  #MOTOR ON
		else:
			self.avl.outputs = 15
		if pos['inputs']&IGNio:
			self.avl.inputs = 6
		else:
			self.avl.inputs = 0
		if pos['inputs' ]&PWRio:
			self.avl.alarms = 0
		else:
			self.avl.alarms = 1
		self.avl.position = pos["pos"]
		self.avl.speed = pos["speed"]
		self.avl.lastLog = self.avl.date = pos["date"]
		self.avl.save()
		print >> self.stdout,"-- Inputs:",self.avl.inputs," Outputs:",self.avl.outputs
	
	def Ping(self):
		pos = self.UnpackPos(self.data[5:19])
		print >> self.stdout ," Inputs: " , pos['inputs']
		self.SetPos(pos)
		response = struct.pack("<BLBB",RSPID_SESSION,self.session.session,CMDID_ACK,0)
		#response = struct.pack("<BLB",RSPID_SESSION,self.session.session,CMDID_DATA)
		time.sleep(SENDDELAY)
		self.socket.sendto(response, self.client_address)
		print >> self.stdout, "Got PING, Position: {0.y},{0.x}".format(self.avl.position)
		
	def DevInfo(self):
		print >> self.stdout, "Got DevInfo response from", self.avl.imei
		print >> self.stdout, "Info:\n", self.data[5:]
		self.avl.comments = "INFO OK\n" + self.data[5:]
		self.avl.save()
		response = struct.pack("<BLBB",RSPID_SESSION,self.session.session,CMDID_ACK,0)
		time.sleep(SENDDELAY)		
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
				if pos['inputs'] & DELTAio:
					io = tracker.IOEvent(type = "IO_FIX", imei=self.avl,
						position = pos['pos'],date = pos['date'], speed = 0, course = 0, odom = 0, altitude = 0,
						inputs = pos['inputs'] & (~DELTAio), outputs = pos['inputs'] & MOTORio, changes ='')
					delta = pos['speed']
					if delta == IGNio:
						io.changes = "IGN ON." if pos['inputs'] & IGNio else "IGN OFF."
					elif delta == MOTORio:
						io.changes = "MOTOR ON." if pos['inputs'] & MOTORio else "MOTOR OFF."
					elif delta == PANICio:
						io.changes = "PANIC ON." if pos['inputs'] & PANICio else "PANIC OFF."
					elif delta == CHRGio:
						io.changes = "CHARGER ON." if pos['inputs'] & CHRGio else "CHARGER OFF."
					elif delta == PWRio:
						io.changes = "POWER ON." if pos['inputs'] & PWRio else "POWER OFF."
					io.save()
					print >> self.stdout, "IO_RECORD {} - {:02X} {:02X}".format(io.changes,pos['inputs'],pos['speed'])
					if self.avl.owner and self.avl.owner.email and delta == PANICio:
						try:
							print >> self.stdout, "Into email send."
							port = 465
							password = '4^4Lyh7nUtys'
							sender = "alertas@zoho.com"
							receiver = self.avl.owner.email.split()
							print >> self.stdout, sender, receiver, password
							message = MIMEMultipart("alternative")
							html = u"""\
<html>
  <body>
	<p>El sistema ha detectado la activaci&oacute;n del bot&oacute;n de p&aacute;nico de la unidad:<br>
	   <a href="http://www.google.com/maps/search/{2},{1}">{0}</a>.
	</p>
  </body>
</html>""".format(self.avl.name,io.position.x,io.position.y)
							message["Subject"] = Header(u"Botón de Pánico Activado","utf-8")
							message["From"] = sender
							message["To"] = ",".join(receiver)
							message.attach(MIMEText(html,"html"))
							print >> self.stdout , "Message Built"
							try:
								server = smtplib.SMTP_SSL("smtp.zoho.com")
								server.login("alertas@zoho.com",password)
								server.sendmail(sender,receiver,message.as_string())
								print >> self.stdout, "Sent email to:", repr(receiver)
							finally:
								server.quit()
						except Exception as e:
							print >> self.stdout, ">>>> Unknown exception"
							print >> self.stdout, e
							print >> self.stdout, repr(e)
							raise	
				else:
					p = "SRID=4326; POINT({0} {1})".format(pos['pos'].x,pos['pos'].y)
					values.append((self.avl.imei, "TRACK", p, pos['speed'], 0, pos['date'], 0,0))
				### WIALON ###
				w = pos['date'].strftime("%d%m%y;%H%M%S;")+nmeaDegrees(pos['pos'].y)+nmeaLat(pos['pos'].y)
				w += nmeaDegrees(pos['pos'].x)+nmeaLon(pos['pos'].x)
				w += "{};NA;NA;NA".format(pos['speed'])
				if pos['inputs'] & DELTAio:
					w = "#D#" + w + ";NA;NA;NA;;NA;"
					if delta == IGNio:
						w += "IGN:1:1" if pos['inputs'] & IGNio else "IGN:1:0"
					elif delta == MOTORio:
						w += "MOTOR:1:1" if pos['inputs'] & MOTORio else "MOTOR:1:0"
					elif delta == PANICio:
						w += "SOS:1:1" if pos['inputs'] & PANICio else "SOS:1:0"
					elif delta == CHRGio:
						w += "CHARGE:1:1" if pos['inputs'] & CHRGio else "CHARGE:1:0"
					elif delta == PWRio:
						w += "POWER:1:1" if pos['inputs'] & PWRio else "POWER:1:0"			
					w +="\r\n"
				else:
					w = "#SD#" + w + "\r\n"
				self.wialon.append(w)
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
			time.sleep(SENDDELAY)
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
				self.SetPos(self.lastPos)
			self.avl.lastLog = self.timeck
			self.avl.save()
			cursor = connection.cursor()
			for i in self.queries:
				cursor.executemany(i[0],i[1])
			transaction.commit_unless_managed()
			connection.close()
			### WIALON ###
			if self.wialon:
				self.wialon.insert(0,"#L#{};NA\r\n".format(self.avl.imei))
				theQueue.put(self.wialon)
			for i in self.wialon:
				print >> self.stdout, "WIALON:",i[:-2]
						
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
		self.wialon = []
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
					elif id == BTLID_ENTER:
						self.avl.fwFile = '0'
						self.avl.save()
						print >> self.stdout,"Bootloader Entered. First row = ",struct.unpack('<H',self.data[5:7])[0]
					elif id == BTLID_DATA:
						row = struct.unpack('<H',self.data[5:7])[0]
						self.avl.fwFile = str(row+1)
						self.avl.save()
						print >> self.stdout,"Bootloader Data OK. Row = ",self.avl.fwFile
					elif id == BTLID_EXIT:
						row,err = struct.unpack("<HB",self.data[5:8])
						self.avl.fwFile = 'OK '+str(err)	## Done with bootloader
						self.avl.save()
						print >> self.stdout,"Bootloader DONE. Ret =", err, " Rows =",row
					else:
						print >> self.stdout,"Invalid token {0}".format(id)
						
					#Bootloader 
					if self.avl.fwFile:
						#self.CheckBoot()
						response = '' 
						if self.avl.fwFile == '-':
							response = struct.pack("<BIBBH",RSPID_SESSION,self.session.session,BTLID_ENTER,boot.rows[0].array_id,boot.rows[0].row_number)
							print >> self.stdout,"Enter Bootloader"
							self.avl.comments = ''	# Reset comments for restart 
							self.avl.save()
						elif (not "OK" in self.avl.fwFile) and (not "ERROR" in self.avl.fwFile):
							try:
								row = int(self.avl.fwFile)
								if row == len(boot.rows):
									sum = 0
									for i in boot.rows:
										for j in i.data:
											sum = (sum + ord(j)) & 0xFFFF
									response = struct.pack("<BIBHHBH",RSPID_SESSION,self.session.session,BTLID_EXIT,len(boot.rows),sum,
										boot.rows[0].array_id,boot.rows[0].row_number)
									print >> self.stdout, "Sending exit:", len(boot.rows) ," SUM = ",sum
								else:
									response = struct.pack("<BIBH",RSPID_SESSION,self.session.session,BTLID_DATA,row)
									for i in boot.rows[row:]:
										response += i.data
										if len(response) >=4*256:
											break
									print >> self.stdout, "Sending row:", row, " len=", len(response)
							except:
								raise
								self.avl.fwFile = 'ERROR RNUM'
								self.avl.save()
						if response:
							cksum = crc.calculate(response)
							response += struct.pack('>H',cksum)
							time.sleep(SENDDELAY*2)
							self.socket.sendto(response,self.client_address)
		finally: 
			pass
			
	def finish(self):
		dt = datetime.now(utc)-self.timeck
		print >> self.stdout, "Finished processing packet in {0.seconds}.{0.microseconds:06d} seconds".format(dt)
		sys.stdout.write(self.stdout.getvalue())
		sys.stdout.flush()

def sendWialon(std,s,data):
	s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVTIMEO,struct.pack("LL",45,0))
	s.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,1)
	for i in data:
		s.send(i)
		r = s.recv(20)
		rs = r.split("#")
		if r[:-2] not in ("#AL#1", "#AD#1", "#ASD#1"):
			raise ValueError(r)
		print >> std,"WORKER: ",i[:-2]
		print >> std,"WORKER: ",r[:-2]
		
def worker():
	while True:
		item = theQueue.get()
		if item is None:
			print "WORKER Exiting..."
			break
		## Process item
		wstdout = io.BytesIO()
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect(("193.193.165.165",20332))
			sendWialon(wstdout,s,item)
		finally:
			s.close()
		sys.stdout.write(wstdout.getvalue())
		wstdout.close()
		sys.stdout.flush()
		##
		theQueue.task_done()

if __name__ == "__main__":
	try:
		## Bootloader
		if len(sys.argv) != 3:
			print "Arguments: [hex file] [version]"
			exit(0)
		f = open(sys.argv[1])
		version = sys.argv[2]
		boot = cyacd.BootloaderData.read(f)
		f.close()
		## 
		server = SocketServer.ThreadingUDPServer(('', 60001), BLURequestHandler)
		#server = SocketServer.UDPServer(('', 50100), BLURequestHandler)
		print "_"*80
		print "Server Started."
		print "-"*80
		sys.stdout.flush()
		
		theQueue = queue.Queue()
		thread = threading.Thread(target=worker)
		thread.start()
		
		server.serve_forever()
	except KeyboardInterrupt:
		sys.stdout.flush()
		theQueue.put(None)
		thread.join()
		print "_"*80
		print "Server received signal, exiting."
		print "-"*80
		
