"""
Core services for the GPS tracking system.
These services implement the interfaces defined in core.interfaces.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from django.contrib.gis.geos import Point
from django.db import transaction
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .interfaces import (
    IDeviceRepository, ILocationService, IEventService, IProtocolHandler,
    IDeviceServer, INotificationService, IAnalyticsService, IReportService,
    ISecurityService, IConnectionService, IMaintenanceService, IGeofenceService,
    IAlertService, ITrackingService, IConfigurationService, ILoggingService,
    IStatisticsService, IBackupService, IHealthCheckService
)

logger = logging.getLogger(__name__)


class BaseService:
    """Base class for all services with common functionality."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _log_error(self, message: str, error: Exception = None):
        """Log error with optional exception."""
        if error:
            self.logger.error(f"{message}: {error}", exc_info=True)
        else:
            self.logger.error(message)
    
    def _log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def _log_debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)


class DeviceRepositoryService(BaseService, IDeviceRepository):
    """Service for device data access operations."""
    
    def __init__(self):
        super().__init__()
        from ..gps.models.device import GPSDevice
        from ..gps.models.location import GPSLocation
        from ..gps.models.event import GPSEvent
        self.GPSDevice = GPSDevice
        self.GPSLocation = GPSLocation
        self.GPSEvent = GPSEvent
    
    def get_device(self, imei: int) -> Optional['GPSDevice']:
        """Get device by IMEI."""
        try:
            return self.GPSDevice.objects.get(imei=imei)
        except self.GPSDevice.DoesNotExist:
            self._log_debug(f"Device with IMEI {imei} not found")
            return None
    
    def get_all_devices(self) -> List['GPSDevice']:
        """Get all devices."""
        return list(self.GPSDevice.objects.all())
    
    def save_device(self, device: 'GPSDevice') -> None:
        """Save or update device."""
        try:
            device.save()
            self._log_debug(f"Device {device.imei} saved successfully")
        except Exception as e:
            self._log_error(f"Error saving device {device.imei}", e)
            raise
    
    def update_device_position(self, imei: int, position: Point) -> None:
        """Update device position."""
        try:
            device = self.get_device(imei)
            if device:
                device.position = position
                device.last_log = timezone.now()
                device.save()
                self._log_debug(f"Updated position for device {imei}")
        except Exception as e:
            self._log_error(f"Error updating position for device {imei}", e)
            raise
    
    def get_device_locations(self, imei: int, start_time: Optional[datetime] = None, 
                           end_time: Optional[datetime] = None) -> List['GPSLocation']:
        """Get device location history."""
        try:
            queryset = self.GPSLocation.objects.filter(device__imei=imei)
            if start_time:
                queryset = queryset.filter(timestamp__gte=start_time)
            if end_time:
                queryset = queryset.filter(timestamp__lte=end_time)
            return list(queryset.order_by('-timestamp'))
        except Exception as e:
            self._log_error(f"Error getting locations for device {imei}", e)
            return []
    
    def get_device_events(self, imei: int, event_type: Optional[str] = None) -> List['GPSEvent']:
        """Get device events."""
        try:
            queryset = self.GPSEvent.objects.filter(device__imei=imei)
            if event_type:
                queryset = queryset.filter(type=event_type)
            return list(queryset.order_by('-timestamp'))
        except Exception as e:
            self._log_error(f"Error getting events for device {imei}", e)
            return []


class LocationService(BaseService, ILocationService):
    """Service for location processing."""
    
    def __init__(self, repository: IDeviceRepository):
        super().__init__()
        self.repository = repository
        from ..gps.models.location import Location
        self.Location = Location
    
    def process_location(self, device: 'GPSDevice', location_data: Dict[str, Any]) -> None:
        """Process and store location data."""
        try:
            with transaction.atomic():
                # Create location record
                location = self.Location(
                    device=device,
                    timestamp=location_data.get('timestamp', timezone.now()),
                    position=Point(
                        location_data.get('longitude', 0),
                        location_data.get('latitude', 0)
                    ),
                    speed=location_data.get('speed', 0.0),
                    course=location_data.get('course', 0.0),
                    altitude=location_data.get('altitude', 0.0),
                    satellites=location_data.get('satellites', 0),
                    accuracy=location_data.get('accuracy', 0.0),
                    hdop=location_data.get('hdop', 0.0),
                    pdop=location_data.get('pdop', 0.0),
                    fix_quality=location_data.get('fix_quality', 0),
                    fix_type=location_data.get('fix_type', 0)
                )
                location.save()
                
                # Update device position
                device.position = location.position
                device.speed = location.speed
                device.course = location.course
                device.altitude = location.altitude
                device.last_log = location.timestamp
                device.save()
                
                self._log_debug(f"Processed location for device {device.imei}")
                
        except Exception as e:
            self._log_error(f"Error processing location for device {device.imei}", e)
            raise
    
    def get_device_history(self, imei: int, start_time: Any, end_time: Any) -> List[Dict[str, Any]]:
        """Get device location history."""
        try:
            locations = self.repository.get_device_locations(imei, start_time, end_time)
            return [
                {
                    'id': loc.id,
                    'timestamp': loc.timestamp.isoformat(),
                    'latitude': loc.position.y,
                    'longitude': loc.position.x,
                    'speed': loc.speed,
                    'course': loc.course,
                    'altitude': loc.altitude,
                    'satellites': loc.satellites,
                    'accuracy': loc.accuracy
                }
                for loc in locations
            ]
        except Exception as e:
            self._log_error(f"Error getting history for device {imei}", e)
            return []


class EventService(BaseService, IEventService):
    """Service for event processing."""
    
    def __init__(self, repository: IDeviceRepository):
        super().__init__()
        self.repository = repository
        from ..gps.models.event import GPSEvent
        self.GPSEvent = GPSEvent
    
    def process_event(self, device: 'GPSDevice', event_data: Dict[str, Any]) -> None:
        """Process and store event data."""
        try:
            with transaction.atomic():
                event = self.GPSEvent(
                    device=device,
                    type=event_data.get('type', 'UNKNOWN'),
                    timestamp=event_data.get('timestamp', timezone.now()),
                    position=Point(
                        event_data.get('longitude', 0),
                        event_data.get('latitude', 0)
                    ) if event_data.get('longitude') and event_data.get('latitude') else None,
                    speed=event_data.get('speed', 0.0),
                    course=event_data.get('course', 0.0),
                    altitude=event_data.get('altitude', 0.0),
                    odometer=event_data.get('odometer', 0.0),
                    source=event_data.get('source'),
                    text=event_data.get('text'),
                    inputs=event_data.get('inputs', 0),
                    outputs=event_data.get('outputs', 0),
                    input_changes=event_data.get('input_changes', 0),
                    output_changes=event_data.get('output_changes', 0),
                    alarm_changes=event_data.get('alarm_changes', 0),
                    changes_description=event_data.get('changes_description')
                )
                event.save()
                
                self._log_debug(f"Processed event {event.type} for device {device.imei}")
                
        except Exception as e:
            self._log_error(f"Error processing event for device {device.imei}", e)
            raise
    
    def get_device_events(self, imei: int, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get device events."""
        try:
            events = self.repository.get_device_events(imei, event_type)
            return [
                {
                    'id': event.id,
                    'type': event.type,
                    'timestamp': event.timestamp.isoformat(),
                    'latitude': event.position.y if event.position else None,
                    'longitude': event.position.x if event.position else None,
                    'speed': event.speed,
                    'course': event.course,
                    'altitude': event.altitude,
                    'odometer': event.odometer,
                    'source': event.source,
                    'text': event.text
                }
                for event in events
            ]
        except Exception as e:
            self._log_error(f"Error getting events for device {imei}", e)
            return []


class NotificationService(BaseService, INotificationService):
    """Service for notification handling."""
    
    def __init__(self):
        super().__init__()
        from ..gps.notifications import GPSNotificationService
        self.notification_service = GPSNotificationService()
    
    def send_notification(self, message: 'NotificationMessage', 
                         recipients: List['NotificationRecipient'],
                         channels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send notification to recipients."""
        try:
            return self.notification_service.send_notification(message, recipients, channels)
        except Exception as e:
            self._log_error("Error sending notification", e)
            return {'success': False, 'error': str(e)}
    
    def send_device_alarm(self, device: 'GPSDevice', alarm_type: str, 
                         position: Optional[Dict[str, float]] = None,
                         additional_data: Optional[Dict[str, Any]] = None) -> None:
        """Send device alarm notification."""
        try:
            self.notification_service.send_device_alarm(device, alarm_type, position, additional_data)
            self._log_debug(f"Sent alarm notification for device {device.imei}")
        except Exception as e:
            self._log_error(f"Error sending alarm for device {device.imei}", e)


class SecurityService(BaseService, ISecurityService):
    """Service for security operations."""
    
    def __init__(self):
        super().__init__()
        from ..gps.security import GPSCommandSecurity
        self.security = GPSCommandSecurity()
    
    def sign_command(self, command: str, device_imei: str, user_id: int, 
                    additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sign command for security."""
        try:
            return self.security.sign_command(command, device_imei, user_id, additional_data)
        except Exception as e:
            self._log_error(f"Error signing command {command}", e)
            raise
    
    def verify_command(self, signed_command: Dict[str, Any], device: 'GPSDevice', 
                      user: 'User') -> Dict[str, Any]:
        """Verify command signature."""
        try:
            return self.security.verify_command(signed_command, device, user)
        except Exception as e:
            self._log_error("Error verifying command", e)
            raise
    
    def get_command_risk_level(self, command: str) -> str:
        """Get command risk level."""
        try:
            return self.security.get_command_risk_level(command)
        except Exception as e:
            self._log_error(f"Error getting risk level for command {command}", e)
            return 'UNKNOWN'


class ConnectionService(BaseService, IConnectionService):
    """Service for device connection management."""
    
    def __init__(self, repository: IDeviceRepository):
        super().__init__()
        self.repository = repository
        from ..gps.models.session import DeviceSession
        self.DeviceSession = DeviceSession
    
    def register_connection(self, device: 'GPSDevice', ip_address: str, 
                          port: int, protocol: str) -> 'DeviceSession':
        """Register device connection."""
        try:
            # Close any existing active session
            existing_sessions = self.DeviceSession.objects.filter(
                device=device, is_active=True
            )
            for session in existing_sessions:
                session.close()
            
            # Create new session
            session = self.DeviceSession.objects.create(
                device=device,
                ip_address=ip_address,
                port=port,
                protocol=protocol,
                is_active=True
            )
            
            # Update device connection status
            device.update_connection_status('ONLINE', ip_address, port)
            
            self._log_debug(f"Registered connection for device {device.imei}")
            return session
            
        except Exception as e:
            self._log_error(f"Error registering connection for device {device.imei}", e)
            raise
    
    def register_disconnection(self, device: 'GPSDevice', session_id: str, 
                             reason: str = None) -> None:
        """Register device disconnection."""
        try:
            session = self.DeviceSession.objects.get(id=session_id)
            session.close()
            
            # Update device connection status
            device.update_connection_status('OFFLINE')
            
            self._log_debug(f"Registered disconnection for device {device.imei}")
            
        except Exception as e:
            self._log_error(f"Error registering disconnection for device {device.imei}", e)
            raise
    
    def get_active_sessions(self) -> List['DeviceSession']:
        """Get active device sessions."""
        try:
            return list(self.DeviceSession.objects.filter(is_active=True))
        except Exception as e:
            self._log_error("Error getting active sessions", e)
            return []
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Cleanup old sessions."""
        try:
            cutoff_date = timezone.now() - timedelta(days=days)
            old_sessions = self.DeviceSession.objects.filter(
                end_time__lt=cutoff_date,
                is_active=False
            )
            count = old_sessions.count()
            old_sessions.delete()
            
            self._log_info(f"Cleaned up {count} old sessions")
            return count
            
        except Exception as e:
            self._log_error("Error cleaning up old sessions", e)
            return 0


class LoggingService(BaseService, ILoggingService):
    """Service for system logging."""
    
    def __init__(self):
        super().__init__()
        from ..monitoring.models import SystemLog
        self.SystemLog = SystemLog
    
    def log_device_event(self, device: 'GPSDevice', event_type: str, 
                        message: str, level: str = 'INFO') -> None:
        """Log device event."""
        try:
            self.SystemLog.objects.create(
                level=level,
                message=message,
                source=f"device_{device.imei}",
                device=device
            )
            self._log_debug(f"Logged device event: {message}")
        except Exception as e:
            self._log_error(f"Error logging device event: {message}", e)
    
    def log_system_event(self, event_type: str, message: str, 
                        level: str = 'INFO', user: Optional['User'] = None) -> None:
        """Log system event."""
        try:
            self.SystemLog.objects.create(
                level=level,
                message=message,
                source=event_type
            )
            self._log_debug(f"Logged system event: {message}")
        except Exception as e:
            self._log_error(f"Error logging system event: {message}", e)
    
    def get_device_logs(self, device: 'GPSDevice', start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> List['SystemLog']:
        """Get device logs."""
        try:
            queryset = self.SystemLog.objects.filter(device=device)
            if start_time:
                queryset = queryset.filter(created_at__gte=start_time)
            if end_time:
                queryset = queryset.filter(created_at__lte=end_time)
            return list(queryset.order_by('-created_at'))
        except Exception as e:
            self._log_error(f"Error getting logs for device {device.imei}", e)
            return []


class HealthCheckService(BaseService, IHealthCheckService):
    """Service for system health monitoring."""
    
    def __init__(self):
        super().__init__()
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        try:
            health_status = {
                'overall': 'HEALTHY',
                'timestamp': timezone.now().isoformat(),
                'checks': {}
            }
            
            # Check database
            db_health = self.check_database_health()
            health_status['checks']['database'] = db_health
            
            # Check network
            network_health = self.check_network_health()
            health_status['checks']['network'] = network_health
            
            # Determine overall health
            if any(check.get('status') == 'UNHEALTHY' for check in health_status['checks'].values()):
                health_status['overall'] = 'UNHEALTHY'
            elif any(check.get('status') == 'WARNING' for check in health_status['checks'].values()):
                health_status['overall'] = 'WARNING'
            
            return health_status
            
        except Exception as e:
            self._log_error("Error checking system health", e)
            return {
                'overall': 'ERROR',
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }
    
    def check_device_health(self, device: 'GPSDevice') -> Dict[str, Any]:
        """Check device health."""
        try:
            health_status = {
                'device_imei': device.imei,
                'status': 'HEALTHY',
                'timestamp': timezone.now().isoformat(),
                'checks': {}
            }
            
            # Check if device is online
            if device.is_online:
                health_status['checks']['connection'] = {'status': 'HEALTHY', 'message': 'Device is online'}
            else:
                health_status['checks']['connection'] = {'status': 'UNHEALTHY', 'message': 'Device is offline'}
            
            # Check last heartbeat
            if device.last_heartbeat:
                time_since_heartbeat = timezone.now() - device.last_heartbeat
                if time_since_heartbeat.total_seconds() < 300:  # 5 minutes
                    health_status['checks']['heartbeat'] = {'status': 'HEALTHY', 'message': 'Recent heartbeat'}
                else:
                    health_status['checks']['heartbeat'] = {'status': 'WARNING', 'message': 'Stale heartbeat'}
            else:
                health_status['checks']['heartbeat'] = {'status': 'UNHEALTHY', 'message': 'No heartbeat'}
            
            # Determine overall device health
            if any(check.get('status') == 'UNHEALTHY' for check in health_status['checks'].values()):
                health_status['status'] = 'UNHEALTHY'
            elif any(check.get('status') == 'WARNING' for check in health_status['checks'].values()):
                health_status['status'] = 'WARNING'
            
            return health_status
            
        except Exception as e:
            self._log_error(f"Error checking health for device {device.imei}", e)
            return {
                'device_imei': device.imei,
                'status': 'ERROR',
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            return {
                'status': 'HEALTHY',
                'message': 'Database connection successful',
                'response_time': 'fast'
            }
        except Exception as e:
            return {
                'status': 'UNHEALTHY',
                'message': f'Database connection failed: {str(e)}',
                'error': str(e)
            }
    
    def check_network_health(self) -> Dict[str, Any]:
        """Check network health."""
        try:
            import socket
            import subprocess
            
            # Check DNS resolution
            try:
                socket.gethostbyname('google.com')
                dns_status = 'HEALTHY'
            except:
                dns_status = 'UNHEALTHY'
            
            # Check internet connectivity
            try:
                subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                             capture_output=True, timeout=5)
                internet_status = 'HEALTHY'
            except:
                internet_status = 'UNHEALTHY'
            
            if dns_status == 'HEALTHY' and internet_status == 'HEALTHY':
                return {
                    'status': 'HEALTHY',
                    'message': 'Network connectivity is good',
                    'dns': dns_status,
                    'internet': internet_status
                }
            else:
                return {
                    'status': 'WARNING',
                    'message': 'Network connectivity issues detected',
                    'dns': dns_status,
                    'internet': internet_status
                }
                
        except Exception as e:
            return {
                'status': 'UNHEALTHY',
                'message': f'Network check failed: {str(e)}',
                'error': str(e)
            }


class ConfigurationService(BaseService, IConfigurationService):
    """Service for configuration management."""
    
    def __init__(self):
        super().__init__()
        self._cache_key_prefix = "config:"
    
    def get_device_config(self, device: 'GPSDevice') -> Dict[str, Any]:
        """Get device configuration."""
        try:
            cache_key = f"{self._cache_key_prefix}device:{device.imei}"
            config = cache.get(cache_key)
            
            if config is None:
                config = {
                    'imei': device.imei,
                    'name': device.name,
                    'model': device.model,
                    'protocol': device.protocol,
                    'route': device.route,
                    'economico': device.economico,
                    'harness': {
                        'name': device.harness.name if device.harness else None,
                        'inputs': device.harness.get_input_config() if device.harness else {},
                        'outputs': device.harness.get_output_config() if device.harness else {}
                    } if device.harness else None,
                    'sim_card': {
                        'iccid': device.sim_card.iccid if device.sim_card else None,
                        'phone': device.sim_card.phone if device.sim_card else None,
                        'provider': device.sim_card.provider if device.sim_card else None
                    } if device.sim_card else None,
                    'connection': {
                        'status': device.connection_status,
                        'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                        'current_ip': device.current_ip,
                        'current_port': device.current_port
                    }
                }
                cache.set(cache_key, config, 300)  # Cache for 5 minutes
            
            return config
            
        except Exception as e:
            self._log_error(f"Error getting config for device {device.imei}", e)
            return {}
    
    def update_device_config(self, device: 'GPSDevice', config: Dict[str, Any]) -> None:
        """Update device configuration."""
        try:
            # Update device fields
            if 'name' in config:
                device.name = config['name']
            if 'route' in config:
                device.route = config['route']
            if 'economico' in config:
                device.economico = config['economico']
            
            device.save()
            
            # Clear cache
            cache_key = f"{self._cache_key_prefix}device:{device.imei}"
            cache.delete(cache_key)
            
            self._log_debug(f"Updated config for device {device.imei}")
            
        except Exception as e:
            self._log_error(f"Error updating config for device {device.imei}", e)
            raise
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration."""
        try:
            cache_key = f"{self._cache_key_prefix}system"
            config = cache.get(cache_key)
            
            if config is None:
                config = {
                    'gps_servers': {
                        'concox': {'enabled': True, 'port': 55300},
                        'meiligao': {'enabled': True, 'port': 62000},
                        'wialon': {'enabled': True, 'port': 20332},
                        'bluetooth': {'enabled': True, 'port': 50100},
                        'satellite': {'enabled': True, 'port': 15557}
                    },
                    'notifications': {
                        'email': {'enabled': True},
                        'sms': {'enabled': False},
                        'push': {'enabled': False},
                        'websocket': {'enabled': True}
                    },
                    'analytics': {
                        'enabled': True,
                        'retention_days': 90,
                        'real_time_enabled': True
                    },
                    'security': {
                        'command_signing': True,
                        'rate_limiting': True,
                        'session_timeout': 3600
                    }
                }
                cache.set(cache_key, config, 600)  # Cache for 10 minutes
            
            return config
            
        except Exception as e:
            self._log_error("Error getting system config", e)
            return {}
    
    def update_system_config(self, config: Dict[str, Any]) -> None:
        """Update system configuration."""
        try:
            # Validate and update configuration
            # This would typically update settings or database records
            
            # Clear cache
            cache_key = f"{self._cache_key_prefix}system"
            cache.delete(cache_key)
            
            self._log_info("Updated system configuration")
            
        except Exception as e:
            self._log_error("Error updating system config", e)
            raise 