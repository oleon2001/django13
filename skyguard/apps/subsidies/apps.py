"""
Subsidies app configuration.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubsidiesConfig(AppConfig):
    """Configuration for the subsidies app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'skyguard.apps.subsidies'
    verbose_name = _('Subsidies')
    
    def ready(self):
        """Initialize the app when ready."""
        try:
            import skyguard.apps.subsidies.signals  # noqa
        except ImportError:
            pass 