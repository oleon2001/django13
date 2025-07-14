"""
Signal handlers for the tracking application.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
import logging

from .models import DeviceSession, TrackingSession, Alert, Geofence

logger = logging.getLogger(__name__)

# Get channel layer safely
def get_safe_channel_layer():
    """Get channel layer safely, handling None case."""
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.warning("Channel layer is None - WebSocket notifications disabled")
            return None
        return channel_layer
    except Exception as e:
        logger.warning(f"Error getting channel layer: {e} - WebSocket notifications disabled")
        return None


@receiver(post_save, sender=TrackingSession)
def broadcast_tracking_session_update(sender, instance, created, **kwargs):
    """Broadcast tracking session updates via WebSocket."""
    if instance.user:
        # Prepare update data
        update_data = {
            'type': 'session_status_change',
            'session_id': instance.id,
            'status': instance.status,
            'timestamp': datetime.now().isoformat(),
            'duration': instance.duration,
            'distance': instance.distance
        }
        
        # Broadcast to user's room
        channel_layer = get_safe_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"tracking_user_{instance.user.id}",
                    update_data
                )
            except Exception as e:
                logger.error(f"Error broadcasting tracking session update: {e}")


@receiver(post_save, sender=DeviceSession)
def broadcast_device_session_update(sender, instance, created, **kwargs):
    """Broadcast device session updates via WebSocket."""
    if instance.session and instance.session.user:
        # Prepare tracking update data
        update_data = {
            'type': 'tracking_update',
            'session_id': instance.session.id,
            'device_imei': instance.device.imei if instance.device else None,
            'position': {
                'latitude': instance.position.y if instance.position else None,
                'longitude': instance.position.x if instance.position else None
            },
            'speed': instance.speed,
            'course': instance.course,
            'timestamp': instance.timestamp.isoformat(),
            'status': instance.status,
            'distance': instance.distance,
            'duration': instance.duration
        }
        
        # Broadcast to user's room
        channel_layer = get_safe_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"tracking_user_{instance.session.user.id}",
                    update_data
                )
            except Exception as e:
                logger.error(f"Error broadcasting device session update: {e}")


@receiver(post_save, sender=Alert)
def broadcast_alert_notification(sender, instance, created, **kwargs):
    """Broadcast alert notifications via WebSocket."""
    if instance.user:
        # Prepare alert data
        alert_data = {
            'type': 'alert_created' if created else 'alert_updated',
            'alert': {
                'id': instance.id,
                'alert_type': instance.alert_type,
                'message': instance.message,
                'severity': instance.severity,
                'acknowledged': instance.acknowledged,
                'created_at': instance.created_at.isoformat(),
                'acknowledged_at': instance.acknowledged_at.isoformat() if instance.acknowledged_at else None,
                'device_imei': instance.device.imei if instance.device else None,
                'position': {
                    'latitude': instance.position.y if instance.position else None,
                    'longitude': instance.position.x if instance.position else None
                } if instance.position else None
            }
        }
        
        # Broadcast to user's room
        channel_layer = get_safe_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"alerts_user_{instance.user.id}",
                    alert_data
                )
            except Exception as e:
                logger.error(f"Error broadcasting alert notification: {e}")


@receiver(post_save, sender=Geofence)
def broadcast_geofence_update(sender, instance, created, **kwargs):
    """Broadcast geofence updates via WebSocket."""
    if instance.user:
        # Prepare geofence data
        geofence_data = {
            'type': 'geofence_updated',
            'geofence': {
                'id': instance.id,
                'name': instance.name,
                'description': instance.description,
                'geofence_type': instance.geofence_type,
                'coordinates': instance.coordinates.coords if instance.coordinates else None,
                'radius': instance.radius,
                'active': instance.active,
                'created_at': instance.created_at.isoformat()
            }
        }
        
        # Broadcast to user's room
        channel_layer = get_safe_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"geofences_user_{instance.user.id}",
                    geofence_data
                )
            except Exception as e:
                logger.error(f"Error broadcasting geofence update: {e}")


def broadcast_geofence_event(geofence, device, event_type, position=None):
    """Broadcast geofence event via WebSocket."""
    if geofence.user:
        # Prepare geofence event data
        event_data = {
            'type': 'geofence_event',
            'geofence_id': geofence.id,
            'device_imei': device.imei if device else None,
            'event_type': event_type,  # 'enter' or 'exit'
            'geofence_name': geofence.name,
            'position': {
                'latitude': position.y if position else None,
                'longitude': position.x if position else None
            } if position else None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Broadcast to user's room
        channel_layer = get_safe_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"geofences_user_{geofence.user.id}",
                    event_data
                )
            except Exception as e:
                logger.error(f"Error broadcasting geofence event: {e}")


def broadcast_tracking_update(session, device_session):
    """Broadcast tracking update via WebSocket."""
    if session.user:
        # Prepare tracking update data
        update_data = {
            'type': 'tracking_update',
            'session_id': session.id,
            'device_imei': device_session.device.imei if device_session.device else None,
            'position': {
                'latitude': device_session.position.y if device_session.position else None,
                'longitude': device_session.position.x if device_session.position else None
            },
            'speed': device_session.speed,
            'course': device_session.course,
            'timestamp': device_session.timestamp.isoformat(),
            'status': device_session.status,
            'distance': device_session.distance,
            'duration': device_session.duration
        }
        
        # Broadcast to user's room
        channel_layer = get_safe_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"tracking_user_{session.user.id}",
                    update_data
                )
            except Exception as e:
                logger.error(f"Error broadcasting tracking update: {e}")


def broadcast_alert_created(alert):
    """Broadcast new alert via WebSocket."""
    if alert.user:
        # Prepare alert data
        alert_data = {
            'type': 'new_alert',
            'alert': {
                'id': alert.id,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'severity': alert.severity,
                'acknowledged': alert.acknowledged,
                'created_at': alert.created_at.isoformat(),
                'device_imei': alert.device.imei if alert.device else None,
                'position': {
                    'latitude': alert.position.y if alert.position else None,
                    'longitude': alert.position.x if alert.position else None
                } if alert.position else None
            }
        }
        
        # Broadcast to user's room
        channel_layer = get_safe_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"alerts_user_{alert.user.id}",
                    alert_data
                )
            except Exception as e:
                logger.error(f"Error broadcasting alert created: {e}") 