"""
Subsidies URLs for the GPS system.
Migrated from legacy django14 system to modern architecture.
"""
from django.urls import path, include
from django.views.generic import RedirectView

from . import views

app_name = 'subsidies'

urlpatterns = [
    # Dashboard
    path('', views.subsidies_dashboard, name='dashboard'),
    
    # Drivers
    path('drivers/', views.drivers_list, name='drivers_list'),
    path('drivers/create/', views.driver_create, name='driver_create'),
    path('drivers/<int:driver_id>/', views.driver_detail, name='driver_detail'),
    path('drivers/<int:driver_id>/edit/', views.driver_edit, name='driver_edit'),
    
    # Daily Logs
    path('logs/', views.daily_logs_list, name='daily_logs_list'),
    path('logs/create/', views.daily_log_create, name='daily_log_create'),
    
    # Time Sheets
    path('timesheet/capture/', views.timesheet_capture, name='timesheet_capture'),
    path('timesheet/report/', views.timesheet_report, name='timesheet_report'),
    
    # Reports
    path('reports/daily/', views.daily_report, name='daily_report'),
    
    # Cash Receipts
    path('receipts/', views.cash_receipts_list, name='cash_receipts_list'),
    path('receipts/create/', views.cash_receipt_create, name='cash_receipt_create'),
    
    # Routes
    path('routes/', views.routes_list, name='routes_list'),
    path('routes/<str:route_code>/', views.route_detail, name='route_detail'),
    
    # Economic Mappings
    path('economic-mappings/', views.economic_mappings_list, name='economic_mappings_list'),
    path('economic-mappings/create/', views.economic_mapping_create, name='economic_mapping_create'),
    
    # API endpoints
    path('api/routes/<str:route_code>/units/', views.api_get_route_units, name='api_route_units'),
    path('api/timesheet/<str:date_str>/<str:unit_name>/', views.api_get_timesheet_data, name='api_timesheet_data'),
    path('api/economic-number/<str:unit_name>/', views.api_get_economic_number, name='api_economic_number'),
] 