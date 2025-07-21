"""
Advanced Geofence Management System for SkyGuard
Integrates with all system modules for comprehensive geofencing functionality.
"""
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from django.utils import timezone
from django.contrib.gis.geos import Point, Polygon
from django.contrib.auth.models import User
from django.db import transaction, models
from django.db.models import Q, Count, Avg, Max, Min
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from skyguard.apps.gps.models import GPSDevice, GeoFence, GeoFenceEvent, GPSEvent
from skyguard.apps.gps.notifications import GeofenceNotificationService
from skyguard.apps.tracking.models import TrackingSession, TrackingEvent

logger = logging.getLogger(__name__)


@dataclass
class GeofenceMetrics:
    """Data class for geofence analytics metrics."""
    total_geofences: int
    active_geofences: int
    entry_events_24h: int
    exit_events_24h: int
    most_active_devices: List[Dict[str, Any]]
    violation_rate: float
    average_dwell_time: float
    performance_score: float


@dataclass
class GeofenceAlert:
    """Data class for intelligent geofence alerts."""
    alert_id: str
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    alert_type: str
    device_id: str
    geofence_id: int
    message: str
    recommended_actions: List[str]
    confidence_score: float
    timestamp: datetime


class GeofencePermissionManager:
    """Advanced permission management for geofences."""
    
    @staticmethod
    def check_create_permission(user: User, device: GPSDevice) -> bool:
        """Check if user can create geofences for a device."""
        # Admin can create for any device
        if user.is_superuser or user.is_staff:
            return True
        
        # User can create for their own devices
        return device.owner == user
    
    @staticmethod
    def check_view_permission(user: User, geofence: GeoFence) -> bool:
        """Check if user can view a geofence."""
        # Admin can view any geofence
        if user.is_superuser or user.is_staff:
            return True
        
        # Owner can view
        if geofence.owner == user:
            return True
        
        # Notified users can view
        return geofence.notify_owners.filter(id=user.id).exists()
    
    @staticmethod
    def check_edit_permission(user: User, geofence: GeoFence) -> bool:
        """Check if user can edit a geofence."""
        # Admin can edit any geofence
        if user.is_superuser or user.is_staff:
            return True
        
        # Only owner can edit
        return geofence.owner == user


class IntelligentGeofenceAnalyzer:
    """Advanced analytics and ML for geofence behavior."""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def analyze_device_behavior(self, device: GPSDevice, 
                              days_back: int = 7) -> Dict[str, Any]:
        """Analyze device behavior patterns within geofences."""
        end_time = timezone.now()
        start_time = end_time - timedelta(days=days_back)
        
        events = GeoFenceEvent.objects.filter(
            device=device,
            timestamp__gte=start_time
        ).select_related('fence').order_by('timestamp')
        
        analysis = {
            'total_events': events.count(),
            'entry_events': events.filter(event_type='ENTRY').count(),
            'exit_events': events.filter(event_type='EXIT').count(),
            'unique_geofences': events.values('fence').distinct().count(),
            'average_dwell_time': self._calculate_average_dwell_time(events),
            'most_visited_geofence': self._get_most_visited_geofence(events),
            'behavior_score': self._calculate_behavior_score(events),
            'anomalies_detected': self._detect_anomalies(events),
            'patterns': self._identify_patterns(events)
        }
        
        return analysis
    
    def _calculate_average_dwell_time(self, events) -> float:
        """Calculate average time spent inside geofences."""
        dwell_times = []
        entry_time = None
        
        for event in events:
            if event.event_type == 'ENTRY':
                entry_time = event.timestamp
            elif event.event_type == 'EXIT' and entry_time:
                dwell_time = (event.timestamp - entry_time).total_seconds()
                dwell_times.append(dwell_time)
                entry_time = None
        
        return np.mean(dwell_times) if dwell_times else 0.0
    
    def _get_most_visited_geofence(self, events) -> Optional[Dict[str, Any]]:
        """Get the most frequently visited geofence."""
        geofence_counts = events.values('fence__id', 'fence__name').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        return geofence_counts if geofence_counts else None
    
    def _calculate_behavior_score(self, events) -> float:
        """Calculate behavioral compliance score (0-100)."""
        if not events.exists():
            return 0.0
        
        # Base score on event patterns and frequency
        total_events = events.count()
        authorized_entries = events.filter(
            event_type='ENTRY',
            fence__devices__isnull=False
        ).count()
        
        if total_events == 0:
            return 100.0
        
        compliance_rate = (authorized_entries / total_events) * 100
        return min(compliance_rate, 100.0)
    
    def _detect_anomalies(self, events) -> List[Dict[str, Any]]:
        """Detect behavioral anomalies in geofence events."""
        anomalies = []
        
        # Check for unusual timing patterns
        event_times = [event.timestamp.hour for event in events]
        if event_times:
            mean_hour = np.mean(event_times)
            std_hour = np.std(event_times)
            
            for event in events:
                hour_zscore = abs((event.timestamp.hour - mean_hour) / std_hour) if std_hour > 0 else 0
                if hour_zscore > 2:  # More than 2 standard deviations
                    anomalies.append({
                        'type': 'unusual_timing',
                        'event_id': event.id,
                        'timestamp': event.timestamp,
                        'severity': 'medium' if hour_zscore > 3 else 'low'
                    })
        
        return anomalies
    
    def _identify_patterns(self, events) -> Dict[str, Any]:
        """Identify behavioral patterns."""
        patterns = {
            'peak_hours': self._get_peak_hours(events),
            'frequent_routes': self._get_frequent_routes(events),
            'seasonal_trends': self._get_seasonal_trends(events)
        }
        
        return patterns
    
    def _get_peak_hours(self, events) -> List[int]:
        """Get peak activity hours."""
        hour_counts = {}
        for event in events:
            hour = event.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if not hour_counts:
            return []
        
        max_count = max(hour_counts.values())
        peak_hours = [hour for hour, count in hour_counts.items() 
                     if count >= max_count * 0.8]
        
        return sorted(peak_hours)
    
    def _get_frequent_routes(self, events) -> List[Dict[str, Any]]:
        """Identify frequent geofence transition routes."""
        routes = {}
        prev_fence = None
        
        for event in events.order_by('timestamp'):
            if event.event_type == 'EXIT':
                prev_fence = event.fence.id
            elif event.event_type == 'ENTRY' and prev_fence:
                route = f"{prev_fence} -> {event.fence.id}"
                routes[route] = routes.get(route, 0) + 1
                prev_fence = None
        
        # Return top 5 routes
        sorted_routes = sorted(routes.items(), key=lambda x: x[1], reverse=True)
        return [{'route': route, 'frequency': freq} for route, freq in sorted_routes[:5]]
    
    def _get_seasonal_trends(self, events) -> Dict[str, Any]:
        """Analyze seasonal and weekly trends."""
        weekday_counts = {}
        month_counts = {}
        
        for event in events:
            weekday = event.timestamp.weekday()
            month = event.timestamp.month
            
            weekday_counts[weekday] = weekday_counts.get(weekday, 0) + 1
            month_counts[month] = month_counts.get(month, 0) + 1
        
        return {
            'busiest_weekday': max(weekday_counts.items(), key=lambda x: x[1])[0] if weekday_counts else None,
            'busiest_month': max(month_counts.items(), key=lambda x: x[1])[0] if month_counts else None,
            'weekday_distribution': weekday_counts,
            'monthly_distribution': month_counts
        }


class AdvancedGeofenceManager:
    """Advanced geofence management with full system integration."""
    
    def __init__(self):
        """Initialize the advanced geofence manager."""
        self.notification_service = GeofenceNotificationService()
        self.permission_manager = GeofencePermissionManager()
        self.analyzer = IntelligentGeofenceAnalyzer()
        self.logger = logger
        
        # Performance settings with fallback defaults
        self.batch_size = 100
        self.cache_timeout = 300
        
        # Safely get channel layer
        try:
            self.channel_layer = get_channel_layer()
        except Exception:
            self.channel_layer = None
    
    @transaction.atomic
    def create_geofence(self, user: User, name: str, geometry: Polygon, 
                       devices: List[GPSDevice], **kwargs) -> GeoFence:
        """Create a new geofence with comprehensive validation."""
        # Validate permissions
        for device in devices:
            if not self.permission_manager.check_create_permission(user, device):
                raise PermissionDenied(f"No permission to create geofence for device {device.name}")
        
        # Validate geometry
        self._validate_geometry(geometry)
        
        # Check geofence limits
        user_geofences_count = GeoFence.objects.filter(owner=user).count()
        max_geofences = 50
        
        if user_geofences_count >= max_geofences:
            raise ValidationError(f"Maximum geofences limit reached ({max_geofences})")
        
        # Create geofence
        geofence = GeoFence.objects.create(
            name=name,
            geometry=geometry,
            owner=user,
            description=kwargs.get('description', ''),
            is_active=kwargs.get('is_active', True),
            notify_on_entry=kwargs.get('notify_on_entry', True),
            notify_on_exit=kwargs.get('notify_on_exit', True),
            alert_on_entry=kwargs.get('alert_on_entry', False),
            alert_on_exit=kwargs.get('alert_on_exit', False),
            notification_cooldown=kwargs.get('notification_cooldown', 300),
            notify_emails=kwargs.get('notify_emails', []),
            notify_sms=kwargs.get('notify_sms', []),
            color=kwargs.get('color', '#3388ff'),
            stroke_color=kwargs.get('stroke_color', '#3388ff'),
            stroke_width=kwargs.get('stroke_width', 2)
        )
        
        # Associate devices
        geofence.devices.set(devices)
        
        # Add notification owners
        if 'notify_owners' in kwargs:
            geofence.notify_owners.set(kwargs['notify_owners'])
        
        # Log creation
        self._log_geofence_action(user, geofence, 'CREATED')
        
        # Broadcast creation
        self._broadcast_geofence_update(geofence, 'created')
        
        # Trigger immediate check for devices already inside
        self._check_initial_device_positions(geofence)
        
        self.logger.info(f"Created geofence '{name}' for {len(devices)} devices by user {user.username}")
        
        return geofence
    
    def check_device_geofences(self, device: GPSDevice, 
                             force_check: bool = False) -> List[Dict[str, Any]]:
        """Enhanced geofence detection with performance optimization."""
        if not device.position:
            return []
        
        cache_key = f"geofence_check_{device.imei}_{device.position.x}_{device.position.y}"
        
        # Use cache for recent checks unless forced
        if not force_check:
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        events_generated = []
        
        # Get active geofences for this device with spatial optimization
        active_geofences = GeoFence.objects.filter(
            is_active=True,
            devices=device
        ).select_related('owner').prefetch_related('notify_owners')
        
        # Batch process geofences for better performance
        for geofence_batch in self._batch_geofences(active_geofences):
            batch_events = self._process_geofence_batch(device, geofence_batch)
            events_generated.extend(batch_events)
        
        # Cache result
        cache.set(cache_key, events_generated, 60)  # Cache for 1 minute
        
        # Update device geofence status
        self._update_device_geofence_status(device, events_generated)
        
        return events_generated
    
    def _batch_geofences(self, geofences) -> List[List[GeoFence]]:
        """Split geofences into batches for processing."""
        geofence_list = list(geofences)
        return [geofence_list[i:i + self.batch_size] 
                for i in range(0, len(geofence_list), self.batch_size)]
    
    def _process_geofence_batch(self, device: GPSDevice, 
                               geofence_batch: List[GeoFence]) -> List[Dict[str, Any]]:
        """Process a batch of geofences for a device."""
        events = []
        
        for geofence in geofence_batch:
            try:
                event = self._check_single_geofence_enhanced(device, geofence)
                if event:
                    events.append(event)
            except Exception as e:
                self.logger.error(f"Error checking geofence {geofence.id} for device {device.imei}: {e}")
        
        return events
    
    def _check_single_geofence_enhanced(self, device: GPSDevice, 
                                      geofence: GeoFence) -> Optional[Dict[str, Any]]:
        """Enhanced single geofence check with intelligent analysis."""
        is_inside = geofence.geometry.contains(device.position)
        
        # Get the last event efficiently
        last_event = GeoFenceEvent.objects.filter(
            device=device,
            fence=geofence
        ).order_by('-timestamp').first()
        
        # Determine event generation with enhanced logic
        should_generate_event = False
        event_type = None
        
        if last_event is None:
            # First time checking - generate entry event only if inside
            if is_inside:
                should_generate_event = True
                event_type = 'ENTRY'
        else:
            # Check for state change with hysteresis
            was_inside = (last_event.event_type == 'ENTRY')
            time_since_last = timezone.now() - last_event.timestamp
            min_interval = timedelta(seconds=30)  # Prevent event spam
            
            if is_inside and not was_inside and time_since_last > min_interval:
                should_generate_event = True
                event_type = 'ENTRY'
            elif not is_inside and was_inside and time_since_last > min_interval:
                should_generate_event = True
                event_type = 'EXIT'
        
        if should_generate_event:
            return self._generate_enhanced_geofence_event(device, geofence, event_type)
        
        return None
    
    @transaction.atomic
    def _generate_enhanced_geofence_event(self, device: GPSDevice, geofence: GeoFence, 
                                        event_type: str) -> Dict[str, Any]:
        """Generate enhanced geofence event with comprehensive tracking."""
        # Create the event
        event = GeoFenceEvent.objects.create(
            fence=geofence,
            device=device,
            event_type=event_type,
            position=device.position,
            timestamp=timezone.now()
        )
        
        # Calculate additional metrics
        dwell_time = self._calculate_dwell_time(device, geofence, event_type)
        distance_from_center = self._calculate_distance_from_center(device.position, geofence)
        
        # Prepare comprehensive event data
        event_data = {
            'id': event.id,
            'device_id': device.imei,
            'device_name': device.name,
            'geofence_id': geofence.id,
            'geofence_name': geofence.name,
            'event_type': event_type,
            'position': [device.position.y, device.position.x],
            'timestamp': event.timestamp.isoformat(),
            'dwell_time': dwell_time,
            'distance_from_center': distance_from_center,
            'device_speed': device.speed or 0,
            'device_course': device.course or 0,
            'battery_level': device.battery_level,
            'signal_strength': device.signal_strength
        }
        
        # Log detailed event information
        self._log_detailed_event(event, event_data)
        
        # Create tracking event if session exists
        self._create_tracking_event(device, event, event_data)
        
        # Send notifications with enhanced data
        self._send_enhanced_notifications(event, geofence, device, event_data)
        
        # Broadcast via WebSocket
        self._broadcast_geofence_event(event_data, geofence.owner.id)
        
        # Generate intelligent alerts if needed
        self._generate_intelligent_alerts(device, geofence, event, event_data)
        
        self.logger.info(
            f"Generated enhanced geofence event: {device.name} {event_type} {geofence.name} "
            f"(dwell: {dwell_time}s, distance: {distance_from_center:.2f}m)"
        )
        
        return event_data
    
    def _calculate_dwell_time(self, device: GPSDevice, geofence: GeoFence, 
                            event_type: str) -> Optional[float]:
        """Calculate dwell time for EXIT events."""
        if event_type != 'EXIT':
            return None
        
        # Find the most recent ENTRY event
        entry_event = GeoFenceEvent.objects.filter(
            device=device,
            fence=geofence,
            event_type='ENTRY',
            timestamp__lte=timezone.now()
        ).order_by('-timestamp').first()
        
        if entry_event:
            return (timezone.now() - entry_event.timestamp).total_seconds()
        
        return None
    
    def _calculate_distance_from_center(self, position: Point, geofence: GeoFence) -> float:
        """Calculate distance from geofence center."""
        try:
            center = geofence.geometry.centroid
            # Simple distance calculation (for precise calculations, use geopy)
            return ((position.x - center.x) ** 2 + (position.y - center.y) ** 2) ** 0.5 * 111000  # Rough meters
        except Exception:
            return 0.0
    
    def _log_detailed_event(self, event: GeoFenceEvent, event_data: Dict[str, Any]):
        """Log detailed event information."""
        try:
            message = f"Geofence event: {event_data['device_name']} {event_data['event_type']} {event_data['geofence_name']}"
            self.logger.info(message)
        except Exception as e:
            self.logger.warning(f"Failed to log detailed event: {e}")
    
    def _create_tracking_event(self, device: GPSDevice, geofence_event: GeoFenceEvent, 
                             event_data: Dict[str, Any]):
        """Create tracking event if active session exists."""
        try:
            active_session = TrackingSession.objects.filter(
                device=device,
                status='ACTIVE'
            ).first()
            
            if active_session:
                TrackingEvent.objects.create(
                    session=active_session,
                    event_type=f'GEOFENCE_{geofence_event.event_type}',
                    position=device.position,
                    timestamp=geofence_event.timestamp,
                    data=event_data,
                    message=f"Device {geofence_event.event_type.lower()} geofence '{geofence_event.fence.name}'"
                )
        except Exception as e:
            self.logger.warning(f"Failed to create tracking event: {e}")
    
    def _send_enhanced_notifications(self, event: GeoFenceEvent, geofence: GeoFence, 
                                   device: GPSDevice, event_data: Dict[str, Any]):
        """Send enhanced notifications with additional context."""
        if not self._should_send_notification(geofence, event.event_type):
            return
        
        if self._is_in_cooldown(geofence, device, event.event_type):
            return
        
        try:
            # Enhanced notification data
            enhanced_data = event_data.copy()
            enhanced_data.update({
                'geofence_description': geofence.description,
                'notification_time': timezone.now().isoformat(),
                'device_last_seen': device.last_log.isoformat() if device.last_log else None,
                'alert_level': self._determine_alert_level(event_data)
            })
            
            self.notification_service.send_geofence_notification(event, geofence, device)
        except Exception as e:
            self.logger.warning(f"Error sending enhanced notification: {e}")
    
    def _should_send_notification(self, geofence: GeoFence, event_type: str) -> bool:
        """Check if notification should be sent."""
        if event_type == 'ENTRY' and not geofence.notify_on_entry:
            return False
        if event_type == 'EXIT' and not geofence.notify_on_exit:
            return False
        return True
    
    def _is_in_cooldown(self, geofence: GeoFence, device: GPSDevice, event_type: str) -> bool:
        """Check cooldown period."""
        if geofence.notification_cooldown <= 0:
            return False
        
        since = timezone.now() - timedelta(seconds=geofence.notification_cooldown)
        return GeoFenceEvent.objects.filter(
            fence=geofence,
            device=device,
            event_type=event_type,
            timestamp__gte=since
        ).exists()
    
    def _determine_alert_level(self, event_data: Dict[str, Any]) -> str:
        """Determine alert level based on event characteristics."""
        # Simple logic - can be enhanced with ML
        if event_data.get('device_speed', 0) > 80:  # High speed
            return 'HIGH'
        elif event_data.get('battery_level', 100) < 20:  # Low battery
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_intelligent_alerts(self, device: GPSDevice, geofence: GeoFence, 
                                   event: GeoFenceEvent, event_data: Dict[str, Any]):
        """Generate intelligent alerts based on patterns and analysis."""
        try:
            # Analyze recent behavior
            behavior_analysis = self.analyzer.analyze_device_behavior(device, days_back=1)
            
            alerts = []
            
            # Check for unusual patterns
            if behavior_analysis['anomalies_detected']:
                alerts.append(GeofenceAlert(
                    alert_id=f"anomaly_{device.imei}_{timezone.now().timestamp()}",
                    severity='MEDIUM',
                    alert_type='BEHAVIORAL_ANOMALY',
                    device_id=device.imei,
                    geofence_id=geofence.id,
                    message=f"Unusual behavior detected for device {device.name}",
                    recommended_actions=['Review device activity', 'Check with driver'],
                    confidence_score=0.8,
                    timestamp=timezone.now()
                ))
            
            # Check for frequent violations
            recent_events = GeoFenceEvent.objects.filter(
                device=device,
                timestamp__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            if recent_events > 10:  # More than 10 events in an hour
                alerts.append(GeofenceAlert(
                    alert_id=f"frequent_{device.imei}_{timezone.now().timestamp()}",
                    severity='HIGH',
                    alert_type='FREQUENT_VIOLATIONS',
                    device_id=device.imei,
                    geofence_id=geofence.id,
                    message=f"Frequent geofence violations detected for {device.name}",
                    recommended_actions=['Check device configuration', 'Review geofence boundaries'],
                    confidence_score=0.9,
                    timestamp=timezone.now()
                ))
            
            # Broadcast alerts
            for alert in alerts:
                self._broadcast_intelligent_alert(alert, geofence.owner.id)
            
        except Exception as e:
            self.logger.warning(f"Error generating intelligent alerts: {e}")
    
    def _broadcast_geofence_event(self, event_data: Dict[str, Any], user_id: int):
        """Broadcast geofence event via WebSocket."""
        if not self.channel_layer:
            return
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"geofences_user_{user_id}",
                {
                    'type': 'geofence_event',
                    'data': event_data
                }
            )
        except Exception as e:
            self.logger.warning(f"Error broadcasting geofence event: {e}")
    
    def _broadcast_intelligent_alert(self, alert: GeofenceAlert, user_id: int):
        """Broadcast intelligent alert via WebSocket."""
        if not self.channel_layer:
            return
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"alerts_user_{user_id}",
                {
                    'type': 'intelligent_alert',
                    'data': asdict(alert)
                }
            )
        except Exception as e:
            self.logger.warning(f"Error broadcasting intelligent alert: {e}")
    
    def _broadcast_geofence_update(self, geofence: GeoFence, action: str):
        """Broadcast geofence updates."""
        if not self.channel_layer:
            return
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"geofences_user_{geofence.owner.id}",
                {
                    'type': 'geofence_update',
                    'data': {
                        'action': action,
                        'geofence_id': geofence.id,
                        'geofence_name': geofence.name,
                        'timestamp': timezone.now().isoformat()
                    }
                }
            )
        except Exception as e:
            self.logger.warning(f"Error broadcasting geofence update: {e}")
    
    def _validate_geometry(self, geometry: Polygon):
        """Validate geofence geometry."""
        if not geometry.valid:
            raise ValidationError("Invalid geometry provided")
        
        # Check polygon complexity
        num_points = len(geometry.coords[0])
        max_points = 1000
        min_points = 3
        
        if num_points > max_points:
            raise ValidationError(f"Polygon too complex ({num_points} points, max {max_points})")
        
        if num_points < min_points:
            raise ValidationError(f"Polygon too simple ({num_points} points, min {min_points})")
        
        # Check area (prevent too small or too large geofences)
        area = geometry.area
        if area < 0.0001:  # Very small area
            raise ValidationError("Geofence area too small")
        
        if area > 10:  # Very large area (rough degrees)
            raise ValidationError("Geofence area too large")
    
    def _check_initial_device_positions(self, geofence: GeoFence):
        """Check if devices are already inside the new geofence."""
        for device in geofence.devices.filter(position__isnull=False):
            try:
                self.check_device_geofences(device, force_check=True)
            except Exception as e:
                self.logger.warning(f"Error checking initial position for device {device.imei}: {e}")
    
    def _update_device_geofence_status(self, device: GPSDevice, events: List[Dict[str, Any]]):
        """Update device's current geofence status."""
        try:
            # Simple status update - can be enhanced
            if events:
                last_event = events[-1]
                cache.set(f"device_last_geofence_{device.imei}", last_event, 3600)
        except Exception as e:
            self.logger.warning(f"Error updating device geofence status: {e}")
    
    def _log_geofence_action(self, user: User, geofence: GeoFence, action: str):
        """Log geofence management actions."""
        try:
            message = f"Geofence {action}: '{geofence.name}' by {user.username}"
            self.logger.info(message)
        except Exception as e:
            self.logger.warning(f"Failed to log geofence action: {e}")
    
    def generate_geofence_metrics(self, user: User, time_window_hours: int = 24) -> GeofenceMetrics:
        """Generate comprehensive geofence metrics."""
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        # Get user's geofences
        user_geofences = GeoFence.objects.filter(owner=user)
        
        # Basic counts
        total_geofences = user_geofences.count()
        active_geofences = user_geofences.filter(is_active=True).count()
        
        # Event counts
        recent_events = GeoFenceEvent.objects.filter(
            fence__owner=user,
            timestamp__gte=start_time
        )
        
        entry_events = recent_events.filter(event_type='ENTRY').count()
        exit_events = recent_events.filter(event_type='EXIT').count()
        
        # Most active devices
        most_active_devices = list(recent_events.values(
            'device__imei', 'device__name'
        ).annotate(
            event_count=Count('id')
        ).order_by('-event_count')[:5])
        
        # Calculate violation rate and other metrics
        total_events = recent_events.count()
        violation_rate = (total_events / max(active_geofences, 1)) if active_geofences > 0 else 0
        
        # Average dwell time calculation
        dwell_times = []
        for geofence in user_geofences:
            dwell_time = self._calculate_average_dwell_time_for_geofence(geofence, start_time)
            if dwell_time:
                dwell_times.append(dwell_time)
        
        average_dwell_time = np.mean(dwell_times) if dwell_times else 0.0
        
        # Performance score (0-100)
        performance_score = min(100, max(0, 100 - (violation_rate * 10)))
        
        return GeofenceMetrics(
            total_geofences=total_geofences,
            active_geofences=active_geofences,
            entry_events_24h=entry_events,
            exit_events_24h=exit_events,
            most_active_devices=most_active_devices,
            violation_rate=violation_rate,
            average_dwell_time=average_dwell_time,
            performance_score=performance_score
        )
    
    def _calculate_average_dwell_time_for_geofence(self, geofence: GeoFence, 
                                                 since: datetime) -> Optional[float]:
        """Calculate average dwell time for a specific geofence."""
        events = GeoFenceEvent.objects.filter(
            fence=geofence,
            timestamp__gte=since
        ).order_by('device', 'timestamp')
        
        dwell_times = []
        device_entries = {}
        
        for event in events:
            device_id = event.device.id
            
            if event.event_type == 'ENTRY':
                device_entries[device_id] = event.timestamp
            elif event.event_type == 'EXIT' and device_id in device_entries:
                dwell_time = (event.timestamp - device_entries[device_id]).total_seconds()
                dwell_times.append(dwell_time)
                del device_entries[device_id]
        
        return np.mean(dwell_times) if dwell_times else None
    
    def get_user_geofences(self, user: User, include_inactive: bool = False) -> List[GeoFence]:
        """Get geofences for a user with permission checking."""
        queryset = GeoFence.objects.filter(
            Q(owner=user) | Q(notify_owners=user)
        ).distinct()
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        return list(queryset.select_related('owner').prefetch_related('devices', 'notify_owners'))
    
    def delete_geofence(self, user: User, geofence_id: int) -> bool:
        """Delete a geofence with permission checking."""
        try:
            geofence = GeoFence.objects.get(id=geofence_id)
            
            if not self.permission_manager.check_edit_permission(user, geofence):
                raise PermissionDenied("No permission to delete this geofence")
            
            # Log deletion before actual deletion
            self._log_geofence_action(user, geofence, 'DELETED')
            
            # Broadcast deletion
            self._broadcast_geofence_update(geofence, 'deleted')
            
            # Delete the geofence
            geofence.delete()
            
            self.logger.info(f"Deleted geofence '{geofence.name}' by user {user.username}")
            return True
            
        except GeoFence.DoesNotExist:
            raise ValidationError("Geofence not found")
        except Exception as e:
            self.logger.error(f"Error deleting geofence {geofence_id}: {e}")
            return False


# Global instance
advanced_geofence_manager = AdvancedGeofenceManager() 