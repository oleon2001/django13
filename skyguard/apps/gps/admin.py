"""
Admin configuration for GPS app.
"""
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import (
    # Core device models
    GPSDevice, SimCard, DeviceHarness, ServerSMS, DeviceStats,
    GPSLocation, GPSEvent, IOEvent, GSMEvent, ResetEvent,
    GeoFence, GeoFenceEvent, AccelerationLog, Overlay, AddressCache,
    
    # Location and event models
    Location, NetworkEvent, DeviceSession,
    
    # Sensor models
    PressureSensorCalibration, PressureWeightLog, AlarmLog, Tracking,
    
    # Driver and ticket models
    Driver, TicketLog, TicketDetail, TimeSheetCapture,
    
    # Asset management models
    CarPark, CarLane, CarSlot, GridlessCar, DemoCar,
    
    # Protocol models
    GPRSSession, GPRSPacket, GPRSRecord, UDPSession, ProtocolLog,
)


@admin.register(GPSDevice)
class GPSDeviceAdmin(admin.ModelAdmin):
    """Admin configuration for GPSDevice model."""
    list_display = ('imei', 'name', 'connection_status', 'route', 'economico', 'last_connection')
    list_filter = ('connection_status', 'route', 'model', 'created_at')
    search_fields = ('imei', 'name', 'economico')
    readonly_fields = ('created_at', 'updated_at', 'last_connection', 'total_connections')
    fieldsets = (
        ('Basic Information', {
            'fields': ('imei', 'name', 'serial', 'model', 'software_version')
        }),
        ('Route & Economic', {
            'fields': ('route', 'economico', 'harness')
        }),
        ('Location', {
            'fields': ('position', 'speed', 'course', 'altitude', 'odometer')
        }),
        ('Hardware', {
            'fields': ('inputs', 'outputs', 'alarm_mask', 'alarms')
        }),
        ('Connection', {
            'fields': ('connection_status', 'current_ip', 'current_port', 'last_connection', 'total_connections')
        }),
        ('SIM Card', {
            'fields': ('sim_card',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SimCard)
class SimCardAdmin(admin.ModelAdmin):
    """Admin configuration for SimCard model."""
    list_display = ('iccid', 'phone', 'provider')
    list_filter = ('provider',)
    search_fields = ('iccid', 'imsi', 'phone')


@admin.register(DeviceHarness)
class DeviceHarnessAdmin(admin.ModelAdmin):
    """Admin configuration for DeviceHarness model."""
    list_display = ('name', 'in00', 'in01', 'out00')
    search_fields = ('name',)


@admin.register(Location)
class LocationAdmin(GISModelAdmin):
    """Admin configuration for Location model."""
    list_display = ('device', 'timestamp', 'speed', 'course', 'altitude')
    list_filter = ('timestamp', 'device')
    search_fields = ('device__imei', 'device__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GPSLocation)
class GPSLocationAdmin(GISModelAdmin):
    """Admin configuration for GPSLocation model."""
    list_display = ('device', 'timestamp', 'speed', 'course', 'satellites')
    list_filter = ('timestamp', 'device')
    search_fields = ('device__imei', 'device__name')


@admin.register(NetworkEvent)
class NetworkEventAdmin(admin.ModelAdmin):
    """Admin configuration for NetworkEvent model."""
    list_display = ('device', 'type', 'timestamp', 'speed', 'course')
    list_filter = ('type', 'timestamp', 'device')
    search_fields = ('device__imei', 'device__name', 'type')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GPSEvent)
class GPSEventAdmin(admin.ModelAdmin):
    """Admin configuration for GPSEvent model."""
    list_display = ('device', 'type', 'timestamp', 'source')
    list_filter = ('type', 'timestamp', 'source')
    search_fields = ('device__imei', 'device__name', 'type')


@admin.register(GeoFence)
class GeoFenceAdmin(GISModelAdmin):
    """Admin configuration for GeoFence model."""
    list_display = ('name', 'owner', 'base', 'is_active')
    list_filter = ('base', 'is_active', 'owner')
    search_fields = ('name', 'owner__username')


@admin.register(DeviceSession)
class DeviceSessionAdmin(admin.ModelAdmin):
    """Admin configuration for DeviceSession model."""
    list_display = ('device', 'start_time', 'end_time', 'is_active', 'ip_address', 'port')
    list_filter = ('is_active', 'start_time', 'end_time', 'protocol')
    search_fields = ('device__imei', 'device__name', 'ip_address')
    readonly_fields = ('created_at', 'updated_at', 'last_activity')


# Sensor Models
@admin.register(PressureSensorCalibration)
class PressureSensorCalibrationAdmin(admin.ModelAdmin):
    """Admin configuration for PressureSensorCalibration model."""
    list_display = ('device', 'name', 'sensor')
    list_filter = ('device',)
    search_fields = ('name', 'sensor', 'device__name')


@admin.register(PressureWeightLog)
class PressureWeightLogAdmin(admin.ModelAdmin):
    """Admin configuration for PressureWeightLog model."""
    list_display = ('device', 'sensor', 'date', 'psi1', 'psi2')
    list_filter = ('device', 'date')
    search_fields = ('device__name', 'sensor')


@admin.register(AlarmLog)
class AlarmLogAdmin(admin.ModelAdmin):
    """Admin configuration for AlarmLog model."""
    list_display = ('device', 'sensor', 'date', 'comment')
    list_filter = ('device', 'date')
    search_fields = ('device__name', 'sensor', 'comment')


# Driver Models
@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """Admin configuration for Driver model."""
    list_display = ('full_name', 'payroll', 'license', 'is_active')
    list_filter = ('is_active', 'civil_status')
    search_fields = ('name', 'middle_name', 'last_name', 'payroll', 'license')


@admin.register(TicketLog)
class TicketLogAdmin(admin.ModelAdmin):
    """Admin configuration for TicketLog model."""
    list_display = ('id', 'route', 'date')
    list_filter = ('route', 'date')


@admin.register(TicketDetail)
class TicketDetailAdmin(admin.ModelAdmin):
    """Admin configuration for TicketDetail model."""
    list_display = ('id', 'device', 'driver_name', 'total', 'received', 'date')
    list_filter = ('device', 'date')
    search_fields = ('driver_name', 'device__name')


# Asset Models
@admin.register(CarPark)
class CarParkAdmin(admin.ModelAdmin):
    """Admin configuration for CarPark model."""
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(CarLane)
class CarLaneAdmin(GISModelAdmin):
    """Admin configuration for CarLane model."""
    list_display = ('park', 'prefix', 'slot_count', 'single')
    list_filter = ('park', 'single')
    search_fields = ('prefix', 'park__name')


@admin.register(CarSlot)
class CarSlotAdmin(GISModelAdmin):
    """Admin configuration for CarSlot model."""
    list_display = ('lane', 'number', 'car_serial', 'car_date')
    list_filter = ('lane', 'car_date')
    search_fields = ('car_serial', 'lane__prefix')


@admin.register(GridlessCar)
class GridlessCarAdmin(GISModelAdmin):
    """Admin configuration for GridlessCar model."""
    list_display = ('car_serial', 'car_date')
    list_filter = ('car_date',)
    search_fields = ('car_serial',)


# Protocol Models
@admin.register(GPRSSession)
class GPRSSessionAdmin(admin.ModelAdmin):
    """Admin configuration for GPRSSession model."""
    list_display = ('device', 'start', 'ip', 'port', 'is_active', 'packets_count')
    list_filter = ('is_active', 'start')
    search_fields = ('device__name', 'ip')


@admin.register(UDPSession)
class UDPSessionAdmin(admin.ModelAdmin):
    """Admin configuration for UDPSession model."""
    list_display = ('device', 'session', 'host', 'port', 'is_active', 'expires')
    list_filter = ('is_active', 'expires')
    search_fields = ('device__name', 'host')


@admin.register(ProtocolLog)
class ProtocolLogAdmin(admin.ModelAdmin):
    """Admin configuration for ProtocolLog model."""
    list_display = ('device', 'protocol', 'level', 'message', 'timestamp')
    list_filter = ('protocol', 'level', 'timestamp')
    search_fields = ('device__name', 'message')


# Additional Models - Simple registration for others
admin.site.register(ServerSMS)
admin.site.register(DeviceStats)
admin.site.register(IOEvent)
admin.site.register(GSMEvent)
admin.site.register(ResetEvent)
admin.site.register(GeoFenceEvent)
admin.site.register(AccelerationLog)
admin.site.register(Overlay)
admin.site.register(AddressCache)
admin.site.register(Tracking)
admin.site.register(TimeSheetCapture)
admin.site.register(DemoCar)
admin.site.register(GPRSPacket)
admin.site.register(GPRSRecord)
