"""
Protocol models for GPS communication (migrated from old backend).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .device import GPSDevice


class GPRSSession(models.Model):
    """Model for GPRS sessions (migrated from old Session model)."""
    start = models.DateTimeField(auto_now_add=True, db_index=True)
    end = models.DateTimeField(auto_now=True)
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='gprs_sessions')
    bytes_transferred = models.PositiveIntegerField(default=0)
    packets_count = models.PositiveIntegerField(default=0)
    records_count = models.PositiveIntegerField(default=0)
    events_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('GPRS session')
        verbose_name_plural = _('GPRS sessions')
        ordering = ['-start']

    def __str__(self):
        return f"From: {self.ip}:{self.port} {self.packets_count} packets, {self.records_count} records, {self.bytes_transferred} bytes, {self.events_count} events"

    def close_session(self):
        """Close the GPRS session."""
        self.is_active = False
        self.end = timezone.now()
        self.save()

    @property
    def duration(self):
        """Get session duration."""
        if self.is_active:
            return timezone.now() - self.start
        return self.end - self.start


class GPRSPacket(models.Model):
    """Model for GPRS packets (migrated from old Packet model)."""
    session = models.ForeignKey(GPRSSession, on_delete=models.CASCADE, related_name='packets')
    request = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('GPRS packet')
        verbose_name_plural = _('GPRS packets')
        ordering = ['-timestamp']

    def __str__(self):
        return f"Packet({len(self.request)//2}):{self.request}"

    @property
    def request_size(self):
        """Get request size in bytes."""
        return len(self.request) // 2

    @property
    def response_size(self):
        """Get response size in bytes."""
        return len(self.response) // 2


class GPRSRecord(models.Model):
    """Model for GPRS records (migrated from old Record model)."""
    packet = models.ForeignKey(GPRSPacket, on_delete=models.CASCADE, related_name='records')
    id_byte = models.SmallIntegerField()
    data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('GPRS record')
        verbose_name_plural = _('GPRS records')
        ordering = ['-timestamp']

    def __str__(self):
        return f"Record {self.id_byte:02x} ({len(self.data)}): {self.data}"

    @property
    def data_size(self):
        """Get data size."""
        return len(self.data)


class UDPSession(models.Model):
    """Model for UDP sessions (migrated from old UdpSession model)."""
    session = models.AutoField(_('session'), primary_key=True)
    device = models.OneToOneField(GPSDevice, on_delete=models.CASCADE, related_name='udp_session')
    expires = models.DateTimeField(_('expires'))
    host = models.CharField(_('host'), max_length=128)
    port = models.IntegerField(_('port'))
    last_record = models.IntegerField(_('last record'), default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('UDP session')
        verbose_name_plural = _('UDP sessions')
        ordering = ['device']

    def __str__(self):
        return f'Session {self.device.imei:015}-{self.session:010}'

    @property
    def is_expired(self):
        """Check if session is expired."""
        return timezone.now() > self.expires

    def extend_session(self, minutes=30):
        """Extend session expiry."""
        self.expires = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save()

    def close_session(self):
        """Close the UDP session."""
        self.is_active = False
        self.save()


class ProtocolLog(models.Model):
    """Model for protocol logging and debugging."""
    PROTOCOL_CHOICES = (
        ('GPRS', 'GPRS'),
        ('UDP', 'UDP'),
        ('TCP', 'TCP'),
        ('HTTP', 'HTTP'),
        ('OTHER', 'Other'),
    )

    LOG_LEVEL_CHOICES = (
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )

    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='protocol_logs')
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES)
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, default='INFO')
    message = models.TextField()
    data = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('protocol log')
        verbose_name_plural = _('protocol logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'protocol']),
            models.Index(fields=['level']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.protocol} {self.level}: {self.message[:50]}" 