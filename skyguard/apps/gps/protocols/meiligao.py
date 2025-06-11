"""
Meiligao protocol implementation for GPS tracking.
"""
import struct
from datetime import datetime
from pytz import utc
from django.contrib.gis.geos import Point

from skyguard.apps.gps.protocols.base import BaseProtocol, BasePosition


class MeiligaoPosition(BasePosition):
    """Meiligao protocol position data."""
    
    def __init__(self, data):
        """Initialize position data from Meiligao packet."""
        super().__init__()
        
        # Extract date and time
        year = 2000 + data[0]
        month = data[1]
        day = data[2]
        hour = data[3]
        minute = data[4]
        second = data[5]
        
        self.timestamp = datetime(year, month, day, hour, minute, second, tzinfo=utc)
        
        # Extract position
        lat = struct.unpack("<i", data[6:10])[0] / 1800000.0
        lon = struct.unpack("<i", data[10:14])[0] / 1800000.0
        self.position = Point(lon, lat)
        
        # Extract speed and course
        self.speed = struct.unpack("<H", data[14:16])[0] / 10.0  # km/h
        self.course = struct.unpack("<H", data[16:18])[0] / 10.0  # degrees
        
        # Extract status
        status = data[18]
        self.is_valid = bool(status & 0x01)
        self.is_moving = bool(status & 0x02)
        self.is_charging = bool(status & 0x04)
        self.is_low_battery = bool(status & 0x08)
        
        # Extract battery level
        self.battery_level = data[19]  # percentage
        
        # Extract signal strength
        self.signal_strength = data[20]  # dBm
        
        # Extract satellites
        self.satellites = data[21]
        
        # Extract altitude
        self.altitude = struct.unpack("<h", data[22:24])[0]  # meters


class MeiligaoProtocol(BaseProtocol):
    """Meiligao protocol implementation."""
    
    def __init__(self):
        """Initialize the Meiligao protocol."""
        super().__init__()
        self.header = b'\x24\x24'
        self.footer = b'\x0D\x0A'
    
    def decode_imei(self, data):
        """Decode IMEI from login packet."""
        if len(data) < 17:
            raise ValueError("Invalid login packet length")
        return int(data[2:17])
    
    def validate_packet(self, data):
        """Validate Meiligao packet."""
        if len(data) < 4:
            return False
        
        if not data.startswith(self.header):
            return False
            
        if not data.endswith(self.footer):
            return False
            
        # Verify checksum
        checksum = sum(data[2:-3]) & 0xFF
        if checksum != data[-3]:
            return False
            
        return True
    
    def decode_position(self, data):
        """Decode position data from packet."""
        if not self.validate_packet(data):
            raise ValueError("Invalid packet")
            
        packet_type = data[2]
        if packet_type != 0x01:  # Position data packet
            raise ValueError(f"Invalid packet type: {packet_type}")
            
        return MeiligaoPosition(data[3:-3]) 