"""
Base models for the tracking application.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils import timezone
from skyguard.apps.gps.models import Device


class Alert(models.Model):
    """Model for device alerts."""
    ALERT_TYPES = [
        ('SOS', 'SOS Alert'),
        ('LOW_BATTERY', 'Low Battery'),
        ('GEOFENCE', 'Geofence Alert'),
        ('SPEED', 'Speed Alert'),
        ('TAMPER', 'Tamper Alert'),
        ('POWER', 'Power Alert'),
        ('OTHER', 'Other Alert'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    position = gis_models.PointField(null=True, blank=True)
    message = models.TextField()
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device.name} - {self.alert_type} at {self.created_at}"


class Geofence(models.Model):
    """Model for geofencing areas."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    area = gis_models.PolygonField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Geofence'
        verbose_name_plural = 'Geofences'

    def __str__(self):
        return self.name


class Route(models.Model):
    """Model for tracking routes."""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='routes')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    distance = models.FloatField(default=0)  # in kilometers
    average_speed = models.FloatField(default=0)  # in km/h
    max_speed = models.FloatField(default=0)  # in km/h
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.device.name} - {self.start_time}"


class RoutePoint(models.Model):
    """Model for storing points in a route."""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='points')
    position = gis_models.PointField()
    speed = models.FloatField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Route Point'
        verbose_name_plural = 'Route Points'
        ordering = ['timestamp']

    def __str__(self):
        return f"Point at {self.timestamp}" 