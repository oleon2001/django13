"""
Service factory for GPS tracking system.
Provides centralized access to all core services.
"""

import logging
from typing import Optional, Dict, Any
from django.apps import apps

logger = logging.getLogger(__name__)


class ServiceFactory:
    """Factory for creating and managing service instances."""
    
    _instances: Dict[str, Any] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize the service factory."""
        if cls._initialized:
            return
        
        try:
            from .services import (
                DeviceRepositoryService, LocationService, EventService,
                NotificationService, SecurityService, ConnectionService,
                LoggingService, HealthCheckService, ConfigurationService
            )
            
            # Create service instances
            device_repo = DeviceRepositoryService()
            
            cls._instances = {
                'device_repository': device_repo,
                'location_service': LocationService(device_repo),
                'event_service': EventService(device_repo),
                'notification_service': NotificationService(),
                'security_service': SecurityService(),
                'connection_service': ConnectionService(device_repo),
                'logging_service': LoggingService(),
                'health_check_service': HealthCheckService(),
                'configuration_service': ConfigurationService(),
            }
            
            cls._initialized = True
            logger.info("Service factory initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing service factory: {e}")
            raise
    
    @classmethod
    def get_device_repository(cls):
        """Get device repository service."""
        cls._ensure_initialized()
        return cls._instances['device_repository']
    
    @classmethod
    def get_location_service(cls):
        """Get location service."""
        cls._ensure_initialized()
        return cls._instances['location_service']
    
    @classmethod
    def get_event_service(cls):
        """Get event service."""
        cls._ensure_initialized()
        return cls._instances['event_service']
    
    @classmethod
    def get_notification_service(cls):
        """Get notification service."""
        cls._ensure_initialized()
        return cls._instances['notification_service']
    
    @classmethod
    def get_security_service(cls):
        """Get security service."""
        cls._ensure_initialized()
        return cls._instances['security_service']
    
    @classmethod
    def get_connection_service(cls):
        """Get connection service."""
        cls._ensure_initialized()
        return cls._instances['connection_service']
    
    @classmethod
    def get_logging_service(cls):
        """Get logging service."""
        cls._ensure_initialized()
        return cls._instances['logging_service']
    
    @classmethod
    def get_health_check_service(cls):
        """Get health check service."""
        cls._ensure_initialized()
        return cls._instances['health_check_service']
    
    @classmethod
    def get_configuration_service(cls):
        """Get configuration service."""
        cls._ensure_initialized()
        return cls._instances['configuration_service']
    
    @classmethod
    def get_service(cls, service_name: str):
        """Get service by name."""
        cls._ensure_initialized()
        return cls._instances.get(service_name)
    
    @classmethod
    def _ensure_initialized(cls):
        """Ensure factory is initialized."""
        if not cls._initialized:
            cls.initialize()
    
    @classmethod
    def reset(cls):
        """Reset factory state (for testing)."""
        cls._instances = {}
        cls._initialized = False


# Convenience functions for easy access to services
def get_device_repository():
    """Get device repository service."""
    return ServiceFactory.get_device_repository()


def get_location_service():
    """Get location service."""
    return ServiceFactory.get_location_service()


def get_event_service():
    """Get event service."""
    return ServiceFactory.get_event_service()


def get_notification_service():
    """Get notification service."""
    return ServiceFactory.get_notification_service()


def get_security_service():
    """Get security service."""
    return ServiceFactory.get_security_service()


def get_connection_service():
    """Get connection service."""
    return ServiceFactory.get_connection_service()


def get_logging_service():
    """Get logging service."""
    return ServiceFactory.get_logging_service()


def get_health_check_service():
    """Get health check service."""
    return ServiceFactory.get_health_check_service()


def get_configuration_service():
    """Get configuration service."""
    return ServiceFactory.get_configuration_service()


def get_service(service_name: str):
    """Get service by name."""
    return ServiceFactory.get_service(service_name) 