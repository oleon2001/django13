"""
URLs for the tracking application.
"""
from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.tracking_dashboard, name='dashboard'),
    
    # Tracking sessions
    path('sessions/start/', views.start_tracking, name='start_tracking'),
    path('sessions/stop/', views.stop_tracking, name='stop_tracking'),
    path('sessions/pause/', views.pause_tracking, name='pause_tracking'),
    path('sessions/resume/', views.resume_tracking, name='resume_tracking'),
    path('sessions/', views.get_user_sessions, name='user_sessions'),
    path('sessions/<str:session_id>/points/', views.get_session_points, name='session_points'),
    path('sessions/<str:session_id>/events/', views.get_session_events, name='session_events'),
    path('devices/<int:device_imei>/sessions/', views.get_device_sessions, name='device_sessions'),
    
    # Tracking points
    path('points/add/', views.add_tracking_point, name='add_tracking_point'),
    
    # Alerts
    path('alerts/', views.get_user_alerts, name='user_alerts'),
    path('alerts/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
    path('devices/<int:device_imei>/alerts/', views.get_device_alerts, name='device_alerts'),
    
    # Geofences
    path('geofences/', views.get_user_geofences, name='user_geofences'),
    path('devices/<int:device_imei>/geofences/', views.check_device_geofences, name='device_geofences'),
]
