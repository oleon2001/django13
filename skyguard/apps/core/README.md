# Core System Documentation

## Overview

The Core system provides the foundational interfaces, services, and utilities for the GPS tracking system. It implements a clean architecture pattern with clear separation of concerns.

## Architecture

### Interfaces (`interfaces.py`)

The core interfaces define the contracts that all GPS-related services must implement:

- **IDeviceRepository**: Device data access operations
- **ILocationService**: Location tracking and management
- **IEventService**: GPS event processing
- **IProtocolHandler**: GPS protocol handling
- **IDeviceServer**: Device server management
- **INotificationService**: Notification delivery
- **IAnalyticsService**: Analytics and reporting
- **IReportService**: Report generation
- **ISecurityService**: Security and authentication
- **IConnectionService**: Connection management
- **IMaintenanceService**: Device maintenance
- **IGeofenceService**: Geofence management
- **IAlertService**: Alert processing
- **ITrackingService**: Real-time tracking
- **IConfigurationService**: Configuration management
- **ILoggingService**: Logging and monitoring
- **IStatisticsService**: Statistics collection
- **IBackupService**: Data backup and restore
- **IHealthCheckService**: System health monitoring

### Services (`services.py`)

Concrete implementations of the core interfaces:

- **DeviceRepositoryService**: Manages device data persistence
- **LocationService**: Handles location tracking and geospatial operations
- **EventService**: Processes GPS events and coordinates
- **NotificationService**: Manages notification delivery across channels
- **SecurityService**: Handles authentication, authorization, and security
- **ConnectionService**: Manages device connections and sessions
- **LoggingService**: Centralized logging and monitoring
- **HealthCheckService**: System health monitoring and diagnostics
- **ConfigurationService**: Dynamic configuration management

### Factory (`factory.py`)

Service factory for centralized service management:

- **ServiceFactory**: Creates and manages service instances
- Convenience functions for easy service access
- Singleton pattern for service instances

### Utilities (`utils.py`)

Common utility functions:

- **Device Authentication**: Token generation and verification
- **Geospatial Operations**: Distance calculation, coordinate validation
- **Data Formatting**: Speed, duration, coordinate formatting
- **Caching**: Device data caching operations
- **Validation**: IMEI validation, coordinate parsing
- **Reporting**: Device report generation

### Configuration (`config.py`)

Dynamic configuration management:

- **CoreConfig**: Centralized configuration manager
- Environment variable support
- Custom configuration file loading
- Configuration validation
- Runtime configuration updates

### Constants (`constants.py`)

System-wide constants and enumerations:

- **DeviceStatus**: Device connection states
- **EventType**: GPS event types
- **ProtocolType**: GPS protocol types
- **AlertType**: Alert categories
- **NotificationChannel**: Notification delivery channels
- **LogLevel**: Logging levels
- **MaintenanceType**: Maintenance categories
- **ReportFormat**: Report output formats

### Exceptions (`exceptions.py`)

Custom exception hierarchy:

- **CoreException**: Base exception class
- **DeviceNotFoundException**: Device not found
- **InvalidIMEIException**: Invalid IMEI format
- **InvalidCoordinatesException**: Invalid GPS coordinates
- **DeviceOfflineException**: Device offline
- **PermissionDeniedException**: Access denied
- **InvalidTokenException**: Invalid authentication
- **RateLimitExceededException**: Rate limiting
- **ServiceUnavailableException**: Service unavailable
- **CommandFailedException**: Command execution failure

## Usage

### Basic Service Access

```python
from skyguard.apps.core.factory import get_device_repository, get_location_service

# Get services
device_repo = get_device_repository()
location_service = get_location_service()

# Use services
device = device_repo.get_device(imei=123456789012345)
locations = location_service.get_device_locations(imei=123456789012345)
```

### Configuration Management

```python
from skyguard.apps.core.config import get_config_value, set_config_value

# Get configuration
timeout = get_config_value('database.timeout', 30)
max_connections = get_config_value('database.max_connections', 100)

# Set configuration
set_config_value('database.timeout', 60)
```

### Utility Functions

```python
from skyguard.apps.core.utils import (
    validate_coordinates, calculate_distance, format_speed,
    generate_device_token, validate_imei
)

# Validate coordinates
is_valid = validate_coordinates(latitude=19.4326, longitude=-99.1332)

# Calculate distance
distance = calculate_distance(point1, point2)

# Format speed
speed_text = format_speed(65.5)  # "65.5 km/h"

# Generate device token
token = generate_device_token(imei=123456789012345)

# Validate IMEI
is_valid_imei = validate_imei("123456789012345")
```

### Exception Handling

```python
from skyguard.apps.core.exceptions import (
    DeviceNotFoundException, InvalidIMEIException, CoreException
)

try:
    device = device_repo.get_device(imei=123456789012345)
except DeviceNotFoundException as e:
    logger.error(f"Device not found: {e.message}")
except CoreException as e:
    logger.error(f"Core error: {e.message}, code: {e.code}")
```

## Configuration

### Environment Variables

The system supports configuration through environment variables:

```bash
# Database configuration
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_NAME=skyguard
export DATABASE_USER=postgres
export DATABASE_PASSWORD=password

# Security configuration
export TOKEN_EXPIRY=3600
export MAX_LOGIN_ATTEMPTS=5

# Notification configuration
export NOTIFICATION_RATE_LIMIT=60
export NOTIFICATION_MAX_RECIPIENTS=100

# Tracking configuration
export TRACKING_MAX_SESSION_DURATION=86400
export TRACKING_MIN_POINT_INTERVAL=1

# Analytics configuration
export ANALYTICS_REAL_TIME_WINDOW=24
export ANALYTICS_ANOMALY_THRESHOLD=0.8

# Monitoring configuration
export MONITORING_HEALTH_CHECK_INTERVAL=300
export MONITORING_METRICS_INTERVAL=60

# WebSocket configuration
export WEBSOCKET_MAX_CONNECTIONS=1000
export WEBSOCKET_HEARTBEAT_INTERVAL=30

# File upload configuration
export FILE_UPLOAD_MAX_SIZE=10485760  # 10MB
```

### Custom Configuration File

Create a JSON configuration file:

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "skyguard",
    "user": "postgres",
    "password": "password",
    "max_connections": 100,
    "timeout": 30
  },
  "security": {
    "token_expiry": 3600,
    "max_login_attempts": 5,
    "lockout_duration": 900,
    "password_min_length": 8,
    "session_timeout": 3600
  },
  "notifications": {
    "rate_limit": 60,
    "max_recipients": 100,
    "message_max_length": 160,
    "quiet_hours_start": 22,
    "quiet_hours_end": 8
  }
}
```

Set the configuration file path in Django settings:

```python
CORE_CONFIG_FILE = '/path/to/custom_config.json'
```

## Testing

### Unit Tests

```python
from skyguard.apps.core.tests import CoreTestCase
from skyguard.apps.core.factory import ServiceFactory

class TestCoreServices(CoreTestCase):
    def setUp(self):
        super().setUp()
        ServiceFactory.reset()
    
    def test_device_repository(self):
        device_repo = ServiceFactory.get_device_repository()
        self.assertIsNotNone(device_repo)
    
    def test_location_service(self):
        location_service = ServiceFactory.get_location_service()
        self.assertIsNotNone(location_service)
```

### Integration Tests

```python
from skyguard.apps.core.tests import CoreIntegrationTestCase

class TestCoreIntegration(CoreIntegrationTestCase):
    def test_device_lifecycle(self):
        # Create device
        device = self.create_test_device()
        
        # Add location
        location = self.create_test_location(device)
        
        # Verify location
        locations = self.location_service.get_device_locations(device.imei)
        self.assertIn(location, locations)
```

## Performance

### Caching

The core system uses Django's cache framework for performance:

```python
from skyguard.apps.core.utils import cache_device_data, get_cached_device_data

# Cache device data
cache_device_data(imei=123456789012345, data=device_data, timeout=300)

# Get cached data
cached_data = get_cached_device_data(imei=123456789012345)
```

### Database Optimization

- Connection pooling
- Query optimization
- Batch operations
- Index optimization

### Memory Management

- Lazy loading of services
- Resource cleanup
- Memory monitoring

## Security

### Authentication

- HMAC-based device tokens
- Token expiration
- Secure token generation

### Authorization

- Permission-based access control
- Role-based security
- Action-based permissions

### Data Protection

- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection

## Monitoring

### Health Checks

```python
from skyguard.apps.core.factory import get_health_check_service

health_service = get_health_check_service()
status = health_service.check_system_health()
```

### Logging

```python
from skyguard.apps.core.factory import get_logging_service

logging_service = get_logging_service()
logging_service.log_event('device_connected', {'imei': 123456789012345})
```

### Metrics

- Service performance metrics
- Database performance metrics
- Cache hit/miss ratios
- Error rates and types

## Deployment

### Requirements

- Python 3.8+
- Django 3.2+
- PostgreSQL 12+
- Redis 6+

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Initialize core services
python manage.py shell -c "from skyguard.apps.core.factory import ServiceFactory; ServiceFactory.initialize()"
```

### Configuration

1. Set environment variables
2. Create custom configuration file (optional)
3. Configure Django settings
4. Initialize services

### Monitoring

1. Set up health checks
2. Configure logging
3. Set up metrics collection
4. Configure alerts

## Troubleshooting

### Common Issues

1. **Service Initialization Failed**
   - Check configuration
   - Verify dependencies
   - Check logs

2. **Database Connection Issues**
   - Verify database settings
   - Check network connectivity
   - Verify credentials

3. **Cache Issues**
   - Check Redis connection
   - Verify cache configuration
   - Check memory usage

4. **Performance Issues**
   - Monitor database performance
   - Check cache hit rates
   - Review query optimization

### Debug Mode

Enable debug mode for detailed logging:

```python
DEBUG = True
CORE_DEBUG = True
```

### Log Analysis

```python
from skyguard.apps.core.factory import get_logging_service

logging_service = get_logging_service()
logs = logging_service.get_recent_logs(level='ERROR', limit=100)
```

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add unit tests

### Testing

- Run unit tests: `python manage.py test skyguard.apps.core`
- Run integration tests: `python manage.py test skyguard.apps.core.tests.integration`
- Run performance tests: `python manage.py test skyguard.apps.core.tests.performance`

### Documentation

- Update README.md
- Add docstrings
- Update API documentation
- Write migration guides 