#!/usr/bin/python
# -*- coding: utf-8 -*-
# Bluetooth AVL command sender

import socket
import struct
from PyCRC.CRCCCITT import CRCCCITT

from django.db import transaction, DatabaseError, IntegrityError, connection
from django.contrib.gis.geos import Point
from django.conf import settings
from skyguard.apps.gps.models.device import GPSDevice
from skyguard.apps.gps.models.protocols import UDPSession

# Constants
PKTID_LOGIN = 0x01
PKTID_PING = 0x02
PKTID_DEVINFO = 0x03
PKTID_DATA = 0x04

RSPID_SESSION = 0x10
RSPID_LOGIN = 0x11

CMDID_DEVINFO = 0x20
CMDID_DATA = 0x21
CMDID_ACK = 0x22
CMDID_MOTORON = 0x23
CMDID_MOTOROFF = 0x24
CMDID_RESET = 0x25

crc = CRCCCITT('1D0F')

def send_cmd(session, cmd):
    """Send a command to a device session."""
    cmd = struct.pack("<BLB", RSPID_SESSION, session.session, cmd)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(cmd, (session.host, session.port))

def blu_avl_reset(device_name):
    """Reset a Bluetooth AVL device."""
    device = GPSDevice.objects.get(name=device_name)
    session = UDPSession.objects.get(device=device)
    send_cmd(session, CMDID_RESET)

def blu_avl_info(device_name):
    """Get information from a Bluetooth AVL device."""
    device = GPSDevice.objects.get(name=device_name)
    session = UDPSession.objects.get(device=device)
    send_cmd(session, CMDID_DEVINFO)

def blu_avl_motor_on(device_name):
    """Turn on the motor of a Bluetooth AVL device."""
    device = GPSDevice.objects.get(name=device_name)
    session = UDPSession.objects.get(device=device)
    send_cmd(session, CMDID_MOTORON)

def blu_avl_motor_off(device_name):
    """Turn off the motor of a Bluetooth AVL device."""
    device = GPSDevice.objects.get(name=device_name)
    session = UDPSession.objects.get(device=device)
    send_cmd(session, CMDID_MOTOROFF) 