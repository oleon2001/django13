"""
Services for the tracking application.
"""
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from django.db.models import Q, Avg, Max, Min, Count
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import (
    TrackingSession, TrackingPoint, TrackingEvent, TrackingConfig,
    Alert, Geofence, Route, RoutePoint
)
from skyguard.apps.gps.models import GPSDevice, GPSLocation


class TrackingService:
    """Service for managing tracking sessions."""
    
    def __init__(self, user: User):
        self.user = user
    
    def create_session(self, device: GPSDevice, session_id: str = None) -> TrackingSession:
        """Create a new tracking session."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session = TrackingSession.objects.create(
            session_id=session_id,
            device=device,
            user=self.user,
            status='ACTIVE',
            start_time=timezone.now()
        )
        
        # Create start event
        TrackingEvent.objects.create(
            session=session,
            event_type='START',
            timestamp=session.start_time,
            message=f"Tracking session started for device {device.name}"
        )
        
        return session
    
    def stop_session(self, session: TrackingSession) -> bool:
        """Stop a tracking session."""
        if session.status == 'COMPLETED':
            return False
        
        session.status = 'COMPLETED'
        session.end_time = timezone.now()
        session.save()
        
        # Create stop event
        TrackingEvent.objects.create(
            session=session,
            event_type='STOP',
            timestamp=session.end_time,
            message=f"Tracking session stopped for device {session.device.name}"
        )
        
        return True
    
    def pause_session(self, session: TrackingSession) -> bool:
        """Pause a tracking session."""
        if session.status != 'ACTIVE':
            return False
        
        session.status = 'PAUSED'
        session.save()
        
        # Create pause event
        TrackingEvent.objects.create(
            session=session,
            event_type='PAUSE',
            timestamp=timezone.now(),
            message=f"Tracking session paused for device {session.device.name}"
        )
        
        return True
    
    def resume_session(self, session: TrackingSession) -> bool:
        """Resume a tracking session."""
        if session.status != 'PAUSED':
            return False
        
        session.status = 'ACTIVE'
        session.save()
        
        # Create resume event
        TrackingEvent.objects.create(
            session=session,
            event_type='RESUME',
            timestamp=timezone.now(),
            message=f"Tracking session resumed for device {session.device.name}"
        )
        
        return True
    
    def add_point(self, session: TrackingSession, position: Point, 
                  speed: float = 0, course: float = 0, altitude: float = 0,
                  accuracy: float = 0, satellites: int = 0) -> TrackingPoint:
        """Add a tracking point to a session."""
        point = TrackingPoint.objects.create(
            session=session,
            position=position,
            speed=speed,
            course=course,
            altitude=altitude,
            accuracy=accuracy,
            satellites=satellites,
            timestamp=timezone.now()
        )
        
        # Update session statistics
        self._update_session_stats(session)
        
        return point
    
    def get_session_points(self, session: TrackingSession, 
                          start_time: datetime = None, 
                          end_time: datetime = None) -> List[TrackingPoint]:
        """Get tracking points for a session."""
        queryset = session.points.all()
        
        if start_time:
            queryset = queryset.filter(timestamp__gte=start_time)
        if end_time:
            queryset = queryset.filter(timestamp__lte=end_time)
        
        return queryset.order_by('timestamp')
    
    def get_session_events(self, session: TrackingSession) -> List[TrackingEvent]:
        """Get events for a session."""
        return session.events.all().order_by('timestamp')
    
    def get_user_sessions(self, status: str = None) -> List[TrackingSession]:
        """Get tracking sessions for the current user."""
        queryset = TrackingSession.objects.filter(user=self.user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-start_time')
    
    def get_device_sessions(self, device: GPSDevice, 
                           status: str = None) -> List[TrackingSession]:
        """Get tracking sessions for a specific device."""
        queryset = TrackingSession.objects.filter(device=device, user=self.user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-start_time')
    
    def _update_session_stats(self, session: TrackingSession):
        """Update session statistics."""
        points = session.points.all()
        
        if points.exists():
            # Calculate total distance
            total_distance = self._calculate_total_distance(points)
            
            # Calculate speed statistics
            speeds = [p.speed for p in points if p.speed > 0]
            avg_speed = sum(speeds) / len(speeds) if speeds else 0
            max_speed = max(speeds) if speeds else 0
            
            session.total_distance = total_distance
            session.average_speed = avg_speed
            session.max_speed = max_speed
            session.save()
    
    def _calculate_total_distance(self, points: List[TrackingPoint]) -> float:
        """Calculate total distance from tracking points."""
        if len(points) < 2:
            return 0
        
        total_distance = 0
        for i in range(1, len(points)):
            prev_point = points[i-1].position
            curr_point = points[i].position
            
            # Calculate distance between points
            distance = prev_point.distance(curr_point) * 111  # Convert to km
            total_distance += distance
        
        return total_distance


class AlertService:
    """Service for managing alerts."""
    
    def __init__(self, user: User):
        self.user = user
    
    def create_alert(self, device: GPSDevice, alert_type: str, 
                    message: str, position: Point = None) -> Alert:
        """Create a new alert."""
        alert = Alert.objects.create(
            device=device,
            alert_type=alert_type,
            position=position,
            message=message
        )
        
        return alert
    
    def acknowledge_alert(self, alert: Alert) -> bool:
        """Acknowledge an alert."""
        if alert.is_acknowledged:
            return False
        
        alert.is_acknowledged = True
        alert.acknowledged_by = self.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return True
    
    def get_device_alerts(self, device: GPSDevice, 
                         acknowledged: bool = None) -> List[Alert]:
        """Get alerts for a specific device."""
        queryset = Alert.objects.filter(device=device)
        
        if acknowledged is not None:
            queryset = queryset.filter(is_acknowledged=acknowledged)
        
        return queryset.order_by('-created_at')
    
    def get_user_alerts(self, acknowledged: bool = None) -> List[Alert]:
        """Get alerts for the current user's devices."""
        user_devices = GPSDevice.objects.filter(owner=self.user)
        queryset = Alert.objects.filter(device__in=user_devices)
        
        if acknowledged is not None:
            queryset = queryset.filter(is_acknowledged=acknowledged)
        
        return queryset.order_by('-created_at')


class GeofenceService:
    """Service for managing geofences."""
    
    def __init__(self, user: User):
        self.user = user
    
    def create_geofence(self, name: str, area: Point, 
                       description: str = "") -> Geofence:
        """Create a new geofence."""
        geofence = Geofence.objects.create(
            name=name,
            description=description,
            area=area,
            is_active=True
        )
        
        return geofence
    
    def check_device_in_geofence(self, device: GPSDevice, 
                                geofence: Geofence) -> bool:
        """Check if a device is inside a geofence."""
        if not device.position:
            return False
        
        return geofence.area.contains(device.position)
    
    def get_device_geofences(self, device: GPSDevice) -> List[Geofence]:
        """Get geofences that contain a device."""
        if not device.position:
            return []
        
        return Geofence.objects.filter(
            area__contains=device.position,
            is_active=True
        )
    
    def get_user_geofences(self) -> List[Geofence]:
        """Get geofences for the current user."""
        return Geofence.objects.filter(is_active=True).order_by('name')


class RouteService:
    """Service for managing routes."""
    
    def __init__(self, user: User):
        self.user = user
    
    def create_route(self, device: GPSDevice, start_time: datetime,
                    end_time: datetime = None) -> Route:
        """Create a new route."""
        route = Route.objects.create(
            device=device,
            start_time=start_time,
            end_time=end_time
        )
        
        return route
    
    def add_route_point(self, route: Route, position: Point, 
                       speed: float = 0, timestamp: datetime = None) -> RoutePoint:
        """Add a point to a route."""
        if not timestamp:
            timestamp = timezone.now()
        
        point = RoutePoint.objects.create(
            route=route,
            position=position,
            speed=speed,
            timestamp=timestamp
        )
        
        # Update route statistics
        self._update_route_stats(route)
        
        return point
    
    def get_route_points(self, route: Route) -> List[RoutePoint]:
        """Get points for a route."""
        return route.points.all().order_by('timestamp')
    
    def get_device_routes(self, device: GPSDevice, 
                         start_date: datetime = None,
                         end_date: datetime = None) -> List[Route]:
        """Get routes for a specific device."""
        queryset = Route.objects.filter(device=device)
        
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)
        
        return queryset.order_by('-start_time')
    
    def _update_route_stats(self, route: Route):
        """Update route statistics."""
        points = route.points.all()
        
        if points.exists():
            # Calculate total distance
            total_distance = self._calculate_route_distance(points)
            
            # Calculate speed statistics
            speeds = [p.speed for p in points if p.speed > 0]
            avg_speed = sum(speeds) / len(speeds) if speeds else 0
            max_speed = max(speeds) if speeds else 0
            
            route.distance = total_distance
            route.average_speed = avg_speed
            route.max_speed = max_speed
            route.save()
    
    def _calculate_route_distance(self, points: List[RoutePoint]) -> float:
        """Calculate total distance from route points."""
        if len(points) < 2:
            return 0
        
        total_distance = 0
        for i in range(1, len(points)):
            prev_point = points[i-1].position
            curr_point = points[i].position
            
            # Calculate distance between points
            distance = prev_point.distance(curr_point) * 111  # Convert to km
            total_distance += distance
        
        return total_distance 