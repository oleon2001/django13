from rest_framework import serializers
from django.contrib.auth.models import User
from .models import GeoFence, GeoFenceEvent, GPSDevice


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class GPSDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSDevice
        fields = ('imei', 'name', 'position', 'speed', 'course', 'altitude', 'last_log', 'is_active')


class GeoFenceSerializer(serializers.ModelSerializer):
    """Serializer for GeoFence model."""
    owner = UserSerializer(read_only=True)
    devices = GPSDeviceSerializer(many=True, read_only=True)
    geometry_coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = GeoFence
        fields = (
            'id', 'name', 'description', 'geometry', 'geometry_coordinates',
            'owner', 'created_at', 'updated_at', 'is_active', 'notify_on_entry',
            'notify_on_exit', 'notify_owners', 'devices', 'base'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'owner')
    
    def get_geometry_coordinates(self, obj):
        """Convert geometry to coordinates array for frontend compatibility."""
        if obj.geometry:
            # Convert PolygonField to coordinates array
            coords = obj.geometry.coords[0]  # Get exterior ring
            return coords
        return []
    
    def to_representation(self, instance):
        """Custom representation for frontend compatibility."""
        data = super().to_representation(instance)
        
        # Add geometry type for frontend
        if instance.geometry:
            data['geometry'] = {
                'type': 'polygon',
                'coordinates': data['geometry_coordinates']
            }
        
        # Add color and stroke properties for frontend
        data['color'] = getattr(instance, 'color', '#3388ff')
        data['stroke_color'] = getattr(instance, 'stroke_color', '#3388ff')
        data['stroke_width'] = getattr(instance, 'stroke_width', 2)
        
        # Add notification settings
        data['notify_emails'] = getattr(instance, 'notify_emails', [])
        data['notify_sms'] = getattr(instance, 'notify_sms', [])
        data['alert_on_entry'] = getattr(instance, 'alert_on_entry', False)
        data['alert_on_exit'] = getattr(instance, 'alert_on_exit', False)
        data['notification_cooldown'] = getattr(instance, 'notification_cooldown', 300)
        
        return data


class GeoFenceEventSerializer(serializers.ModelSerializer):
    """Serializer for GeoFenceEvent model."""
    fence = GeoFenceSerializer(read_only=True)
    device = GPSDeviceSerializer(read_only=True)
    position_coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = GeoFenceEvent
        fields = (
            'id', 'fence', 'device', 'event_type', 'position', 'position_coordinates',
            'timestamp', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
    
    def get_position_coordinates(self, obj):
        """Convert position to coordinates array."""
        if obj.position:
            return [obj.position.y, obj.position.x]  # [lat, lng]
        return []
    
    def to_representation(self, instance):
        """Custom representation for frontend compatibility."""
        data = super().to_representation(instance)
        
        # Add device and geofence names for easier frontend consumption
        data['device_name'] = instance.device.name if instance.device else None
        data['geofence_name'] = instance.fence.name if instance.fence else None
        
        return data 