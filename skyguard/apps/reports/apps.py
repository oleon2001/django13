"""
Reports app configuration.
"""
from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """Reports application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'skyguard.apps.reports'
    verbose_name = 'Reports' 