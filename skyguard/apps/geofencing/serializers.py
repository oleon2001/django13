"""
Serializers para el sistema de geofencing SkyGuard
"""
from rest_framework import serializers
from .models import GeoFence
from skyguard.apps.gps.models import GPSDevice
from skyguard.apps.reports.models import Route


class GeoFenceSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo GeoFence
    """
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    route_name = serializers.CharField(source='route.name', read_only=True)
    
    class Meta:
        model = GeoFence
        fields = [
            'id', 'name', 'polygon', 'owner', 'owner_name',
            'route', 'route_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class GeofenceEventSerializer(serializers.Serializer):
    """
    Serializer para eventos de geofencing
    """
    id = serializers.IntegerField()
    device_id = serializers.IntegerField()
    device_name = serializers.CharField()
    geofence_id = serializers.IntegerField()
    geofence_name = serializers.CharField()
    event_type = serializers.CharField()  # 'entry' o 'exit'
    timestamp = serializers.DateTimeField()
    location = serializers.DictField()


class GeofenceStatisticsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de geofencing
    """
    geofence_id = serializers.IntegerField()
    geofence_name = serializers.CharField()
    total_entries = serializers.IntegerField()
    total_exits = serializers.IntegerField()
    unique_devices = serializers.IntegerField()
    average_duration = serializers.FloatField()  # en minutos
    date_range = serializers.DictField()


class DeviceLocationSerializer(serializers.Serializer):
    """
    Serializer para ubicaciones de dispositivos
    """
    device_id = serializers.IntegerField()
    device_name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    speed = serializers.FloatField()
    heading = serializers.FloatField()


class GeofenceMonitoringSerializer(serializers.Serializer):
    """
    Serializer para monitoreo de geofences
    """
    geofence_id = serializers.IntegerField()
    geofence_name = serializers.CharField()
    devices_inside = serializers.ListField(
        child=DeviceLocationSerializer()
    )
    total_devices_inside = serializers.IntegerField()
    last_updated = serializers.DateTimeField()


class GeofenceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear geofences
    """
    class Meta:
        model = GeoFence
        fields = ['name', 'polygon', 'owner', 'route']
        
    def validate_polygon(self, value):
        """
        Validar que el polígono sea válido
        """
        if not value:
            raise serializers.ValidationError("El polígono es requerido")
        
        # Aquí se pueden agregar validaciones adicionales del polígono
        # Por ejemplo, verificar que tenga al menos 3 puntos
        
        return value


class GeofenceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar geofences
    """
    class Meta:
        model = GeoFence
        fields = ['name', 'polygon', 'route']
        
    def validate_polygon(self, value):
        """
        Validar que el polígono sea válido
        """
        if not value:
            raise serializers.ValidationError("El polígono es requerido")
        
        return value


class GeofenceFilterSerializer(serializers.Serializer):
    """
    Serializer para filtrar geofences
    """
    owner_id = serializers.IntegerField(required=False)
    route_id = serializers.IntegerField(required=False)
    active_only = serializers.BooleanField(default=True)
    search = serializers.CharField(required=False) 