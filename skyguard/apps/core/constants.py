"""
Constants for the GPS tracking system core.
"""

from enum import Enum


class DeviceStatus(Enum):
    """Device connection status."""
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    SLEEPING = 'SLEEPING'
    ERROR = 'ERROR'


class EventType(Enum):
    """GPS event types."""
    TRACK = 'TRACK'
    IO_FIX = 'IO_FIX'
    IO_NOFIX = 'IO_NOFIX'
    GPS_LOST = 'GPS_LOST'
    GPS_OK = 'GPS_OK'
    CURRENT_FIX = 'CURRENT_FIX'
    CURRENT_TIME = 'CURRENT_TIME'
    STARTUP_FIX = 'STARTUP_FIX'
    STARTUP_TIME = 'STARTUP_TIME'
    SMS_RECEIVED = 'SMS_RECEIVED'
    CALL_RECEIVED = 'CALL_RECEIVED'
    RESET = 'RESET'
    ALARM = 'ALARM'
    PRESSURE = 'PRESSURE'
    PEOPLE = 'PEOPLE'


class ProtocolType(Enum):
    """GPS protocol types."""
    CONCOX = 'concox'
    MEILIGAO = 'meiligao'
    WIALON = 'wialon'
    BLUETOOTH = 'bluetooth'
    SATELLITE = 'satellite'


class AlertType(Enum):
    """Alert types."""
    SOS = 'SOS'
    LOW_BATTERY = 'LOW_BATTERY'
    GEOFENCE = 'GEOFENCE'
    SPEED = 'SPEED'
    TAMPER = 'TAMPER'
    POWER = 'POWER'
    OTHER = 'OTHER'


class NotificationChannel(Enum):
    """Notification channels."""
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'
    WEBSOCKET = 'websocket'
    WEBHOOK = 'webhook'


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
    EMERGENCY = 'emergency'


class LogLevel(Enum):
    """Log levels."""
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


class MaintenanceType(Enum):
    """Maintenance types."""
    ROUTINE = 'ROUTINE'
    REPAIR = 'REPAIR'
    UPGRADE = 'UPGRADE'
    BATTERY = 'BATTERY'
    OTHER = 'OTHER'


class ReportFormat(Enum):
    """Report formats."""
    PDF = 'pdf'
    CSV = 'csv'
    JSON = 'json'
    XLSX = 'xlsx'


class CommandRiskLevel(Enum):
    """Command risk levels."""
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'


# GPS Protocol Constants
GPS_PROTOCOLS = {
    'concox': {
        'name': 'Concox',
        'port': 55300,
        'description': 'Concox GPS protocol'
    },
    'meiligao': {
        'name': 'Meiligao',
        'port': 62000,
        'description': 'Meiligao GPS protocol'
    },
    'wialon': {
        'name': 'Wialon',
        'port': 20332,
        'description': 'Wialon GPS protocol'
    },
    'bluetooth': {
        'name': 'Bluetooth',
        'port': 50100,
        'description': 'Bluetooth GPS protocol'
    },
    'satellite': {
        'name': 'Satellite',
        'port': 15557,
        'description': 'Satellite GPS protocol'
    }
}

# Device Model Constants
DEVICE_MODELS = {
    0: 'Unknown',
    1: 'SGB4612',
    2: 'SGP4612',
}

# GSM Operator Constants
GSM_OPERATORS = {
    0: 'Telcel',
    1: 'Movistar',
    2: 'IusaCell',
}

# Route Constants
ROUTES = {
    92: "Ruta 4",
    112: "Ruta 6",
    114: "Ruta 12",
    115: "Ruta 31",
    90: "Ruta 82",
    88: "Ruta 118",
    215: "Ruta 140",
    89: "Ruta 202",
    116: "Ruta 207",
    96: "Ruta 400",
    97: "Ruta 408",
}

# Cache Keys
CACHE_KEYS = {
    'device_data': 'device_data:{imei}',
    'device_config': 'device_config:{imei}',
    'system_config': 'system_config',
    'analytics_metrics': 'analytics_metrics',
    'health_status': 'health_status',
    'active_sessions': 'active_sessions',
}

# Time Constants
TIME_CONSTANTS = {
    'HEARTBEAT_TIMEOUT': 300,  # 5 minutes
    'SESSION_TIMEOUT': 3600,   # 1 hour
    'CACHE_TIMEOUT': 300,      # 5 minutes
    'BACKUP_RETENTION': 30,    # 30 days
    'LOG_RETENTION': 90,       # 90 days
}

# Security Constants
SECURITY_CONSTANTS = {
    'TOKEN_EXPIRY': 3600,      # 1 hour
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 900,   # 15 minutes
    'PASSWORD_MIN_LENGTH': 8,
    'SESSION_TIMEOUT': 3600,   # 1 hour
}

# Notification Constants
NOTIFICATION_CONSTANTS = {
    'RATE_LIMIT': 60,          # 1 minute
    'MAX_RECIPIENTS': 100,
    'MESSAGE_MAX_LENGTH': 160,
    'QUIET_HOURS_START': 22,   # 10 PM
    'QUIET_HOURS_END': 8,      # 8 AM
}

# Analytics Constants
ANALYTICS_CONSTANTS = {
    'REAL_TIME_WINDOW': 24,    # 24 hours
    'HISTORY_RETENTION': 90,   # 90 days
    'ANOMALY_THRESHOLD': 0.8,
    'EFFICIENCY_THRESHOLD': 0.7,
}

# Geofence Constants
GEOFENCE_CONSTANTS = {
    'MAX_POLYGON_POINTS': 1000,
    'MIN_POLYGON_POINTS': 3,
    'MAX_GEOFENCES_PER_DEVICE': 50,
}

# Tracking Constants
TRACKING_CONSTANTS = {
    'MAX_SESSION_DURATION': 86400,  # 24 hours
    'MIN_POINT_INTERVAL': 1,        # 1 second
    'MAX_POINT_INTERVAL': 3600,     # 1 hour
    'MAX_SESSION_POINTS': 10000,
}

# Error Messages
ERROR_MESSAGES = {
    'DEVICE_NOT_FOUND': 'Device not found',
    'INVALID_IMEI': 'Invalid IMEI format',
    'INVALID_COORDINATES': 'Invalid GPS coordinates',
    'DEVICE_OFFLINE': 'Device is offline',
    'PERMISSION_DENIED': 'Permission denied',
    'INVALID_TOKEN': 'Invalid authentication token',
    'RATE_LIMIT_EXCEEDED': 'Rate limit exceeded',
    'SERVICE_UNAVAILABLE': 'Service temporarily unavailable',
    'INVALID_COMMAND': 'Invalid command',
    'COMMAND_FAILED': 'Command execution failed',
}

# Success Messages
SUCCESS_MESSAGES = {
    'DEVICE_UPDATED': 'Device updated successfully',
    'LOCATION_SAVED': 'Location saved successfully',
    'EVENT_SAVED': 'Event saved successfully',
    'COMMAND_SENT': 'Command sent successfully',
    'NOTIFICATION_SENT': 'Notification sent successfully',
    'REPORT_GENERATED': 'Report generated successfully',
    'BACKUP_CREATED': 'Backup created successfully',
    'MAINTENANCE_SCHEDULED': 'Maintenance scheduled successfully',
}

# API Response Codes
API_CODES = {
    'SUCCESS': 200,
    'CREATED': 201,
    'NO_CONTENT': 204,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'METHOD_NOT_ALLOWED': 405,
    'RATE_LIMITED': 429,
    'INTERNAL_ERROR': 500,
    'SERVICE_UNAVAILABLE': 503,
}

# Database Constants
DATABASE_CONSTANTS = {
    'MAX_CONNECTIONS': 100,
    'CONNECTION_TIMEOUT': 30,
    'QUERY_TIMEOUT': 60,
    'BATCH_SIZE': 1000,
}

# File Upload Constants
FILE_CONSTANTS = {
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10 MB
    'ALLOWED_EXTENSIONS': ['.csv', '.xlsx', '.json', '.xml'],
    'UPLOAD_DIR': 'uploads/',
    'BACKUP_DIR': 'backups/',
    'REPORT_DIR': 'reports/',
}

# WebSocket Constants
WEBSOCKET_CONSTANTS = {
    'MAX_CONNECTIONS': 1000,
    'HEARTBEAT_INTERVAL': 30,
    'CONNECTION_TIMEOUT': 300,
    'MAX_MESSAGE_SIZE': 1024 * 1024,  # 1 MB
}

# Monitoring Constants
MONITORING_CONSTANTS = {
    'HEALTH_CHECK_INTERVAL': 300,  # 5 minutes
    'METRICS_COLLECTION_INTERVAL': 60,  # 1 minute
    'ALERT_CHECK_INTERVAL': 30,  # 30 seconds
    'LOG_ROTATION_INTERVAL': 86400,  # 24 hours
}

# Default Values
DEFAULT_VALUES = {
    'DEVICE_NAME': 'Unknown Device',
    'DEVICE_ICON': 'default.png',
    'DEFAULT_SPEED': 0.0,
    'DEFAULT_COURSE': 0.0,
    'DEFAULT_ALTITUDE': 0.0,
    'DEFAULT_SATELLITES': 0,
    'DEFAULT_ACCURACY': 0.0,
    'DEFAULT_HDOP': 0.0,
    'DEFAULT_PDOP': 0.0,
    'DEFAULT_FIX_QUALITY': 0,
    'DEFAULT_FIX_TYPE': 0,
} 