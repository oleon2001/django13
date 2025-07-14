"""
Configuration for the tracking application.
"""
from django.apps import AppConfig


class TrackingConfig(AppConfig):
    """Configuration for the tracking application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'skyguard.apps.tracking'
    verbose_name = 'Tracking'
    
    def ready(self):
        """Initialize the tracking application."""
        try:
            import skyguard.apps.tracking.signals
        except ImportError:
            pass
