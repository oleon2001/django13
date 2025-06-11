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

settings.DEBUG = False


class CFERequestHandler(SocketServer.BaseRequestHandler ):
	def setup(self):
		print "*"*80
		print datetime.now().ctime(), self.client_address, 'connected!'

	def handle(self):
		self.imei = None
		print self.request
		data = self.request[0]
		socket = self.request[1]
		nBytes = len(data)
		try: 
			imei,outputs = data.split(",",1)
			self.imei = int(imei)
			self.outs = int(outputs)
			self.dev = tracker.SGAvl.objects.get(imei = self.imei)
			self.dev.outputs = self.outs
			self.dev.save()
			print "From:", self.imei
			print "Outputs:", self.outs
			print "Bytes", nBytes
			if self.dev.outputs != self.dev.inputs:
				response = "*CFE"+str(self.dev.inputs)+"\0"
				socket.sendto(response,self.client_address)
				print "Sent COMMAND:",response
			else:
				response = "*ACK\0"
				socket.sendto(response,self.client_address)
				print "Sent ",response
		finally: 
			pass
		#	self.request.close()
			
	def finish(self):
		sys.stdout.flush()
		pass

if __name__ == "__main__":
	try:
		#server = SocketServer.ThreadingUDPServer(('', 50000), CFERequestHandler)
		server = SocketServer.UDPServer(('', 51000), CFERequestHandler)
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
