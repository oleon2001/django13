from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from datetime import datetime, date
from typing import Dict, Any
from .models import Route, Driver, Ticket, TimeSheet, GeoFence, Statistics, SensorData
from .services import ReportService
from .serializers import (
    RouteSerializer, DriverSerializer, TicketSerializer, 
    TimeSheetSerializer, GeoFenceSerializer, StatisticsSerializer
)

class RouteViewSet(viewsets.ModelViewSet):
    """API para gestión de rutas"""
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """Genera reporte de una ruta para una fecha específica"""
        try:
            route = self.get_object()
            report_date_str = request.query_params.get('date', date.today().isoformat())
            report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
            
            report_data = ReportService.get_route_report(route.code, report_date)
            
            return Response({
                'success': True,
                'data': report_data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def export_csv(self, request, pk=None):
        """Exporta reporte de ruta a CSV"""
        try:
            route = self.get_object()
            report_date_str = request.query_params.get('date', date.today().isoformat())
            report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
            
            csv_data = ReportService.export_tickets_csv(route.code, report_date)
            
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="ruta_{route.code}_{report_date}.csv"'
            
            return response
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class DriverViewSet(viewsets.ModelViewSet):
    """API para gestión de conductores"""
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """Genera reporte de un conductor para un rango de fechas"""
        try:
            driver = self.get_object()
            start_date_str = request.query_params.get('start_date', date.today().isoformat())
            end_date_str = request.query_params.get('end_date', date.today().isoformat())
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            report_data = ReportService.get_driver_report(driver.id, start_date, end_date)
            
            return Response({
                'success': True,
                'data': report_data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class TicketViewSet(viewsets.ModelViewSet):
    """API para gestión de tickets"""
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra tickets por parámetros de consulta"""
        queryset = Ticket.objects.all()
        
        # Filtros opcionales
        route_code = self.request.query_params.get('route_code')
        if route_code:
            queryset = queryset.filter(route__code=route_code)
        
        driver_id = self.request.query_params.get('driver_id')
        if driver_id:
            queryset = queryset.filter(driver_id=driver_id)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(date__date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(date__date__lte=date_to)
        
        return queryset.select_related('device', 'driver', 'route')

class TimeSheetViewSet(viewsets.ModelViewSet):
    """API para gestión de horarios"""
    queryset = TimeSheet.objects.all()
    serializer_class = TimeSheetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra horarios por parámetros de consulta"""
        queryset = TimeSheet.objects.all()
        
        device_id = self.request.query_params.get('device_id')
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        driver_id = self.request.query_params.get('driver_id')
        if driver_id:
            queryset = queryset.filter(driver_id=driver_id)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset.select_related('device', 'driver')

class GeoFenceViewSet(viewsets.ModelViewSet):
    """API para gestión de cercas geográficas"""
    queryset = GeoFence.objects.all()
    serializer_class = GeoFenceSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Obtiene eventos de entrada/salida de una cerca geográfica"""
        try:
            geofence = self.get_object()
            start_date_str = request.query_params.get('start_date', date.today().isoformat())
            end_date_str = request.query_params.get('end_date', date.today().isoformat())
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            events = ReportService.get_geofence_events(geofence.id, start_date, end_date)
            
            return Response({
                'success': True,
                'data': events
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class StatisticsViewSet(viewsets.ModelViewSet):
    """API para gestión de estadísticas"""
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calculate_daily(self, request):
        """Calcula estadísticas diarias para todos los dispositivos"""
        try:
            date_str = request.data.get('date', date.today().isoformat())
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            statistics = ReportService.calculate_daily_statistics(target_date)
            
            return Response({
                'success': True,
                'message': f'Estadísticas calculadas para {target_date}',
                'data': {
                    'date': target_date.isoformat(),
                    'devices_processed': len(statistics)
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def device_stats(self, request):
        """Obtiene estadísticas de un dispositivo específico"""
        try:
            device_id = request.query_params.get('device_id')
            start_date_str = request.query_params.get('start_date', date.today().isoformat())
            end_date_str = request.query_params.get('end_date', date.today().isoformat())
            
            if not device_id:
                return Response({
                    'success': False,
                    'error': 'device_id es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            stats = ReportService.get_device_statistics(int(device_id), start_date, end_date)
            
            return Response({
                'success': True,
                'data': stats
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ReportAPIViewSet(viewsets.ViewSet):
    """API para reportes generales"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Obtiene resumen general del sistema"""
        try:
            # Estadísticas generales
            total_devices = GPSDevice.objects.count()
            total_drivers = Driver.objects.count()
            total_routes = Route.objects.count()
            total_tickets_today = Ticket.objects.filter(
                date__date=date.today()
            ).count()
            
            # Dispositivos activos hoy
            active_devices_today = GPSLocation.objects.filter(
                timestamp__date=date.today()
            ).values('device').distinct().count()
            
            return Response({
                'success': True,
                'data': {
                    'total_devices': total_devices,
                    'total_drivers': total_drivers,
                    'total_routes': total_routes,
                    'tickets_today': total_tickets_today,
                    'active_devices_today': active_devices_today,
                    'date': date.today().isoformat()
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST) 