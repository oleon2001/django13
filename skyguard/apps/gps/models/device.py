"""
Device models for the GPS application.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils import timezone

from skyguard.core.models import BaseDevice, BaseLocation, BaseEvent


class GPSDevice(BaseDevice):
    """Model for GPS tracking devices."""
    protocol = models.CharField(max_length=20)
    firmware_version = models.CharField(max_length=50, null=True, blank=True)
    last_maintenance = models.DateTimeField(null=True, blank=True)
    maintenance_interval = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name = 'GPS Device'
        verbose_name_plural = 'GPS Devices'


class GPSLocation(BaseLocation):
    """Model for GPS location data."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='locations')
    hdop = models.FloatField(null=True, blank=True)  # Horizontal Dilution of Precision
    pdop = models.FloatField(null=True, blank=True)  # Position Dilution of Precision
    fix_quality = models.IntegerField(null=True, blank=True)
    fix_type = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = 'GPS Location'
        verbose_name_plural = 'GPS Locations'


class GPSEvent(BaseEvent):
    """Model for GPS device events."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='events')
    position = gis_models.PointField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    course = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    odometer = models.FloatField(null=True, blank=True)
    raw_data = models.BinaryField(null=True, blank=True)

    class Meta:
        verbose_name = 'GPS Event'
        verbose_name_plural = 'GPS Events' 