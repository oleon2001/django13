"""
Core application configuration.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'skyguard.apps.core'
    verbose_name = 'Core Services'
    
    def ready(self):
        """Initialize core services when app is ready."""
        try:
            # Import and initialize core services
            from .services import (
                DeviceRepositoryService, LocationService, EventService,
                NotificationService, SecurityService, ConnectionService,
                LoggingService, HealthCheckService, ConfigurationService
            )
            
            # Register services with the application
            self.device_repository = DeviceRepositoryService()
            self.location_service = LocationService(self.device_repository)
            self.event_service = EventService(self.device_repository)
            self.notification_service = NotificationService()
            self.security_service = SecurityService()
            self.connection_service = ConnectionService(self.device_repository)
            self.logging_service = LoggingService()
            self.health_check_service = HealthCheckService()
            self.configuration_service = ConfigurationService()
            
        except Exception as e:
            # Log error but don't prevent app from loading
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error initializing core services: {e}") 