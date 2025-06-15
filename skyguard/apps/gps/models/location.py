"""
Location models for GPS devices.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils import timezone

from .device import GPSDevice


class Location(models.Model):
    """
    Model for storing device locations.
    """
    device = models.ForeignKey(
        GPSDevice,
        on_delete=models.CASCADE,
        related_name='locations'
    )
    timestamp = models.DateTimeField(default=timezone.now)
    position = gis_models.PointField()
    speed = models.FloatField(default=0.0)
    course = models.FloatField(default=0.0)
    altitude = models.FloatField(default=0.0)
    satellites = models.PositiveSmallIntegerField(default=0)
    accuracy = models.FloatField(default=0.0)
    hdop = models.FloatField(default=0.0)
    pdop = models.FloatField(default=0.0)
    fix_quality = models.PositiveSmallIntegerField(default=0)
    fix_type = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.device.imei} - {self.timestamp}"

    @property
    def latitude(self):
        """Get latitude from position."""
        return self.position.y if self.position else None

    @property
    def longitude(self):
        """Get longitude from position."""
        return self.position.x if self.position else None 