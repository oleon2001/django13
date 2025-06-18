#!/usr/bin/python
# -*- coding: utf-8 -*-
# Bluetooth AVL server

import socket
import struct
import socketserver as SocketServer
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

import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

import decimal
from geopy.point import Point as gPoint
from geopy.distance import distance as geoLen

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
import django
django.setup()

# Import Django modules
from django.db import transaction, DatabaseError, IntegrityError, connection
from django.contrib.gis.geos import Point
from django.conf import settings
from skyguard.gps.tracker.models import SGAvl, SGHarness
from skyguard.apps.gps.models.protocols import UDPSession
from skyguard.apps.gps.models.device import GPSDevice

# Implementación directa de CRC-CCITT
class CRCCCITT:
    def __init__(self, poly='1D0F'):
        self.poly = int(poly, 16)
        self.table = self._generate_table()

    def _generate_table(self):
        table = []
        for i in range(256):
            crc = i << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ self.poly) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
            table.append(crc)
        return table

    def calculate(self, data):
        crc = 0xFFFF
        for byte in data:
            crc = ((crc << 8) ^ self.table[((crc >> 8) ^ byte) & 0xFF]) & 0xFFFF
        return crc

crc = CRCCCITT('1D0F')

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

RECID_TRACKS   =0x30
RECID_PEOPLE   =0x31

MOTORio     =(1<<0)
IGNio       =(1<<1)
PANICio     =(1<<2)
CHRGio      =(1<<3)
PWRio       =(1<<4)
DELTAio     =(1<<7)

SENDDELAY  = 0.15

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
		
class BLURequestHandler(SocketServer.BaseRequestHandler):
	def UnpackPos(self,data):
		"""
		Unpack a gps position record
		"""
		ct,lat,lon,speed,inputs = struct.unpack("<IiiBB",data)
		dt = datetime.fromtimestamp(ct,utc)
		if abs(dt-datetime.now(utc)>timedelta(days=20)):
			dt = datetime.now(utc)
			print("Invalid time in position", file=self.stdout)
			
		return {'date': dt,'pos': Point(lon/10000000.0,lat/10000000.0),'speed': speed, 'inputs': inputs}

	def Login(self):
		if self.nBytes != 15:
			print("Invalid LOGIN size: {0}".format(self.nBytes), file=self.stdout)
		imei, = struct.unpack("<Q",self.data[1:9])
		mac, = struct.unpack("<Q", self.data[9:15]+b'\x00\x00')
		print("Session request from IMEI: {0:015d} MAC ID: {1:012X}".format(imei,mac), file=self.stdout)
		try:
			avl = SGAvl.objects.get(imei = imei)
		except SGAvl.DoesNotExist:
			print("Device not found. Creating...", file=self.stdout)
			harness = SGHarness.objects.get(name = "default")
			avl = SGAvl(imei=imei,name = "{:015d}".format(imei), harness = harness, comments ="")
			avl.save()
		#delete old sessions
		try:
			gps_device = GPSDevice.objects.get(imei=avl.imei)
		except GPSDevice.DoesNotExist:
			gps_device = GPSDevice.objects.create(
				imei=avl.imei,
				name=avl.name,
				protocol='wialon'
			)
		
		# Actualizar información de conexión del dispositivo GPS
		gps_device.current_ip = self.host
		gps_device.current_port = self.port
		gps_device.connection_status = 'ONLINE'
		gps_device.last_heartbeat = self.timeck
		gps_device.last_connection = self.timeck
		gps_device.last_log = self.timeck
		gps_device.position = avl.position
		gps_device.speed = avl.speed
		gps_device.total_connections += 1
		gps_device.save()
		print(f"Updated GPS device connection: {self.host}:{self.port}", file=self.stdout)
		
		sessions = UDPSession.objects.filter(device=gps_device)
		if sessions:
			sessions.delete()
		expires = self.timeck + SESSION_EXPIRE
		session = UDPSession(device=gps_device, expires=expires, host=self.host, port=self.port)
		session.save()
		if not avl.comments or (not 'INFO OK' in avl.comments):
			response = struct.pack("<BLB",RSPID_SESSION,session.session,CMDID_DEVINFO)	# Refresh dev info
			print("Sent login response w/DevInfo", file=self.stdout)
		else:
			response = struct.pack("<BLB",RSPID_SESSION,session.session,CMDID_DATA)
			print("Sent login response", file=self.stdout)
		time.sleep(SENDDELAY)
		self.socket.sendto(response, self.client_address)
		self.avl = avl

	def FindSession(self):
		self.sessionNo, = struct.unpack("<L",self.data[1:5])
		self.session = None
		try:
			self.session = UDPSession.objects.get(session = self.sessionNo)
			self.session.expires = self.timeck + SESSION_EXPIRE
			self.session.host = self.host
			self.session.port = self.port
			self.avl = SGAvl.objects.get(imei = self.session.device.imei)
			print("AVL:", self.avl, file=self.stdout)
			self.session.save()
		except UDPSession.DoesNotExist: 
			print("Unknown session #", self.sessionNo, file=self.stdout)
		except: 
			raise
		
	def SendLogin(self):
		time.sleep(SENDDELAY)
		self.socket.sendto(bytes([RSPID_LOGIN]), self.client_address)
		print("Sent login request.", file=self.stdout)
	
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
		print("-- Inputs:",self.avl.inputs," Outputs:",self.avl.outputs, file=self.stdout)
	
	def Ping(self):
		pos = self.UnpackPos(self.data[5:19])
		print(" Inputs: " , pos['inputs'], file=self.stdout)
		self.SetPos(pos)
		
		# Actualizar heartbeat del dispositivo GPS
		try:
			gps_device = GPSDevice.objects.get(imei=self.avl.imei)
			gps_device.last_heartbeat = self.timeck
			gps_device.position = pos["pos"]
			gps_device.speed = pos["speed"]
			gps_device.last_log = pos["date"]
			gps_device.connection_status = 'ONLINE'
			gps_device.current_ip = self.host
			gps_device.current_port = self.port
			gps_device.save()
			print(f"Updated GPS device heartbeat and position", file=self.stdout)
		except GPSDevice.DoesNotExist:
			print(f"GPS device not found for IMEI {self.avl.imei}", file=self.stdout)
		
		response = struct.pack("<BLBB",RSPID_SESSION,self.session.session,CMDID_ACK,0)
		#response = struct.pack("<BLB",RSPID_SESSION,self.session.session,CMDID_DATA)
		time.sleep(SENDDELAY)
		self.socket.sendto(response, self.client_address)
		print("Got PING, Position: {0.y},{0.x}".format(self.avl.position), file=self.stdout)
		
	def DevInfo(self):
		print("Got DevInfo response from", self.avl.imei, file=self.stdout)
		print("Info:\n", self.data[5:], file=self.stdout)
		self.avl.comments = "INFO OK\n" + self.data[5:].decode('utf-8', errors='ignore')
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
		print("Unpacked {0} positions.".format(len(positions)), file=self.stdout)
		evs = tracker.Event.objects.filter(imei = self.avl, date__range = (positions[0]["date"],positions[-1]["date"]))
		if positions and evs:
			print("Duplicate track records found", file=self.stdout)
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
					print("IO_RECORD {} - {:02X} {:02X}".format(io.changes,pos['inputs'],pos['speed']), file=self.stdout)
					if self.avl.owner and self.avl.owner.email and delta == PANICio:
						try:
							print("Into email send.", file=self.stdout)
							port = 465
							password = '4^4Lyh7nUtys'
							sender = "alertas@zoho.com"
							receiver = self.avl.owner.email.split()
							print(sender, receiver, password, file=self.stdout)
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
							print("Message Built", file=self.stdout)
							try:
								server = smtplib.SMTP_SSL("smtp.zoho.com")
								server.login("alertas@zoho.com",password)
								server.sendmail(sender,receiver,message.as_string())
								print("Sent email to:", repr(receiver), file=self.stdout)
							finally:
								server.quit()
						except Exception as e:
							print(">>>> Unknown exception", file=self.stdout)
							print(e, file=self.stdout)
							print(repr(e), file=self.stdout)
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
			print("Invalid time in people", file=self.stdout)
		return {'date': dt, 'in': countIn, 'out': countOut, 'id': mac}
	
	def UnpackPeople(self,data):
		people = []
		while len(data) >= 18:
			people.append(self.UnpackTof(data[:18]))
			data = data[18:]
		print("Unpacked {0} tof records.".format(len(people)), file=self.stdout)
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
			print("Dropped {0} TOF duplicates.".format(len(people)-len(values)), file=self.stdout)
		
	def RxData(self):
		if crc.calculate(self.data) != 0:
			print("CRC Failiure. Discarding packet", file=self.stdout)
			return
		self.lastPos = None
		data = self.data[5:-2]
		records = []
		id0 = id1 = 0
		while data:
			if len(data)<=8:
				print("Invalid record header, len=", len(data), file=self.stdout)
				data =''
			else:
				id,size = struct.unpack("<II",data[:8])
				if size>248:
					print("Invalid record size =", size, file=self.stdout)
					data =''
				else:
					id1 = id
					if not id0:
						id0 = id
					rec = data[8:8+size]
					data = data[8+size:]
					records.append(rec)
		if id0:
			print("Extracted {0} records.".format(len(records)), file=self.stdout)
			response = struct.pack("<BIBBII",RSPID_SESSION,self.session.session,CMDID_ACK,len(records),id0,id1)
			time.sleep(SENDDELAY)
			self.socket.sendto(response, self.client_address)
			self.queries = []
			for rec in records:
				id = rec[0]
				if id == RECID_TRACKS:
					self.UnpackTracks(rec[1:])
				elif id == RECID_PEOPLE:
					self.UnpackPeople(rec[1:])
				else:
					print("Invalid RECID: {0:02X}".format(id), file=self.stdout)
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
				print("WIALON:",i[:-2], file=self.stdout)
						
	def setup(self):
		self.timeck = datetime.now(utc)
		self.localtime = datetime.now(timezone(settings.TIME_ZONE))
		self.stdout = io.StringIO()
		print("*"*80, file=self.stdout)
		print(self.localtime.ctime(), self.client_address, 'connected!', file=self.stdout)

	def handle(self):
		self.imei = None
		self.socket = self.request[1]
		self.data = self.request[0]
		self.nBytes = len(self.data)
		self.host = self.client_address[0]
		self.port = self.client_address[1]
		self.wialon = []
		print("RX len = {0} from {1}:{2}".format(len(self.data), self.host, self.port), file=self.stdout)
		try: 
			id = self.data[0]
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
						print("Invalid token {0}".format(id), file=self.stdout)
						
		finally: 
			pass
			
	def finish(self):
		dt = datetime.now(utc)-self.timeck
		print("Finished processing packet in {0.seconds}.{0.microseconds:06d} seconds".format(dt), file=self.stdout)
		sys.stdout.write(self.stdout.getvalue())
		sys.stdout.flush()

def sendWialon(std,s,data):
	s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVTIMEO,struct.pack("LL",45,0))
	s.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,1)
	for i in data:
		s.send(i.encode())
		r = s.recv(20)
		rs = r.split(b"#")
		if r[:-2] not in (b"#AL#1", b"#AD#1", b"#ASD#1"):
			raise ValueError(r)
		print("WORKER: ",i[:-2], file=std)
		print("WORKER: ",r[:-2].decode(), file=std)
		
def worker(theQueue):
	while True:
		item = theQueue.get()
		if item is None:
			print("WORKER Exiting...")
			break
		# Process item
		wstdout = io.StringIO()
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect(("193.193.165.165",20332))
			sendWialon(wstdout,s,item)
		finally:
			s.close()
		sys.stdout.write(wstdout.getvalue())
		wstdout.close()
		sys.stdout.flush()
		theQueue.task_done()
