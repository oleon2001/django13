"""
API REST para el sistema de geofencing SkyGuard
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta

from .models import GeoFence
from .serializers import GeoFenceSerializer, GeofenceEventSerializer
from .services import GeofencingService


class GeofencingViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar geofences
    """
    queryset = GeoFence.objects.all()
    serializer_class = GeoFenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar geofences por propietario
        """
        queryset = GeoFence.objects.all()
        owner_id = self.request.query_params.get('owner_id', None)
        route_id = self.request.query_params.get('route_id', None)
        
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        if route_id:
            queryset = queryset.filter(route_id=route_id)
            
        return queryset

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """
        Obtener eventos de entrada/salida de un geofence
        """
        try:
            geofence = self.get_object()
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if not start_date:
                start_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = timezone.now().strftime('%Y-%m-%d')
            
            events = GeofencingService.get_geofence_events(
                geofence_id=geofence.id,
                start_date=start_date,
                end_date=end_date
            )
            
            serializer = GeofenceEventSerializer(events, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'geofence': GeoFenceSerializer(geofence).data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def devices_inside(self, request, pk=None):
        """
        Obtener dispositivos actualmente dentro del geofence
        """
        try:
            geofence = self.get_object()
            devices = GeofencingService.get_devices_in_geofence(geofence.id)
            
            return Response({
                'success': True,
                'data': devices,
                'geofence': GeoFenceSerializer(geofence).data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Obtener estadísticas del geofence
        """
        try:
            geofence = self.get_object()
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if not start_date:
                start_date = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = timezone.now().strftime('%Y-%m-%d')
            
            stats = GeofencingService.get_geofence_statistics(
                geofence_id=geofence.id,
                start_date=start_date,
                end_date=end_date
            )
            
            return Response({
                'success': True,
                'data': stats,
                'geofence': GeoFenceSerializer(geofence).data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def monitor(self, request):
        """
        Monitorear todos los geofences activos
        """
        try:
            monitoring_data = GeofencingService.monitor_geofences()
            
            return Response({
                'success': True,
                'data': monitoring_data,
                'timestamp': timezone.now()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def check_device(self, request):
        """
        Verificar si un dispositivo está dentro de un geofence
        """
        try:
            device_id = request.data.get('device_id')
            geofence_id = request.data.get('geofence_id')
            
            if not device_id or not geofence_id:
                return Response({
                    'success': False,
                    'error': 'device_id y geofence_id son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            is_inside = GeofencingService.check_device_in_geofence(
                device_id=device_id,
                geofence_id=geofence_id
            )
            
            return Response({
                'success': True,
                'device_id': device_id,
                'geofence_id': geofence_id,
                'is_inside': is_inside
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST) 