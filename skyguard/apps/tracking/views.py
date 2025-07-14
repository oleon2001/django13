"""
Views for the tracking application.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import (
    TrackingSession, TrackingPoint, TrackingEvent, TrackingConfig,
    Alert, Geofence, Route, RoutePoint
)
from .services import TrackingService, AlertService, GeofenceService, RouteService
from skyguard.apps.gps.models import GPSDevice


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tracking_dashboard(request):
    """Dashboard for tracking functionality."""
    tracking_service = TrackingService(request.user)
    alert_service = AlertService(request.user)
    geofence_service = GeofenceService(request.user)
    
    # Get user's devices
    devices = GPSDevice.objects.filter(owner=request.user, is_active=True)
    
    # Get active sessions
    active_sessions = tracking_service.get_user_sessions(status='ACTIVE')
    
    # Get recent alerts
    recent_alerts = alert_service.get_user_alerts(acknowledged=False)[:10]
    
    # Get geofences
    geofences = geofence_service.get_user_geofences()
    
    context = {
        'devices': devices,
        'active_sessions': active_sessions,
        'recent_alerts': recent_alerts,
        'geofences': geofences,
    }
    
    return Response(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_tracking(request):
    """Start a new tracking session."""
    try:
        device_imei = request.data.get('device_imei')
        session_id = request.data.get('session_id')
        
        if not device_imei:
            return Response(
                {'error': 'device_imei is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        device = get_object_or_404(GPSDevice, imei=device_imei, owner=request.user)
        
        tracking_service = TrackingService(request.user)
        session = tracking_service.create_session(device, session_id)
        
        return Response({
            'session_id': session.session_id,
            'device_name': device.name,
            'start_time': session.start_time,
            'status': session.status
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_tracking(request):
    """Stop a tracking session."""
    try:
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = get_object_or_404(TrackingSession, session_id=session_id, user=request.user)
        
        tracking_service = TrackingService(request.user)
        success = tracking_service.stop_session(session)
        
        if success:
            return Response({
                'session_id': session.session_id,
                'end_time': session.end_time,
                'status': session.status,
                'total_distance': session.total_distance,
                'average_speed': session.average_speed,
                'max_speed': session.max_speed
            })
        else:
            return Response(
                {'error': 'Session is already completed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause_tracking(request):
    """Pause a tracking session."""
    try:
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = get_object_or_404(TrackingSession, session_id=session_id, user=request.user)
        
        tracking_service = TrackingService(request.user)
        success = tracking_service.pause_session(session)
        
        if success:
            return Response({
                'session_id': session.session_id,
                'status': session.status
            })
        else:
            return Response(
                {'error': 'Session cannot be paused'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume_tracking(request):
    """Resume a tracking session."""
    try:
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'session_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = get_object_or_404(TrackingSession, session_id=session_id, user=request.user)
        
        tracking_service = TrackingService(request.user)
        success = tracking_service.resume_session(session)
        
        if success:
            return Response({
                'session_id': session.session_id,
                'status': session.status
            })
        else:
            return Response(
                {'error': 'Session cannot be resumed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_tracking_point(request):
    """Add a tracking point to a session."""
    try:
        session_id = request.data.get('session_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        speed = request.data.get('speed', 0)
        course = request.data.get('course', 0)
        altitude = request.data.get('altitude', 0)
        accuracy = request.data.get('accuracy', 0)
        satellites = request.data.get('satellites', 0)
        
        if not all([session_id, latitude, longitude]):
            return Response(
                {'error': 'session_id, latitude, and longitude are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = get_object_or_404(TrackingSession, session_id=session_id, user=request.user)
        
        position = Point(float(longitude), float(latitude))
        
        tracking_service = TrackingService(request.user)
        point = tracking_service.add_point(
            session=session,
            position=position,
            speed=float(speed),
            course=float(course),
            altitude=float(altitude),
            accuracy=float(accuracy),
            satellites=int(satellites)
        )
        
        return Response({
            'point_id': point.id,
            'timestamp': point.timestamp,
            'position': {
                'latitude': point.position.y,
                'longitude': point.position.x
            },
            'speed': point.speed,
            'course': point.course
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_points(request, session_id):
    """Get tracking points for a session."""
    try:
        session = get_object_or_404(TrackingSession, session_id=session_id, user=request.user)
        
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        
        tracking_service = TrackingService(request.user)
        points = tracking_service.get_session_points(session, start_time, end_time)
        
        points_data = []
        for point in points:
            points_data.append({
                'id': point.id,
                'timestamp': point.timestamp,
                'position': {
                    'latitude': point.position.y,
                    'longitude': point.position.x
                },
                'speed': point.speed,
                'course': point.course,
                'altitude': point.altitude,
                'accuracy': point.accuracy,
                'satellites': point.satellites
            })
        
        return Response({
            'session_id': session_id,
            'points': points_data,
            'total_points': len(points_data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_events(request, session_id):
    """Get events for a session."""
    try:
        session = get_object_or_404(TrackingSession, session_id=session_id, user=request.user)
        
        tracking_service = TrackingService(request.user)
        events = tracking_service.get_session_events(session)
        
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'event_type': event.event_type,
                'timestamp': event.timestamp,
                'message': event.message,
                'data': event.data
            })
        
        return Response({
            'session_id': session_id,
            'events': events_data,
            'total_events': len(events_data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_sessions(request):
    """Get tracking sessions for the current user."""
    try:
        status_filter = request.GET.get('status')
        
        tracking_service = TrackingService(request.user)
        sessions = tracking_service.get_user_sessions(status=status_filter)
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'session_id': session.session_id,
                'device_name': session.device.name,
                'device_imei': session.device.imei,
                'status': session.status,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'total_distance': session.total_distance,
                'average_speed': session.average_speed,
                'max_speed': session.max_speed,
                'duration': session.duration.total_seconds() if session.duration else None
            })
        
        return Response({
            'sessions': sessions_data,
            'total_sessions': len(sessions_data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_device_sessions(request, device_imei):
    """Get tracking sessions for a specific device."""
    try:
        device = get_object_or_404(GPSDevice, imei=device_imei, owner=request.user)
        
        status_filter = request.GET.get('status')
        
        tracking_service = TrackingService(request.user)
        sessions = tracking_service.get_device_sessions(device, status=status_filter)
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'session_id': session.session_id,
                'status': session.status,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'total_distance': session.total_distance,
                'average_speed': session.average_speed,
                'max_speed': session.max_speed,
                'duration': session.duration.total_seconds() if session.duration else None
            })
        
        return Response({
            'device_imei': device_imei,
            'device_name': device.name,
            'sessions': sessions_data,
            'total_sessions': len(sessions_data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acknowledge_alert(request, alert_id):
    """Acknowledge an alert."""
    try:
        alert = get_object_or_404(Alert, id=alert_id)
        
        # Check if user has access to the device
        if alert.device.owner != request.user:
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        alert_service = AlertService(request.user)
        success = alert_service.acknowledge_alert(alert)
        
        if success:
            return Response({
                'alert_id': alert_id,
                'acknowledged': True,
                'acknowledged_at': alert.acknowledged_at
            })
        else:
            return Response(
                {'error': 'Alert is already acknowledged'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_device_alerts(request, device_imei):
    """Get alerts for a specific device."""
    try:
        device = get_object_or_404(GPSDevice, imei=device_imei, owner=request.user)
        
        acknowledged = request.GET.get('acknowledged')
        if acknowledged is not None:
            acknowledged = acknowledged.lower() == 'true'
        
        alert_service = AlertService(request.user)
        alerts = alert_service.get_device_alerts(device, acknowledged=acknowledged)
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'is_acknowledged': alert.is_acknowledged,
                'acknowledged_by': alert.acknowledged_by.username if alert.acknowledged_by else None,
                'acknowledged_at': alert.acknowledged_at,
                'created_at': alert.created_at,
                'position': {
                    'latitude': alert.position.y,
                    'longitude': alert.position.x
                } if alert.position else None
            })
        
        return Response({
            'device_imei': device_imei,
            'device_name': device.name,
            'alerts': alerts_data,
            'total_alerts': len(alerts_data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_alerts(request):
    """Get alerts for the current user's devices."""
    try:
        acknowledged = request.GET.get('acknowledged')
        if acknowledged is not None:
            acknowledged = acknowledged.lower() == 'true'
        
        alert_service = AlertService(request.user)
        alerts = alert_service.get_user_alerts(acknowledged=acknowledged)
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'device_name': alert.device.name,
                'device_imei': alert.device.imei,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'is_acknowledged': alert.is_acknowledged,
                'acknowledged_by': alert.acknowledged_by.username if alert.acknowledged_by else None,
                'acknowledged_at': alert.acknowledged_at,
                'created_at': alert.created_at,
                'position': {
                    'latitude': alert.position.y,
                    'longitude': alert.position.x
                } if alert.position else None
            })
        
        return Response({
            'alerts': alerts_data,
            'total_alerts': len(alerts_data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_geofences(request):
    """Get geofences for the current user."""
    try:
        geofence_service = GeofenceService(request.user)
        geofences = geofence_service.get_user_geofences()
        
        geofences_data = []
        for geofence in geofences:
            geofences_data.append({
                'id': geofence.id,
                'name': geofence.name,
                'description': geofence.description,
                'is_active': geofence.is_active,
                'created_at': geofence.created_at,
                'updated_at': geofence.updated_at
            })
        
        return Response({
            'geofences': geofences_data,
            'total_geofences': len(geofences_data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_device_geofences(request, device_imei):
    """Check which geofences a device is currently in."""
    try:
        device = get_object_or_404(GPSDevice, imei=device_imei, owner=request.user)
        
        geofence_service = GeofenceService(request.user)
        geofences = geofence_service.get_device_geofences(device)
        
        geofences_data = []
        for geofence in geofences:
            geofences_data.append({
                'id': geofence.id,
                'name': geofence.name,
                'description': geofence.description
            })
        
        return Response({
            'device_imei': device_imei,
            'device_name': device.name,
            'geofences': geofences_data,
            'total_geofences': len(geofences_data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
