"""
Views for geofence management.
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .models import GeoFence, GeoFenceEvent, GPSDevice
from .serializers import GeoFenceSerializer, GeoFenceEventSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def geofence_list(request):
    """
    List all geofences or create a new one.
    """
    if request.method == 'GET':
        # Get query parameters for filtering
        is_active = request.GET.get('is_active')
        device_id = request.GET.get('device_id')
        search = request.GET.get('search')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Start with user's geofences
        geofences = GeoFence.objects.filter(owner=request.user)
        
        # Apply filters
        if is_active is not None:
            geofences = geofences.filter(is_active=is_active.lower() == 'true')
        
        if device_id:
            geofences = geofences.filter(devices__imei=device_id)
        
        if search:
            geofences = geofences.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        if start_date:
            geofences = geofences.filter(created_at__gte=start_date)
        
        if end_date:
            geofences = geofences.filter(created_at__lte=end_date)
        
        # Serialize and return
        serializer = GeoFenceSerializer(geofences, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Create new geofence
        serializer = GeoFenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def geofence_detail(request, geofence_id):
    """
    Retrieve, update or delete a geofence.
    """
    geofence = get_object_or_404(GeoFence, id=geofence_id, owner=request.user)
    
    if request.method == 'GET':
        serializer = GeoFenceSerializer(geofence)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = GeoFenceSerializer(geofence, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        geofence.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def geofence_events(request, geofence_id):
    """
    Get events for a specific geofence.
    """
    geofence = get_object_or_404(GeoFence, id=geofence_id, owner=request.user)
    
    # Get query parameters
    device_id = request.GET.get('device_id')
    event_type = request.GET.get('event_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    limit = int(request.GET.get('limit', 100))
    offset = int(request.GET.get('offset', 0))
    
    events = GeoFenceEvent.objects.filter(fence=geofence)
    
    # Apply filters
    if device_id:
        events = events.filter(device__imei=device_id)
    
    if event_type:
        events = events.filter(event_type=event_type)
    
    if start_date:
        events = events.filter(timestamp__gte=start_date)
    
    if end_date:
        events = events.filter(timestamp__lte=end_date)
    
    # Apply pagination
    events = events[offset:offset + limit]
    
    serializer = GeoFenceEventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_point_in_geofence(request, geofence_id):
    """
    Check if a point is inside a geofence.
    """
    geofence = get_object_or_404(GeoFence, id=geofence_id, owner=request.user)
    
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    if not lat or not lng:
        return Response(
            {'error': 'Latitude and longitude are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return Response(
            {'error': 'Invalid coordinates'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if point is inside the geofence
    from django.contrib.gis.geos import Point
    point = Point(lng, lat)  # Note: Point takes (x, y) which is (lng, lat)
    inside = geofence.geometry.contains(point)
    
    return Response({'inside': inside})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_devices_to_geofence(request, geofence_id):
    """
    Assign devices to a geofence.
    """
    geofence = get_object_or_404(GeoFence, id=geofence_id, owner=request.user)
    
    device_ids = request.data.get('device_ids', [])
    
    if not isinstance(device_ids, list):
        return Response(
            {'error': 'device_ids must be a list'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get devices that belong to the user
    devices = GPSDevice.objects.filter(imei__in=device_ids, owner=request.user)
    
    # Assign devices to geofence
    geofence.devices.set(devices)
    
    return Response({'message': f'Assigned {devices.count()} devices to geofence'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_geofence_devices(request, geofence_id):
    """
    Get devices assigned to a geofence.
    """
    geofence = get_object_or_404(GeoFence, id=geofence_id, owner=request.user)
    
    devices = geofence.devices.all()
    device_ids = [device.imei for device in devices]
    
    return Response({'device_ids': device_ids})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def geofence_stats(request):
    """
    Get geofence statistics.
    """
    user = request.user
    
    # Get basic stats
    total_geofences = GeoFence.objects.filter(owner=user).count()
    active_geofences = GeoFence.objects.filter(owner=user, is_active=True).count()
    
    # Get recent events (last 24 hours)
    yesterday = timezone.now() - timedelta(days=1)
    recent_events = GeoFenceEvent.objects.filter(
        fence__owner=user,
        timestamp__gte=yesterday
    ).count()
    
    # Get recent events list
    recent_events_list = GeoFenceEvent.objects.filter(
        fence__owner=user
    ).order_by('-timestamp')[:10]
    
    events_serializer = GeoFenceEventSerializer(recent_events_list, many=True)
    
    stats = {
        'total_geofences': total_geofences,
        'active_geofences': active_geofences,
        'total_events_today': recent_events,
        'recent_events': events_serializer.data
    }
    
    return Response(stats) 