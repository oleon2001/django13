"""
Models for the monitoring application.
"""
from django.db import models
from django.utils import timezone
from skyguard.apps.gps.models import Device


class DeviceStatus(models.Model):
    """Model for device status monitoring."""
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='status')
    is_online = models.BooleanField(default=False)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    battery_level = models.FloatField(null=True, blank=True)
    signal_strength = models.IntegerField(null=True, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    last_maintenance = models.DateTimeField(null=True, blank=True)
    next_maintenance = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Device Status'
        verbose_name_plural = 'Device Statuses'

    def __str__(self):
        return f"{self.device.name} Status"


class MaintenanceLog(models.Model):
    """Model for device maintenance logs."""
    MAINTENANCE_TYPES = [
        ('ROUTINE', 'Routine Check'),
        ('REPAIR', 'Repair'),
        ('UPGRADE', 'Firmware Upgrade'),
        ('BATTERY', 'Battery Replacement'),
        ('OTHER', 'Other'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    description = models.TextField()
    performed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_maintenance'
    )
    performed_at = models.DateTimeField(default=timezone.now)
    next_maintenance_due = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Maintenance Log'
        verbose_name_plural = 'Maintenance Logs'
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.device.name} - {self.maintenance_type} at {self.performed_at}"


class SystemLog(models.Model):
    """Model for system-wide logging."""
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    source = models.CharField(max_length=100)
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'System Log'
        verbose_name_plural = 'System Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.level} - {self.source} at {self.created_at}"


class Notification(models.Model):
    """Model for system notifications."""
    NOTIFICATION_TYPES = [
        ('ALERT', 'Alert'),
        ('MAINTENANCE', 'Maintenance'),
        ('SYSTEM', 'System'),
        ('USER', 'User'),
    ]

    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    recipient = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.created_at}"
