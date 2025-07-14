"""
Core interfaces for the GPS tracking system.
These interfaces define the contract for all GPS-related services.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from django.contrib.gis.geos import Point


class IDeviceRepository(ABC):
    """Interface for device data access operations."""
    
    @abstractmethod
    def get_device(self, imei: int) -> Optional['GPSDevice']:
        """Get device by IMEI."""
        pass
    
    @abstractmethod
    def get_all_devices(self) -> List['GPSDevice']:
        """Get all devices."""
        pass
    
    @abstractmethod
    def save_device(self, device: 'GPSDevice') -> None:
        """Save or update device."""
        pass
    
    @abstractmethod
    def update_device_position(self, imei: int, position: Point) -> None:
        """Update device position."""
        pass
    
    @abstractmethod
    def get_device_locations(self, imei: int, start_time: Optional[datetime] = None, 
                           end_time: Optional[datetime] = None) -> List['GPSLocation']:
        """Get device location history."""
        pass
    
    @abstractmethod
    def get_device_events(self, imei: int, event_type: Optional[str] = None) -> List['GPSEvent']:
        """Get device events."""
        pass


class ILocationService(ABC):
    """Interface for location processing services."""
    
    @abstractmethod
    def process_location(self, device: 'GPSDevice', location_data: Dict[str, Any]) -> None:
        """Process and store location data."""
        pass
    
    @abstractmethod
    def get_device_history(self, imei: int, start_time: Any, end_time: Any) -> List[Dict[str, Any]]:
        """Get device location history."""
        pass


class IEventService(ABC):
    """Interface for event processing services."""
    
    @abstractmethod
    def process_event(self, device: 'GPSDevice', event_data: Dict[str, Any]) -> None:
        """Process and store event data."""
        pass
    
    @abstractmethod
    def get_device_events(self, imei: int, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get device events."""
        pass


class IProtocolHandler(ABC):
    """Interface for GPS protocol handlers."""
    
    @abstractmethod
    def decode_packet(self, data: bytes) -> Dict[str, Any]:
        """Decode incoming packet data."""
        pass
    
    @abstractmethod
    def encode_command(self, command: str, params: Dict[str, Any]) -> bytes:
        """Encode outgoing command."""
        pass
    
    @abstractmethod
    def validate_packet(self, data: bytes) -> bool:
        """Validate packet integrity."""
        pass
    
    @abstractmethod
    def send_ping(self, device: 'GPSDevice') -> Dict[str, Any]:
        """Send ping command to device."""
        pass


class IDeviceServer(ABC):
    """Interface for GPS device servers."""
    
    @abstractmethod
    def start(self, host: str = '', port: int = 0) -> None:
        """Start the server."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the server."""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if server is running."""
        pass


class INotificationService(ABC):
    """Interface for notification services."""
    
    @abstractmethod
    def send_notification(self, message: 'NotificationMessage', 
                         recipients: List['NotificationRecipient'],
                         channels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send notification to recipients."""
        pass
    
    @abstractmethod
    def send_device_alarm(self, device: 'GPSDevice', alarm_type: str, 
                         position: Optional[Dict[str, float]] = None,
                         additional_data: Optional[Dict[str, Any]] = None) -> None:
        """Send device alarm notification."""
        pass


class IAnalyticsService(ABC):
    """Interface for analytics services."""
    
    @abstractmethod
    def generate_real_time_metrics(self, time_window_hours: int = 24) -> 'AnalyticsMetrics':
        """Generate real-time analytics metrics."""
        pass
    
    @abstractmethod
    def analyze_device_performance(self, device_imei: str, 
                                 days_back: int = 7) -> 'DeviceAnalytics':
        """Analyze device performance."""
        pass
    
    @abstractmethod
    def detect_driving_patterns(self, device_imei: str, 
                              days_back: int = 30) -> Dict[str, Any]:
        """Detect driving patterns."""
        pass


class IReportService(ABC):
    """Interface for report generation services."""
    
    @abstractmethod
    def generate_report(self, report_type: str, device_id: int, 
                       start_date: datetime, end_date: datetime, 
                       format: str = 'pdf') -> 'HttpResponse':
        """Generate report."""
        pass
    
    @abstractmethod
    def get_available_reports(self) -> List[Dict[str, Any]]:
        """Get list of available reports."""
        pass


class ISecurityService(ABC):
    """Interface for security services."""
    
    @abstractmethod
    def sign_command(self, command: str, device_imei: str, user_id: int, 
                    additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sign command for security."""
        pass
    
    @abstractmethod
    def verify_command(self, signed_command: Dict[str, Any], device: 'GPSDevice', 
                      user: 'User') -> Dict[str, Any]:
        """Verify command signature."""
        pass
    
    @abstractmethod
    def get_command_risk_level(self, command: str) -> str:
        """Get command risk level."""
        pass


class IConnectionService(ABC):
    """Interface for device connection management."""
    
    @abstractmethod
    def register_connection(self, device: 'GPSDevice', ip_address: str, 
                          port: int, protocol: str) -> 'DeviceSession':
        """Register device connection."""
        pass
    
    @abstractmethod
    def register_disconnection(self, device: 'GPSDevice', session_id: str, 
                             reason: str = None) -> None:
        """Register device disconnection."""
        pass
    
    @abstractmethod
    def get_active_sessions(self) -> List['DeviceSession']:
        """Get active device sessions."""
        pass
    
    @abstractmethod
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Cleanup old sessions."""
        pass


class IMaintenanceService(ABC):
    """Interface for device maintenance services."""
    
    @abstractmethod
    def schedule_maintenance(self, device: 'GPSDevice', maintenance_type: str, 
                           scheduled_date: datetime) -> 'MaintenanceLog':
        """Schedule device maintenance."""
        pass
    
    @abstractmethod
    def record_maintenance(self, device: 'GPSDevice', maintenance_type: str, 
                         description: str, performed_by: 'User') -> 'MaintenanceLog':
        """Record maintenance performed."""
        pass
    
    @abstractmethod
    def get_maintenance_history(self, device: 'GPSDevice') -> List['MaintenanceLog']:
        """Get device maintenance history."""
        pass


class IGeofenceService(ABC):
    """Interface for geofence services."""
    
    @abstractmethod
    def create_geofence(self, name: str, geometry: Point, owner: 'User') -> 'GeoFence':
        """Create new geofence."""
        pass
    
    @abstractmethod
    def check_device_in_geofence(self, device: 'GPSDevice', geofence: 'GeoFence') -> bool:
        """Check if device is inside geofence."""
        pass
    
    @abstractmethod
    def get_device_geofences(self, device: 'GPSDevice') -> List['GeoFence']:
        """Get geofences for device."""
        pass


class IAlertService(ABC):
    """Interface for alert services."""
    
    @abstractmethod
    def create_alert(self, device: 'GPSDevice', alert_type: str, 
                    message: str, position: Optional[Point] = None) -> 'Alert':
        """Create new alert."""
        pass
    
    @abstractmethod
    def acknowledge_alert(self, alert: 'Alert', acknowledged_by: 'User') -> None:
        """Acknowledge alert."""
        pass
    
    @abstractmethod
    def get_unacknowledged_alerts(self, user: 'User') -> List['Alert']:
        """Get unacknowledged alerts for user."""
        pass


class ITrackingService(ABC):
    """Interface for tracking services."""
    
    @abstractmethod
    def start_tracking_session(self, device: 'GPSDevice', user: 'User') -> 'TrackingSession':
        """Start tracking session."""
        pass
    
    @abstractmethod
    def stop_tracking_session(self, session: 'TrackingSession') -> None:
        """Stop tracking session."""
        pass
    
    @abstractmethod
    def add_tracking_point(self, session: 'TrackingSession', position: Point, 
                          speed: float, timestamp: datetime) -> 'TrackingPoint':
        """Add tracking point to session."""
        pass
    
    @abstractmethod
    def get_active_sessions(self, user: 'User') -> List['TrackingSession']:
        """Get active tracking sessions for user."""
        pass


class IConfigurationService(ABC):
    """Interface for configuration services."""
    
    @abstractmethod
    def get_device_config(self, device: 'GPSDevice') -> Dict[str, Any]:
        """Get device configuration."""
        pass
    
    @abstractmethod
    def update_device_config(self, device: 'GPSDevice', config: Dict[str, Any]) -> None:
        """Update device configuration."""
        pass
    
    @abstractmethod
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration."""
        pass
    
    @abstractmethod
    def update_system_config(self, config: Dict[str, Any]) -> None:
        """Update system configuration."""
        pass


class ILoggingService(ABC):
    """Interface for logging services."""
    
    @abstractmethod
    def log_device_event(self, device: 'GPSDevice', event_type: str, 
                        message: str, level: str = 'INFO') -> None:
        """Log device event."""
        pass
    
    @abstractmethod
    def log_system_event(self, event_type: str, message: str, 
                        level: str = 'INFO', user: Optional['User'] = None) -> None:
        """Log system event."""
        pass
    
    @abstractmethod
    def get_device_logs(self, device: 'GPSDevice', start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> List['SystemLog']:
        """Get device logs."""
        pass


class IStatisticsService(ABC):
    """Interface for statistics services."""
    
    @abstractmethod
    def calculate_device_statistics(self, device: 'GPSDevice', 
                                  start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate device statistics."""
        pass
    
    @abstractmethod
    def calculate_fleet_statistics(self, devices: List['GPSDevice'], 
                                 start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate fleet statistics."""
        pass
    
    @abstractmethod
    def generate_daily_report(self, date: datetime) -> Dict[str, Any]:
        """Generate daily report."""
        pass


class IBackupService(ABC):
    """Interface for backup services."""
    
    @abstractmethod
    def create_backup(self, backup_type: str = 'full') -> str:
        """Create system backup."""
        pass
    
    @abstractmethod
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup."""
        pass
    
    @abstractmethod
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups."""
        pass
    
    @abstractmethod
    def cleanup_old_backups(self, days_to_keep: int = 30) -> int:
        """Cleanup old backups."""
        pass


class IHealthCheckService(ABC):
    """Interface for health check services."""
    
    @abstractmethod
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        pass
    
    @abstractmethod
    def check_device_health(self, device: 'GPSDevice') -> Dict[str, Any]:
        """Check device health."""
        pass
    
    @abstractmethod
    def check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        pass
    
    @abstractmethod
    def check_network_health(self) -> Dict[str, Any]:
        """Check network health."""
        pass 