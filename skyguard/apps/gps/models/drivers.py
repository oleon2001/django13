"""
Driver and ticket models for GPS system (migrated from old backend).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .device import GPSDevice


class Driver(models.Model):
    """Model for drivers (migrated from old backend)."""
    CIVIL_STATUS_CHOICES = (
        ("SOL", "Soltero"),
        ("CAS", "Casado"),
        ("VIU", "Viudo"),
        ("DIV", "Divorciado")
    )

    name = models.CharField(_('name'), max_length=40)
    middle_name = models.CharField(_('middle name'), max_length=40)
    last_name = models.CharField(_('last name'), max_length=40)
    birth_date = models.DateField(_('birth date'))
    civil_status = models.CharField(_('civil status'), max_length=3, choices=CIVIL_STATUS_CHOICES)
    payroll = models.CharField(_('payroll'), max_length=40)
    social_security = models.CharField(_('social security'), max_length=40)
    tax_id = models.CharField(_('tax ID'), max_length=40)
    license = models.CharField(_('license'), max_length=40, null=True, blank=True)
    license_expiry = models.DateField(_('license expiry'), null=True, blank=True)
    address = models.TextField(_('address'))
    phone = models.CharField(_('phone'), max_length=40)
    phone1 = models.CharField(_('phone 1'), max_length=40, null=True, blank=True)
    phone2 = models.CharField(_('phone 2'), max_length=40, null=True, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('driver')
        verbose_name_plural = _('drivers')
        ordering = ['middle_name', 'last_name', 'name']

    def __str__(self):
        return f"{self.middle_name} {self.last_name}, {self.name}"

    @property
    def full_name(self):
        """Get full name."""
        return f"{self.name} {self.middle_name} {self.last_name}"

    @property
    def is_license_valid(self):
        """Check if license is valid."""
        if self.license_expiry:
            return self.license_expiry >= timezone.now().date()
        return False


class TicketLog(models.Model):
    """Model for ticket logs (migrated from TicketsLog)."""
    ROUTE_CHOICES = GPSDevice.ROUTE_CHOICES

    id = models.AutoField(_('folio'), primary_key=True)
    data = models.TextField(_('data'))
    route = models.IntegerField(_('route'), null=True, blank=True, choices=ROUTE_CHOICES)
    date = models.DateTimeField(_('start date'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('ticket log')
        verbose_name_plural = _('ticket logs')
        ordering = ['-date']

    def __str__(self):
        return f"Ticket {self.id} - Route {self.route}"


class TicketDetail(models.Model):
    """Model for ticket details (migrated from TicketDetails)."""
    id = models.AutoField(_('folio'), primary_key=True)
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='ticket_details')
    date = models.DateTimeField(_('start date'), null=True, blank=True)
    driver_name = models.CharField(_('driver name'), max_length=80)
    total = models.IntegerField(_('total'))
    received = models.IntegerField(_('received'))
    ticket_data = models.TextField(_('ticket data'))
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('ticket detail')
        verbose_name_plural = _('ticket details')
        ordering = ['-date']

    def __str__(self):
        return f"Ticket {self.id} - {self.driver_name}"


class TimeSheetCapture(models.Model):
    """Model for timesheet capture (migrated from old backend)."""
    id = models.AutoField(_('folio'), primary_key=True)
    name = models.CharField(_('name'), max_length=20)
    date = models.DateTimeField(_('start date'), null=True, blank=True)
    driver_name = models.CharField(_('driver name'), max_length=80)
    laps = models.IntegerField(_('laps'))
    times = models.TextField(_('times'))
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('timesheet capture')
        verbose_name_plural = _('timesheet captures')
        ordering = ['-date']

    def __str__(self):
        return f"Timesheet {self.id} - {self.driver_name}"


class CardTransaction(models.Model):
    """Model for card transactions (migrated from Tarjetas)."""
    line_name = models.TextField(_('line name'), db_column='nombre_linea')
    branch_name = models.TextField(_('branch name'), db_column='nombre_ramal')
    line = models.IntegerField(_('line'), db_column='linea')
    economico = models.IntegerField(_('economic'), db_column='economico')
    date = models.DateTimeField(_('date'), db_column='dfecha', primary_key=True)
    type = models.IntegerField(_('type'), db_column='itipo')
    unit = models.CharField(_('unit'), max_length=12, db_column='cunidad')
    card = models.IntegerField(_('card'), db_column='itarjeta')
    amount = models.IntegerField(_('amount'), db_column='imonto')

    objects = models.Manager()

    class Meta:
        db_table = 'tbltarjetas'
        managed = False  # This is an external table
        verbose_name = _('card transaction')
        verbose_name_plural = _('card transactions')
        get_latest_by = 'date'
        ordering = ['line', 'economico', 'date']

    def __str__(self):
        return f"Card {self.card} - {self.amount} @ {self.date}" 