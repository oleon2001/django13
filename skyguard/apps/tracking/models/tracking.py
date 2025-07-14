"""
Tracking models for the tracking application.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils import timezone
from django.contrib.auth.models import User
from skyguard.apps.gps.models import GPSDevice


class TrackingSession(models.Model):
    """Model for tracking sessions."""
    SESSION_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    session_id = models.CharField(max_length=40, unique=True)
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='tracking_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracking_sessions')
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='ACTIVE')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    total_distance = models.FloatField(default=0)  # in kilometers
    average_speed = models.FloatField(default=0)  # in km/h
    max_speed = models.FloatField(default=0)  # in km/h
    duration = models.DurationField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tracking Session'
        verbose_name_plural = 'Tracking Sessions'
        ordering = ['-start_time']

    def __str__(self):
        return f"Session {self.session_id} - {self.device.name}"

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == 'ACTIVE'

    @property
    def is_completed(self):
        return self.status == 'COMPLETED'


class TrackingPoint(models.Model):
    """Model for storing tracking points."""
    session = models.ForeignKey(TrackingSession, on_delete=models.CASCADE, related_name='points')
    position = gis_models.PointField()
    speed = models.FloatField(default=0)
    course = models.FloatField(default=0)
    altitude = models.FloatField(default=0)
    timestamp = models.DateTimeField()
    accuracy = models.FloatField(default=0)
    satellites = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tracking Point'
        verbose_name_plural = 'Tracking Points'
        ordering = ['timestamp']

    def __str__(self):
        return f"Point at {self.timestamp}"


class TrackingEvent(models.Model):
    """Model for tracking events."""
    EVENT_TYPES = [
        ('START', 'Session Start'),
        ('STOP', 'Session Stop'),
        ('PAUSE', 'Session Pause'),
        ('RESUME', 'Session Resume'),
        ('GEOFENCE_ENTER', 'Geofence Enter'),
        ('GEOFENCE_EXIT', 'Geofence Exit'),
        ('SPEED_ALERT', 'Speed Alert'),
        ('BATTERY_LOW', 'Battery Low'),
        ('SIGNAL_LOST', 'Signal Lost'),
        ('SIGNAL_RESTORED', 'Signal Restored'),
        ('OTHER', 'Other Event'),
    ]

    session = models.ForeignKey(TrackingSession, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    position = gis_models.PointField(null=True, blank=True)
    timestamp = models.DateTimeField()
    data = models.JSONField(default=dict, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tracking Event'
        verbose_name_plural = 'Tracking Events'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"


class TrackingConfig(models.Model):
    """Model for tracking configuration."""
    device = models.OneToOneField(GPSDevice, on_delete=models.CASCADE, related_name='tracking_config')
    auto_start = models.BooleanField(default=False)
    auto_stop = models.BooleanField(default=False)
    geofence_alerts = models.BooleanField(default=True)
    speed_alerts = models.BooleanField(default=True)
    battery_alerts = models.BooleanField(default=True)
    signal_alerts = models.BooleanField(default=True)
    min_speed_threshold = models.FloatField(default=5.0)  # km/h
    max_speed_threshold = models.FloatField(default=120.0)  # km/h
    battery_threshold = models.FloatField(default=20.0)  # percentage
    update_interval = models.IntegerField(default=30)  # seconds
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tracking Configuration'
        verbose_name_plural = 'Tracking Configurations'

    def __str__(self):
        return f"Config for {self.device.name}"


class TrackingReport(models.Model):
    """Model for tracking reports."""
    REPORT_TYPES = [
        ('DAILY', 'Daily Report'),
        ('WEEKLY', 'Weekly Report'),
        ('MONTHLY', 'Monthly Report'),
        ('CUSTOM', 'Custom Report'),
    ]

    session = models.ForeignKey(TrackingSession, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    data = models.JSONField(default=dict)
    file_path = models.CharField(max_length=500, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_tracking_reports')
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tracking Report'
        verbose_name_plural = 'Tracking Reports'
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.title} - {self.session.session_id}" 