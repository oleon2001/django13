"""
Base interfaces for the SkyGuard system.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Any, Protocol
from django.contrib.gis.geos import Point

from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent


class IDeviceRepository(ABC):
    """Interface for device repositories."""
    
    @abstractmethod
    def get_device(self, imei: int) -> Any:
        """Get a device by IMEI."""
        pass
    
    @abstractmethod
    def save_device(self, device: Any) -> None:
        """Save a device."""
        pass
    
    @abstractmethod
    def update_device_position(self, imei: int, position: Point) -> None:
        """Update device position."""
        pass


class ILocationService(Protocol):
    """Interface for location services."""
    
    def process_location(self, device: GPSDevice, location_data: dict) -> None:
        """Process location data for a device."""
        ...
    
    def get_device_history(self, imei: int, start_time: Any, end_time: Any) -> List[dict]:
        """Get location history for a device."""
        ...


class IEventService(Protocol):
    """Interface for event services."""
    
    def process_event(self, device: GPSDevice, event_data: dict) -> None:
        """Process an event for a device."""
        ...
    
    def get_device_events(self, imei: int, event_type: Optional[str] = None) -> List[dict]:
        """Get events for a device."""
        ...


class IProtocolHandler(ABC):
    """Interface for protocol handlers."""
    
    @abstractmethod
    def decode_packet(self, data: bytes) -> dict:
        """Decode a protocol packet."""
        pass
    
    @abstractmethod
    def encode_command(self, command_type: str, data: dict) -> bytes:
        """Encode a command for the protocol."""
        pass
    
    @abstractmethod
    def validate_packet(self, data: bytes) -> bool:
        """Validate a protocol packet."""
        pass


class IGPSDeviceRepository(Protocol):
    """Interface for GPS device repository."""
    
    def get_device(self, imei: int) -> Optional[GPSDevice]:
        """Get a device by IMEI."""
        ...
    
    def create_location(self, device: GPSDevice, location_data: dict) -> GPSLocation:
        """Create a location record."""
        ...
    
    def update_device_position(self, imei: int, position: Point) -> None:
        """Update device position."""
        ...
    
    def create_event(self, device: GPSDevice, event_data: dict) -> GPSEvent:
        """Create an event record."""
        ...
    
    def get_device_locations(self, imei: int, start_time: Any, end_time: Any) -> List[GPSLocation]:
        """Get device locations."""
        ...
    
    def get_device_events(self, imei: int, event_type: Optional[str] = None) -> List[GPSEvent]:
        """Get device events."""
        ... 