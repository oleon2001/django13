"""
Asset management models for GPS system (migrated from old backend).
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import pytz
from django.conf import settings

# Set up timezone
localtz = pytz.timezone(settings.TIME_ZONE)


class CarPark(models.Model):
    """Model for car parks (migrated from old backend)."""
    name = models.CharField(_('name'), max_length=30)
    description = models.TextField(_('description'), max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('car park')
        verbose_name_plural = _('car parks')
        ordering = ['name']

    def __str__(self):
        return self.name


class CarLane(models.Model):
    """Model for car lanes (migrated from old backend)."""
    prefix = models.CharField(_('prefix'), max_length=5)
    slot_count = models.SmallIntegerField(_('slot count'), default=62)
    start = gis_models.PointField(_('start'))
    end = gis_models.PointField(_('end'))
    single = models.BooleanField(_('single'), default=False)
    park = models.ForeignKey(CarPark, on_delete=models.CASCADE, related_name='lanes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('car lane')
        verbose_name_plural = _('car lanes')
        ordering = ['park', 'prefix']

    def __str__(self):
        return f"{self.park.name} - Lane {self.prefix}"


class CarSlot(models.Model):
    """Model for car slots (migrated from old backend)."""
    lane = models.ForeignKey(CarLane, on_delete=models.CASCADE, related_name='slots')
    number = models.SmallIntegerField(_('number'))
    position = gis_models.PointField(_('position'))
    car_serial = models.CharField(_('car serial'), max_length=80, null=True, blank=True, db_index=True)
    car_date = models.DateTimeField(_('car date'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        unique_together = [('lane', 'number')]
        verbose_name = _('car slot')
        verbose_name_plural = _('car slots')
        ordering = ['lane', 'number']

    def __str__(self):
        return f'{self.lane.prefix}{self.number:03d}'

    @property
    def number_display(self):
        """Get display number (1-indexed)."""
        return self.number + 1

    @property
    def is_occupied(self):
        """Check if slot is occupied."""
        return bool(self.car_serial)

    def car_date_localized(self):
        """Get car date in local timezone."""
        if self.car_date:
            if not self.car_date.tzinfo:
                self.car_date = pytz.utc.localize(self.car_date)
            return self.car_date.astimezone(localtz)
        return None


class GridlessCar(models.Model):
    """Model for gridless car tracking (migrated from old backend)."""
    position = gis_models.PointField(_('position'))
    car_serial = models.CharField(_('car serial'), max_length=80, null=True, blank=True, db_index=True)
    car_date = models.DateTimeField(_('car date'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('gridless car')
        verbose_name_plural = _('gridless cars')
        ordering = ['-car_date']

    def __str__(self):
        return f"Car {self.car_serial} @ {self.car_date}"

    def car_date_localized(self):
        """Get car date in local timezone."""
        if self.car_date:
            if not self.car_date.tzinfo:
                self.car_date = pytz.utc.localize(self.car_date)
            return self.car_date.astimezone(localtz)
        return None


class DemoCar(models.Model):
    """Model for demo car tracking (migrated from old backend)."""
    position = gis_models.PointField(_('position'))
    car_serial = models.CharField(_('car serial'), max_length=80, null=True, blank=True, db_index=True)
    car_date = models.DateTimeField(_('car date'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('demo car')
        verbose_name_plural = _('demo cars')
        ordering = ['-car_date']

    def __str__(self):
        return f"Demo Car {self.car_serial} @ {self.car_date}"

    def car_date_localized(self):
        """Get car date in local timezone."""
        if self.car_date:
            if not self.car_date.tzinfo:
                self.car_date = pytz.utc.localize(self.car_date)
            return self.car_date.astimezone(localtz)
        return None 