/**
 * Core exceptions for the GPS tracking system.
 * Migrated from backend Django exceptions to TypeScript.
 */

export class CoreException extends Error {
  public code: string;
  public details: Record<string, any>;

  constructor(message: string, code: string = 'UNKNOWN_ERROR', details: Record<string, any> = {}) {
    super(message);
    this.name = 'CoreException';
    this.code = code;
    this.details = details;
  }
}

export class DeviceNotFoundException extends CoreException {
  constructor(public imei: string, message?: string) {
    super(message || `Device with IMEI ${imei} not found`, 'DEVICE_NOT_FOUND');
    this.name = 'DeviceNotFoundException';
  }
}

export class InvalidIMEIException extends CoreException {
  constructor(public imei: string, message?: string) {
    super(message || `Invalid IMEI format: ${imei}`, 'INVALID_IMEI');
    this.name = 'InvalidIMEIException';
  }
}

export class InvalidCoordinatesException extends CoreException {
  constructor(public latitude: number, public longitude: number, message?: string) {
    super(message || `Invalid coordinates: ${latitude}, ${longitude}`, 'INVALID_COORDINATES');
    this.name = 'InvalidCoordinatesException';
  }
}

export class DeviceOfflineException extends CoreException {
  constructor(public imei: string, message?: string) {
    super(message || `Device ${imei} is offline`, 'DEVICE_OFFLINE');
    this.name = 'DeviceOfflineException';
  }
}

export class PermissionDeniedException extends CoreException {
  constructor(public action: string, public user?: string, message?: string) {
    super(message || `Permission denied for action: ${action}`, 'PERMISSION_DENIED');
    this.name = 'PermissionDeniedException';
  }
}

export class InvalidTokenException extends CoreException {
  constructor(public token?: string, message?: string) {
    super(message || 'Invalid or expired token', 'INVALID_TOKEN');
    this.name = 'InvalidTokenException';
  }
}

export class RateLimitExceededException extends CoreException {
  constructor(public limit: number, public window: number, message?: string) {
    super(message || `Rate limit exceeded: ${limit} requests per ${window} seconds`, 'RATE_LIMIT_EXCEEDED');
    this.name = 'RateLimitExceededException';
  }
}

export class ServiceUnavailableException extends CoreException {
  constructor(public service: string, message?: string) {
    super(message || `Service ${service} is unavailable`, 'SERVICE_UNAVAILABLE');
    this.name = 'ServiceUnavailableException';
  }
}

export class InvalidCommandException extends CoreException {
  constructor(public command: string, message?: string) {
    super(message || `Invalid command: ${command}`, 'INVALID_COMMAND');
    this.name = 'InvalidCommandException';
  }
}

export class CommandFailedException extends CoreException {
  constructor(public command: string, public error?: string, message?: string) {
    super(message || `Command ${command} failed: ${error}`, 'COMMAND_FAILED');
    this.name = 'CommandFailedException';
  }
}

export class ConfigurationException extends CoreException {
  constructor(public configKey: string, message?: string) {
    super(message || `Configuration error for key: ${configKey}`, 'CONFIGURATION_ERROR');
    this.name = 'ConfigurationException';
  }
}

export class DatabaseException extends CoreException {
  constructor(public operation: string, public table?: string, message?: string) {
    super(message || `Database error during ${operation}`, 'DATABASE_ERROR');
    this.name = 'DatabaseException';
  }
}

export class CacheException extends CoreException {
  constructor(public operation: string, public key?: string, message?: string) {
    super(message || `Cache error during ${operation}`, 'CACHE_ERROR');
    this.name = 'CacheException';
  }
}

export class NotificationException extends CoreException {
  constructor(public channel: string, public recipient?: string, message?: string) {
    super(message || `Notification error for channel: ${channel}`, 'NOTIFICATION_ERROR');
    this.name = 'NotificationException';
  }
}

export class ProtocolException extends CoreException {
  constructor(public protocol: string, public operation: string, message?: string) {
    super(message || `Protocol error for ${protocol}: ${operation}`, 'PROTOCOL_ERROR');
    this.name = 'ProtocolException';
  }
}

export class SecurityException extends CoreException {
  constructor(public checkType: string, public securityDetails?: string, message?: string) {
    super(message || `Security check failed: ${checkType}`, 'SECURITY_ERROR', { details: securityDetails });
    this.name = 'SecurityException';
  }
}

export class ValidationException extends CoreException {
  constructor(public field: string, public value: any, message?: string) {
    super(message || `Validation error for field ${field}: ${value}`, 'VALIDATION_ERROR');
    this.name = 'ValidationException';
  }
}

export class TimeoutException extends CoreException {
  constructor(public operation: string, public timeout: number, message?: string) {
    super(message || `Operation ${operation} timed out after ${timeout}ms`, 'TIMEOUT_ERROR');
    this.name = 'TimeoutException';
  }
}

export class ConnectionException extends CoreException {
  constructor(public host: string, public port: number, message?: string) {
    super(message || `Connection failed to ${host}:${port}`, 'CONNECTION_ERROR');
    this.name = 'ConnectionException';
  }
}

export class FileException extends CoreException {
  constructor(public operation: string, public filePath: string, message?: string) {
    super(message || `File operation ${operation} failed for ${filePath}`, 'FILE_ERROR');
    this.name = 'FileException';
  }
}

export class BackupException extends CoreException {
  constructor(public backupType: string, message?: string) {
    super(message || `Backup error for type: ${backupType}`, 'BACKUP_ERROR');
    this.name = 'BackupException';
  }
}

export class ReportException extends CoreException {
  constructor(public reportType: string, message?: string) {
    super(message || `Report error for type: ${reportType}`, 'REPORT_ERROR');
    this.name = 'ReportException';
  }
}

export class MaintenanceException extends CoreException {
  constructor(public maintenanceType: string, public deviceId?: number, message?: string) {
    super(message || `Maintenance error for type: ${maintenanceType}`, 'MAINTENANCE_ERROR');
    this.name = 'MaintenanceException';
  }
}

export class HealthCheckException extends CoreException {
  constructor(public component: string, public status: string, message?: string) {
    super(message || `Health check failed for ${component}: ${status}`, 'HEALTH_CHECK_ERROR');
    this.name = 'HealthCheckException';
  }
}

export class AnalyticsException extends CoreException {
  constructor(public operation: string, public metric?: string, message?: string) {
    super(message || `Analytics error during ${operation}`, 'ANALYTICS_ERROR');
    this.name = 'AnalyticsException';
  }
}

export class GeofenceException extends CoreException {
  constructor(public operation: string, public geofenceId?: number, message?: string) {
    super(message || `Geofence error during ${operation}`, 'GEOFENCE_ERROR');
    this.name = 'GeofenceException';
  }
}

export class AlertException extends CoreException {
  constructor(public alertType: string, public deviceId?: number, message?: string) {
    super(message || `Alert error for type: ${alertType}`, 'ALERT_ERROR');
    this.name = 'AlertException';
  }
}

export class TrackingException extends CoreException {
  constructor(public operation: string, public sessionId?: string, message?: string) {
    super(message || `Tracking error during ${operation}`, 'TRACKING_ERROR');
    this.name = 'TrackingException';
  }
}

export class StatisticsException extends CoreException {
  constructor(public operation: string, public period?: string, message?: string) {
    super(message || `Statistics error during ${operation}`, 'STATISTICS_ERROR');
    this.name = 'StatisticsException';
  }
}

export class LoggingException extends CoreException {
  constructor(public operation: string, public level?: string, message?: string) {
    super(message || `Logging error during ${operation}`, 'LOGGING_ERROR');
    this.name = 'LoggingException';
  }
}

// Utility function to create exceptions from API responses
export function createExceptionFromResponse(response: any): CoreException {
  const { code, details, message } = response;
  
  switch (code) {
    case 'DEVICE_NOT_FOUND':
      return new DeviceNotFoundException(response.device_imei, message);
    case 'INVALID_IMEI':
      return new InvalidIMEIException(response.imei, message);
    case 'INVALID_COORDINATES':
      return new InvalidCoordinatesException(response.latitude, response.longitude, message);
    case 'DEVICE_OFFLINE':
      return new DeviceOfflineException(response.imei, message);
    case 'PERMISSION_DENIED':
      return new PermissionDeniedException(response.action, response.user, message);
    case 'INVALID_TOKEN':
      return new InvalidTokenException(response.token, message);
    case 'RATE_LIMIT_EXCEEDED':
      return new RateLimitExceededException(response.limit, response.window, message);
    case 'SERVICE_UNAVAILABLE':
      return new ServiceUnavailableException(response.service, message);
    case 'INVALID_COMMAND':
      return new InvalidCommandException(response.command, message);
    case 'COMMAND_FAILED':
      return new CommandFailedException(response.command, response.error, message);
    case 'CONFIGURATION_ERROR':
      return new ConfigurationException(response.config_key, message);
    case 'DATABASE_ERROR':
      return new DatabaseException(response.operation, response.table, message);
    case 'CACHE_ERROR':
      return new CacheException(response.operation, response.key, message);
    case 'NOTIFICATION_ERROR':
      return new NotificationException(response.channel, response.recipient, message);
    case 'PROTOCOL_ERROR':
      return new ProtocolException(response.protocol, response.operation, message);
    case 'SECURITY_ERROR':
      return new SecurityException(response.check_type, response.details, message);
    case 'VALIDATION_ERROR':
      return new ValidationException(response.field, response.value, message);
    case 'TIMEOUT_ERROR':
      return new TimeoutException(response.operation, response.timeout, message);
    case 'CONNECTION_ERROR':
      return new ConnectionException(response.host, response.port, message);
    case 'FILE_ERROR':
      return new FileException(response.operation, response.file_path, message);
    case 'BACKUP_ERROR':
      return new BackupException(response.backup_type, message);
    case 'REPORT_ERROR':
      return new ReportException(response.report_type, message);
    case 'MAINTENANCE_ERROR':
      return new MaintenanceException(response.maintenance_type, response.device_id, message);
    case 'HEALTH_CHECK_ERROR':
      return new HealthCheckException(response.component, response.status, message);
    case 'ANALYTICS_ERROR':
      return new AnalyticsException(response.operation, response.metric, message);
    case 'GEOFENCE_ERROR':
      return new GeofenceException(response.operation, response.geofence_id, message);
    case 'ALERT_ERROR':
      return new AlertException(response.alert_type, response.device_id, message);
    case 'TRACKING_ERROR':
      return new TrackingException(response.operation, response.session_id, message);
    case 'STATISTICS_ERROR':
      return new StatisticsException(response.operation, response.period, message);
    case 'LOGGING_ERROR':
      return new LoggingException(response.operation, response.level, message);
    default:
      return new CoreException(message || 'Unknown error occurred', code, details);
  }
} 