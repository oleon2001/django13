"""
Device command module for Bluetooth AVL devices in Tracking app.
"""
import socket
import struct
from enum import Enum
from django.core.exceptions import ObjectDoesNotExist
import skyguard.apps.gps.models as gps_models
from skyguard.apps.tracking.models import UdpSession

Device = gps_models.Device

# Comandos y respuestas
class CommandType(Enum):
    DEVINFO = 0x20
    DATA = 0x21
    ACK = 0x22
    MOTORON = 0x23
    MOTOROFF = 0x24
    RESET = 0x25


def send_cmd(session, cmd):
    """Send a command to a Bluetooth AVL device via UDP."""
    RSPID_SESSION = 0x10
    packet = struct.pack("<BLB", RSPID_SESSION, session.session, cmd)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (session.host, session.port))
    sock.close()


def blu_avl_reset(name):
    """Send RESET command to Bluetooth AVL device by name."""
    avl = Device.objects.get(name=name)
    session = UdpSession.objects.get(imei=avl)
    send_cmd(session, CommandType.RESET.value)


def blu_avl_info(name):
    """Send DEVINFO command to Bluetooth AVL device by name."""
    avl = Device.objects.get(name=name)
    session = UdpSession.objects.get(imei=avl)
    send_cmd(session, CommandType.DEVINFO.value)


def blu_avl_motor_on(name):
    """Send MOTORON command to Bluetooth AVL device by name."""
    avl = Device.objects.get(name=name)
    session = UdpSession.objects.get(imei=avl)
    send_cmd(session, CommandType.MOTORON.value)


def blu_avl_motor_off(name):
    """Send MOTOROFF command to Bluetooth AVL device by name."""
    avl = Device.objects.get(name=name)
    session = UdpSession.objects.get(imei=avl)
    send_cmd(session, CommandType.MOTOROFF.value) 