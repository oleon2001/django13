"""
Event models for GPS devices.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils import timezone

from .device import GPSDevice


class NetworkEvent(models.Model):
    """
    Model for storing network events from GPS devices.
    """
    EVENT_TYPES = [
        ('CONNECT', 'Device Connected'),
        ('DISCONNECT', 'Device Disconnected'),
        ('LOGIN', 'Device Login'),
        ('LOGOUT', 'Device Logout'),
        ('ALARM', 'Device Alarm'),
        ('TRACK', 'Location Track'),
        ('STATUS', 'Status Update'),
        ('CONFIG', 'Configuration Update'),
        ('OTHER', 'Other Event'),
    ]

    device = models.ForeignKey(
        GPSDevice,
        on_delete=models.CASCADE,
        related_name='events'
    )
    type = models.CharField(max_length=20, choices=EVENT_TYPES, default='OTHER')
    timestamp = models.DateTimeField(default=timezone.now)
    position = gis_models.PointField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    course = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    odometer = models.FloatField(null=True, blank=True)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['type']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.device.imei} - {self.type} - {self.timestamp}"

    @property
    def latitude(self):
        """Get latitude from position."""
        return self.position.y if self.position else None

    @property
    def longitude(self):
        """Get longitude from position."""
        return self.position.x if self.position else None 