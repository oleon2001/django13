"""
Repositories for the GPS application.
"""
from typing import Optional, List
from django.contrib.gis.geos import Point
from django.utils import timezone

from skyguard.core.interfaces import IDeviceRepository
from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent


class GPSDeviceRepository(IDeviceRepository):
    """Repository for GPS devices."""
    
    def get_device(self, imei: int) -> Optional[GPSDevice]:
        """Get a GPS device by IMEI."""
        try:
            return GPSDevice.objects.get(imei=imei)
        except GPSDevice.DoesNotExist:
            return None
    
    def get_all_devices(self) -> List[GPSDevice]:
        """Get all GPS devices."""
        return list(GPSDevice.objects.all())
    
    def save_device(self, device: GPSDevice) -> None:
        """Save a GPS device."""
        device.save()
    
    def update_device_position(self, imei: int, position: Point) -> None:
        """Update GPS device position."""
        device = self.get_device(imei)
        if device:
            device.position = position
            device.last_log = timezone.now()
            device.save()
    
    def get_device_locations(self, imei: int, start_time=None, end_time=None) -> List[GPSLocation]:
        """Get location history for a device."""
        query = GPSLocation.objects.filter(device__imei=imei)
        if start_time:
            query = query.filter(timestamp__gte=start_time)
        if end_time:
            query = query.filter(timestamp__lte=end_time)
        return query.order_by('timestamp')
    
    def get_device_events(self, imei: int, event_type=None) -> List[GPSEvent]:
        """Get events for a device."""
        query = GPSEvent.objects.filter(device__imei=imei)
        if event_type:
            query = query.filter(type=event_type)
        return query.order_by('-timestamp')
    
    def create_location(self, device: GPSDevice, location_data: dict) -> GPSLocation:
        """Create a new location record."""
        location = GPSLocation(
            device=device,
            position=location_data['position'],
            speed=location_data.get('speed', 0),
            course=location_data.get('course', 0),
            altitude=location_data.get('altitude', 0),
            satellites=location_data.get('satellites', 0),
            accuracy=location_data.get('accuracy', 0),
            timestamp=location_data.get('timestamp', timezone.now()),
            hdop=location_data.get('hdop'),
            pdop=location_data.get('pdop'),
            fix_quality=location_data.get('fix_quality'),
            fix_type=location_data.get('fix_type')
        )
        location.save()
        return location
    
    def create_event(self, device: GPSDevice, event_data: dict) -> GPSEvent:
        """Create a new event record."""
        event = GPSEvent(
            device=device,
            type=event_data['type'],
            timestamp=event_data.get('timestamp', timezone.now()),
            position=event_data.get('position'),
            speed=event_data.get('speed'),
            course=event_data.get('course'),
            altitude=event_data.get('altitude'),
            odometer=event_data.get('odometer'),
            raw_data=event_data.get('raw_data')
        )
        event.save()
        return event 