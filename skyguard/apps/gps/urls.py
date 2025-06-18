"""
URL patterns for the GPS application.
"""
from django.urls import path

from . import views

app_name = 'gps'

urlpatterns = [
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
    
    # User endpoints
    path('users/me/', views.get_current_user, name='current-user'),
    
    # Real-time position endpoints
    path('positions/real-time/', views.get_real_time_positions, name='real_time_positions'),
    path('devices/<int:imei>/trail/', views.get_device_trail, name='device_trail'),
]
