"""
Apps configuration for the GPS application.
"""
from django.apps import AppConfig


class GPSConfig(AppConfig):
    """Configuration for the GPS application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'skyguard.apps.gps'
    verbose_name = 'GPS Tracking'
    
    def ready(self):
        """Initialize the application."""
        # Import signal handlers
        from . import signals
