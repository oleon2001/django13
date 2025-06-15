"""
Device session models.
"""
from django.db import models
from django.utils import timezone

from .device import GPSDevice


class DeviceSession(models.Model):
    """
    Model for tracking device connection sessions.
    """
    device = models.ForeignKey(
        GPSDevice,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    protocol = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    bytes_sent = models.PositiveBigIntegerField(default=0)
    bytes_received = models.PositiveBigIntegerField(default=0)
    packets_sent = models.PositiveIntegerField(default=0)
    packets_received = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['device', 'start_time']),
            models.Index(fields=['is_active']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f"{self.device.imei} - {self.start_time}"

    def close(self):
        """
        Close the session.
        """
        self.end_time = timezone.now()
        self.is_active = False
        self.save()

    def update_activity(self):
        """
        Update the last activity timestamp.
        """
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def update_stats(self, bytes_sent=0, bytes_received=0, packets_sent=0, packets_received=0):
        """
        Update session statistics.
        """
        self.bytes_sent += bytes_sent
        self.bytes_received += bytes_received
        self.packets_sent += packets_sent
        self.packets_received += packets_received
        self.save(update_fields=[
            'bytes_sent',
            'bytes_received',
            'packets_sent',
            'packets_received',
            'updated_at'
        ]) 