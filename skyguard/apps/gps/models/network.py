"""
Network models for the GPS application.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from .device import GPSDevice

class NetworkEvent(models.Model):
    """Model for network events."""
    EVENT_TYPES = (
        ('CONNECT', 'Connection'),
        ('DISCONNECT', 'Disconnection'),
        ('TIMEOUT', 'Timeout'),
        ('ERROR', 'Error'),
        ('RECONNECT', 'Reconnection'),
        ('AUTH_FAIL', 'Authentication Failed'),
        ('PROTOCOL_ERROR', 'Protocol Error'),
    )

    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='network_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField()
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField()
    protocol = models.CharField(max_length=20)
    session_id = models.CharField(max_length=50, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    raw_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('network event')
        verbose_name_plural = _('network events')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.device.imei} - {self.event_type} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # Actualizar estadísticas del dispositivo
        if self.event_type == 'CONNECT':
            self.device.total_connections += 1
            self.device.last_connection = self.timestamp
            if not self.device.first_connection:
                self.device.first_connection = self.timestamp
            self.device.save()
        super().save(*args, **kwargs)

class NetworkSession(models.Model):
    """Model for network sessions."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField()
    protocol = models.CharField(max_length=20)
    bytes_sent = models.BigIntegerField(default=0)
    bytes_received = models.BigIntegerField(default=0)
    packets_sent = models.IntegerField(default=0)
    packets_received = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('network session')
        verbose_name_plural = _('network sessions')
        ordering = ['-start_time']

    def __str__(self):
        return f"Session {self.device} from {self.start_time}"

class NetworkMessage(models.Model):
    """Model for network messages."""
    MESSAGE_TYPES = (
        ('COMMAND', 'Command'),
        ('RESPONSE', 'Response'),
        ('ALERT', 'Alert'),
        ('DATA', 'Data'),
    )

    session = models.ForeignKey(NetworkSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    timestamp = models.DateTimeField()
    direction = models.CharField(max_length=10, choices=(('IN', 'Incoming'), ('OUT', 'Outgoing')))
    raw_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('network message')
        verbose_name_plural = _('network messages')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.message_type} at {self.timestamp}"

class CellTower(models.Model):
    """Model for storing cell tower information."""
    mcc = models.IntegerField()  # Mobile Country Code
    mnc = models.IntegerField()  # Mobile Network Code
    lac = models.IntegerField()  # Location Area Code
    cell_id = models.BigIntegerField()  # Cell ID
    signal_strength = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cell Tower'
        verbose_name_plural = 'Cell Towers'
        unique_together = ['mcc', 'mnc', 'lac', 'cell_id']

    def __str__(self):
        return f"{self.mcc}-{self.mnc} {self.lac}-{self.cell_id}"


class WiFiAccessPoint(models.Model):
    """Model for storing WiFi access point information."""
    mac_address = models.CharField(max_length=17)
    signal_strength = models.IntegerField()
    ssid = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'WiFi Access Point'
        verbose_name_plural = 'WiFi Access Points'
        unique_together = ['mac_address']

    def __str__(self):
        return f"{self.mac_address} ({self.ssid or 'Unknown'})" 