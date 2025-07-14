"""
Subsidies models for the GPS system.
Migrated from legacy django14 system to modern architecture.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from skyguard.apps.gps.models import GPSDevice


class Driver(models.Model):
    """Model for drivers/operators."""
    name = models.CharField(_('Nombre'), max_length=40)
    middle = models.CharField(_('A. Paterno'), max_length=40)
    last = models.CharField(_('A. Materno'), max_length=40)
    birth = models.DateField(_('F. de nacimiento'))
    cstatus = models.CharField(_('Estado Civil'), max_length=40, choices=[
        ("SOL", "Soltero"),
        ("CAS", "Casado"),
        ("VIU", "Viudo"),
        ("DIV", "Divorciado")
    ])
    payroll = models.CharField('Nómina', max_length=40)
    socials = models.CharField(_('Seguro social'), max_length=40)
    taxid = models.CharField(_('RFC'), max_length=40)
    license = models.CharField(_('Licencia'), max_length=40, null=True, blank=True)
    lic_exp = models.DateField("Vencimiento", null=True, blank=True)
    address = models.TextField('Dirección')
    phone = models.CharField('Teléfono', max_length=40)
    phone1 = models.CharField('Teléfono 1', max_length=40, null=True, blank=True)
    phone2 = models.CharField('Teléfono 2', max_length=40, null=True, blank=True)
    active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Chofer')
        verbose_name_plural = _('Choferes')
        ordering = ('middle', 'last', 'name')

    def __str__(self):
        return f"{self.middle} {self.last}, {self.name}"

    @property
    def full_name(self):
        """Get full name of driver."""
        return f"{self.middle} {self.last}, {self.name}"


class DailyLog(models.Model):
    """Model for daily driver logs."""
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='daily_logs')
    route = models.IntegerField(_('Ruta'), null=True, blank=True)
    start = models.DateTimeField(_('Inicio'), null=False)
    stop = models.DateTimeField(_('Fin'), null=False)
    regular = models.IntegerField(_('Ordinarias'), default=0)
    preferent = models.IntegerField(_('Preferentes'), default=0)
    total = models.IntegerField(_('Total de pasajeros'), default=0)
    due = models.DecimalField(_('A pagar'), max_digits=10, decimal_places=2, default=0)
    payed = models.DecimalField(_('Pagado'), max_digits=10, decimal_places=2, default=0)
    difference = models.DecimalField(_('Diferencia'), max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Registro')
        verbose_name_plural = _('Registros')
        ordering = ['-start']

    def __str__(self):
        return f"{self.driver.full_name} - {self.start.date()}"

    def save(self, *args, **kwargs):
        """Calculate difference on save."""
        self.difference = self.due - self.payed
        super().save(*args, **kwargs)


class CashReceipt(models.Model):
    """Model for cash receipts."""
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='cash_receipts')
    ticket1 = models.IntegerField("Folio de Caseta", null=False, blank=False)
    ticket2 = models.IntegerField("Folio de Liquidación", null=True, blank=True)
    payed1 = models.DecimalField(_('$ Vuelta 1'), max_digits=10, decimal_places=2, null=True, blank=True)
    payed2 = models.DecimalField(_('$ Vuelta 2'), max_digits=10, decimal_places=2, null=True, blank=True)
    payed3 = models.DecimalField(_('$ Vuelta 3'), max_digits=10, decimal_places=2, null=True, blank=True)
    payed4 = models.DecimalField(_('$ Vuelta 4'), max_digits=10, decimal_places=2, null=True, blank=True)
    payed5 = models.DecimalField(_('$ Vuelta 5'), max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Recibo de efectivo')
        verbose_name_plural = _('Recibos de efectivo')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.driver.full_name} - Ticket {self.ticket1}"

    @property
    def total_payed(self):
        """Calculate total payed amount."""
        total = 0
        for i in range(1, 6):
            amount = getattr(self, f'payed{i}', 0) or 0
            total += amount
        return total


class TimeSheetCapture(models.Model):
    """Model for time sheet captures."""
    date = models.DateField(_('date'), null=False)
    name = models.CharField(_('name'), max_length=100)
    times = models.JSONField(_('times'), default=list)
    driver = models.CharField(_('driver'), max_length=100, blank=True)
    route = models.CharField(_('route'), max_length=50, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Time Sheet Capture')
        verbose_name_plural = _('Time Sheet Captures')
        ordering = ['-date', 'name']
        unique_together = ['date', 'name']

    def __str__(self):
        return f"{self.name} - {self.date}"

    @property
    def rounds_count(self):
        """Get number of rounds."""
        return len(self.times)

    @property
    def total_duration(self):
        """Calculate total duration."""
        total_minutes = 0
        for start_time, end_time in self.times:
            if start_time and end_time:
                # Parse time strings and calculate difference
                try:
                    from datetime import datetime
                    start = datetime.strptime(start_time, '%H:%M')
                    end = datetime.strptime(end_time, '%H:%M')
                    duration = end - start
                    total_minutes += duration.total_seconds() / 60
                except:
                    pass
        return total_minutes


class SubsidyRoute(models.Model):
    """Model for subsidy routes."""
    ROUTE_CHOICES = [
        ('A6', 'Ruta A6'),
        ('155', 'Ruta 155'),
        ('202', 'Ruta 202'),
        ('31', 'Ruta 31'),
        ('207E', 'Ruta 207E'),
        ('207P', 'Ruta 207P'),
        ('400S1', 'Ruta 400 Sector 1'),
        ('400S2', 'Ruta 400 Sector 2'),
        ('400S4H', 'Ruta 400 Sector 4 H'),
        ('400S4J', 'Ruta 400 Sector 4 J'),
    ]

    name = models.CharField(_('name'), max_length=100, unique=True)
    route_code = models.CharField(_('route code'), max_length=20, choices=ROUTE_CHOICES)
    company = models.CharField(_('company'), max_length=200)
    branch = models.CharField(_('branch'), max_length=200, blank=True)
    flag = models.CharField(_('flag'), max_length=100)
    units = models.JSONField(_('units'), default=list)
    km = models.DecimalField(_('kilometers'), max_digits=8, decimal_places=3)
    frequency = models.IntegerField(_('frequency'), default=0)
    time_minutes = models.IntegerField(_('time in minutes'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Subsidy Route')
        verbose_name_plural = _('Subsidy Routes')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.company}"

    @property
    def units_count(self):
        """Get number of units."""
        return len(self.units)


class SubsidyReport(models.Model):
    """Model for subsidy reports."""
    REPORT_TYPES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('timesheet', 'Time Sheet Report'),
        ('cash', 'Cash Report'),
    ]

    route = models.ForeignKey(SubsidyRoute, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(_('report type'), max_length=20, choices=REPORT_TYPES)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subsidy_reports')
    file_path = models.CharField(_('file path'), max_length=500, blank=True)
    report_data = models.JSONField(_('report data'), default=dict)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Subsidy Report')
        verbose_name_plural = _('Subsidy Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.route.name} - {self.report_type} ({self.start_date} to {self.end_date})"


class EconomicMapping(models.Model):
    """Model for economic number mappings."""
    unit_name = models.CharField(_('unit name'), max_length=100, unique=True)
    economic_number = models.CharField(_('economic number'), max_length=20)
    route = models.CharField(_('route'), max_length=50, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Economic Mapping')
        verbose_name_plural = _('Economic Mappings')
        ordering = ['unit_name']

    def __str__(self):
        return f"{self.unit_name} -> {self.economic_number}" 