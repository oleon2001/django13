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

from skyguard.apps.gps.models import GPSDevice, GeoFence, GeoFenceEvent
from skyguard.apps.gps.notifications import GeofenceNotificationService
from skyguard.apps.gps.services.geofence_manager import advanced_geofence_manager

logger = logging.getLogger(__name__)

# Safely import and initialize channel layer
def get_safe_channel_layer():
    """Get channel layer safely without causing connection errors."""
    try:
        from channels.layers import get_channel_layer
        return get_channel_layer()
    except Exception as e:
        logger.debug(f"Channel layer not available: {e}")
        return None

channel_layer = get_safe_channel_layer()


class GeofenceDetectionService:
    """Service for automatic geofence detection and event generation."""
    
    def __init__(self):
        """Initialize the geofence detection service."""
        self.notification_service = GeofenceNotificationService()
        self.logger = logger
        self.advanced_manager = advanced_geofence_manager
    
    def check_device_geofences(self, device: GPSDevice) -> List[Dict[str, Any]]:
        """
        Check all geofences for a device and detect entry/exit events.
        Now uses the advanced manager for better performance and features.
        
        Args:
            device: GPS device to check
            
        Returns:
            List of events generated
        """
        return self.advanced_manager.check_device_geofences(device)
    
    def _check_single_geofence(self, device: GPSDevice, geofence: GeoFence) -> Optional[Dict[str, Any]]:
        """
        Check a single geofence for entry/exit events.
        Deprecated: Use advanced_manager for new implementations.
        
        Args:
            device: GPS device
            geofence: Geofence to check
            
        Returns:
            Event data if an event was generated, None otherwise
        """
        logger.warning("Using deprecated _check_single_geofence method. Use advanced_manager instead.")
        return self.advanced_manager._check_single_geofence_enhanced(device, geofence)
    
    @transaction.atomic
    def _generate_geofence_event(self, device: GPSDevice, geofence: GeoFence, event_type: str) -> Dict[str, Any]:
        """
        Generate a geofence event and trigger notifications.
        Deprecated: Use advanced_manager for new implementations.
        
        Args:
            device: GPS device
            geofence: Geofence
            event_type: 'ENTRY' or 'EXIT'
            
        Returns:
            Event data
        """
        logger.warning("Using deprecated _generate_geofence_event method. Use advanced_manager instead.")
        return self.advanced_manager._generate_enhanced_geofence_event(device, geofence, event_type)
    
    def _broadcast_event(self, event_data: Dict[str, Any], user_id: int):
        """
        Broadcast event via WebSocket to the geofence owner.
        
        Args:
            event_data: Event data to broadcast
            user_id: User ID to send to
        """
        # Use advanced manager's method
        self.advanced_manager._broadcast_geofence_event(event_data, user_id)
    
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
            self.logger.warning(f"Error sending geofence notification: {e}")
    
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
        return self.advanced_manager._is_in_cooldown(geofence, device, event_type)
    
    def create_geofence(self, name: str, geometry: Point, owner) -> GeoFence:
        """
        Create a new geofence.
        Deprecated: Use advanced_manager.create_geofence instead.
        
        Args:
            name: Geofence name
            geometry: Polygon geometry
            owner: Owner user
            
        Returns:
            Created geofence
        """
        logger.warning("Using deprecated create_geofence method. Use advanced_manager.create_geofence instead.")
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
    
    # New methods for integration with advanced manager
    def analyze_device_behavior(self, device: GPSDevice, days_back: int = 7) -> Dict[str, Any]:
        """Analyze device behavior patterns within geofences."""
        return self.advanced_manager.analyzer.analyze_device_behavior(device, days_back)
    
    def generate_metrics(self, user, time_window_hours: int = 24):
        """Generate geofence metrics for a user."""
        return self.advanced_manager.generate_geofence_metrics(user, time_window_hours)
    
    def get_user_geofences(self, user, include_inactive: bool = False):
        """Get geofences for a user with permission checking."""
        return self.advanced_manager.get_user_geofences(user, include_inactive)


# Global instance - maintaining backward compatibility
geofence_detection_service = GeofenceDetectionService() 