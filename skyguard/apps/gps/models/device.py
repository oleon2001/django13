"""
Device models for the GPS application.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from .base import BaseDevice, BaseLocation, BaseEvent, BaseGeoFence


class GPSDevice(BaseDevice):
    """Model for GPS devices."""
    MODEL_CHOICES = (
        (0, 'Unknown'),
        (1, 'SGB4612'),
        (2, 'SGP4612'),
    )

    GSM_OPERATOR_CHOICES = (
        (0, 'Telcel'),
        (1, 'Movistar'),
        (2, 'IusaCell'),
    )

    serial = models.IntegerField(_('serial'), default=0)
    model = models.SmallIntegerField(_('model'), default=0, choices=MODEL_CHOICES)
    software_version = models.CharField(_('version'), max_length=4, default='----')
    inputs = models.IntegerField(_('inputs'), default=0)
    outputs = models.IntegerField(_('outputs'), default=0)
    alarm_mask = models.IntegerField(_('alarm mask'), default=0x0141)
    alarms = models.IntegerField(_('alarms'), default=0)
    firmware_file = models.CharField(_('firmware file'), max_length=16, blank=True)
    last_firmware_update = models.DateTimeField(_('last firmware update'), null=True, blank=True)
    comments = models.TextField(_('Comments'), null=True, blank=True)
    sim_card = models.OneToOneField('SimCard', on_delete=models.SET_NULL, null=True, blank=True, related_name='device')

    objects = models.Manager()

    class Meta:
        verbose_name = _('GPS device')
        verbose_name_plural = _('GPS devices')


class SimCard(models.Model):
    """Model for SIM cards."""
    iccid = models.BigIntegerField(primary_key=True)
    imsi = models.BigIntegerField(null=True)
    provider = models.SmallIntegerField(default=0, choices=GPSDevice.GSM_OPERATOR_CHOICES)
    phone = models.CharField(max_length=16)

    objects = models.Manager()

    def __str__(self):
        return f"{self.phone} ({self.iccid})"


class GPSLocation(BaseLocation):
    """Model for GPS location data."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='locations')
    hdop = models.FloatField(null=True, blank=True)  # Horizontal Dilution of Precision
    pdop = models.FloatField(null=True, blank=True)  # Position Dilution of Precision
    fix_quality = models.IntegerField(null=True, blank=True)
    fix_type = models.CharField(max_length=20, null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('GPS location')
        verbose_name_plural = _('GPS locations')


class GPSEvent(BaseEvent):
    """Model for GPS events."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='events')
    source = models.CharField(max_length=20, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    inputs = models.IntegerField(default=0)
    outputs = models.IntegerField(default=0)
    input_changes = models.IntegerField(default=0)
    output_changes = models.IntegerField(default=0)
    alarm_changes = models.IntegerField(default=0)
    changes_description = models.TextField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('GPS event')
        verbose_name_plural = _('GPS events')


class GeoFence(BaseGeoFence):
    """Model for geofences."""
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notify_on_entry = models.BooleanField(default=True)
    notify_on_exit = models.BooleanField(default=True)
    notify_owners = models.ManyToManyField(User, related_name='notified_fences', blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('geofence')
        verbose_name_plural = _('geofences')


class GeoFenceEvent(models.Model):
    """Model for geofence events."""
    EVENT_TYPES = (
        ('ENTRY', 'Entry'),
        ('EXIT', 'Exit'),
    )

    fence = models.ForeignKey(GeoFence, on_delete=models.CASCADE, related_name='events')
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='fence_events')
    event_type = models.CharField(max_length=5, choices=EVENT_TYPES)
    position = gis_models.PointField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('geofence event')
        verbose_name_plural = _('geofence events')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}" 