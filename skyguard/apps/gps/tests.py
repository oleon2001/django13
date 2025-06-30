"""
Tests for the GPS application.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.gis.geos import Point
from django.utils import timezone
import json

from .models import GPSDevice, GPSLocation, GPSEvent
from .services import GPSService
from .repositories import GPSDeviceRepository
from .protocols import GPSProtocolHandler, ConcoxProtocolHandler, WialonProtocolHandler


class GPSDeviceTests(TestCase):
    """Tests for GPS device models and operations."""
    
    def setUp(self):
        """Set up test data."""
        self.device = GPSDevice.objects.create(
            imei=123456789012345,
            name='Test Device',
            protocol='concox',
            position=Point(0, 0),
            is_active=True
        )
        self.repository = GPSDeviceRepository()
        self.service = GPSService(self.repository)
    
    def test_device_creation(self):
        """Test device creation."""
        self.assertEqual(self.device.imei, 123456789012345)
        self.assertEqual(self.device.name, 'Test Device')
        self.assertEqual(self.device.protocol, 'concox')
        self.assertTrue(self.device.is_active)
    
    def test_device_repository(self):
        """Test device repository operations."""
        # Test get_device
        device = self.repository.get_device(123456789012345)
        self.assertEqual(device, self.device)
        
        # Test update_device_position
        new_position = Point(1, 1)
        self.repository.update_device_position(123456789012345, new_position)
        self.device.refresh_from_db()
        self.assertEqual(self.device.position, new_position)
    
    def test_location_creation(self):
        """Test location creation and processing."""
        location_data = {
            'position': Point(1, 1),
            'speed': 50.0,
            'course': 90.0,
            'altitude': 100.0,
            'satellites': 8,
            'accuracy': 5.0,
            'hdop': 1.0,
            'pdop': 2.0,
            'fix_quality': 1,
            'fix_type': 3,
            'timestamp': timezone.now()
        }
        
        self.service.process_location(self.device, location_data)
        
        # Check location was created
        location = GPSLocation.objects.filter(device=self.device).first()
        self.assertIsNotNone(location)
        self.assertEqual(location.position, location_data['position'])
        self.assertEqual(location.speed, location_data['speed'])
        
        # Check device was updated
        self.device.refresh_from_db()
        self.assertEqual(self.device.position, location_data['position'])
        self.assertEqual(self.device.speed, location_data['speed'])
    
    def test_event_creation(self):
        """Test event creation and processing."""
        event_data = {
            'type': 'TRACK',
            'timestamp': timezone.now(),
            'position': Point(1, 1),
            'speed': 50.0,
            'course': 90.0,
            'altitude': 100.0,
            'odometer': 1000.0
        }
        
        self.service.process_event(self.device, event_data)
        
        # Check event was created
        event = GPSEvent.objects.filter(device=self.device).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.type, event_data['type'])
        self.assertEqual(event.position, event_data['position'])
        
        # Check device was updated
        self.device.refresh_from_db()
        self.assertEqual(self.device.position, event_data['position'])
        self.assertEqual(self.device.speed, event_data['speed'])


class GPSProtocolTests(TestCase):
    """Tests for GPS protocol handlers."""
    
    def setUp(self):
        """Set up test data."""
        self.handler = GPSProtocolHandler()
    
    def test_protocol_handler_selection(self):
        """Test protocol handler selection."""
        # Test valid protocol
        handler = self.handler.get_handler('concox')
        self.assertIsInstance(handler, ConcoxProtocolHandler)
        
        # Test invalid protocol
        with self.assertRaises(ValueError):
            self.handler.get_handler('invalid')
    
    def test_concox_protocol(self):
        """Test Concox protocol handler."""
        handler = ConcoxProtocolHandler()
        
        # Test packet validation
        valid_packet = b'\x78\x78\x0B\x01\x03\x51\x08\x42\x70\x00\x32\x01\x00\x0D\x0A'
        self.assertTrue(handler.validate_packet(valid_packet))
        
        # Test packet decoding
        data = handler.decode_packet(valid_packet)
        self.assertIn('imei', data)
        self.assertIn('position', data)
        
        # Test command encoding
        command = handler.encode_command('SET_INTERVAL', {'interval': 60})
        self.assertGreater(len(command), 0)


class GPSViewTests(TestCase):
    """Tests for GPS views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.device = GPSDevice.objects.create(
            imei=123456789012345,
            name='Test Device',
            protocol='concox',
            position=Point(0, 0),
            is_active=True
        )
    
    def test_device_data_endpoint(self):
        """Test device data endpoint."""
        # Create a valid Concox packet
        packet = b'\x78\x78\x0B\x01\x03\x51\x08\x42\x70\x00\x32\x01\x00\x0D\x0A'
        
        # Send POST request
        response = self.client.post(
            reverse('gps:device_data', args=['concox']),
            data=packet,
            content_type='application/octet-stream'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check device was updated
        self.device.refresh_from_db()
        self.assertIsNotNone(self.device.last_log)
    
    def test_device_command_endpoint(self):
        """Test device command endpoint."""
        # Create command data
        command_data = {
            'command': 'SET_INTERVAL',
            'params': {'interval': 60}
        }
        
        # Send POST request
        response = self.client.post(
            reverse('gps:device_command', args=[self.device.imei]),
            data=json.dumps(command_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'Command sent')
    
    def test_device_history_endpoint(self):
        """Test device history endpoint."""
        # Create some location data
        location = GPSLocation.objects.create(
            device=self.device,
            position=Point(1, 1),
            speed=50.0,
            course=90.0,
            altitude=100.0,
            satellites=8,
            accuracy=5.0,
            timestamp=timezone.now()
        )
        
        # Send GET request
        response = self.client.get(
            reverse('gps:device_history', args=[self.device.imei])
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('locations', data)
        self.assertEqual(len(data['locations']), 1)
    
    def test_device_events_endpoint(self):
        """Test device events endpoint."""
        # Create some event data
        event = GPSEvent.objects.create(
            device=self.device,
            type='TRACK',
            position=Point(1, 1),
            speed=50.0,
            course=90.0,
            altitude=100.0,
            timestamp=timezone.now()
        )
        
        # Send GET request
        response = self.client.get(
            reverse('gps:device_events', args=[self.device.imei])
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('events', data)
        self.assertEqual(len(data['events']), 1) 