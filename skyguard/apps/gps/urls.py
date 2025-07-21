"""
URL patterns for the GPS application.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views, vehicle_views, driver_views, geofence_views
from .api.geofence_views import GeofenceViewSet, GeofenceEventViewSet, DeviceGeofenceAnalyticsViewSet

app_name = 'gps'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'geofences', GeofenceViewSet, basename='geofence')
router.register(r'geofence-events', GeofenceEventViewSet, basename='geofence-event')
router.register(r'device-analytics', DeviceGeofenceAnalyticsViewSet, basename='device-analytics')

urlpatterns = [
    # Include ViewSet URLs
    path('', include(router.urls)),
    
    # Device CRUD endpoints
    path('devices/', views.list_devices, name='list_devices'),  # GET for list, POST for create
    path('devices/<int:imei>/', views.update_device, name='update_device'),  # PATCH for update, DELETE for delete
    path('devices/<int:imei>/test-connection/', views.test_device_connection, name='test_device_connection'),
    
    # Location and event processing endpoints
    path('location/', views.process_location, name='process_location'),
    path('event/', views.process_event, name='process_event'),
    
    # Device history endpoint
    path('history/<int:imei>/', views.get_device_history, name='get_device_history'),
    
    # Device command endpoint
    path('devices/<int:imei>/command/', views.DeviceCommandView.as_view(), name='device_command'),
    
    # Device history endpoint (class-based view)
    path('devices/<int:imei>/history/', views.DeviceHistoryView.as_view(), name='device_history'),
    
    # Device events endpoint
    path('devices/<int:imei>/events/', views.DeviceEventsView.as_view(), name='device_events'),
    
    # Device connection endpoints
    path('devices/<int:imei>/connections/', views.device_connections, name='device_connections'),
    path('devices/<int:imei>/connection-stats/', views.device_connection_stats, name='device_connection_stats'),
    path('devices/<int:imei>/status/', views.device_current_status, name='device_current_status'),
    
    # Session management endpoints
    path('sessions/active/', views.active_sessions, name='active_sessions'),
    path('sessions/cleanup/', views.cleanup_sessions, name='cleanup_sessions'),
    
    # Device status management
    path('devices/check-status/', views.check_all_devices_status, name='check_all_devices_status'),
    path('devices/activity-status/', views.get_devices_activity_status, name='get_devices_activity_status'),
    
    # User endpoints
    path('users/me/', views.get_current_user, name='current-user'),
    
    # Real-time position endpoints
    path('positions/real-time/', views.get_real_time_positions, name='real_time_positions'),
    path('devices/<int:imei>/trail/', views.get_device_trail, name='device_trail'),
    
    # Vehicle endpoints
    path('vehicles/', vehicle_views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:vehicle_id>/', vehicle_views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/available-devices/', vehicle_views.available_gps_devices, name='available_gps_devices'),
    path('vehicles/available-drivers/', vehicle_views.available_drivers, name='available_drivers_for_vehicles'),
    path('vehicles/<int:vehicle_id>/assign-device/', vehicle_views.assign_device_to_vehicle, name='assign_device_to_vehicle'),
    path('vehicles/<int:vehicle_id>/assign-driver/', vehicle_views.assign_driver_to_vehicle, name='assign_driver_to_vehicle'),
    
    # Driver endpoints
    path('drivers/', driver_views.driver_list, name='driver_list'),
    path('drivers/<int:driver_id>/', driver_views.driver_detail, name='driver_detail'),
    path('drivers/available-vehicles/', driver_views.available_vehicles, name='available_vehicles'),
    path('drivers/<int:driver_id>/assign-vehicle/', driver_views.assign_vehicle_to_driver, name='assign_vehicle_to_driver'),
    
    # Legacy geofence endpoints (mantener compatibilidad)
    path('legacy-geofences/', geofence_views.geofence_list, name='legacy_geofence_list'),
    path('legacy-geofences/<int:geofence_id>/', geofence_views.geofence_detail, name='legacy_geofence_detail'),
    path('legacy-geofences/<int:geofence_id>/events/', geofence_views.geofence_events, name='legacy_geofence_events'),
    path('legacy-geofences/<int:geofence_id>/check-point/', geofence_views.check_point_in_geofence, name='legacy_check_point_in_geofence'),
    path('legacy-geofences/<int:geofence_id>/assign-devices/', geofence_views.assign_devices_to_geofence, name='legacy_assign_devices_to_geofence'),
    path('legacy-geofences/<int:geofence_id>/devices/', geofence_views.get_geofence_devices, name='legacy_get_geofence_devices'),
    path('legacy-geofences/stats/', geofence_views.geofence_stats, name='legacy_geofence_stats'),
]
