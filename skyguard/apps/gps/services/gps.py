"""
GPS service implementation.
"""
from typing import List, Optional, Any
from django.utils import timezone
from django.contrib.gis.geos import Point

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
            # Validar y normalizar estructura de datos
            if 'position' not in location_data:
                # Si no hay position, crear desde lat/lon
                if 'latitude' in location_data and 'longitude' in location_data:
                    lat = float(location_data['latitude'])
                    lon = float(location_data['longitude'])
                    location_data['position'] = Point(lon, lat)  # Point(x, y) = Point(lon, lat)
                else:
                    raise InvalidLocationDataError('Missing position or latitude/longitude')
            
            # Validar campos requeridos
            required_fields = ['timestamp']
            if not all(field in location_data for field in required_fields):
                raise InvalidLocationDataError('Missing required location fields')
            
            # Asegurar que position es un objeto Point
            if not isinstance(location_data['position'], Point):
                if isinstance(location_data['position'], (list, tuple)):
                    lon, lat = location_data['position']
                    location_data['position'] = Point(lon, lat)
                else:
                    raise InvalidLocationDataError('Invalid position format')
            
            # Crear registro de ubicación
            location = self.repository.create_location(device, location_data)
            
            # Actualizar posición del dispositivo
            self.repository.update_device_position(device.imei, location.position)
            
            # Crear evento de tracking
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
            self.repository.create_event(device, event_data)
        except Exception as e:
            raise InvalidEventDataError(f'Error processing event: {str(e)}')

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