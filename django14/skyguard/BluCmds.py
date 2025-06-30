#!/usr/bin/python
# -*- coding: utf-8 -*-
# Bluetooth AVL command sender

import socket
import struct
from PyCRC.CRCCCITT import CRCCCITT

#os.environ['DJANGO_SETTINGS_MODULE'] = 'sites.www.settings'
#path = '/home/django13/skyguard'
#if path not in sys.path:
#    sys.path.append(path)

from django.db import transaction, DatabaseError, IntegrityError, connection
from django.contrib.gis.geos import Point
from django.conf import settings
import gps.tracker.models as tracker
import gps.udp.models as udp


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

crc = CRCCCITT('1D0F')

def sendCmd(session,cmd):
	cmd = struct.pack("<BLB",RSPID_SESSION,session.session,cmd)
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.sendto(cmd,(session.host,session.port))
	
def BluAvlReset(name):
	avl = tracker.SGAvl.objects.get(name = name)
	session = udp.UdpSession.objects.get(imei = avl)
	sendCmd(session,CMDID_RESET)

def BluAvlInfo(name):
	avl = tracker.SGAvl.objects.get(name = name)
	session = udp.UdpSession.objects.get(imei = avl)
	sendCmd(session,CMDID_DEVINFO)
	
def BluAvlMotorON(name):
	avl = tracker.SGAvl.objects.get(name = name)
	session = udp.UdpSession.objects.get(imei = avl)
	sendCmd(session,CMDID_MOTORON)

def BluAvlMotorOFF(name):
	avl = tracker.SGAvl.objects.get(name = name)
	session = udp.UdpSession.objects.get(imei = avl)
	sendCmd(session,CMDID_MOTOROFF)

