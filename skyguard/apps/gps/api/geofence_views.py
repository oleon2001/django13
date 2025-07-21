"""
Enhanced Geofence API Views with comprehensive functionality.
"""
import logging
from typing import Dict, Any, List
from django.contrib.auth.models import User
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from skyguard.apps.gps.models import GPSDevice, GeoFence, GeoFenceEvent
from skyguard.apps.gps.serializers import GeoFenceSerializer, GeoFenceEventSerializer
from skyguard.apps.gps.services.geofence_manager import advanced_geofence_manager
from skyguard.apps.gps.services.geofence_service import geofence_detection_service

logger = logging.getLogger(__name__)


class GeofencePagination(PageNumberPagination):
    """Custom pagination for geofence lists."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class GeofenceViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for Geofence management."""
    
    serializer_class = GeoFenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = GeofencePagination
    
    def get_queryset(self):
        """Get geofences for the current user."""
        user = self.request.user
        
        # Use advanced manager for permission-aware queries
        geofences = advanced_geofence_manager.get_user_geofences(
            user, 
            include_inactive=self.request.query_params.get('include_inactive', 'false').lower() == 'true'
        )
        
        # Apply filters
        name = self.request.query_params.get('name')
        if name:
            geofences = [g for g in geofences if name.lower() in g.name.lower()]
        
        device_imei = self.request.query_params.get('device')
        if device_imei:
            geofences = [g for g in geofences if g.devices.filter(imei=device_imei).exists()]
        
        return geofences
    
    def create(self, request, *args, **kwargs):
        """Create a new geofence with enhanced validation."""
        try:
            data = request.data
            
            # Extract required fields
            name = data.get('name')
            geometry_data = data.get('geometry')
            device_ids = data.get('devices', [])
            
            if not name:
                return Response(
                    {'error': 'Name is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not geometry_data:
                return Response(
                    {'error': 'Geometry is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse geometry
            try:
                if isinstance(geometry_data, dict):
                    # GeoJSON format
                    geometry = GEOSGeometry(str(geometry_data))
                else:
                    # WKT format
                    geometry = GEOSGeometry(geometry_data)
                
                if not isinstance(geometry, Polygon):
                    return Response(
                        {'error': 'Geometry must be a polygon'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                return Response(
                    {'error': f'Invalid geometry: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get devices
            devices = []
            if device_ids:
                devices = GPSDevice.objects.filter(
                    Q(imei__in=device_ids) | Q(id__in=device_ids)
                )
                if len(devices) != len(device_ids):
                    return Response(
                        {'error': 'Some devices not found'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Create geofence using advanced manager
            geofence = advanced_geofence_manager.create_geofence(
                user=request.user,
                name=name,
                geometry=geometry,
                devices=devices,
                description=data.get('description', ''),
                is_active=data.get('is_active', True),
                notify_on_entry=data.get('notify_on_entry', True),
                notify_on_exit=data.get('notify_on_exit', True),
                alert_on_entry=data.get('alert_on_entry', False),
                alert_on_exit=data.get('alert_on_exit', False),
                notification_cooldown=data.get('notification_cooldown', 300),
                notify_emails=data.get('notify_emails', []),
                notify_sms=data.get('notify_sms', []),
                color=data.get('color', '#3388ff'),
                stroke_color=data.get('stroke_color', '#3388ff'),
                stroke_width=data.get('stroke_width', 2)
            )
            
            # Get notification owners if specified
            notify_owner_ids = data.get('notify_owners', [])
            if notify_owner_ids:
                notify_owners = User.objects.filter(id__in=notify_owner_ids)
                geofence.notify_owners.set(notify_owners)
            
            serializer = self.get_serializer(geofence)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Error creating geofence: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete a geofence with permission checking."""
        try:
            geofence_id = kwargs.get('pk')
            success = advanced_geofence_manager.delete_geofence(request.user, geofence_id)
            
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'Failed to delete geofence'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Error deleting geofence: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get comprehensive geofence metrics."""
        try:
            time_window = int(request.query_params.get('hours', 24))
            metrics = advanced_geofence_manager.generate_geofence_metrics(
                request.user, 
                time_window
            )
            
            return Response({
                'total_geofences': metrics.total_geofences,
                'active_geofences': metrics.active_geofences,
                'entry_events_24h': metrics.entry_events_24h,
                'exit_events_24h': metrics.exit_events_24h,
                'most_active_devices': metrics.most_active_devices,
                'violation_rate': metrics.violation_rate,
                'average_dwell_time': metrics.average_dwell_time,
                'performance_score': metrics.performance_score,
                'time_window_hours': time_window
            })
            
        except Exception as e:
            logger.error(f"Error generating geofence metrics: {e}")
            return Response(
                {'error': 'Failed to generate metrics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def check_devices(self, request, pk=None):
        """Manually trigger geofence check for all devices."""
        try:
            geofence = self.get_object()
            results = []
            
            for device in geofence.devices.filter(position__isnull=False):
                events = advanced_geofence_manager.check_device_geofences(
                    device, 
                    force_check=True
                )
                results.append({
                    'device_imei': device.imei,
                    'device_name': device.name,
                    'events_generated': len(events),
                    'events': events
                })
            
            return Response({
                'geofence_id': geofence.id,
                'geofence_name': geofence.name,
                'devices_checked': len(results),
                'results': results
            })
            
        except Exception as e:
            logger.error(f"Error checking devices for geofence {pk}: {e}")
            return Response(
                {'error': 'Failed to check devices'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Get events for a specific geofence."""
        try:
            geofence = self.get_object()
            
            # Get query parameters
            days_back = int(request.query_params.get('days', 7))
            device_imei = request.query_params.get('device')
            event_type = request.query_params.get('type')
            
            since = timezone.now() - timezone.timedelta(days=days_back)
            
            events = GeoFenceEvent.objects.filter(
                fence=geofence,
                timestamp__gte=since
            ).select_related('device')
            
            if device_imei:
                events = events.filter(device__imei=device_imei)
            
            if event_type and event_type.upper() in ['ENTRY', 'EXIT']:
                events = events.filter(event_type=event_type.upper())
            
            events = events.order_by('-timestamp')
            
            # Apply pagination
            page = self.paginate_queryset(events)
            if page is not None:
                serializer = GeoFenceEventSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = GeoFenceEventSerializer(events, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting events for geofence {pk}: {e}")
            return Response(
                {'error': 'Failed to get events'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get detailed analytics for a specific geofence."""
        try:
            geofence = self.get_object()
            days_back = int(request.query_params.get('days', 7))
            
            # Get events for analysis
            since = timezone.now() - timezone.timedelta(days=days_back)
            events = GeoFenceEvent.objects.filter(
                fence=geofence,
                timestamp__gte=since
            ).select_related('device').order_by('timestamp')
            
            # Basic statistics
            total_events = events.count()
            entry_events = events.filter(event_type='ENTRY').count()
            exit_events = events.filter(event_type='EXIT').count()
            unique_devices = events.values('device').distinct().count()
            
            # Calculate average dwell time
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
            
            average_dwell_time = sum(dwell_times) / len(dwell_times) if dwell_times else 0
            
            # Most active devices
            device_activity = events.values(
                'device__imei', 'device__name'
            ).annotate(
                event_count=models.Count('id')
            ).order_by('-event_count')[:5]
            
            # Hourly distribution
            hourly_distribution = {}
            for event in events:
                hour = event.timestamp.hour
                hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
            
            return Response({
                'geofence_id': geofence.id,
                'geofence_name': geofence.name,
                'analysis_period_days': days_back,
                'statistics': {
                    'total_events': total_events,
                    'entry_events': entry_events,
                    'exit_events': exit_events,
                    'unique_devices': unique_devices,
                    'average_dwell_time_seconds': average_dwell_time
                },
                'most_active_devices': list(device_activity),
                'hourly_distribution': hourly_distribution,
                'dwell_times': dwell_times[:10]  # Sample of dwell times
            })
            
        except Exception as e:
            logger.error(f"Error generating analytics for geofence {pk}: {e}")
            return Response(
                {'error': 'Failed to generate analytics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GeofenceEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing geofence events."""
    
    serializer_class = GeoFenceEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = GeofencePagination
    
    def get_queryset(self):
        """Get geofence events for the current user."""
        user = self.request.user
        
        # Base query - user can see events for their geofences or devices
        queryset = GeoFenceEvent.objects.filter(
            Q(fence__owner=user) | Q(device__owner=user)
        ).select_related('fence', 'device').distinct()
        
        # Apply filters
        device_imei = self.request.query_params.get('device')
        if device_imei:
            queryset = queryset.filter(device__imei=device_imei)
        
        geofence_id = self.request.query_params.get('geofence')
        if geofence_id:
            queryset = queryset.filter(fence__id=geofence_id)
        
        event_type = self.request.query_params.get('type')
        if event_type and event_type.upper() in ['ENTRY', 'EXIT']:
            queryset = queryset.filter(event_type=event_type.upper())
        
        # Date filters
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
        if from_date:
            try:
                from_datetime = timezone.datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__gte=from_datetime)
            except ValueError:
                pass
        
        if to_date:
            try:
                to_datetime = timezone.datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__lte=to_datetime)
            except ValueError:
                pass
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary of recent geofence events."""
        try:
            # Get events from last 24 hours
            since = timezone.now() - timezone.timedelta(hours=24)
            events = self.get_queryset().filter(timestamp__gte=since)
            
            total_events = events.count()
            entry_events = events.filter(event_type='ENTRY').count()
            exit_events = events.filter(event_type='EXIT').count()
            
            # Most active geofences
            active_geofences = events.values(
                'fence__id', 'fence__name'
            ).annotate(
                event_count=models.Count('id')
            ).order_by('-event_count')[:5]
            
            # Most active devices
            active_devices = events.values(
                'device__imei', 'device__name'
            ).annotate(
                event_count=models.Count('id')
            ).order_by('-event_count')[:5]
            
            return Response({
                'period': '24 hours',
                'total_events': total_events,
                'entry_events': entry_events,
                'exit_events': exit_events,
                'most_active_geofences': list(active_geofences),
                'most_active_devices': list(active_devices)
            })
            
        except Exception as e:
            logger.error(f"Error generating event summary: {e}")
            return Response(
                {'error': 'Failed to generate summary'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeviceGeofenceAnalyticsViewSet(viewsets.GenericViewSet):
    """ViewSet for device-specific geofence analytics."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def behavior_analysis(self, request, pk=None):
        """Get behavioral analysis for a specific device."""
        try:
            device = GPSDevice.objects.get(
                Q(imei=pk) | Q(id=pk),
                Q(owner=request.user) | Q(geofences__owner=request.user)
            )
            
            days_back = int(request.query_params.get('days', 7))
            analysis = advanced_geofence_manager.analyzer.analyze_device_behavior(
                device, 
                days_back
            )
            
            return Response({
                'device_imei': device.imei,
                'device_name': device.name,
                'analysis_period_days': days_back,
                'analysis': analysis
            })
            
        except GPSDevice.DoesNotExist:
            return Response(
                {'error': 'Device not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error analyzing device behavior: {e}")
            return Response(
                {'error': 'Failed to analyze device behavior'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def check_geofences(self, request, pk=None):
        """Manually check geofences for a specific device."""
        try:
            device = GPSDevice.objects.get(
                Q(imei=pk) | Q(id=pk),
                owner=request.user
            )
            
            events = advanced_geofence_manager.check_device_geofences(
                device, 
                force_check=True
            )
            
            return Response({
                'device_imei': device.imei,
                'device_name': device.name,
                'position': [device.position.y, device.position.x] if device.position else None,
                'events_generated': len(events),
                'events': events,
                'timestamp': timezone.now().isoformat()
            })
            
        except GPSDevice.DoesNotExist:
            return Response(
                {'error': 'Device not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error checking device geofences: {e}")
            return Response(
                {'error': 'Failed to check device geofences'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 