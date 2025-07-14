"""
Configuration management for the GPS tracking system core.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CoreConfig:
    """Configuration manager for core system."""
    
    def __init__(self):
        self._config_cache = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from settings and environment."""
        try:
            # Load from Django settings
            self._config_cache.update({
                'database': {
                    'host': getattr(settings, 'DATABASE_HOST', 'localhost'),
                    'port': getattr(settings, 'DATABASE_PORT', 5432),
                    'name': getattr(settings, 'DATABASE_NAME', 'skyguard'),
                    'user': getattr(settings, 'DATABASE_USER', 'postgres'),
                    'password': getattr(settings, 'DATABASE_PASSWORD', ''),
                    'max_connections': getattr(settings, 'DATABASE_MAX_CONNECTIONS', 100),
                    'timeout': getattr(settings, 'DATABASE_TIMEOUT', 30),
                },
                'cache': {
                    'timeout': getattr(settings, 'CACHE_TIMEOUT', 300),
                    'max_size': getattr(settings, 'CACHE_MAX_SIZE', 1000),
                },
                'security': {
                    'token_expiry': getattr(settings, 'TOKEN_EXPIRY', 3600),
                    'max_login_attempts': getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5),
                    'lockout_duration': getattr(settings, 'LOCKOUT_DURATION', 900),
                    'password_min_length': getattr(settings, 'PASSWORD_MIN_LENGTH', 8),
                    'session_timeout': getattr(settings, 'SESSION_TIMEOUT', 3600),
                },
                'notifications': {
                    'rate_limit': getattr(settings, 'NOTIFICATION_RATE_LIMIT', 60),
                    'max_recipients': getattr(settings, 'NOTIFICATION_MAX_RECIPIENTS', 100),
                    'message_max_length': getattr(settings, 'NOTIFICATION_MESSAGE_MAX_LENGTH', 160),
                    'quiet_hours_start': getattr(settings, 'NOTIFICATION_QUIET_HOURS_START', 22),
                    'quiet_hours_end': getattr(settings, 'NOTIFICATION_QUIET_HOURS_END', 8),
                },
                'tracking': {
                    'max_session_duration': getattr(settings, 'TRACKING_MAX_SESSION_DURATION', 86400),
                    'min_point_interval': getattr(settings, 'TRACKING_MIN_POINT_INTERVAL', 1),
                    'max_point_interval': getattr(settings, 'TRACKING_MAX_POINT_INTERVAL', 3600),
                    'max_session_points': getattr(settings, 'TRACKING_MAX_SESSION_POINTS', 10000),
                },
                'geofence': {
                    'max_polygon_points': getattr(settings, 'GEOFENCE_MAX_POLYGON_POINTS', 1000),
                    'min_polygon_points': getattr(settings, 'GEOFENCE_MIN_POLYGON_POINTS', 3),
                    'max_geofences_per_device': getattr(settings, 'GEOFENCE_MAX_PER_DEVICE', 50),
                },
                'analytics': {
                    'real_time_window': getattr(settings, 'ANALYTICS_REAL_TIME_WINDOW', 24),
                    'history_retention': getattr(settings, 'ANALYTICS_HISTORY_RETENTION', 90),
                    'anomaly_threshold': getattr(settings, 'ANALYTICS_ANOMALY_THRESHOLD', 0.8),
                    'efficiency_threshold': getattr(settings, 'ANALYTICS_EFFICIENCY_THRESHOLD', 0.7),
                },
                'monitoring': {
                    'health_check_interval': getattr(settings, 'MONITORING_HEALTH_CHECK_INTERVAL', 300),
                    'metrics_collection_interval': getattr(settings, 'MONITORING_METRICS_INTERVAL', 60),
                    'alert_check_interval': getattr(settings, 'MONITORING_ALERT_CHECK_INTERVAL', 30),
                    'log_rotation_interval': getattr(settings, 'MONITORING_LOG_ROTATION_INTERVAL', 86400),
                },
                'websocket': {
                    'max_connections': getattr(settings, 'WEBSOCKET_MAX_CONNECTIONS', 1000),
                    'heartbeat_interval': getattr(settings, 'WEBSOCKET_HEARTBEAT_INTERVAL', 30),
                    'connection_timeout': getattr(settings, 'WEBSOCKET_CONNECTION_TIMEOUT', 300),
                    'max_message_size': getattr(settings, 'WEBSOCKET_MAX_MESSAGE_SIZE', 1024 * 1024),
                },
                'file_upload': {
                    'max_file_size': getattr(settings, 'FILE_UPLOAD_MAX_SIZE', 10 * 1024 * 1024),
                    'allowed_extensions': getattr(settings, 'FILE_UPLOAD_ALLOWED_EXTENSIONS', 
                                                ['.csv', '.xlsx', '.json', '.xml']),
                    'upload_dir': getattr(settings, 'FILE_UPLOAD_DIR', 'uploads/'),
                    'backup_dir': getattr(settings, 'FILE_BACKUP_DIR', 'backups/'),
                    'report_dir': getattr(settings, 'FILE_REPORT_DIR', 'reports/'),
                },
                'time': {
                    'heartbeat_timeout': getattr(settings, 'TIME_HEARTBEAT_TIMEOUT', 300),
                    'session_timeout': getattr(settings, 'TIME_SESSION_TIMEOUT', 3600),
                    'cache_timeout': getattr(settings, 'TIME_CACHE_TIMEOUT', 300),
                    'backup_retention': getattr(settings, 'TIME_BACKUP_RETENTION', 30),
                    'log_retention': getattr(settings, 'TIME_LOG_RETENTION', 90),
                },
            })
            
            # Load from environment variables
            self._load_env_config()
            
            # Load from custom config file if exists
            self._load_custom_config()
            
            logger.info("Core configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading core configuration: {e}")
            raise
    
    def _load_env_config(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'DATABASE_HOST': ('database', 'host'),
            'DATABASE_PORT': ('database', 'port'),
            'DATABASE_NAME': ('database', 'name'),
            'DATABASE_USER': ('database', 'user'),
            'DATABASE_PASSWORD': ('database', 'password'),
            'CACHE_TIMEOUT': ('cache', 'timeout'),
            'TOKEN_EXPIRY': ('security', 'token_expiry'),
            'NOTIFICATION_RATE_LIMIT': ('notifications', 'rate_limit'),
            'TRACKING_MAX_SESSION_DURATION': ('tracking', 'max_session_duration'),
            'ANALYTICS_REAL_TIME_WINDOW': ('analytics', 'real_time_window'),
            'MONITORING_HEALTH_CHECK_INTERVAL': ('monitoring', 'health_check_interval'),
            'WEBSOCKET_MAX_CONNECTIONS': ('websocket', 'max_connections'),
            'FILE_UPLOAD_MAX_SIZE': ('file_upload', 'max_file_size'),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # Try to convert to appropriate type
                    if env_var in ['DATABASE_PORT', 'CACHE_TIMEOUT', 'TOKEN_EXPIRY', 
                                 'NOTIFICATION_RATE_LIMIT', 'TRACKING_MAX_SESSION_DURATION',
                                 'ANALYTICS_REAL_TIME_WINDOW', 'MONITORING_HEALTH_CHECK_INTERVAL',
                                 'WEBSOCKET_MAX_CONNECTIONS', 'FILE_UPLOAD_MAX_SIZE']:
                        value = int(value)
                    elif env_var in ['ANALYTICS_ANOMALY_THRESHOLD', 'ANALYTICS_EFFICIENCY_THRESHOLD']:
                        value = float(value)
                    
                    # Set nested config value
                    section, key = config_path
                    if section not in self._config_cache:
                        self._config_cache[section] = {}
                    self._config_cache[section][key] = value
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment variable {env_var}: {value}, error: {e}")
    
    def _load_custom_config(self):
        """Load custom configuration from file."""
        config_file = getattr(settings, 'CORE_CONFIG_FILE', None)
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    custom_config = json.load(f)
                
                # Merge custom config with existing config
                for section, values in custom_config.items():
                    if section not in self._config_cache:
                        self._config_cache[section] = {}
                    self._config_cache[section].update(values)
                
                logger.info(f"Custom configuration loaded from {config_file}")
                
            except Exception as e:
                logger.error(f"Error loading custom configuration from {config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        try:
            keys = key.split('.')
            value = self._config_cache
            
            for k in keys:
                value = value[k]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        try:
            keys = key.split('.')
            config = self._config_cache
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            # Update cache
            cache.set('core_config', self._config_cache, 300)
            
        except Exception as e:
            logger.error(f"Error setting configuration {key}: {e}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        return self._config_cache.get(section, {})
    
    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        """Update configuration section."""
        if section not in self._config_cache:
            self._config_cache[section] = {}
        
        self._config_cache[section].update(values)
        
        # Update cache
        cache.set('core_config', self._config_cache, 300)
    
    def reload(self) -> None:
        """Reload configuration."""
        self._config_cache = {}
        self._load_config()
    
    def export(self) -> Dict[str, Any]:
        """Export current configuration."""
        return self._config_cache.copy()
    
    def validate(self) -> bool:
        """Validate configuration."""
        try:
            required_sections = ['database', 'security', 'notifications', 'tracking']
            
            for section in required_sections:
                if section not in self._config_cache:
                    logger.error(f"Missing required configuration section: {section}")
                    return False
            
            # Validate specific values
            if self.get('database.max_connections', 0) <= 0:
                logger.error("Database max_connections must be positive")
                return False
            
            if self.get('security.token_expiry', 0) <= 0:
                logger.error("Token expiry must be positive")
                return False
            
            if self.get('notifications.rate_limit', 0) <= 0:
                logger.error("Notification rate limit must be positive")
                return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.get_section('database')
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.get_section('security')
    
    def get_notifications_config(self) -> Dict[str, Any]:
        """Get notifications configuration."""
        return self.get_section('notifications')
    
    def get_tracking_config(self) -> Dict[str, Any]:
        """Get tracking configuration."""
        return self.get_section('tracking')
    
    def get_analytics_config(self) -> Dict[str, Any]:
        """Get analytics configuration."""
        return self.get_section('analytics')
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.get_section('monitoring')
    
    def get_websocket_config(self) -> Dict[str, Any]:
        """Get WebSocket configuration."""
        return self.get_section('websocket')
    
    def get_file_upload_config(self) -> Dict[str, Any]:
        """Get file upload configuration."""
        return self.get_section('file_upload')


# Global configuration instance
core_config = CoreConfig()


def get_config() -> CoreConfig:
    """Get global configuration instance."""
    return core_config


def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    return core_config.get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Set configuration value."""
    core_config.set(key, value)


def reload_config() -> None:
    """Reload configuration."""
    core_config.reload()


def validate_config() -> bool:
    """Validate configuration."""
    return core_config.validate() 