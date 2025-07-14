"""
Sensor models for GPS devices (migrated from old backend).
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .device import GPSDevice


class PressureSensorCalibration(models.Model):
    """Model for PSI sensor calibration (migrated from PsiCal)."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='pressure_calibrations')
    sensor = models.CharField(_('sensor serial'), max_length=32)
    offset_psi1 = models.DecimalField(_('PSI1 offset'), max_digits=10, decimal_places=6)
    offset_psi2 = models.DecimalField(_('PSI2 offset'), max_digits=10, decimal_places=6)
    multiplier_psi1 = models.DecimalField(_('PSI1 multiplier'), max_digits=10, decimal_places=6)
    multiplier_psi2 = models.DecimalField(_('PSI2 multiplier'), max_digits=10, decimal_places=6)
    name = models.CharField(_('name'), max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('pressure sensor calibration')
        verbose_name_plural = _('pressure sensor calibrations')
        unique_together = [('device', 'sensor')]

    def __str__(self):
        return f"{self.device.name} - {self.name} ({self.sensor})"


class PressureWeightLog(models.Model):
    """Model for PSI weight logs (migrated from PsiWeightLog)."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='pressure_logs')
    sensor = models.CharField(_('sensor serial'), max_length=32)
    date = models.DateTimeField()
    psi1 = models.DecimalField(_('PSI1'), max_digits=20, decimal_places=6)
    psi2 = models.DecimalField(_('PSI2'), max_digits=20, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('pressure weight log')
        verbose_name_plural = _('pressure weight logs')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['device', 'date']),
            models.Index(fields=['sensor']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.sensor[:8]} @ {self.date}"


class AlarmLog(models.Model):
    """Model for alarm logs (migrated from old backend)."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='alarm_logs')
    sensor = models.CharField(_('sensor serial'), max_length=32)
    date = models.DateTimeField()
    checksum = models.IntegerField()
    duration = models.IntegerField()
    comment = models.CharField(max_length=24)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('alarm log')
        verbose_name_plural = _('alarm logs')
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return f'Sensor alarm {self.comment}:{self.sensor[:8]} @ {self.date.strftime("%H:%M:%S")}'


class Tracking(models.Model):
    """Model for tracking sessions (migrated from old backend)."""
    tracking = models.CharField(_('tracking'), max_length=40, unique=True)
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='legacy_tracking_sessions')
    stop_fence = models.ForeignKey('GeoFence', on_delete=models.CASCADE, related_name='stop_sessions')
    fences = models.ManyToManyField('GeoFence', related_name='tracking_events')
    start = models.DateTimeField(db_index=True)
    stop = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('tracking session')
        verbose_name_plural = _('tracking sessions')
        ordering = ['-start']

    def __str__(self):
        return self.tracking

    @property
    def is_active(self):
        """Check if tracking session is active."""
        return self.stop is None

    def end_tracking(self):
        """End the tracking session."""
        if self.is_active:
            self.stop = timezone.now()
            self.save() 