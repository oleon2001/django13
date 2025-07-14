"""
Custom exceptions for the GPS tracking system core.
"""

from typing import Optional, Dict, Any


class CoreException(Exception):
    """Base exception for core system."""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class DeviceNotFoundException(CoreException):
    """Raised when a device is not found."""
    
    def __init__(self, imei: int, message: str = None):
        if message is None:
            message = f"Device with IMEI {imei} not found"
        super().__init__(message, "DEVICE_NOT_FOUND", {"imei": imei})


class InvalidIMEIException(CoreException):
    """Raised when IMEI format is invalid."""
    
    def __init__(self, imei: str, message: str = None):
        if message is None:
            message = f"Invalid IMEI format: {imei}"
        super().__init__(message, "INVALID_IMEI", {"imei": imei})


class InvalidCoordinatesException(CoreException):
    """Raised when GPS coordinates are invalid."""
    
    def __init__(self, latitude: float, longitude: float, message: str = None):
        if message is None:
            message = f"Invalid coordinates: {latitude}, {longitude}"
        super().__init__(message, "INVALID_COORDINATES", {
            "latitude": latitude,
            "longitude": longitude
        })


class DeviceOfflineException(CoreException):
    """Raised when device is offline."""
    
    def __init__(self, imei: int, message: str = None):
        if message is None:
            message = f"Device {imei} is offline"
        super().__init__(message, "DEVICE_OFFLINE", {"imei": imei})


class PermissionDeniedException(CoreException):
    """Raised when permission is denied."""
    
    def __init__(self, action: str, user: str = None, message: str = None):
        if message is None:
            message = f"Permission denied for action: {action}"
        super().__init__(message, "PERMISSION_DENIED", {
            "action": action,
            "user": user
        })


class InvalidTokenException(CoreException):
    """Raised when authentication token is invalid."""
    
    def __init__(self, token: str = None, message: str = None):
        if message is None:
            message = "Invalid authentication token"
        super().__init__(message, "INVALID_TOKEN", {"token": token})


class RateLimitExceededException(CoreException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, limit: int, window: int, message: str = None):
        if message is None:
            message = f"Rate limit exceeded: {limit} requests per {window} seconds"
        super().__init__(message, "RATE_LIMIT_EXCEEDED", {
            "limit": limit,
            "window": window
        })


class ServiceUnavailableException(CoreException):
    """Raised when service is temporarily unavailable."""
    
    def __init__(self, service: str, message: str = None):
        if message is None:
            message = f"Service {service} is temporarily unavailable"
        super().__init__(message, "SERVICE_UNAVAILABLE", {"service": service})


class InvalidCommandException(CoreException):
    """Raised when command is invalid."""
    
    def __init__(self, command: str, message: str = None):
        if message is None:
            message = f"Invalid command: {command}"
        super().__init__(message, "INVALID_COMMAND", {"command": command})


class CommandFailedException(CoreException):
    """Raised when command execution fails."""
    
    def __init__(self, command: str, error: str = None, message: str = None):
        if message is None:
            message = f"Command {command} failed"
        super().__init__(message, "COMMAND_FAILED", {
            "command": command,
            "error": error
        })


class ConfigurationException(CoreException):
    """Raised when configuration is invalid."""
    
    def __init__(self, config_key: str, message: str = None):
        if message is None:
            message = f"Invalid configuration for key: {config_key}"
        super().__init__(message, "CONFIGURATION_ERROR", {"config_key": config_key})


class DatabaseException(CoreException):
    """Raised when database operation fails."""
    
    def __init__(self, operation: str, table: str = None, message: str = None):
        if message is None:
            message = f"Database operation failed: {operation}"
        super().__init__(message, "DATABASE_ERROR", {
            "operation": operation,
            "table": table
        })


class CacheException(CoreException):
    """Raised when cache operation fails."""
    
    def __init__(self, operation: str, key: str = None, message: str = None):
        if message is None:
            message = f"Cache operation failed: {operation}"
        super().__init__(message, "CACHE_ERROR", {
            "operation": operation,
            "key": key
        })


class NotificationException(CoreException):
    """Raised when notification fails."""
    
    def __init__(self, channel: str, recipient: str = None, message: str = None):
        if message is None:
            message = f"Notification failed for channel: {channel}"
        super().__init__(message, "NOTIFICATION_ERROR", {
            "channel": channel,
            "recipient": recipient
        })


class ProtocolException(CoreException):
    """Raised when protocol operation fails."""
    
    def __init__(self, protocol: str, operation: str, message: str = None):
        if message is None:
            message = f"Protocol {protocol} operation failed: {operation}"
        super().__init__(message, "PROTOCOL_ERROR", {
            "protocol": protocol,
            "operation": operation
        })


class SecurityException(CoreException):
    """Raised when security check fails."""
    
    def __init__(self, check_type: str, details: str = None, message: str = None):
        if message is None:
            message = f"Security check failed: {check_type}"
        super().__init__(message, "SECURITY_ERROR", {
            "check_type": check_type,
            "details": details
        })


class ValidationException(CoreException):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, value: Any, message: str = None):
        if message is None:
            message = f"Validation failed for field {field}: {value}"
        super().__init__(message, "VALIDATION_ERROR", {
            "field": field,
            "value": value
        })


class TimeoutException(CoreException):
    """Raised when operation times out."""
    
    def __init__(self, operation: str, timeout: int, message: str = None):
        if message is None:
            message = f"Operation {operation} timed out after {timeout} seconds"
        super().__init__(message, "TIMEOUT_ERROR", {
            "operation": operation,
            "timeout": timeout
        })


class ConnectionException(CoreException):
    """Raised when connection fails."""
    
    def __init__(self, host: str, port: int, message: str = None):
        if message is None:
            message = f"Connection failed to {host}:{port}"
        super().__init__(message, "CONNECTION_ERROR", {
            "host": host,
            "port": port
        })


class FileException(CoreException):
    """Raised when file operation fails."""
    
    def __init__(self, operation: str, file_path: str, message: str = None):
        if message is None:
            message = f"File operation failed: {operation} on {file_path}"
        super().__init__(message, "FILE_ERROR", {
            "operation": operation,
            "file_path": file_path
        })


class BackupException(CoreException):
    """Raised when backup operation fails."""
    
    def __init__(self, backup_type: str, message: str = None):
        if message is None:
            message = f"Backup operation failed: {backup_type}"
        super().__init__(message, "BACKUP_ERROR", {"backup_type": backup_type})


class ReportException(CoreException):
    """Raised when report generation fails."""
    
    def __init__(self, report_type: str, message: str = None):
        if message is None:
            message = f"Report generation failed: {report_type}"
        super().__init__(message, "REPORT_ERROR", {"report_type": report_type})


class MaintenanceException(CoreException):
    """Raised when maintenance operation fails."""
    
    def __init__(self, maintenance_type: str, device_id: int = None, message: str = None):
        if message is None:
            message = f"Maintenance operation failed: {maintenance_type}"
        super().__init__(message, "MAINTENANCE_ERROR", {
            "maintenance_type": maintenance_type,
            "device_id": device_id
        })


class HealthCheckException(CoreException):
    """Raised when health check fails."""
    
    def __init__(self, component: str, status: str, message: str = None):
        if message is None:
            message = f"Health check failed for {component}: {status}"
        super().__init__(message, "HEALTH_CHECK_ERROR", {
            "component": component,
            "status": status
        })


class AnalyticsException(CoreException):
    """Raised when analytics operation fails."""
    
    def __init__(self, operation: str, metric: str = None, message: str = None):
        if message is None:
            message = f"Analytics operation failed: {operation}"
        super().__init__(message, "ANALYTICS_ERROR", {
            "operation": operation,
            "metric": metric
        })


class GeofenceException(CoreException):
    """Raised when geofence operation fails."""
    
    def __init__(self, operation: str, geofence_id: int = None, message: str = None):
        if message is None:
            message = f"Geofence operation failed: {operation}"
        super().__init__(message, "GEOFENCE_ERROR", {
            "operation": operation,
            "geofence_id": geofence_id
        })


class AlertException(CoreException):
    """Raised when alert operation fails."""
    
    def __init__(self, alert_type: str, device_id: int = None, message: str = None):
        if message is None:
            message = f"Alert operation failed: {alert_type}"
        super().__init__(message, "ALERT_ERROR", {
            "alert_type": alert_type,
            "device_id": device_id
        })


class TrackingException(CoreException):
    """Raised when tracking operation fails."""
    
    def __init__(self, operation: str, session_id: str = None, message: str = None):
        if message is None:
            message = f"Tracking operation failed: {operation}"
        super().__init__(message, "TRACKING_ERROR", {
            "operation": operation,
            "session_id": session_id
        })


class StatisticsException(CoreException):
    """Raised when statistics operation fails."""
    
    def __init__(self, operation: str, period: str = None, message: str = None):
        if message is None:
            message = f"Statistics operation failed: {operation}"
        super().__init__(message, "STATISTICS_ERROR", {
            "operation": operation,
            "period": period
        })


class LoggingException(CoreException):
    """Raised when logging operation fails."""
    
    def __init__(self, operation: str, level: str = None, message: str = None):
        if message is None:
            message = f"Logging operation failed: {operation}"
        super().__init__(message, "LOGGING_ERROR", {
            "operation": operation,
            "level": level
        }) 