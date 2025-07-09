"""
URLs for the reports application.
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Report types and generation
    path('available/', views.available_reports, name='available_reports'),
    path('generate/', views.generate_report, name='generate_report'),
    path('device/<int:device_id>/', views.device_reports, name='device_reports'),
    
    # Templates management
    path('templates/', views.report_templates, name='report_templates'),
    path('templates/create/', views.create_report_template, name='create_report_template'),
    path('templates/<int:template_id>/delete/', views.delete_report_template, name='delete_report_template'),
    
    # Executions and statistics
    path('executions/', views.report_executions, name='report_executions'),
    path('statistics/', views.report_statistics, name='report_statistics'),
    
    # Download reports
    path('download/<int:execution_id>/', views.ReportDownloadView.as_view(), name='download_report'),
] 