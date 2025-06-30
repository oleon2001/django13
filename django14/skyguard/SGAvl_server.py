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
import gps.tracker.models as tracker
import gps.gprs.models as gprs

localtz = timezone(settings.TIME_ZONE)
settings.DEBUG = False

def UnpackFix(data):
	"""
	Unpack a GpsFullRec
	"""
	ct,lat,lon,alt,vel,crs = struct.unpack("<IiiHBB",data)
	dt = datetime.fromtimestamp(ct,utc)
	if abs(dt-datetime.now(utc)>timedelta(days=20)):
		dt = datetime.now(utc)
	return {'date': dt,#datetime.fromtimestamp(ct,utc),
			'pos':Point(lon/10000000.0,
						lat/10000000.0),
			'speed':vel, 'course':crs * 1.40625, 'altitude':alt}

def UnpackDeltaFix01(data,orig):
	"""
	Unpack a GpsDiffRec with no scaling on the deltas
	"""
	dct,dlat,dlon,dalt,vel,crs = struct.unpack("<HhhbBB",data)
	return {'date': orig['date']+timedelta(seconds = dct),
			'pos':Point(orig['pos'].x + (dlon / 10000000.0),
						orig['pos'].y + (dlat / 10000000.0)),
			'speed':vel, 'course':crs * 1.40625, 'altitude':orig['altitude']+dalt}

def GetOnOff(bit,data):
	"""
	Used to comment on the inputs status (active low)
	"""
	if ((data >>  bit) & 1) == 0:	return "ON"
	else:							return "OFF"

def GetOffOn(bit,data):
	"""
	Used to comment on the outputs status (active high)
	"""
	if ((data >>  bit) & 1) == 0:	return "OFF"
	else:							return "ON"

def GetCorrectTime(data, repair = True, out=None):
	ct, = struct.unpack("<I",data)
	if ct<10000 or ct > (time.time()+900):
		if repair:
			ct=time.time()
		else:
			if (out):
				print >> out,"Discarded time %d"%(ct)
			ct = None
	return ct

class BadRecord(Exception):
	def __init__(self,value,data = None):
		self.value = value
		if isinstance(data,str):
			self.data = data
		else:
			self.data = None
	def __str__(self):
		if self.data:
			return "INVALID RECORD %s[%d] (%s)" % (repr(self.value),len(self.data),self.data.encode('hex'))
		return "INVALID RECORD %s" % repr(value)

class SGAvlRequestHandler(SocketServer.BaseRequestHandler ):

	def UpdateDevPosition(self): ##############################
		if self.dev.date and not self.dev.date.tzinfo:
			self.dev.date = localtz.localize(self.dev.date)
		if not self.dev.date or self.dev.date<self.events[-1].date:
			self.dev.date = self.events[-1].date
			#if self.dev.odom==0:
			self.dev.position = self.events[-1].position
			#self.dev.speed = self.events[-1].speed
			#self.dev.course = self.events[-1].course
			#self.dev.altitude = self.events[-1].altitude
			if self.dev.lastLog and not self.dev.lastLog.tzinfo:
				self.dev.lastLog = localtz.localize(self.dev.lastLog)
			if not self.dev.lastLog or self.dev.lastLog < self.events[-1].date:
				self.dev.lastLog = self.events[-1].date

	def DecodeIOS(self,data,type,fix):
		if self.doneOuts:
			return
		if (fix and len(data)!= 24) or (not fix and len(data)!=12):
			raise BadRecord(type,data)
		old_ins, old_outs = self.dev.inputs, self.dev.outputs
		self.dev.inputs, self.dev.outputs = struct.unpack("<II",data[:8])
		if self.dev.imei == 13949000489073:
			print >>self.stdout, "IOS %d - %d"%(self.dev.inputs, self.dev.outputs)
		ins, outs = self.dev.inputs, self.dev.outputs
		if (fix):
			gpsfix = UnpackFix(data[8:])
			e = tracker.IOEvent(type=type, imei=self.dev,
				position = gpsfix['pos'], date = gpsfix['date'],
				speed = gpsfix['speed'] ,
				course = gpsfix['course'],
				altitude = gpsfix['altitude'],
				inputs=ins, outputs=outs, changes='', odom = self.dev.odom )
			#if self.dev.odom:
			#	e.odom = self.dev.odom
		else:
			e = tracker.IOEvent(type=type, imei=self.dev,
				date = datetime.fromtimestamp(GetCorrectTime(data[8:]),utc),
				inputs=ins, outputs=outs, changes='')
		mask = self.dev.alarmMask
		mask = mask & (~ins) & 0xFFFF
		self.dev.alarms = self.dev.alarms | mask
		ch_in = ins ^ old_ins
		ch_out = outs ^ old_outs
		e.indelta = ch_in;
		e.outdelta = ch_out;
		e.alarmdelta = mask;
		# Changed inputs
		for i in range(0,16):
			if ch_in &(1<<i) != 0:
				e.changes += "%s=%s "%(self.harness.GetInputCableName(i), GetOnOff(i,ins))
		# Changed outputs (Reversed logic)
		for i in range(0,16):
			if ch_out &(1<<i) != 0:
				e.changes += "%s=%s "%(self.harness.GetOutputCableName(i), GetOffOn(i,outs))
		#### REMOVE THE DOK EVENTS
		if 'BAT_DOK' in e.changes:
			pass
		else:
			self.events.append(e)
		if fix and self.checkDevicePos:
			self.UpdateDevPosition()

	def DecodeCALLRX(self,data):
		type = "CALL_RECEIVED"
		if len(data) < 4:
			raise BadRecord(type,data)
		self.events.append( tracker.GsmEvent(type=type, imei=self.dev,
			date = datetime.fromtimestamp(GetCorrectTime(data[:4]),utc),
			source = data[4:], text = type))

	def DecodePressure(self,data):
		type = "PRESSURE INFO"
		if len(data) != 25:
			raise BadRecord(type,data)
		id0,id1,id2,p1,p2,count = struct.unpack("<IIIIIB",data[4:])
		dt = datetime.fromtimestamp(GetCorrectTime(data[:4]))
		id = (id0<<64) | (id1<<32) | id2
		id = "%024X"%id
		psi1= (p1/count-1638.4)*150.0/13107.0
		psi2= (p2/count-1638.4)*150.0/13107.0
		if psi1 != 0 and psi1 !=0:
			print >>self.stdout , "{2} - Presion de 0x{0} = {1:f} / {2:f}  @{3}".format(id,psi1,psi2,dt)
			self.events.append( tracker.PsiWeightLog(imei = self.dev, sensor = id, date = dt, psi1 = str(psi1), psi2 = str(psi2)))

	def DecodePeople(self,data):
		type = "PEOPLE INFO"
		if len(data) != 24:
			raise BadRecord(type,data)
		id0,id1,id2,p1,p2 = struct.unpack("<IIIII",data[4:])
		dt = GetCorrectTime(data[:4],False,self.stdout)
		if dt:
			dt = datetime.fromtimestamp(dt)
			id = (id0<<64) | (id1<<32) | id2
			id = "%024X"%id
			psi1= p1
			psi2= p2
			if psi1 != 0 and psi1 !=0:
				print >>self.stdout , "{2} - PEOPLE FROM 0x{0} = {1:f} / {2:f}  @{3}".format(id,psi1,psi2,dt)
				self.events.append( tracker.PsiWeightLog(imei = self.dev, sensor = id, date = dt, psi1 = str(psi1), psi2 = str(psi2)))

	def DecodeAlarm(self,data,startflag):
		type = "ALARM INFO"
		if len(data) != 24:
			raise BadRecord(type,data)
		id0,id1,id2,p1,p2 = struct.unpack("<IIIII",data[4:])
		dt = GetCorrectTime(data[:4],False)
		if dt:
			dt = datetime.fromtimestamp(dt,utc)
			id = (id0<<64) | (id1<<32) | id2
			id = "%024X"%id
			psi1= p1
			psi2= p2
			if startflag:
				cmt = "START"
			else:
				cmt = "STOP"
			print >>self.stdout , "{2} - ALARM FROM 0x{0} = {1} / {2}  @{3}".format(id,psi1,psi2,dt)
			self.events.append( tracker.AlarmLog(imei = self.dev, sensor = id, date = dt, cksum = psi1, duration = psi2,comment = cmt))

	def DecodeSMSRX(self,data):
		type = "SMS_RECEIVED"
		if len(data) < 6:
			raise BadRecord(type,data)
		pl = ord(data[4])
		sl = ord(data[5])
		if len(data) != 6+pl+sl:
			raise BadRecord(type,data)
		ev = tracker.GsmEvent(type=type, imei=self.dev,
			date = datetime.fromtimestamp(GetCorrectTime(data[:4]),utc),
			source = data[6:6+pl], text = data[6+pl:], odom = self.dev.odom)
		#if self.dev.odom:
		#	ev.odom = self.dev.odom
		self.events.append(ev)

	def updateOdom(self,pos):
		#if self.dev.odom:
			p0 = gPoint(self.dev.position.y,self.dev.position.x)
			p1 = gPoint(pos.y,pos.x)
			self.dev.position = pos
			dis = geoLen(p0,p1).m
			#self.dev.odom += dis
			#print >>self.stdout, "ODOM UPDATE:",dis,self.dev.odom
			return self.dev.odom
		#else:
		#	return 0

	def DecodeGpsA0(self,data,idbyte):
		nGps = idbyte - 0xA0
		if len(data) != (16 + 9*nGps):
			raise BadRecord(type,data)
		orig = UnpackFix(data[0:16])
		self.updateOdom(orig['pos'])
		ev = tracker.Event(type="TRACK", imei=self.dev,
			position = orig['pos'],	date = orig['date'],
			speed = orig['speed'], course = orig['course'],
			altitude = orig['altitude'],
			odom = self.dev.odom)
		#if self.dev.odom:
		#	ev.odom = self.updateOdom(orig['pos'])
		self.events.append(ev)
		for i in range(nGps):
			dif = UnpackDeltaFix01(data[i*9+16:i*9+25],orig)
			self.updateOdom(orig['pos'])
			ev = tracker.Event(type="TRACK", imei=self.dev,
				position = dif['pos'],	date = dif['date'],
				speed = dif['speed'], course = dif['course'],
				altitude = dif['altitude'],
				odom = self.dev.odom)
			#if self.dev.odom:
			#	ev.odom = self.updateOdom(dif['pos'])
			#print >>self.stdout,"EV ODOM:",ev.odom
			self.events.append(ev)
		if self.checkDevicePos:
			self.UpdateDevPosition()

	def Decode_FIX(self,data,type):
		if len(data) != 16:
			raise BadRecord(type,data)
		fix = UnpackFix(data)
		self.events.append(tracker.Event(type=type, imei=self.dev,
			position = fix['pos'], date = fix['date'],
			speed = fix['speed'], course = fix['course'],altitude = fix['altitude'],
			odom = self.dev.odom))
		self.UpdateDevPosition()

	def Decode_Ctime(self,data,type):
		if len(data) != 4:
			raise BadRecord(type,data)
		# in a login without fix, update device pos from later fixes
		if (type[:3]!="GPS"):
			self.checkDevicePos = True
		dct = datetime.fromtimestamp(GetCorrectTime(data),utc)
		self.dev.lastLog = dct
		self.events.append(tracker.Event(type=type, imei=self.dev,
			date = dct))

	def DecodeResetText(self,data):
		type = "CPU_RESET"
		if len(data) < 6 :
			raise BadRecord(type,data)
		ct = GetCorrectTime(data[:4])
		reason, = struct.unpack("<H",data[4:6])
		r = "%04x"%reason
		if   reason <0xF000: r += " CME ERROR"
		elif reason==0xF020: r += " EINVAL"
		elif reason==0xF021: r += " NOFIX"
		elif reason==0xF022: r += " UPGRADE"
		elif reason==0xF023: r += " NOCOMMS"
		elif reason==0xF024: r += " GSMERROR"
		elif reason==0xF025: r += " GSKUNKTXT"
		elif reason==0xF026: r += " GSMTMOUT"
		else : r +=  " NO FOUND??"
		txt = data[6:].split('\0')[0]
		try:
			txt.decode('ascii')
			r = r + txt
		except UnicodeDecodeError:
			r = r + "Garbage #$%"
		self.events.append(tracker.ResetEvent(type=type, imei=self.dev,
			date = datetime.fromtimestamp(ct,utc),
			reason = r))
		print >>self.stdout, "Reset",r

	def DecodeCPURESET(self,data):
		type = "CPU_RESET"
		if len(data) != 6 and len(data) != 8:
			raise BadRecord(type,data)
		ct = GetCorrectTime(data[:4])
		reason, = struct.unpack("<H",data[4:6])
		r = "%04x"%(reason)
		if   reason <0xF000: r += " CME ERROR"
		elif reason==0xF020: r += " EINVAL"
		elif reason==0xF021: r += " NOFIX"
		elif reason==0xF022: r += " UPGRADE"
		elif reason==0xF023: r += " NOCOMMS"
		elif reason==0xF024: r += " GSMERROR"
		elif reason==0xF025: r += " GSKUNKTXT"
		elif reason==0xF026: r += " GSMTMOUT"
		else : r += " NO FOUND??"
		self.events.append(tracker.ResetEvent(type=type, imei=self.dev,
			date = datetime.fromtimestamp(ct,utc),
			reason = r))
		print >>self.stdout, "Reset",reason,r

	def ParseRec(self,idbyte,data):
		try:
			# Generic TRACK
			if 0xA0<=idbyte<=0xBF:		self.DecodeGpsA0(data,idbyte)
			# Relación de I/Os Sucede cuando detecta un cambio reportable de las entradas
			elif idbyte == 0x02:		self.DecodeIOS(data,"IO_NOFIX",False)
			elif idbyte == 0x03:		self.DecodeIOS(data,"IO_FIX",True)
			# These happen if we loose GPS after 30s and when
			# we get it back before 5 minutes
			elif idbyte == 0x04:		self.Decode_Ctime(data,"GPS_LOST")
			elif idbyte == 0x05:		self.Decode_FIX(data,"GPS_OK")
			# Login event: The first record in a transmition is one of these,
			# STARTUP events ocurr only after reset, CURRENT events on the rest
			elif idbyte == 0x06:		self.Decode_FIX(data,"CURRENT_FIX")
			elif idbyte == 0x07:		self.Decode_Ctime(data,"CURRENT_TIME")
			elif idbyte == 0x08:		self.Decode_FIX(data,"STARTUP_FIX")
			elif idbyte == 0x09:		self.Decode_Ctime(data,"STARTUP_TIME")
			# Caller ID and SMS reports
			elif idbyte == 0x10:		self.DecodeCALLRX(data)
			elif idbyte == 0x11:		self.DecodeSMSRX(data)
			# Reporte de razón de Reset del CPU
			elif idbyte == 0x12:		self.DecodeCPURESET(data)
			elif idbyte == 0x13:		self.DecodeResetText(data)
			elif idbyte == 0x20:		self.DecodePressure(data)
			elif idbyte == 0x21:		self.DecodePeople(data)
			elif idbyte == 0x22:		self.DecodeAlarm(data,True)
			elif idbyte == 0x23:		self.DecodeAlarm(data,False)
			else:
				print >> self.stdout, ">>>> Unknown event 0x%02X: %s"%(idbyte,data.encode("hex"))
		except BadRecord as ex:
			print >> self.stdout, ">>>> IDBYTE = %02X: %s"%(idbyte,str(ex))


	def GetRecords(self,packet):
		recs = []
		data = packet.request
		if self.dev:
			while len(data)>7:
				recNo,recLen,id = struct.unpack("<LHB",data[0:7])
				if not self.version:
					self.version = data[0:4]
				if recLen>(len(data)-6):
					print >> self.stdout, ">>>> Invalid recLen, discarding rest of packet (RecNo = %d, recLen= %d, data= %d)"%(recNo,recLen,len(data))
					return recs
				recs.append(gprs.Record(idbyte=id, data=data[7:6+recLen]))
				data = data[6+recLen:]
		self.session.records += len(recs)
		return recs

	def GetPacket(self,login):
		data = self.request.recv(2048)
		nBytes = len(data)
		self.session.bytes += nBytes
		if not data:
			return None
		if login and (len(data) < 8):
			print >> self.stdout, "Invalid login (len=%d) %s"%(len(data),data.encode("hex"))
			#print "---->Invalid login (len=%d) %s"%(len(data),data.encode("hex"))
			return None
		if login:
			self.imei, = struct.unpack("<Q",data[:8])
			print >> self.stdout, "Login from %015d"%(self.imei)
			#print "---->Login from %015d"%(self.imei),datetime.now().ctime(), self.client_address, 'connected!'
			self.FindOrCreateDev()
			data = data[8:]
		packet = gprs.Packet(request = data)
		return packet

	@transaction.commit_on_success()
	def FindOrCreateDev(self):
		# find device or create it
		try:
			self.dev = tracker.SGAvl.objects.get(imei = self.imei)
			self.harness = self.dev.harness
		except tracker.SGAvl.DoesNotExist:
			try:
				self.harness = tracker.SGHarness.objects.get(name = "default")
			except tracker.SGHarness.DoesNotExist:
				print >> self.stdout, ">>>> Creating default harness"
				self.harness = tracker.SGHarness(name = "default",
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
			if self.imei < 10000000000000 or imei >899999999999999:
				print >> self.stdout, "Invalid device imei. Not creating..."
				self.dev = None
			else:
				self.dev = tracker.SGAvl(imei=self.imei,name = "%015d"%self.imei, harness = self.harness, comments ="")
				self.dev.save()
				print >> self.stdout, ">>>> Created device %s"%self.dev.name
		self.session.dev = self.dev

	def setup(self):
		self.timeck = datetime.now()
		self.stdout = io.BytesIO()
		print >> self.stdout, "*"*80
		print >> self.stdout, datetime.now().ctime(), self.client_address, 'connected!'
		self.request.setsockopt(socket.SOL_SOCKET,socket.SO_RCVTIMEO,struct.pack("LL",45,0))
		self.request.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,1)
		self.session = gprs.Session(ip = self.client_address[0], port = self.client_address[1])
		self.session.start = datetime.now(utc)

	def handle(self):
		self.imei = None
		self.doneOuts = None
		try:
			login = True
			self.packets = []
			self.version = None
			while True:
				# Get data
				packet = self.GetPacket(login)
				if not packet:
					return
				# Separate records
				packet.recs = self.GetRecords(packet)
				# Prepare response
				response = '\xA0'+chr(len(packet.recs))
				# Commands for login
				if login and self.dev:
					print >> self.stdout, "IMEI: ", self.dev.imei
					if self.dev.newOutputs != None:
						print >> self.stdout, "Setting outputs"
						# Outputs set
						outs = ""
						for i in range(0,16):
							if (self.dev.newOutputs>>i) & 1:
								outs +=chr(1)
							else:
								outs +=chr(0)
						#for c in self.dev.newOutputs:
						#	if c == '0':
						#		outs =chr(0) + outs
						#	else:
						#		outs =chr(1) + outs
						if len(outs)!=16:
							print >> self.stdout, "Invalid output string for device %s: %s"%(self.dev.imei,self.dev.newOutputs)
						else:
							response += chr(0xC0)+outs
							print >> self.stdout, "Response +",repr(response)
						self.dev.outputs = self.dev.newOutputs
						self.dev.newOutputs = None
						self.dev.save()
						self.doneOuts = True
					if self.dev.newInflags:
						# Input Flags change
						try:
							infs = self.dev.newInflags.decode("hex")
							if len(infs) != 16:
								print >> self.stdout, "Invalid inflags for device %s: %s"%(self.dev.imei,self.dev.newInflags)
							else:
								response += chr(0xC1)+infs
						except TypeError:
							print >> self.stdout, "Invalid inflags for device %s: %s"%(self.dev.imei,self.dev.newInflags)
						self.dev.newInflags = ''
					if self.dev.fwFile:
						# Firmware update
						response += chr(0xC2)
					msgs = tracker.ServerSMS.objects.filter(imei = self.dev, sent__isnull = True)
					if len(msgs):
						msg = msgs[0]
						response += chr(0xC3)
						response += chr(len(msg.msg))
						response += msg.msg.encode('ascii','replace')
						msg.sent = datetime.now()
						msg.save()
						print >> self.stdout, ">> Mensaje '%s' Enviado <<<"%(msg.msg.encode('ascii','replace'))
				packet.response = response
				self.request.send(response)
				login = False
				# Packet done, perhaps save hex values??
				self.packets.append(packet)
		except socket.error as (err,strerr):
			if err == errno.EAGAIN:
				print >> self.stdout, "Socket timeout. ","+"*30
		except Exception as e:
			print >> self.stdout, ">>>> Unknown exception"
			print >> self.stdout, e
			print >> self.stdout, repr(e)
			raise

	#@transaction.commit_manually()
	def finish(self):
		try:
			t1 = datetime.now()
			self.session.packets = len(self.packets)
			self.events = []
			try:
				if not self.imei or not self.session or not self.session.dev:
					print >> self.stdout, "Invalid Session"
					print >> self.stdout, "*"*80
					sys.stdout.write(self.stdout.getvalue())
					sys.stdout.flush()
					return
			except:
				print >> self.stdout,"Exception raised for IMEI: %015d"%self.imei
				raise
			#finally:
			#	sys.stdout.write(self.stdout.getvalue())
			#	sys.stdout.flush()
			# With a session, save packets and records
			self.session.save()
			#self.checkDevicePos = False
			self.checkDevicePos = True
			for p in self.packets:
				p.session = self.session
				p.request =  p.request.encode("hex")
				p.response = p.response.encode("hex")
				p.save()
			#transaction.commit()
			values = []
			for p in self.packets:
				for r in p.recs:
					r.packet = p
					self.ParseRec(r.idbyte,r.data)
					r.data = r.data.encode("hex")
					values.append((p.id,r.idbyte,r.data))
			cursor = connection.cursor()
			query =	'''INSERT INTO gprs_record (packet_id , idbyte, data) VALUES (%s,%s,%s) '''
			cursor.executemany(query, values)
			transaction.commit_unless_managed()
			t2 = datetime.now()
			self.session.events = len(self.events)

			#People Events
			pValues = []
			pQuery = '''INSERT INTO tracker_psiweightlog (imei_id , sensor, date, psi1, psi2 ) VALUES (%s, %s, %s, %s, %s) '''
			values = []
			query = '''INSERT INTO tracker_event (imei_id , type, position, speed, course, date, odom, altitude ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) '''
			rec0 = self.events[0]
			self.events = self.events[1:]
			self.events.append(rec0)
			for e in self.events:
				if type(e) == tracker.Event:
					if (e.position):
						pos = "SRID=4326; POINT({0} {1})".format(e.position.x,e.position.y)
					else:
						pos = None
					values.append((e.imei.imei , e.type, pos, e.speed, e.course, e.date, e.odom, e.altitude ))
				elif type(e) == tracker.PsiWeightLog:
					pValues.append((e.imei.imei,e.sensor,e.date,str(e.psi1),str(e.psi2)))
				else:
					cursor = connection.cursor()
					cursor.executemany(query, values)
					values = []
					transaction.commit_unless_managed()
					e.save()
			cursor = connection.cursor()
			if pValues:
				cursor.executemany(pQuery, pValues)
			if values:
				cursor.executemany(query, values)
			if pValues or values:
				transaction.commit_unless_managed()
			t3 = datetime.now()
			if self.version and self.version != self.dev.swversion:
				self.dev.swversion = self.version
			self.dev.save()
			self.session.end = datetime.now(utc)
			if (self.dev.swversion == "1.10" or self.dev.swversion == "1.40") and (self.dev.inputs &2 == 2) and not self.dev.fwFile :
				self.dev.fwFile = "1.41"
				self.dev.save()
				if self.dev.sim:
					args = ["ssh",
						"sms@skyguard.dlinkddns.com",
						"gammu","sendsms","TEXT",self.dev.sim.phone,"-text",
						'"UPGRADE %s"'%self.dev.fwFile]
					subprocess.call(args)
			self.session.save()
			#transaction.commit()
			#Post event actions - Tracking Geofences
			#tracks = tracker.Tracking.objects.filter(imei = self.dev.imei).filter(stop = None)
			#for tr in tracks:
			#	for e in self.events:
			#		if type(e) == tracker.Event and e.type in ["TRACK","IO_FIX"]:
			#			if tr.stopFence.fence.contains(e.position):
			#				tr.stop = e.date
			#				tr.save()
			#				break
			connection.close()

			print >> self.stdout, self.session

			secs = lambda td: ((td.microseconds / 1000) + (td.seconds + td.days * 24 * 3600) * 10**3) / float(10**3)
			dt1 = t1-self.timeck
			dt2 = t2 - t1
			dt3 = t3 - t2
			dtt = t3 - self.timeck

			print >> self.stdout, "Comms: {0:9.3f} - Data: {1:9.3f} - Events: {2:9.3f} TOTAL {3:6.3f}  EV {4:5}".format(secs(dt1),secs(dt2),secs(dt3),secs(dtt),self.session.events)
			print >> self.stdout, datetime.now().ctime(),self.client_address, 'disconnected!'
			print >> self.stdout, "*"*80
		finally:
			sys.stdout.write(self.stdout.getvalue())
			sys.stdout.flush()

if __name__ == "__main__":
	try:
		server = SocketServer.ThreadingTCPServer(('', 60010), SGAvlRequestHandler)
		#server = SocketServer.TCPServer(('', 60010), SGAvlRequestHandler)
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
