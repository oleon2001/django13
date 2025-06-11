"""
Base models for the SkyGuard system.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils import timezone


class BaseDevice(models.Model):
    """Base model for all tracking devices."""
    imei = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    last_log = models.DateTimeField(default=timezone.now)
    position = gis_models.PointField(null=True, blank=True)
    speed = models.FloatField(default=0)
    course = models.FloatField(default=0)
    altitude = models.FloatField(default=0)
    odometer = models.FloatField(default=0)
    battery_level = models.FloatField(null=True, blank=True)
    signal_strength = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-last_log']

    def __str__(self):
        return f"{self.name} ({self.imei})"


class BaseLocation(models.Model):
    """Base model for location data."""
    position = gis_models.PointField()
    speed = models.FloatField()
    course = models.FloatField()
    altitude = models.FloatField()
    satellites = models.IntegerField()
    accuracy = models.FloatField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-timestamp']

    def __str__(self):
        return f"Location at {self.timestamp}"


class BaseEvent(models.Model):
    """Base model for device events."""
    EVENT_TYPES = (
        ('TRACK', 'Track'),
        ('IO', 'Input/Output'),
        ('ALERT', 'Alert'),
        ('STATUS', 'Status'),
    )

    type = models.CharField(max_length=10, choices=EVENT_TYPES)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.type} at {self.timestamp}" 