"""
Unit tests for GPS services.
"""
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.gis.geos import Point

from skyguard.apps.gps.services import GPSService
from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
from skyguard.core.exceptions import (
    DeviceNotFoundError,
    InvalidLocationDataError,
    InvalidEventDataError,
)


class GPSServiceTest(TestCase):
    """Test cases for GPS service."""
    
    def setUp(self):
        """Set up test data."""
        self.repository = Mock()
        self.service = GPSService(self.repository)
        
        # Create test device
        self.device = GPSDevice.objects.create(
            imei=123456789012345,
            name='Test Device',
            protocol='concox'
        )
        
        # Create test location
        self.location = GPSLocation.objects.create(
            device=self.device,
            timestamp=datetime.now(),
            position=Point(0, 0),
            speed=0,
            course=0,
            altitude=0
        )
        
        # Create test event
        self.event = GPSEvent.objects.create(
            device=self.device,
            type='TRACK',
            timestamp=datetime.now(),
            position=Point(0, 0),
            speed=0,
            course=0,
            altitude=0
        )
    
    def test_process_location_valid_data(self):
        """Test processing valid location data."""
        # Arrange
        location_data = {
            'latitude': 0,
            'longitude': 0,
            'timestamp': datetime.now(),
            'speed': 0,
            'course': 0,
            'altitude': 0
        }
        self.repository.create_location.return_value = self.location
        
        # Act
        self.service.process_location(self.device, location_data)
        
        # Assert
        self.repository.create_location.assert_called_once()
        self.repository.update_device_position.assert_called_once()
    
    def test_process_location_invalid_data(self):
        """Test processing invalid location data."""
        # Arrange
        location_data = {
            'latitude': 0,
            'longitude': 0
            # Missing timestamp
        }
        
        # Act & Assert
        with self.assertRaises(InvalidLocationDataError):
            self.service.process_location(self.device, location_data)
    
    def test_get_device_history_device_not_found(self):
        """Test getting history for non-existent device."""
        # Arrange
        self.repository.get_device.return_value = None
        
        # Act & Assert
        with self.assertRaises(DeviceNotFoundError):
            self.service.get_device_history(123456789012345, None, None)
    
    def test_get_device_history_success(self):
        """Test getting device history successfully."""
        # Arrange
        self.repository.get_device.return_value = self.device
        self.repository.get_device_locations.return_value = [self.location]
        
        # Act
        history = self.service.get_device_history(
            self.device.imei,
            datetime.now() - timedelta(hours=1),
            datetime.now()
        )
        
        # Assert
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['position']['latitude'], 0)
        self.assertEqual(history[0]['position']['longitude'], 0)
    
    def test_process_event_valid_data(self):
        """Test processing valid event data."""
        # Arrange
        event_data = {
            'type': 'TRACK',
            'timestamp': datetime.now(),
            'position': Point(0, 0),
            'speed': 0,
            'course': 0,
            'altitude': 0
        }
        self.repository.create_event.return_value = self.event
        
        # Act
        self.service.process_event(self.device, event_data)
        
        # Assert
        self.repository.create_event.assert_called_once()
    
    def test_process_event_invalid_data(self):
        """Test processing invalid event data."""
        # Arrange
        event_data = {
            'type': 'TRACK'
            # Missing timestamp
        }
        
        # Act & Assert
        with self.assertRaises(InvalidEventDataError):
            self.service.process_event(self.device, event_data)
    
    def test_get_device_events_device_not_found(self):
        """Test getting events for non-existent device."""
        # Arrange
        self.repository.get_device.return_value = None
        
        # Act & Assert
        with self.assertRaises(DeviceNotFoundError):
            self.service.get_device_events(123456789012345)
    
    def test_get_device_events_success(self):
        """Test getting device events successfully."""
        # Arrange
        self.repository.get_device.return_value = self.device
        self.repository.get_device_events.return_value = [self.event]
        
        # Act
        events = self.service.get_device_events(self.device.imei)
        
        # Assert
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'TRACK')
        self.assertEqual(events[0]['position']['latitude'], 0)
        self.assertEqual(events[0]['position']['longitude'], 0) 