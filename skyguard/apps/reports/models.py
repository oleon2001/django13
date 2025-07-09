"""
Report models for the GPS system.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from skyguard.apps.gps.models import GPSDevice, GPSEvent, GPSLocation


class ReportTemplate(models.Model):
    """Model for report templates."""
    REPORT_TYPES = (
        ('ticket', 'Ticket Report'),
        ('stats', 'Statistics Report'),
        ('people', 'People Count Report'),
        ('alarm', 'Alarm Report'),
        ('sensor', 'Sensor Report'),
        ('custom', 'Custom Report'),
    )

    FORMAT_CHOICES = (
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('xlsx', 'Excel'),
    )

    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    report_type = models.CharField(_('report type'), max_length=20, choices=REPORT_TYPES)
    format = models.CharField(_('format'), max_length=10, choices=FORMAT_CHOICES, default='pdf')
    template_data = models.JSONField(_('template data'), default=dict)
    is_active = models.BooleanField(_('is active'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('report template')
        verbose_name_plural = _('report templates')
        ordering = ['name']

    def __str__(self):
        return self.name


class ReportExecution(models.Model):
    """Model for report executions."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='executions')
    executed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='executed_reports')
    parameters = models.JSONField(_('parameters'), default=dict)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    result_file = models.FileField(_('result file'), upload_to='reports/', null=True, blank=True)
    error_message = models.TextField(_('error message'), blank=True)
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('report execution')
        verbose_name_plural = _('report executions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.name} - {self.status}"

    @property
    def duration(self):
        """Get execution duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class TicketReport(models.Model):
    """Model for ticket reports."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='ticket_reports')
    driver_name = models.CharField(_('driver name'), max_length=100)
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    received_amount = models.DecimalField(_('received amount'), max_digits=10, decimal_places=2)
    difference = models.DecimalField(_('difference'), max_digits=10, decimal_places=2)
    ticket_data = models.JSONField(_('ticket data'), default=dict)
    report_date = models.DateField(_('report date'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('ticket report')
        verbose_name_plural = _('ticket reports')
        ordering = ['-report_date']

    def __str__(self):
        return f"{self.device.name} - {self.driver_name} - {self.report_date}"


class StatisticsReport(models.Model):
    """Model for statistics reports."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='statistics_reports')
    report_date = models.DateField(_('report date'))
    total_distance = models.DecimalField(_('total distance'), max_digits=10, decimal_places=2)
    total_passengers = models.IntegerField(_('total passengers'), default=0)
    total_tickets = models.IntegerField(_('total tickets'), default=0)
    average_speed = models.DecimalField(_('average speed'), max_digits=5, decimal_places=2)
    operating_hours = models.DecimalField(_('operating hours'), max_digits=5, decimal_places=2)
    statistics_data = models.JSONField(_('statistics data'), default=dict)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('statistics report')
        verbose_name_plural = _('statistics reports')
        ordering = ['-report_date']

    def __str__(self):
        return f"{self.device.name} - {self.report_date}"


class PeopleCountReport(models.Model):
    """Model for people count reports."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='people_count_reports')
    report_date = models.DateField(_('report date'))
    total_people = models.IntegerField(_('total people'), default=0)
    peak_hour = models.TimeField(_('peak hour'), null=True, blank=True)
    peak_count = models.IntegerField(_('peak count'), default=0)
    hourly_data = models.JSONField(_('hourly data'), default=dict)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('people count report')
        verbose_name_plural = _('people count reports')
        ordering = ['-report_date']

    def __str__(self):
        return f"{self.device.name} - {self.report_date}"


class AlarmReport(models.Model):
    """Model for alarm reports."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='alarm_reports')
    report_date = models.DateField(_('report date'))
    total_alarms = models.IntegerField(_('total alarms'), default=0)
    critical_alarms = models.IntegerField(_('critical alarms'), default=0)
    warning_alarms = models.IntegerField(_('warning alarms'), default=0)
    alarm_types = models.JSONField(_('alarm types'), default=dict)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('alarm report')
        verbose_name_plural = _('alarm reports')
        ordering = ['-report_date']

    def __str__(self):
        return f"{self.device.name} - {self.report_date}" 