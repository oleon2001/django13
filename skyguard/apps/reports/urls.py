"""
Report URLs.
Migrated from legacy django14 system to modern architecture.
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard
    path('', views.report_dashboard, name='dashboard'),
    
    # Modern report views
    path('ticket/', views.ticket_report_view, name='ticket_report'),
    path('statistics/', views.statistics_report_view, name='statistics_report'),
    path('people/', views.people_count_report_view, name='people_count_report'),
    path('alarm/', views.alarm_report_view, name='alarm_report'),
    path('route/', views.route_report_view, name='route_report'),
    
    # Report executions
    path('executions/', views.report_executions_list, name='executions_list'),
    path('executions/<int:pk>/', views.report_execution_detail, name='execution_detail'),
    
    # API endpoints
    path('api/generate/', views.api_generate_report, name='api_generate_report'),
    path('api/reports/', views.api_available_reports, name='api_available_reports'),
    path('api/routes/', views.api_route_choices, name='api_route_choices'),
    
    # Legacy compatibility URLs (migrated from django14)
    path('legacy/ticket/', views.legacy_ticket_report, name='legacy_ticket_report'),
    path('legacy/people/', views.legacy_people_count_report, name='legacy_people_count_report'),
    path('legacy/alarm/', views.legacy_alarm_report, name='legacy_alarm_report'),
    
    # Legacy URL patterns for backward compatibility
    path('rutas/conteo/', views.legacy_people_count_report, name='legacy_people_count'),
    path('rutas/csv/', views.legacy_people_count_report, name='legacy_people_count_csv'),
    path('rutas/alarma/', views.legacy_alarm_report, name='legacy_alarm'),
    path('ptickets/', views.legacy_ticket_report, name='legacy_ticket_pdf'),
] 