"""
Protocol handlers for GPS devices.
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from django.contrib.gis.geos import Point
import struct
import binascii

from skyguard.core.interfaces import IProtocolHandler
from skyguard.apps.gps.models import GPSDevice


class GPSProtocolHandler(IProtocolHandler):
    """Base class for GPS protocol handlers."""
    
    def __init__(self):
        """Initialize the protocol handler."""
        self.supported_protocols = {
            'concox': ConcoxProtocolHandler,
            'meiligao': MeiligaoProtocolHandler,
            'wialon': WialonProtocolHandler
        }
    
    def get_handler(self, protocol: str) -> 'GPSProtocolHandler':
        """Get the appropriate protocol handler."""
        handler_class = self.supported_protocols.get(protocol.lower())
        if not handler_class:
            raise ValueError(f"Unsupported protocol: {protocol}")
        return handler_class()
    
    def decode_packet(self, data: bytes) -> Dict[str, Any]:
        """Decode a protocol packet."""
        raise NotImplementedError
    
    def encode_command(self, command: str, params: Dict[str, Any]) -> bytes:
        """Encode a command for the device."""
        raise NotImplementedError
    
    def validate_packet(self, data: bytes) -> bool:
        """Validate a protocol packet."""
        raise NotImplementedError


class ConcoxProtocolHandler(GPSProtocolHandler):
    """Handler for Concox protocol."""
    
    def decode_packet(self, data: bytes) -> Dict[str, Any]:
        """Decode a Concox protocol packet."""
        try:
            # Basic packet structure: Start Bit(2) + Packet Length(1) + Protocol Number(1) + Information Content + Information Serial Number(2) + Error Check(2) + Stop Bit(2)
            if len(data) < 8:
                return {}
            
            # Extract IMEI (first 8 bytes after start bit)
            imei = int.from_bytes(data[2:10], byteorder='big')
            
            # Extract GPS data
            lat = struct.unpack('>i', data[10:14])[0] / 1800000.0
            lon = struct.unpack('>i', data[14:18])[0] / 1800000.0
            speed = struct.unpack('>H', data[18:20])[0] / 10.0
            course = struct.unpack('>H', data[20:22])[0]
            altitude = struct.unpack('>h', data[22:24])[0]
            satellites = data[24]
            
            return {
                'imei': imei,
                'position': Point(lon, lat),
                'speed': speed,
                'course': course,
                'altitude': altitude,
                'satellites': satellites,
                'timestamp': datetime.now()
            }
        except Exception:
            return {}
    
    def encode_command(self, command: str, params: Dict[str, Any]) -> bytes:
        """Encode a Concox protocol command."""
        try:
            if command == 'SET_INTERVAL':
                interval = params.get('interval', 60)
                return struct.pack('>BBHB', 0x78, 0x78, 0x80, interval)
            elif command == 'SET_IP':
                ip = params.get('ip', '0.0.0.0')
                port = params.get('port', 0)
                ip_parts = [int(x) for x in ip.split('.')]
                return struct.pack('>BBBBBBH', 0x78, 0x78, 0x80, *ip_parts, port)
            return b''
        except Exception:
            return b''
    
    def validate_packet(self, data: bytes) -> bool:
        """Validate a Concox protocol packet."""
        try:
            if len(data) < 8:
                return False
            # Check start and stop bits
            if data[0:2] != b'\x78\x78' or data[-2:] != b'\x0D\x0A':
                return False
            # Check packet length
            if data[2] != len(data) - 4:
                return False
            return True
        except Exception:
            return False


class MeiligaoProtocolHandler(GPSProtocolHandler):
    """Handler for Meiligao protocol."""
    
    def decode_packet(self, data: bytes) -> Dict[str, Any]:
        """Decode a Meiligao protocol packet."""
        try:
            # Basic packet structure: Start Bit(2) + Packet Length(1) + Protocol Number(1) + Information Content + Information Serial Number(2) + Error Check(2) + Stop Bit(2)
            if len(data) < 8:
                return {}
            
            # Extract IMEI (first 8 bytes after start bit)
            imei = int.from_bytes(data[2:10], byteorder='big')
            
            # Extract GPS data
            lat = struct.unpack('>i', data[10:14])[0] / 1800000.0
            lon = struct.unpack('>i', data[14:18])[0] / 1800000.0
            speed = struct.unpack('>H', data[18:20])[0] / 10.0
            course = struct.unpack('>H', data[20:22])[0]
            altitude = struct.unpack('>h', data[22:24])[0]
            satellites = data[24]
            
            return {
                'imei': imei,
                'position': Point(lon, lat),
                'speed': speed,
                'course': course,
                'altitude': altitude,
                'satellites': satellites,
                'timestamp': datetime.now()
            }
        except Exception:
            return {}
    
    def encode_command(self, command: str, params: Dict[str, Any]) -> bytes:
        """Encode a Meiligao protocol command."""
        try:
            if command == 'SET_INTERVAL':
                interval = params.get('interval', 60)
                return struct.pack('>BBHB', 0x78, 0x78, 0x80, interval)
            elif command == 'SET_IP':
                ip = params.get('ip', '0.0.0.0')
                port = params.get('port', 0)
                ip_parts = [int(x) for x in ip.split('.')]
                return struct.pack('>BBBBBBH', 0x78, 0x78, 0x80, *ip_parts, port)
            return b''
        except Exception:
            return b''
    
    def validate_packet(self, data: bytes) -> bool:
        """Validate a Meiligao protocol packet."""
        try:
            if len(data) < 8:
                return False
            # Check start and stop bits
            if data[0:2] != b'\x78\x78' or data[-2:] != b'\x0D\x0A':
                return False
            # Check packet length
            if data[2] != len(data) - 4:
                return False
            return True
        except Exception:
            return False


class WialonProtocolHandler(GPSProtocolHandler):
    """Handler for Wialon protocol."""
    
    def decode_packet(self, data: bytes) -> Dict[str, Any]:
        """Decode a Wialon protocol packet."""
        try:
            # Basic packet structure: Start Bit(2) + Packet Length(1) + Protocol Number(1) + Information Content + Information Serial Number(2) + Error Check(2) + Stop Bit(2)
            if len(data) < 8:
                return {}
            
            # Extract IMEI (first 8 bytes after start bit)
            imei = int.from_bytes(data[2:10], byteorder='big')
            
            # Extract GPS data
            lat = struct.unpack('>i', data[10:14])[0] / 1800000.0
            lon = struct.unpack('>i', data[14:18])[0] / 1800000.0
            speed = struct.unpack('>H', data[18:20])[0] / 10.0
            course = struct.unpack('>H', data[20:22])[0]
            altitude = struct.unpack('>h', data[22:24])[0]
            satellites = data[24]
            
            return {
                'imei': imei,
                'position': Point(lon, lat),
                'speed': speed,
                'course': course,
                'altitude': altitude,
                'satellites': satellites,
                'timestamp': datetime.now()
            }
        except Exception:
            return {}
    
    def encode_command(self, command: str, params: Dict[str, Any]) -> bytes:
        """Encode a Wialon protocol command."""
        try:
            if command == 'SET_INTERVAL':
                interval = params.get('interval', 60)
                return struct.pack('>BBHB', 0x78, 0x78, 0x80, interval)
            elif command == 'SET_IP':
                ip = params.get('ip', '0.0.0.0')
                port = params.get('port', 0)
                ip_parts = [int(x) for x in ip.split('.')]
                return struct.pack('>BBBBBBH', 0x78, 0x78, 0x80, *ip_parts, port)
            return b''
        except Exception:
            return b''
    
    def validate_packet(self, data: bytes) -> bool:
        """Validate a Wialon protocol packet."""
        try:
            if len(data) < 8:
                return False
            # Check start and stop bits
            if data[0:2] != b'\x78\x78' or data[-2:] != b'\x0D\x0A':
                return False
            # Check packet length
            if data[2] != len(data) - 4:
                return False
            return True
        except Exception:
            return False 