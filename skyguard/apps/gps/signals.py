"""
Django signals for GPS tracking system.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import GPSDevice, GPSLocation, GPSEvent, GeoFence, GeoFenceEvent
from .tasks import process_geofence_detection

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


def get_safe_channel_layer():
    """Get channel layer safely."""
    try:
        return get_channel_layer()
    except Exception as e:
        logger.warning(f"Could not get channel layer: {e}")
        return None


@receiver(post_save, sender=GPSDevice)
def device_position_updated(sender, instance, created, **kwargs):
    """
    Signal fired when a GPS device position is updated.
    Triggers geofence detection if the device has a position.
    """
    # Skip if this is a new device creation
    if created:
        logger.info(f"New GPS device created: {instance.name} ({instance.imei})")
        return
    
    # Only process if device has a position
    if not instance.position:
        return
    
    # Skip if device is not online
    if instance.connection_status != 'ONLINE':
        return
    
    try:
        # Trigger geofence detection asynchronously
        process_geofence_detection.delay(instance.imei)
        logger.debug(f"Queued geofence detection for device {instance.name} ({instance.imei})")
        
    except Exception as e:
        logger.error(f"Error queuing geofence detection for device {instance.imei}: {e}")


@receiver(post_save, sender=GPSLocation)
def location_created(sender, instance, created, **kwargs):
    """
    Signal fired when a new GPS location is created.
    This can also trigger geofence detection.
    """
    if not created:
        return
    
    # Get the device from the location
    if hasattr(instance, 'device'):
        device = instance.device
        
        # Update device position if this is the latest location
        if device.position != instance.position:
            device.position = instance.position
            device.last_log = instance.timestamp
            device.save(update_fields=['position', 'last_log'])
        
        # Trigger geofence detection
        try:
            process_geofence_detection.delay(device.imei)
            logger.debug(f"Triggered geofence detection from location update for device {device.name}")
        except Exception as e:
            logger.error(f"Error triggering geofence detection from location: {e}")


@receiver(post_save, sender=GeoFenceEvent)
def geofence_event_created(sender, instance, created, **kwargs):
    """
    Signal fired when a geofence event is created.
    Broadcasts the event via WebSocket.
    """
    if not created:
        return
    
    try:
        # Prepare event data for WebSocket broadcast
        event_data = {
            'type': 'geofence_event',
            'data': {
                'id': instance.id,
                'device_id': instance.device.imei,
                'device_name': instance.device.name,
                'geofence_id': instance.fence.id,
                'geofence_name': instance.fence.name,
                'event_type': instance.event_type,
                'position': [instance.position.y, instance.position.x] if instance.position else None,
                'timestamp': instance.timestamp.isoformat(),
                'created_at': instance.created_at.isoformat()
            }
        }
        
        # Broadcast to geofence owner
        channel_layer = get_safe_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"geofences_user_{instance.fence.owner.id}",
                event_data
            )
            
            # Also broadcast to general GPS tracking room for this user
            async_to_sync(channel_layer.group_send)(
                f"gps_user_{instance.fence.owner.id}",
                event_data
            )
        
        logger.info(
            f"Broadcasted geofence event: {instance.device.name} "
            f"{instance.event_type} {instance.fence.name}"
        )
        
    except Exception as e:
        logger.error(f"Error broadcasting geofence event: {e}")


@receiver(post_save, sender=GeoFence)
def geofence_updated(sender, instance, created, **kwargs):
    """
    Signal fired when a geofence is created or updated.
    """
    if created:
        logger.info(f"New geofence created: {instance.name} by {instance.owner.username}")
        
        # Broadcast new geofence to owner
        geofence_data = {
            'type': 'geofence_created',
            'data': {
                'id': instance.id,
                'name': instance.name,
                'description': instance.description,
                'is_active': instance.is_active,
                'created_at': instance.created_at.isoformat()
            }
        }
    else:
        logger.info(f"Geofence updated: {instance.name}")
        
        # Broadcast geofence update
        geofence_data = {
            'type': 'geofence_updated',
            'data': {
                'id': instance.id,
                'name': instance.name,
                'description': instance.description,
                'is_active': instance.is_active,
                'updated_at': instance.updated_at.isoformat()
            }
        }
    
    # Broadcast via WebSocket
    try:
        channel_layer = get_safe_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"geofences_user_{instance.owner.id}",
                geofence_data
            )
    except Exception as e:
        logger.error(f"Error broadcasting geofence update: {e}")


@receiver(pre_save, sender=GPSDevice)
def device_status_change(sender, instance, **kwargs):
    """
    Signal fired before a GPS device is saved.
    Detects status changes and logs them.
    """
    if instance.pk:  # Only for existing devices
        try:
            old_instance = GPSDevice.objects.get(pk=instance.pk)
            
            # Check for connection status change
            if old_instance.connection_status != instance.connection_status:
                logger.info(
                    f"Device {instance.name} ({instance.imei}) status changed: "
                    f"{old_instance.connection_status} -> {instance.connection_status}"
                )
                
                # Broadcast status change via WebSocket
                status_data = {
                    'type': 'device_status_change',
                    'data': {
                        'device_id': instance.imei,
                        'device_name': instance.name,
                        'old_status': old_instance.connection_status,
                        'new_status': instance.connection_status,
                        'timestamp': timezone.now().isoformat()
                    }
                }
                
                channel_layer = get_safe_channel_layer()
                if channel_layer and instance.owner:
                    async_to_sync(channel_layer.group_send)(
                        f"gps_user_{instance.owner.id}",
                        status_data
                    )
                    
        except GPSDevice.DoesNotExist:
            pass  # Device is being created
        except Exception as e:
            logger.error(f"Error in device status change signal: {e}")


@receiver(post_save, sender=GPSEvent)
def gps_event_created(sender, instance, created, **kwargs):
    """
    Signal fired when a GPS event is created.
    """
    if not created:
        return
    
    try:
        # Broadcast GPS event via WebSocket
        event_data = {
            'type': 'gps_event',
            'data': {
                'id': instance.id,
                'device_id': instance.device.imei if hasattr(instance, 'device') else None,
                'event_type': instance.type,
                'position': [instance.position.y, instance.position.x] if instance.position else None,
                'timestamp': instance.timestamp.isoformat(),
                'speed': instance.speed,
                'course': instance.course,
                'raw_data': instance.get_raw_data()
            }
        }
        
        # Broadcast to device owner
        channel_layer = get_safe_channel_layer()
        if channel_layer and hasattr(instance, 'device') and instance.device.owner:
            async_to_sync(channel_layer.group_send)(
                f"gps_user_{instance.device.owner.id}",
                event_data
            )
        
        logger.debug(f"Broadcasted GPS event: {instance.type}")
        
    except Exception as e:
        logger.error(f"Error broadcasting GPS event: {e}")


# Additional signal for manual geofence testing
@receiver(post_save, sender=GPSDevice)
def trigger_manual_geofence_check(sender, instance, **kwargs):
    """
    Manual trigger for geofence checking.
    This can be called from admin interface or API.
    """
    # This is called via a custom admin action or API endpoint
    # We'll implement this as a separate function that can be called manually
    pass


def manual_geofence_check(device_imei):
    """
    Manually trigger geofence check for a specific device.
    
    Args:
        device_imei: IMEI of the device to check
    """
    try:
        process_geofence_detection.delay(device_imei)
        logger.info(f"Manually triggered geofence check for device {device_imei}")
    except Exception as e:
        logger.error(f"Error manually triggering geofence check: {e}") 