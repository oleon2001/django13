"""
Base protocol classes for GPS devices.
"""
import struct
from datetime import datetime
from django.contrib.gis.geos import Point


class BaseProtocol:
    """Base class for GPS protocols."""
    
    def __init__(self):
        """Initialize the protocol."""
        self.device = None
        self.imei = None
        
    def decode_imei(self, data):
        """Decode IMEI from protocol data."""
        raise NotImplementedError("Subclasses must implement decode_imei()")
        
    def decode_position(self, data):
        """Decode position data from protocol."""
        raise NotImplementedError("Subclasses must implement decode_position()")
        
    def encode_command(self, command_type, data=None):
        """Encode command for the protocol."""
        raise NotImplementedError("Subclasses must implement encode_command()")
        
    def validate_packet(self, data):
        """Validate incoming packet data."""
        raise NotImplementedError("Subclasses must implement validate_packet()")
        
    def parse_packet(self, data):
        """Parse incoming packet data."""
        raise NotImplementedError("Subclasses must implement parse_packet()")


class BasePosition:
    """Base class for position data."""
    
    def __init__(self, latitude, longitude, speed=0, course=0, altitude=0, satellites=0, accuracy=0):
        """Initialize position data."""
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.course = course
        self.altitude = altitude
        self.satellites = satellites
        self.accuracy = accuracy
        self.timestamp = datetime.now()
        
    @property
    def point(self):
        """Get the position as a GeoDjango Point."""
        return Point(self.longitude, self.latitude)
        
    def to_dict(self):
        """Convert position to dictionary."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'course': self.course,
            'altitude': self.altitude,
            'satellites': self.satellites,
            'accuracy': self.accuracy,
            'timestamp': self.timestamp
        } 