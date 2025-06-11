"""
Services for the GPS application.
"""
from typing import List, Optional, Any
from django.utils import timezone

from skyguard.core.interfaces import ILocationService, IEventService, IGPSDeviceRepository
from skyguard.core.exceptions import (
    DeviceNotFoundError,
    InvalidLocationDataError,
    InvalidEventDataError,
)
from skyguard.apps.gps.models import GPSDevice


class GPSService(ILocationService, IEventService):
    """Service for GPS device operations."""
    
    def __init__(self, repository: IGPSDeviceRepository):
        """
        Initialize the GPS service.
        
        Args:
            repository: Repository for GPS device operations
        """
        self.repository = repository
    
    def process_location(self, device: GPSDevice, location_data: dict) -> None:
        """
        Process location data for a GPS device.
        
        Args:
            device: GPS device
            location_data: Location data dictionary
            
        Raises:
            InvalidLocationDataError: If location data is invalid
        """
        try:
            # Validate required fields
            required_fields = ['latitude', 'longitude', 'timestamp']
            if not all(field in location_data for field in required_fields):
                raise InvalidLocationDataError('Missing required location fields')
            
            # Create location record
            location = self.repository.create_location(device, location_data)
            
            # Update device position
            self.repository.update_device_position(device.imei, location.position)
            
            # Create track event
            event_data = {
                'type': 'TRACK',
                'timestamp': location.timestamp,
                'position': location.position,
                'speed': location.speed,
                'course': location.course,
                'altitude': location.altitude,
                'odometer': device.odometer
            }
            self.process_event(device, event_data)
        except Exception as e:
            raise InvalidLocationDataError(f'Error processing location: {str(e)}')
    
    def get_device_history(self, imei: int, start_time: Any, end_time: Any) -> List[dict]:
        """
        Get location history for a GPS device.
        
        Args:
            imei: Device IMEI
            start_time: Start time for history
            end_time: End time for history
            
        Returns:
            List of location records
            
        Raises:
            DeviceNotFoundError: If device is not found
        """
        try:
            device = self.repository.get_device(imei)
            if not device:
                raise DeviceNotFoundError(f'Device not found: {imei}')
            
            locations = self.repository.get_device_locations(imei, start_time, end_time)
            return [{
                'timestamp': loc.timestamp,
                'position': {
                    'latitude': loc.position.y,
                    'longitude': loc.position.x
                },
                'speed': loc.speed,
                'course': loc.course,
                'altitude': loc.altitude,
                'satellites': loc.satellites,
                'accuracy': loc.accuracy,
                'hdop': loc.hdop,
                'pdop': loc.pdop,
                'fix_quality': loc.fix_quality,
                'fix_type': loc.fix_type
            } for loc in locations]
        except DeviceNotFoundError:
            raise
        except Exception as e:
            raise InvalidLocationDataError(f'Error getting device history: {str(e)}')
    
    def process_event(self, device: GPSDevice, event_data: dict) -> None:
        """
        Process an event for a GPS device.
        
        Args:
            device: GPS device
            event_data: Event data dictionary
            
        Raises:
            InvalidEventDataError: If event data is invalid
        """
        try:
            # Validate required fields
            required_fields = ['type', 'timestamp']
            if not all(field in event_data for field in required_fields):
                raise InvalidEventDataError('Missing required event fields')
            
            # Create event record
            event = self.repository.create_event(device, event_data)
            
            # Update device state if needed
            if event.type == 'TRACK':
                device.speed = event.speed
                device.course = event.course
                device.altitude = event.altitude
                device.save()
        except Exception as e:
            raise InvalidEventDataError(f'Error processing event: {str(e)}')
    
    def get_device_events(self, imei: int, event_type: Optional[str] = None) -> List[dict]:
        """
        Get events for a GPS device.
        
        Args:
            imei: Device IMEI
            event_type: Optional event type filter
            
        Returns:
            List of event records
            
        Raises:
            DeviceNotFoundError: If device is not found
        """
        try:
            device = self.repository.get_device(imei)
            if not device:
                raise DeviceNotFoundError(f'Device not found: {imei}')
            
            events = self.repository.get_device_events(imei, event_type)
            return [{
                'type': event.type,
                'timestamp': event.timestamp,
                'position': {
                    'latitude': event.position.y,
                    'longitude': event.position.x
                } if event.position else None,
                'speed': event.speed,
                'course': event.course,
                'altitude': event.altitude,
                'odometer': event.odometer
            } for event in events]
        except DeviceNotFoundError:
            raise
        except Exception as e:
            raise InvalidEventDataError(f'Error getting device events: {str(e)}') 