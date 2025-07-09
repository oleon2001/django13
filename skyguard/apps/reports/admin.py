"""
Admin configuration for the reports application.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ReportTemplate, ReportExecution, TicketReport, 
    StatisticsReport, PeopleCountReport, AlarmReport
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin for report templates."""
    list_display = ['name', 'report_type', 'format', 'is_active', 'created_by', 'created_at']
    list_filter = ['report_type', 'format', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'report_type', 'format')
        }),
        ('Configuration', {
            'fields': ('template_data', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    """Admin for report executions."""
    list_display = ['template', 'executed_by', 'status', 'created_at', 'duration_display']
    list_filter = ['status', 'template__report_type', 'created_at']
    search_fields = ['template__name', 'executed_by__username']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'duration_display']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Execution Information', {
            'fields': ('template', 'executed_by', 'status')
        }),
        ('Parameters', {
            'fields': ('parameters',)
        }),
        ('Timing', {
            'fields': ('created_at', 'started_at', 'completed_at', 'duration_display')
        }),
        ('Results', {
            'fields': ('result_file', 'error_message')
        }),
    )
    
    def duration_display(self, obj):
        """Display duration in a readable format."""
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        return "N/A"
    duration_display.short_description = 'Duration'


@admin.register(TicketReport)
class TicketReportAdmin(admin.ModelAdmin):
    """Admin for ticket reports."""
    list_display = ['device', 'driver_name', 'total_amount', 'received_amount', 'difference', 'report_date']
    list_filter = ['report_date', 'device__route']
    search_fields = ['device__name', 'driver_name']
    readonly_fields = ['created_at']
    ordering = ['-report_date']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('device', 'driver_name', 'report_date')
        }),
        ('Financial Data', {
            'fields': ('total_amount', 'received_amount', 'difference')
        }),
        ('Details', {
            'fields': ('ticket_data', 'created_at')
        }),
    )


@admin.register(StatisticsReport)
class StatisticsReportAdmin(admin.ModelAdmin):
    """Admin for statistics reports."""
    list_display = ['device', 'report_date', 'total_distance', 'total_passengers', 'average_speed', 'operating_hours']
    list_filter = ['report_date', 'device__route']
    search_fields = ['device__name']
    readonly_fields = ['created_at']
    ordering = ['-report_date']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('device', 'report_date')
        }),
        ('Statistics', {
            'fields': ('total_distance', 'total_passengers', 'total_tickets', 'average_speed', 'operating_hours')
        }),
        ('Details', {
            'fields': ('statistics_data', 'created_at')
        }),
    )


@admin.register(PeopleCountReport)
class PeopleCountReportAdmin(admin.ModelAdmin):
    """Admin for people count reports."""
    list_display = ['device', 'report_date', 'total_people', 'peak_hour', 'peak_count']
    list_filter = ['report_date', 'device__route']
    search_fields = ['device__name']
    readonly_fields = ['created_at']
    ordering = ['-report_date']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('device', 'report_date')
        }),
        ('Count Data', {
            'fields': ('total_people', 'peak_hour', 'peak_count')
        }),
        ('Details', {
            'fields': ('hourly_data', 'created_at')
        }),
    )


@admin.register(AlarmReport)
class AlarmReportAdmin(admin.ModelAdmin):
    """Admin for alarm reports."""
    list_display = ['device', 'report_date', 'total_alarms', 'critical_alarms', 'warning_alarms']
    list_filter = ['report_date', 'device__route']
    search_fields = ['device__name']
    readonly_fields = ['created_at']
    ordering = ['-report_date']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('device', 'report_date')
        }),
        ('Alarm Data', {
            'fields': ('total_alarms', 'critical_alarms', 'warning_alarms')
        }),
        ('Details', {
            'fields': ('alarm_types', 'created_at')
        }),
    ) 