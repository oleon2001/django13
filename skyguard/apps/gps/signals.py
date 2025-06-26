"""
Signal handlers for the GPS application.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime

from .models import GPSDevice, GPSLocation, GPSEvent


channel_layer = get_channel_layer()


@receiver(post_save, sender=GPSLocation)
def update_device_position(sender, instance, created, **kwargs):
    """Update device position when a new location is saved."""
    if created:
        device = instance.device
        device.position = instance.position
        device.speed = instance.speed
        device.course = instance.course
        device.altitude = instance.altitude
        device.last_log = instance.timestamp
        device.save()


@receiver(post_save, sender=GPSEvent)
def handle_device_event(sender, instance, created, **kwargs):
    """Handle device events."""
    if created:
        device = instance.device
        
        # Update device state based on event type
        if instance.type == 'TRACK':
            device.position = instance.position
            device.speed = instance.speed
            device.course = instance.course
            device.altitude = instance.altitude
            device.last_log = instance.timestamp
            device.save()
        
        # TODO: Handle other event types 


@receiver(post_save, sender=GPSLocation)
def broadcast_gps_location_update(sender, instance, created, **kwargs):
    """Broadcast GPS location updates via WebSocket."""
    if created and instance.device:
        device = instance.device
        
        # Prepare update data
        update_data = {
            'type': 'gps_update',
            'device_imei': str(device.imei),
            'position': {
                'latitude': instance.position.y if instance.position else None,
                'longitude': instance.position.x if instance.position else None
            },
            'speed': instance.speed,
            'course': instance.course,
            'timestamp': instance.timestamp.isoformat(),
            'status': device.connection_status,
            'altitude': instance.altitude,
            'satellites': instance.satellites,
            'accuracy': instance.accuracy,
        }
        
        # Broadcast to user's room
        if device.owner:
            async_to_sync(channel_layer.group_send)(
                f"gps_user_{device.owner.id}",
                update_data
            )
        
        # Broadcast to analytics room
        async_to_sync(channel_layer.group_send)(
            "gps_analytics",
            {
                'type': 'analytics_update',
                'data': {
                    'event_type': 'location_update',
                    'device_imei': str(device.imei),
                    'timestamp': instance.timestamp.isoformat(),
                    'speed': instance.speed,
                    'position': update_data['position']
                }
            }
        )


@receiver(post_save, sender=GPSDevice)
def broadcast_device_status_change(sender, instance, created, **kwargs):
    """Broadcast device status changes via WebSocket."""
    if not created:  # Only for updates, not new devices
        # Detect status changes
        if hasattr(instance, '_state') and instance._state.adding is False:
            update_data = {
                'type': 'device_status_change',
                'device_imei': str(instance.imei),
                'status': instance.connection_status,
                'timestamp': datetime.now().isoformat(),
                'last_heartbeat': instance.last_heartbeat.isoformat() if instance.last_heartbeat else None,
                'connection_quality': instance.connection_quality,
                'error_count': instance.error_count
            }
            
            # Broadcast to user's room
            if instance.owner:
                async_to_sync(channel_layer.group_send)(
                    f"gps_user_{instance.owner.id}",
                    update_data
                )


@receiver(post_save, sender=GPSEvent)
def broadcast_gps_event(sender, instance, created, **kwargs):
    """Broadcast GPS events (especially alarms) via WebSocket."""
    if created and instance.device and instance.type in ['ALARM', 'PANIC', 'SOS']:
        device = instance.device
        
        # Determine alarm severity
        severity = 'high' if instance.type in ['PANIC', 'SOS'] else 'medium'
        
        alarm_data = {
            'type': 'alarm_notification',
            'device_imei': str(device.imei),
            'alarm_type': instance.type,
            'message': f"Alarm: {instance.type} from {device.name}",
            'position': {
                'latitude': instance.position.y if instance.position else None,
                'longitude': instance.position.x if instance.position else None
            } if instance.position else None,
            'timestamp': instance.timestamp.isoformat(),
            'severity': severity,
            'device_name': device.name
        }
        
        # Broadcast to user's room
        if device.owner:
            async_to_sync(channel_layer.group_send)(
                f"gps_user_{device.owner.id}",
                alarm_data
            )
        
        # Also broadcast to analytics for monitoring
        async_to_sync(channel_layer.group_send)(
            "gps_analytics",
            {
                'type': 'analytics_update',
                'data': {
                    'event_type': 'alarm',
                    'device_imei': str(device.imei),
                    'alarm_type': instance.type,
                    'severity': severity,
                    'timestamp': instance.timestamp.isoformat()
                }
            }
        ) 