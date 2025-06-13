"""
Admin interface for the GPS application.
"""
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import GPSDevice, GPSLocation, GPSEvent


@admin.register(GPSDevice)
class GPSDeviceAdmin(GISModelAdmin):
    """Admin interface for GPS devices."""
    list_display = ('imei', 'name', 'protocol', 'firmware_version', 'last_log', 'is_active')
    list_filter = ('protocol', 'is_active', 'created_at')
    search_fields = ('imei', 'name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Device Information', {
            'fields': ('imei', 'name', 'protocol', 'firmware_version')
        }),
        ('Status', {
            'fields': ('is_active', 'last_log', 'position', 'speed', 'course', 'altitude')
        }),
        ('Maintenance', {
            'fields': ('last_maintenance', 'maintenance_interval')
        }),
        ('System', {
            'fields': ('battery_level', 'signal_strength', 'odometer')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(GPSLocation)
class GPSLocationAdmin(GISModelAdmin):
    """Admin interface for GPS locations."""
    list_display = ('device', 'timestamp', 'speed', 'course', 'altitude', 'satellites')
    list_filter = ('timestamp', 'satellites', 'fix_quality', 'fix_type')
    search_fields = ('device__imei', 'device__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Device', {
            'fields': ('device',)
        }),
        ('Location', {
            'fields': ('position', 'speed', 'course', 'altitude')
        }),
        ('GPS Data', {
            'fields': ('satellites', 'accuracy', 'hdop', 'pdop', 'fix_quality', 'fix_type')
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'created_at')
        })
    )


@admin.register(GPSEvent)
class GPSEventAdmin(admin.ModelAdmin):
    """Admin interface for GPS events."""
    list_display = ('device', 'type', 'timestamp', 'speed', 'course', 'altitude')
    list_filter = ('type', 'timestamp')
    search_fields = ('device__imei', 'device__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Device', {
            'fields': ('device',)
        }),
        ('Event', {
            'fields': ('type', 'timestamp')
        }),
        ('Location', {
            'fields': ('position', 'speed', 'course', 'altitude')
        }),
        ('Additional Data', {
            'fields': ('odometer', 'raw_data')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )
