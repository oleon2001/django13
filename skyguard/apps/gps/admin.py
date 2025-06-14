"""
Admin interface for the GPS application.
"""
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import (
    GPSDevice, GPSLocation, GPSEvent, GeoFence, GeoFenceEvent,
    SimCard, NetworkEvent, NetworkSession, NetworkMessage
)


@admin.register(GPSDevice)
class GPSDeviceAdmin(GISModelAdmin):
    """Admin interface for GPS devices."""
    list_display = ('imei', 'name', 'model', 'software_version', 'last_log', 'owner')
    list_filter = ('model', 'created_at', 'last_log')
    search_fields = ('imei', 'name', 'serial')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Device Information', {
            'fields': ('imei', 'name', 'model', 'software_version', 'serial')
        }),
        ('Status', {
            'fields': ('position', 'speed', 'course', 'altitude', 'last_log')
        }),
        ('Hardware', {
            'fields': ('inputs', 'outputs', 'alarm_mask', 'alarms')
        }),
        ('Firmware', {
            'fields': ('firmware_file', 'last_firmware_update')
        }),
        ('System', {
            'fields': ('odometer', 'icon', 'owner', 'sim_card')
        }),
        ('Additional', {
            'fields': ('comments',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(SimCard)
class SimCardAdmin(admin.ModelAdmin):
    """Admin interface for SIM cards."""
    list_display = ('iccid', 'phone', 'provider', 'imsi')
    list_filter = ('provider',)
    search_fields = ('iccid', 'phone', 'imsi')


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
            'fields': ('type', 'timestamp', 'source', 'text')
        }),
        ('Location', {
            'fields': ('position', 'speed', 'course', 'altitude')
        }),
        ('IO Status', {
            'fields': ('inputs', 'outputs', 'input_changes', 'output_changes', 'alarm_changes')
        }),
        ('Additional Data', {
            'fields': ('odometer', 'raw_data', 'changes_description')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )


@admin.register(GeoFence)
class GeoFenceAdmin(GISModelAdmin):
    """Admin interface for geofences."""
    list_display = ('name', 'owner', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'owner', 'description')
        }),
        ('Geometry', {
            'fields': ('geometry',)
        }),
        ('Notifications', {
            'fields': ('is_active', 'notify_on_entry', 'notify_on_exit', 'notify_owners')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(GeoFenceEvent)
class GeoFenceEventAdmin(admin.ModelAdmin):
    """Admin interface for geofence events."""
    list_display = ('fence', 'device', 'event_type', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('fence__name', 'device__imei', 'device__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Event Information', {
            'fields': ('fence', 'device', 'event_type', 'timestamp')
        }),
        ('Location', {
            'fields': ('position',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )


@admin.register(NetworkEvent)
class NetworkEventAdmin(admin.ModelAdmin):
    """Admin interface for network events."""
    list_display = ('device', 'event_type', 'timestamp', 'protocol')
    list_filter = ('event_type', 'protocol', 'timestamp')
    search_fields = ('device__imei', 'device__name')
    readonly_fields = ('created_at',)


@admin.register(NetworkSession)
class NetworkSessionAdmin(admin.ModelAdmin):
    """Admin interface for network sessions."""
    list_display = ('device', 'start_time', 'end_time', 'protocol')
    list_filter = ('protocol', 'start_time')
    search_fields = ('device__imei', 'device__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NetworkMessage)
class NetworkMessageAdmin(admin.ModelAdmin):
    """Admin interface for network messages."""
    list_display = ('session', 'message_type', 'direction', 'timestamp')
    list_filter = ('message_type', 'direction', 'timestamp')
    search_fields = ('session__device__imei', 'session__device__name')
    readonly_fields = ('created_at',)
