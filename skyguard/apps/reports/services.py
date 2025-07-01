from django.db.models import Q, Avg, Sum, Count
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import json
import csv
from io import StringIO
from typing import List, Dict, Any, Optional
from .models import Route, Driver, Ticket, TimeSheet, GeoFence, Statistics, SensorData
from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent

class ReportService:
    """Servicio principal para generación de reportes"""
    
    @staticmethod
    def get_device_statistics(device_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Obtiene estadísticas de un dispositivo para un rango de fechas"""
        try:
            device = GPSDevice.objects.get(id=device_id)
            
            # Obtener ubicaciones en el rango de fechas
            locations = GPSLocation.objects.filter(
                device=device,
                timestamp__date__range=[start_date, end_date]
            ).order_by('timestamp')
            
            if not locations:
                return {
                    'device': device,
                    'total_locations': 0,
                    'total_distance': 0,
                    'avg_speed': 0,
                    'first_location': None,
                    'last_location': None
                }
            
            # Calcular distancia total
            total_distance = 0
            speeds = []
            
            for i in range(1, len(locations)):
                prev_loc = locations[i-1]
                curr_loc = locations[i]
                
                # Calcular distancia entre puntos
                if prev_loc.latitude and prev_loc.longitude and curr_loc.latitude and curr_loc.longitude:
                    p1 = Point(prev_loc.longitude, prev_loc.latitude)
                    p2 = Point(curr_loc.longitude, curr_loc.latitude)
                    distance = p1.distance(p2) * 111  # Convertir a km (aproximado)
                    total_distance += distance
                
                # Calcular velocidad si hay timestamp
                if prev_loc.timestamp and curr_loc.timestamp:
                    time_diff = (curr_loc.timestamp - prev_loc.timestamp).total_seconds() / 3600  # horas
                    if time_diff > 0:
                        speed = distance / time_diff if distance > 0 else 0
                        speeds.append(speed)
            
            avg_speed = sum(speeds) / len(speeds) if speeds else 0
            
            return {
                'device': device,
                'total_locations': len(locations),
                'total_distance': round(total_distance, 2),
                'avg_speed': round(avg_speed, 2),
                'first_location': locations.first(),
                'last_location': locations.last(),
                'date_range': f"{start_date} - {end_date}"
            }
            
        except GPSDevice.DoesNotExist:
            raise ValueError(f"Dispositivo con ID {device_id} no encontrado")
    
    @staticmethod
    def get_route_report(route_code: int, report_date: date) -> Dict[str, Any]:
        """Genera reporte por ruta para una fecha específica"""
        try:
            route = Route.objects.get(code=route_code)
            
            # Obtener dispositivos de la ruta
            devices = GPSDevice.objects.filter(route_code=route_code)
            
            # Obtener tickets del día
            tickets = Ticket.objects.filter(
                route=route,
                date__date=report_date
            )
            
            # Obtener horarios del día
            timesheets = TimeSheet.objects.filter(
                device__in=devices,
                date=report_date
            )
            
            # Calcular estadísticas
            total_tickets = tickets.count()
            total_revenue = tickets.aggregate(total=Sum('total'))['total'] or 0
            total_received = tickets.aggregate(total=Sum('received'))['total'] or 0
            total_laps = timesheets.aggregate(total=Sum('laps'))['total'] or 0
            
            return {
                'route': route,
                'date': report_date,
                'devices_count': devices.count(),
                'tickets_count': total_tickets,
                'total_revenue': total_revenue,
                'total_received': total_received,
                'total_laps': total_laps,
                'tickets': tickets,
                'timesheets': timesheets
            }
            
        except Route.DoesNotExist:
            raise ValueError(f"Ruta con código {route_code} no encontrada")
    
    @staticmethod
    def get_driver_report(driver_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Genera reporte de conductor para un rango de fechas"""
        try:
            driver = Driver.objects.get(id=driver_id)
            
            # Obtener tickets del conductor
            tickets = Ticket.objects.filter(
                driver=driver,
                date__date__range=[start_date, end_date]
            )
            
            # Obtener horarios del conductor
            timesheets = TimeSheet.objects.filter(
                driver=driver,
                date__range=[start_date, end_date]
            )
            
            # Calcular estadísticas
            total_tickets = tickets.count()
            total_revenue = tickets.aggregate(total=Sum('total'))['total'] or 0
            total_laps = timesheets.aggregate(total=Sum('laps'))['total'] or 0
            avg_laps_per_day = total_laps / (end_date - start_date).days if (end_date - start_date).days > 0 else 0
            
            return {
                'driver': driver,
                'date_range': f"{start_date} - {end_date}",
                'total_tickets': total_tickets,
                'total_revenue': total_revenue,
                'total_laps': total_laps,
                'avg_laps_per_day': round(avg_laps_per_day, 2),
                'tickets': tickets,
                'timesheets': timesheets
            }
            
        except Driver.DoesNotExist:
            raise ValueError(f"Conductor con ID {driver_id} no encontrado")
    
    @staticmethod
    def get_geofence_events(geofence_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Obtiene eventos de entrada/salida de una cerca geográfica"""
        try:
            geofence = GeoFence.objects.get(id=geofence_id)
            
            # Obtener ubicaciones en el rango de fechas
            locations = GPSLocation.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).order_by('timestamp')
            
            events = []
            inside_fence = False
            
            for location in locations:
                if location.latitude and location.longitude:
                    point = Point(location.longitude, location.latitude)
                    currently_inside = geofence.fence.contains(point)
                    
                    if currently_inside != inside_fence:
                        events.append({
                            'device': location.device,
                            'timestamp': location.timestamp,
                            'event_type': 'enter' if currently_inside else 'exit',
                            'location': location
                        })
                        inside_fence = currently_inside
            
            return events
            
        except GeoFence.DoesNotExist:
            raise ValueError(f"Cerca geográfica con ID {geofence_id} no encontrada")
    
    @staticmethod
    def export_tickets_csv(route_code: int, report_date: date) -> str:
        """Exporta tickets de una ruta a formato CSV"""
        try:
            route = Route.objects.get(code=route_code)
            tickets = Ticket.objects.filter(
                route=route,
                date__date=report_date
            ).select_related('device', 'driver')
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Encabezados
            writer.writerow([
                'ID', 'Dispositivo', 'Conductor', 'Fecha', 'Total', 'Recibido', 'Diferencia'
            ])
            
            # Datos
            for ticket in tickets:
                writer.writerow([
                    ticket.id,
                    ticket.device.name,
                    f"{ticket.driver.middle} {ticket.driver.last} {ticket.driver.name}",
                    ticket.date.strftime('%Y-%m-%d %H:%M:%S'),
                    float(ticket.total),
                    float(ticket.received),
                    float(ticket.total - ticket.received)
                ])
            
            return output.getvalue()
            
        except Route.DoesNotExist:
            raise ValueError(f"Ruta con código {route_code} no encontrada")
    
    @staticmethod
    def calculate_daily_statistics(date: date) -> List[Dict[str, Any]]:
        """Calcula estadísticas diarias para todos los dispositivos"""
        devices = GPSDevice.objects.all()
        statistics = []
        
        for device in devices:
            try:
                # Obtener ubicaciones del día
                locations = GPSLocation.objects.filter(
                    device=device,
                    timestamp__date=date
                ).order_by('timestamp')
                
                if locations:
                    # Calcular distancia
                    total_distance = 0
                    speeds = []
                    
                    for i in range(1, len(locations)):
                        prev_loc = locations[i-1]
                        curr_loc = locations[i]
                        
                        if prev_loc.latitude and prev_loc.longitude and curr_loc.latitude and curr_loc.longitude:
                            p1 = Point(prev_loc.longitude, prev_loc.latitude)
                            p2 = Point(curr_loc.longitude, curr_loc.latitude)
                            distance = p1.distance(p2) * 111
                            total_distance += distance
                            
                            if prev_loc.timestamp and curr_loc.timestamp:
                                time_diff = (curr_loc.timestamp - prev_loc.timestamp).total_seconds() / 3600
                                if time_diff > 0:
                                    speed = distance / time_diff if distance > 0 else 0
                                    speeds.append(speed)
                    
                    avg_speed = sum(speeds) / len(speeds) if speeds else 0
                    
                    # Crear o actualizar estadísticas
                    stats, created = Statistics.objects.get_or_create(
                        device=device,
                        date=date,
                        defaults={
                            'route_id': device.route_code,
                            'distance': round(total_distance, 2),
                            'avg_speed': round(avg_speed, 2)
                        }
                    )
                    
                    if not created:
                        stats.distance = round(total_distance, 2)
                        stats.avg_speed = round(avg_speed, 2)
                        stats.save()
                    
                    statistics.append({
                        'device': device,
                        'distance': round(total_distance, 2),
                        'avg_speed': round(avg_speed, 2),
                        'locations_count': len(locations)
                    })
                    
            except Exception as e:
                print(f"Error calculando estadísticas para dispositivo {device.id}: {e}")
                continue
        
        return statistics 