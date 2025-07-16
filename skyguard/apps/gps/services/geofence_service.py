"""
Service for automatic geofence detection and management.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from skyguard.core.interfaces import IGeofenceService
from skyguard.apps.gps.models import GPSDevice, GeoFence, GeoFenceEvent
from skyguard.apps.gps.notifications import GeofenceNotificationService

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


class GeofenceDetectionService(IGeofenceService):
    """Service for automatic geofence detection and event generation."""
    
    def __init__(self):
        """Initialize the geofence detection service."""
        self.notification_service = GeofenceNotificationService()
        self.logger = logger
    
    def check_device_geofences(self, device: GPSDevice) -> List[Dict[str, Any]]:
        """
        Check all geofences for a device and detect entry/exit events.
        
        Args:
            device: GPS device to check
            
        Returns:
            List of events generated
        """
        if not device.position:
            self.logger.debug(f"Device {device.imei} has no position")
            return []
        
        events_generated = []
        
        # Get all active geofences for this device
        active_geofences = GeoFence.objects.filter(
            is_active=True,
            devices=device
        ).prefetch_related('events')
        
        for geofence in active_geofences:
            event = self._check_single_geofence(device, geofence)
            if event:
                events_generated.append(event)
        
        return events_generated
    
    def _check_single_geofence(self, device: GPSDevice, geofence: GeoFence) -> Optional[Dict[str, Any]]:
        """
        Check a single geofence for entry/exit events.
        
        Args:
            device: GPS device
            geofence: Geofence to check
            
        Returns:
            Event data if an event was generated, None otherwise
        """
        is_inside = geofence.geometry.contains(device.position)
        
        # Get the last event for this device/geofence combination
        last_event = GeoFenceEvent.objects.filter(
            device=device,
            fence=geofence
        ).order_by('-timestamp').first()
        
        # Determine if we need to generate an event
        should_generate_event = False
        event_type = None
        
        if last_event is None:
            # First time checking this device/geofence - generate event if inside
            if is_inside:
                should_generate_event = True
                event_type = 'ENTRY'
        else:
            # Check for state change
            was_inside = (last_event.event_type == 'ENTRY')
            
            if is_inside and not was_inside:
                # Device entered geofence
                should_generate_event = True
                event_type = 'ENTRY'
            elif not is_inside and was_inside:
                # Device exited geofence
                should_generate_event = True
                event_type = 'EXIT'
        
        if should_generate_event:
            return self._generate_geofence_event(device, geofence, event_type)
        
        return None
    
    @transaction.atomic
    def _generate_geofence_event(self, device: GPSDevice, geofence: GeoFence, event_type: str) -> Dict[str, Any]:
        """
        Generate a geofence event and trigger notifications.
        
        Args:
            device: GPS device
            geofence: Geofence
            event_type: 'ENTRY' or 'EXIT'
            
        Returns:
            Event data
        """
        # Create the event
        event = GeoFenceEvent.objects.create(
            fence=geofence,
            device=device,
            event_type=event_type,
            position=device.position,
            timestamp=timezone.now()
        )
        
        self.logger.info(f"Generated geofence event: {device.name} {event_type} {geofence.name}")
        
        # Prepare event data
        event_data = {
            'id': event.id,
            'device_id': device.imei,
            'device_name': device.name,
            'geofence_id': geofence.id,
            'geofence_name': geofence.name,
            'event_type': event_type,
            'position': [device.position.y, device.position.x],  # [lat, lng]
            'timestamp': event.timestamp.isoformat()
        }
        
        # Send WebSocket notification
        self._broadcast_event(event_data, geofence.owner.id)
        
        # Send notifications (email/SMS) if configured
        self._send_notifications(event, geofence, device)
        
        return event_data
    
    def _broadcast_event(self, event_data: Dict[str, Any], user_id: int):
        """
        Broadcast event via WebSocket to the geofence owner.
        
        Args:
            event_data: Event data to broadcast
            user_id: User ID to send to
        """
        if channel_layer:
            try:
                message = {
                    'type': 'geofence_event',
                    'data': event_data
                }
                
                async_to_sync(channel_layer.group_send)(
                    f"geofences_user_{user_id}",
                    message
                )
                
                self.logger.debug(f"Broadcasted geofence event to user {user_id}")
            except Exception as e:
                self.logger.error(f"Error broadcasting geofence event: {e}")
    
    def _send_notifications(self, event: GeoFenceEvent, geofence: GeoFence, device: GPSDevice):
        """
        Send notifications for geofence events.
        
        Args:
            event: The geofence event
            geofence: The geofence
            device: The GPS device
        """
        # Check if notifications are enabled for this event type
        if event.event_type == 'ENTRY' and not geofence.notify_on_entry:
            return
        if event.event_type == 'EXIT' and not geofence.notify_on_exit:
            return
        
        # Check cooldown period
        if self._is_in_cooldown(geofence, device, event.event_type):
            self.logger.debug(f"Geofence {geofence.name} is in cooldown for device {device.name}")
            return
        
        # Send notifications
        try:
            self.notification_service.send_geofence_notification(event, geofence, device)
        except Exception as e:
            self.logger.error(f"Error sending geofence notification: {e}")
    
    def _is_in_cooldown(self, geofence: GeoFence, device: GPSDevice, event_type: str) -> bool:
        """
        Check if geofence is in cooldown period for notifications.
        
        Args:
            geofence: The geofence
            device: The GPS device
            event_type: Type of event
            
        Returns:
            True if in cooldown, False otherwise
        """
        cooldown_seconds = geofence.notification_cooldown
        if cooldown_seconds <= 0:
            return False
        
        # Check for recent events of the same type
        since = timezone.now() - timedelta(seconds=cooldown_seconds)
        recent_events = GeoFenceEvent.objects.filter(
            fence=geofence,
            device=device,
            event_type=event_type,
            timestamp__gte=since
        ).exists()
        
        return recent_events
    
    def create_geofence(self, name: str, geometry: Point, owner) -> GeoFence:
        """
        Create a new geofence.
        
        Args:
            name: Geofence name
            geometry: Polygon geometry
            owner: Owner user
            
        Returns:
            Created geofence
        """
        return GeoFence.objects.create(
            name=name,
            geometry=geometry,
            owner=owner,
            is_active=True
        )
    
    def check_device_in_geofence(self, device: GPSDevice, geofence: GeoFence) -> bool:
        """
        Check if device is inside geofence.
        
        Args:
            device: GPS device
            geofence: Geofence to check
            
        Returns:
            True if device is inside geofence
        """
        if not device.position:
            return False
        
        return geofence.geometry.contains(device.position)
    
    def get_device_geofences(self, device: GPSDevice) -> List[GeoFence]:
        """
        Get all geofences that contain a device.
        
        Args:
            device: GPS device
            
        Returns:
            List of geofences containing the device
        """
        if not device.position:
            return []
        
        return GeoFence.objects.filter(
            geometry__contains=device.position,
            is_active=True
        )
    
    def get_recent_events(self, user_id: int, hours: int = 24) -> List[GeoFenceEvent]:
        """
        Get recent geofence events for a user.
        
        Args:
            user_id: User ID
            hours: Number of hours to look back
            
        Returns:
            List of recent events
        """
        since = timezone.now() - timedelta(hours=hours)
        
        return GeoFenceEvent.objects.filter(
            fence__owner_id=user_id,
            timestamp__gte=since
        ).select_related('fence', 'device').order_by('-timestamp')


# Global instance
geofence_detection_service = GeofenceDetectionService() 