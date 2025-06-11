"""
Signal handlers for the GPS application.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import GPSDevice, GPSLocation, GPSEvent


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