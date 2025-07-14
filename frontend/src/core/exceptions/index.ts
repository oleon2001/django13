// Core exceptions migrated from Django backend
// Based on skyguard/apps/core/exceptions.py

export class CoreException extends Error {
  public code?: string;
  public details?: Record<string, any>;

  constructor(message: string, code?: string, details?: Record<string, any>) {
    super(message);
    this.name = 'CoreException';
    this.code = code;
    this.details = details;
  }
}

export class DeviceNotFoundException extends CoreException {
  constructor(imei: number, message?: string) {
    super(message || `Device with IMEI ${imei} not found`, 'DEVICE_NOT_FOUND', { imei });
    this.name = 'DeviceNotFoundException';
  }
}

export class InvalidIMEIException extends CoreException {
  constructor(imei: string, message?: string) {
    super(message || `Invalid IMEI format: ${imei}`, 'INVALID_IMEI', { imei });
    this.name = 'InvalidIMEIException';
  }
}

export class InvalidCoordinatesException extends CoreException {
  constructor(latitude: number, longitude: number, message?: string) {
    super(
      message || `Invalid coordinates: lat=${latitude}, lon=${longitude}`,
      'INVALID_COORDINATES',
      { latitude, longitude }
    );
    this.name = 'InvalidCoordinatesException';
  }
}

export class DeviceOfflineException extends CoreException {
  constructor(imei: number, message?: string) {
    super(message || `Device ${imei} is offline`, 'DEVICE_OFFLINE', { imei });
    this.name = 'DeviceOfflineException';
  }
}

export class PermissionDeniedException extends CoreException {
  constructor(action: string, user?: string, message?: string) {
    super(
      message || `Permission denied for action: ${action}`,
      'PERMISSION_DENIED',
      { action, user }
    );
    this.name = 'PermissionDeniedException';
  }
}

export class InvalidTokenException extends CoreException {
  constructor(token?: string, message?: string) {
    super(message || 'Invalid authentication token', 'INVALID_TOKEN', { token });
    this.name = 'InvalidTokenException';
  }
}

export class RateLimitExceededException extends CoreException {
  constructor(limit: number, window: number, message?: string) {
    super(
      message || `Rate limit exceeded: ${limit} requests per ${window} seconds`,
      'RATE_LIMIT_EXCEEDED',
      { limit, window }
    );
    this.name = 'RateLimitExceededException';
  }
}

export class ServiceUnavailableException extends CoreException {
  constructor(service: string, message?: string) {
    super(message || `Service ${service} is unavailable`, 'SERVICE_UNAVAILABLE', { service });
    this.name = 'ServiceUnavailableException';
  }
}

export class InvalidCommandException extends CoreException {
  constructor(command: string, message?: string) {
    super(message || `Invalid command: ${command}`, 'INVALID_COMMAND', { command });
    this.name = 'InvalidCommandException';
  }
}

export class CommandFailedException extends CoreException {
  constructor(command: string, error?: string, message?: string) {
    super(
      message || `Command ${command} failed: ${error}`,
      'COMMAND_FAILED',
      { command, error }
    );
    this.name = 'CommandFailedException';
  }
}

export class ConfigurationException extends CoreException {
  constructor(configKey: string, message?: string) {
    super(message || `Configuration error for key: ${configKey}`, 'CONFIGURATION_ERROR', { configKey });
    this.name = 'ConfigurationException';
  }
}

export class DatabaseException extends CoreException {
  constructor(operation: string, table?: string, message?: string) {
    super(
      message || `Database error during ${operation}`,
      'DATABASE_ERROR',
      { operation, table }
    );
    this.name = 'DatabaseException';
  }
}

export class CacheException extends CoreException {
  constructor(operation: string, key?: string, message?: string) {
    super(
      message || `Cache error during ${operation}`,
      'CACHE_ERROR',
      { operation, key }
    );
    this.name = 'CacheException';
  }
}

export class NotificationException extends CoreException {
  constructor(channel: string, recipient?: string, message?: string) {
    super(
      message || `Notification error for channel: ${channel}`,
      'NOTIFICATION_ERROR',
      { channel, recipient }
    );
    this.name = 'NotificationException';
  }
}

export class ProtocolException extends CoreException {
  constructor(protocol: string, operation: string, message?: string) {
    super(
      message || `Protocol error for ${protocol} during ${operation}`,
      'PROTOCOL_ERROR',
      { protocol, operation }
    );
    this.name = 'ProtocolException';
  }
}

export class SecurityException extends CoreException {
  constructor(checkType: string, details?: string, message?: string) {
    super(
      message || `Security check failed: ${checkType}`,
      'SECURITY_ERROR',
      { checkType, details }
    );
    this.name = 'SecurityException';
  }
}

export class ValidationException extends CoreException {
  constructor(field: string, value: any, message?: string) {
    super(
      message || `Validation error for field: ${field}`,
      'VALIDATION_ERROR',
      { field, value }
    );
    this.name = 'ValidationException';
  }
}

export class TimeoutException extends CoreException {
  constructor(operation: string, timeout: number, message?: string) {
    super(
      message || `Operation ${operation} timed out after ${timeout}ms`,
      'TIMEOUT_ERROR',
      { operation, timeout }
    );
    this.name = 'TimeoutException';
  }
}

export class ConnectionException extends CoreException {
  constructor(host: string, port: number, message?: string) {
    super(
      message || `Connection failed to ${host}:${port}`,
      'CONNECTION_ERROR',
      { host, port }
    );
    this.name = 'ConnectionException';
  }
}

export class FileException extends CoreException {
  constructor(operation: string, filePath: string, message?: string) {
    super(
      message || `File error during ${operation}: ${filePath}`,
      'FILE_ERROR',
      { operation, filePath }
    );
    this.name = 'FileException';
  }
}

export class BackupException extends CoreException {
  constructor(backupType: string, message?: string) {
    super(
      message || `Backup error for type: ${backupType}`,
      'BACKUP_ERROR',
      { backupType }
    );
    this.name = 'BackupException';
  }
}

export class ReportException extends CoreException {
  constructor(reportType: string, message?: string) {
    super(
      message || `Report error for type: ${reportType}`,
      'REPORT_ERROR',
      { reportType }
    );
    this.name = 'ReportException';
  }
}

export class MaintenanceException extends CoreException {
  constructor(maintenanceType: string, deviceId?: number, message?: string) {
    super(
      message || `Maintenance error for type: ${maintenanceType}`,
      'MAINTENANCE_ERROR',
      { maintenanceType, deviceId }
    );
    this.name = 'MaintenanceException';
  }
}

export class HealthCheckException extends CoreException {
  constructor(component: string, status: string, message?: string) {
    super(
      message || `Health check failed for ${component}: ${status}`,
      'HEALTH_CHECK_ERROR',
      { component, status }
    );
    this.name = 'HealthCheckException';
  }
}

export class AnalyticsException extends CoreException {
  constructor(operation: string, metric?: string, message?: string) {
    super(
      message || `Analytics error during ${operation}`,
      'ANALYTICS_ERROR',
      { operation, metric }
    );
    this.name = 'AnalyticsException';
  }
}

export class GeofenceException extends CoreException {
  constructor(operation: string, geofenceId?: number, message?: string) {
    super(
      message || `Geofence error during ${operation}`,
      'GEOFENCE_ERROR',
      { operation, geofenceId }
    );
    this.name = 'GeofenceException';
  }
}

export class AlertException extends CoreException {
  constructor(alertType: string, deviceId?: number, message?: string) {
    super(
      message || `Alert error for type: ${alertType}`,
      'ALERT_ERROR',
      { alertType, deviceId }
    );
    this.name = 'AlertException';
  }
}

export class TrackingException extends CoreException {
  constructor(operation: string, sessionId?: string, message?: string) {
    super(
      message || `Tracking error during ${operation}`,
      'TRACKING_ERROR',
      { operation, sessionId }
    );
    this.name = 'TrackingException';
  }
}

export class StatisticsException extends CoreException {
  constructor(operation: string, period?: string, message?: string) {
    super(
      message || `Statistics error during ${operation}`,
      'STATISTICS_ERROR',
      { operation, period }
    );
    this.name = 'StatisticsException';
  }
}

export class LoggingException extends CoreException {
  constructor(operation: string, level?: string, message?: string) {
    super(
      message || `Logging error during ${operation}`,
      'LOGGING_ERROR',
      { operation, level }
    );
    this.name = 'LoggingException';
  }
}

// Utility function to create exceptions from API responses
export function createExceptionFromResponse(response: any): CoreException {
  const { code, details, message } = response;
  
  switch (code) {
    case 'DEVICE_NOT_FOUND':
      return new DeviceNotFoundException(details?.imei, message);
    case 'INVALID_IMEI':
      return new InvalidIMEIException(details?.imei, message);
    case 'INVALID_COORDINATES':
      return new InvalidCoordinatesException(details?.latitude, details?.longitude, message);
    case 'DEVICE_OFFLINE':
      return new DeviceOfflineException(details?.imei, message);
    case 'PERMISSION_DENIED':
      return new PermissionDeniedException(details?.action, details?.user, message);
    case 'INVALID_TOKEN':
      return new InvalidTokenException(details?.token, message);
    case 'RATE_LIMIT_EXCEEDED':
      return new RateLimitExceededException(details?.limit, details?.window, message);
    case 'SERVICE_UNAVAILABLE':
      return new ServiceUnavailableException(details?.service, message);
    case 'INVALID_COMMAND':
      return new InvalidCommandException(details?.command, message);
    case 'COMMAND_FAILED':
      return new CommandFailedException(details?.command, details?.error, message);
    case 'CONFIGURATION_ERROR':
      return new ConfigurationException(details?.configKey, message);
    case 'DATABASE_ERROR':
      return new DatabaseException(details?.operation, details?.table, message);
    case 'CACHE_ERROR':
      return new CacheException(details?.operation, details?.key, message);
    case 'NOTIFICATION_ERROR':
      return new NotificationException(details?.channel, details?.recipient, message);
    case 'PROTOCOL_ERROR':
      return new ProtocolException(details?.protocol, details?.operation, message);
    case 'SECURITY_ERROR':
      return new SecurityException(details?.checkType, details?.details, message);
    case 'VALIDATION_ERROR':
      return new ValidationException(details?.field, details?.value, message);
    case 'TIMEOUT_ERROR':
      return new TimeoutException(details?.operation, details?.timeout, message);
    case 'CONNECTION_ERROR':
      return new ConnectionException(details?.host, details?.port, message);
    case 'FILE_ERROR':
      return new FileException(details?.operation, details?.filePath, message);
    case 'BACKUP_ERROR':
      return new BackupException(details?.backupType, message);
    case 'REPORT_ERROR':
      return new ReportException(details?.reportType, message);
    case 'MAINTENANCE_ERROR':
      return new MaintenanceException(details?.maintenanceType, details?.deviceId, message);
    case 'HEALTH_CHECK_ERROR':
      return new HealthCheckException(details?.component, details?.status, message);
    case 'ANALYTICS_ERROR':
      return new AnalyticsException(details?.operation, details?.metric, message);
    case 'GEOFENCE_ERROR':
      return new GeofenceException(details?.operation, details?.geofenceId, message);
    case 'ALERT_ERROR':
      return new AlertException(details?.alertType, details?.deviceId, message);
    case 'TRACKING_ERROR':
      return new TrackingException(details?.operation, details?.sessionId, message);
    case 'STATISTICS_ERROR':
      return new StatisticsException(details?.operation, details?.period, message);
    case 'LOGGING_ERROR':
      return new LoggingException(details?.operation, details?.level, message);
    default:
      return new CoreException(message || 'Unknown error occurred', code, details);
  }
} 