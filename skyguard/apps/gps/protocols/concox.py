"""
Concox protocol implementation for GPS tracking.
"""
import struct
from datetime import datetime
from pytz import utc
from django.contrib.gis.geos import Point

from skyguard.apps.gps.protocols.base import BaseProtocol, BasePosition


class ConcoxPosition(BasePosition):
    """Concox protocol position data."""
    
    def __init__(self, data):
        """Initialize position data from Concox packet."""
        super().__init__()
        
        # Extract date and time
        year = 2000 + (data[0] >> 4)
        month = data[0] & 0x0F
        day = data[1] & 0x1F
        hour = data[2] & 0x1F
        minute = data[3] & 0x3F
        second = data[4] & 0x3F
        
        self.timestamp = datetime(year, month, day, hour, minute, second, tzinfo=utc)
        
        # Extract position
        lat = struct.unpack("<i", data[5:9])[0] / 1800000.0
        lon = struct.unpack("<i", data[9:13])[0] / 1800000.0
        self.position = Point(lon, lat)
        
        # Extract speed and course
        self.speed = data[13]  # km/h
        self.course = struct.unpack("<H", data[14:16])[0] / 10.0  # degrees
        
        # Extract status
        status = struct.unpack("<H", data[16:18])[0]
        self.is_valid = bool(status & 0x0001)
        self.is_moving = bool(status & 0x0002)
        self.is_charging = bool(status & 0x0004)
        self.is_low_battery = bool(status & 0x0008)
        
        # Extract battery level
        self.battery_level = data[18]  # percentage
        
        # Extract signal strength
        self.signal_strength = data[19]  # dBm
        
        # Extract satellites
        self.satellites = data[20]
        
        # Extract altitude
        self.altitude = struct.unpack("<h", data[21:23])[0]  # meters


class ConcoxProtocol(BaseProtocol):
    """Concox protocol implementation."""
    
    def __init__(self):
        """Initialize the Concox protocol."""
        super().__init__()
        self.header = b'\x78\x78'
        self.footer = b'\x0D\x0A'
    
    def decode_imei(self, data):
        """Decode IMEI from login packet."""
        if len(data) < 17:
            raise ValueError("Invalid login packet length")
        return int(data[2:17])
    
    def validate_packet(self, data):
        """Validate Concox packet."""
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
        if packet_type != 0x12:  # Position data packet
            raise ValueError(f"Invalid packet type: {packet_type}")
            
        return ConcoxPosition(data[3:-3]) 