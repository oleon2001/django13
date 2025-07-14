"""
Admin configuration for the tracking application.
"""
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import (
    TrackingSession, TrackingPoint, TrackingEvent, TrackingConfig,
    Alert, Geofence, Route, RoutePoint
)


@admin.register(TrackingSession)
class TrackingSessionAdmin(admin.ModelAdmin):
    """Admin for TrackingSession model."""
    list_display = ('session_id', 'device', 'user', 'status', 'start_time', 'end_time', 'total_distance')
    list_filter = ('status', 'start_time', 'end_time')
    search_fields = ('session_id', 'device__name', 'user__username')
    readonly_fields = ('session_id', 'start_time', 'end_time', 'duration', 'total_distance', 'average_speed', 'max_speed')
    ordering = ('-start_time',)
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'device', 'user', 'status', 'notes')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration')
        }),
        ('Statistics', {
            'fields': ('total_distance', 'average_speed', 'max_speed')
        }),
    )


@admin.register(TrackingPoint)
class TrackingPointAdmin(GISModelAdmin):
    """Admin for TrackingPoint model."""
    list_display = ('id', 'session', 'timestamp', 'speed', 'course', 'altitude', 'accuracy')
    list_filter = ('timestamp', 'session__status')
    search_fields = ('session__session_id', 'session__device__name')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Point Information', {
            'fields': ('session', 'position', 'timestamp')
        }),
        ('GPS Data', {
            'fields': ('speed', 'course', 'altitude', 'accuracy', 'satellites')
        }),
    )


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    """Admin for TrackingEvent model."""
    list_display = ('id', 'session', 'event_type', 'timestamp', 'message')
    list_filter = ('event_type', 'timestamp', 'session__status')
    search_fields = ('session__session_id', 'message', 'session__device__name')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Event Information', {
            'fields': ('session', 'event_type', 'timestamp', 'message')
        }),
        ('Additional Data', {
            'fields': ('position', 'data')
        }),
    )


@admin.register(TrackingConfig)
class TrackingConfigAdmin(admin.ModelAdmin):
    """Admin for TrackingConfig model."""
    list_display = ('device', 'auto_start', 'auto_stop', 'geofence_alerts', 'speed_alerts')
    list_filter = ('auto_start', 'auto_stop', 'geofence_alerts', 'speed_alerts', 'battery_alerts', 'signal_alerts')
    search_fields = ('device__name', 'device__imei')
    ordering = ('device__name',)
    
    fieldsets = (
        ('Device', {
            'fields': ('device',)
        }),
        ('Auto Tracking', {
            'fields': ('auto_start', 'auto_stop')
        }),
        ('Alerts', {
            'fields': ('geofence_alerts', 'speed_alerts', 'battery_alerts', 'signal_alerts')
        }),
        ('Thresholds', {
            'fields': ('min_speed_threshold', 'max_speed_threshold', 'battery_threshold', 'update_interval')
        }),
    )


@admin.register(Alert)
class AlertAdmin(GISModelAdmin):
    """Admin for Alert model."""
    list_display = ('id', 'device', 'alert_type', 'is_acknowledged', 'acknowledged_by', 'created_at')
    list_filter = ('alert_type', 'is_acknowledged', 'created_at', 'acknowledged_at')
    search_fields = ('device__name', 'device__imei', 'message', 'acknowledged_by__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('device', 'alert_type', 'message', 'position')
        }),
        ('Status', {
            'fields': ('is_acknowledged', 'acknowledged_by', 'acknowledged_at')
        }),
        ('Timing', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Geofence)
class GeofenceAdmin(GISModelAdmin):
    """Admin for Geofence model."""
    list_display = ('id', 'name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Geofence Information', {
            'fields': ('name', 'description', 'area', 'is_active')
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Route)
class RouteAdmin(GISModelAdmin):
    """Admin for Route model."""
    list_display = ('id', 'device', 'start_time', 'end_time', 'distance', 'average_speed', 'max_speed', 'is_completed')
    list_filter = ('is_completed', 'start_time', 'end_time')
    search_fields = ('device__name', 'device__imei')
    readonly_fields = ('distance', 'average_speed', 'max_speed')
    ordering = ('-start_time',)
    
    fieldsets = (
        ('Route Information', {
            'fields': ('device', 'start_time', 'end_time', 'is_completed')
        }),
        ('Statistics', {
            'fields': ('distance', 'average_speed', 'max_speed')
        }),
    )


@admin.register(RoutePoint)
class RoutePointAdmin(GISModelAdmin):
    """Admin for RoutePoint model."""
    list_display = ('id', 'route', 'timestamp', 'speed')
    list_filter = ('timestamp', 'route__is_completed')
    search_fields = ('route__device__name', 'route__device__imei')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Point Information', {
            'fields': ('route', 'position', 'timestamp')
        }),
        ('GPS Data', {
            'fields': ('speed',)
        }),
    )
