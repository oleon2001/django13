"""
Base models for the GPS application.
"""
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import json

class BaseDevice(models.Model):
    """Base model for GPS devices."""
    imei = models.BigIntegerField(_('imei'), primary_key=True)
    name = models.CharField(_('name'), max_length=50)
    position = models.PointField(_('position'), null=True, blank=True)
    speed = models.FloatField(_('speed'), default=0)
    course = models.FloatField(_('course'), default=0)
    altitude = models.FloatField(_('altitude'), default=0)
    last_log = models.DateTimeField(_('last update'), null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    icon = models.CharField(_('icon'), max_length=64, default='default.png')
    odometer = models.FloatField(_('odometer'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-last_log']

    def __str__(self):
        return f"{self.name} ({self.imei})"

class BaseLocation(models.Model):
    """Base model for location data."""
    position = models.PointField()
    speed = models.FloatField()
    course = models.FloatField()
    altitude = models.FloatField()
    satellites = models.IntegerField()
    accuracy = models.FloatField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-timestamp']

    def __str__(self):
        return f"Location at {self.timestamp}"

class BaseEvent(models.Model):
    """Base model for GPS events."""
    type = models.CharField(max_length=50)
    position = models.PointField(null=True, blank=True)
    speed = models.FloatField(default=0)
    course = models.FloatField(default=0)
    altitude = models.FloatField(default=0)
    timestamp = models.DateTimeField()
    odometer = models.FloatField(default=0)
    raw_data = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.type} at {self.timestamp}"

    def get_raw_data(self):
        """Get raw data as JSON."""
        if self.raw_data:
            try:
                return json.loads(self.raw_data)
            except json.JSONDecodeError:
                return None
        return None

    def set_raw_data(self, data):
        """Set raw data from JSON."""
        if data is not None:
            self.raw_data = json.dumps(data)
        else:
            self.raw_data = None

class BaseGeoFence(models.Model):
    """Base model for geofences."""
    name = models.CharField(_('name'), max_length=50, unique=True)
    geometry = models.PolygonField(_('polygon'))
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name 