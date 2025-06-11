"""
URL patterns for the GPS application.
"""
from django.urls import path

from . import views

app_name = 'gps'

urlpatterns = [
    # Device data endpoint
    path('data/<str:protocol>/', views.device_data, name='device_data'),
    
    # Device command endpoint
    path('devices/<int:imei>/command/', views.DeviceCommandView.as_view(), name='device_command'),
    
    # Device history endpoint
    path('devices/<int:imei>/history/', views.DeviceHistoryView.as_view(), name='device_history'),
    
    # Device events endpoint
    path('devices/<int:imei>/events/', views.DeviceEventsView.as_view(), name='device_events'),
    
    path('users/me/', views.get_current_user, name='current-user'),
]
