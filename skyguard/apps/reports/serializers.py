from rest_framework import serializers
from .models import Route, Driver, Ticket, TimeSheet, GeoFence, Statistics, SensorData
from skyguard.apps.gps.models import GPSDevice, GPSLocation

class RouteSerializer(serializers.ModelSerializer):
    """Serializer para rutas"""
    class Meta:
        model = Route
        fields = '__all__'

class DriverSerializer(serializers.ModelSerializer):
    """Serializer para conductores"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = '__all__'
    
    def get_full_name(self, obj):
        return f"{obj.middle} {obj.last} {obj.name}"

class GPSDeviceSerializer(serializers.ModelSerializer):
    """Serializer para dispositivos GPS"""
    class Meta:
        model = GPSDevice
        fields = ['id', 'name', 'imei', 'route_code']

class TicketSerializer(serializers.ModelSerializer):
    """Serializer para tickets"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)
    route_name = serializers.CharField(source='route.name', read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'

class TimeSheetSerializer(serializers.ModelSerializer):
    """Serializer para horarios"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)
    
    class Meta:
        model = TimeSheet
        fields = '__all__'

class GeoFenceSerializer(serializers.ModelSerializer):
    """Serializer para cercas geográficas"""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    route_name = serializers.CharField(source='route.name', read_only=True)
    
    class Meta:
        model = GeoFence
        fields = '__all__'

class StatisticsSerializer(serializers.ModelSerializer):
    """Serializer para estadísticas"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    route_name = serializers.CharField(source='route.name', read_only=True)
    
    class Meta:
        model = Statistics
        fields = '__all__'

class SensorDataSerializer(serializers.ModelSerializer):
    """Serializer para datos de sensores"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = SensorData
        fields = '__all__'

# Serializers para reportes
class DeviceStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas de dispositivos"""
    device = GPSDeviceSerializer()
    total_locations = serializers.IntegerField()
    total_distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_speed = serializers.DecimalField(max_digits=5, decimal_places=2)
    first_location = serializers.DateTimeField(allow_null=True)
    last_location = serializers.DateTimeField(allow_null=True)
    date_range = serializers.CharField()

class RouteReportSerializer(serializers.Serializer):
    """Serializer para reportes de rutas"""
    route = RouteSerializer()
    date = serializers.DateField()
    devices_count = serializers.IntegerField()
    tickets_count = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_received = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_laps = serializers.IntegerField()
    tickets = TicketSerializer(many=True)
    timesheets = TimeSheetSerializer(many=True)

class DriverReportSerializer(serializers.Serializer):
    """Serializer para reportes de conductores"""
    driver = DriverSerializer()
    date_range = serializers.CharField()
    total_tickets = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_laps = serializers.IntegerField()
    avg_laps_per_day = serializers.DecimalField(max_digits=5, decimal_places=2)
    tickets = TicketSerializer(many=True)
    timesheets = TimeSheetSerializer(many=True)

class GeofenceEventSerializer(serializers.Serializer):
    """Serializer para eventos de cercas geográficas"""
    device = GPSDeviceSerializer()
    timestamp = serializers.DateTimeField()
    event_type = serializers.CharField()  # 'enter' o 'exit'
    location = serializers.DictField()  # Datos de ubicación

class SystemSummarySerializer(serializers.Serializer):
    """Serializer para resumen del sistema"""
    total_devices = serializers.IntegerField()
    total_drivers = serializers.IntegerField()
    total_routes = serializers.IntegerField()
    tickets_today = serializers.IntegerField()
    active_devices_today = serializers.IntegerField()
    date = serializers.DateField()

# Serializers para filtros y consultas
class DateRangeFilterSerializer(serializers.Serializer):
    """Serializer para filtros de rango de fechas"""
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    date = serializers.DateField(required=False)

class RouteFilterSerializer(serializers.Serializer):
    """Serializer para filtros de ruta"""
    route_code = serializers.IntegerField(required=False)
    date = serializers.DateField(required=False)

class DriverFilterSerializer(serializers.Serializer):
    """Serializer para filtros de conductor"""
    driver_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

class DeviceFilterSerializer(serializers.Serializer):
    """Serializer para filtros de dispositivo"""
    device_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False) 