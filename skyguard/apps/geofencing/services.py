from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
from skyguard.apps.reports.models import GeoFence

class GeofencingService:
    """Servicio para gestión de cercas geográficas"""
    
    @staticmethod
    def create_geofence(name: str, coordinates: List[tuple], owner_id: int, route_id: Optional[int] = None) -> GeoFence:
        """
        Crea una nueva cerca geográfica
        
        Args:
            name: Nombre de la cerca
            coordinates: Lista de coordenadas [(lon, lat), (lon, lat), ...]
            owner_id: ID del propietario
            route_id: ID de la ruta (opcional)
        """
        try:
            # Crear polígono
            polygon = Polygon(coordinates)
            
            # Crear cerca geográfica
            geofence = GeoFence.objects.create(
                name=name,
                fence=polygon,
                owner_id=owner_id,
                route_id=route_id
            )
            
            return geofence
            
        except Exception as e:
            raise ValueError(f"Error creando cerca geográfica: {str(e)}")
    
    @staticmethod
    def check_device_in_geofence(device_id: int, geofence_id: int) -> bool:
        """
        Verifica si un dispositivo está dentro de una cerca geográfica
        
        Args:
            device_id: ID del dispositivo
            geofence_id: ID de la cerca geográfica
        """
        try:
            device = GPSDevice.objects.get(id=device_id)
            geofence = GeoFence.objects.get(id=geofence_id)
            
            if not device.current_location:
                return False
            
            point = Point(device.current_location.longitude, device.current_location.latitude)
            return geofence.fence.contains(point)
            
        except (GPSDevice.DoesNotExist, GeoFence.DoesNotExist):
            return False
    
    @staticmethod
    def get_devices_in_geofence(geofence_id: int) -> List[GPSDevice]:
        """
        Obtiene todos los dispositivos dentro de una cerca geográfica
        
        Args:
            geofence_id: ID de la cerca geográfica
        """
        try:
            geofence = GeoFence.objects.get(id=geofence_id)
            
            # Obtener dispositivos con ubicación actual
            devices = GPSDevice.objects.filter(
                current_location__isnull=False
            )
            
            devices_in_fence = []
            for device in devices:
                if device.current_location:
                    point = Point(device.current_location.longitude, device.current_location.latitude)
                    if geofence.fence.contains(point):
                        devices_in_fence.append(device)
            
            return devices_in_fence
            
        except GeoFence.DoesNotExist:
            return []
    
    @staticmethod
    def get_geofence_events(geofence_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Obtiene eventos de entrada/salida de una cerca geográfica
        
        Args:
            geofence_id: ID de la cerca geográfica
            start_date: Fecha de inicio
            end_date: Fecha de fin
        """
        try:
            geofence = GeoFence.objects.get(id=geofence_id)
            
            # Obtener ubicaciones en el rango de fechas
            locations = GPSLocation.objects.filter(
                timestamp__range=[start_date, end_date]
            ).order_by('device', 'timestamp')
            
            events = []
            device_states = {}  # Estado de cada dispositivo
            
            for location in locations:
                if location.latitude and location.longitude:
                    point = Point(location.longitude, location.latitude)
                    currently_inside = geofence.fence.contains(point)
                    
                    # Verificar cambio de estado
                    device_id = location.device.id
                    previous_state = device_states.get(device_id, None)
                    
                    if previous_state is not None and previous_state != currently_inside:
                        events.append({
                            'device': location.device,
                            'timestamp': location.timestamp,
                            'event_type': 'enter' if currently_inside else 'exit',
                            'location': location,
                            'coordinates': {
                                'latitude': location.latitude,
                                'longitude': location.longitude
                            }
                        })
                    
                    device_states[device_id] = currently_inside
            
            return events
            
        except GeoFence.DoesNotExist:
            return []
    
    @staticmethod
    def create_geofence_event(device_id: int, geofence_id: int, event_type: str, location_id: int) -> GPSEvent:
        """
        Crea un evento de cerca geográfica
        
        Args:
            device_id: ID del dispositivo
            geofence_id: ID de la cerca geográfica
            event_type: Tipo de evento ('enter' o 'exit')
            location_id: ID de la ubicación
        """
        try:
            device = GPSDevice.objects.get(id=device_id)
            geofence = GeoFence.objects.get(id=geofence_id)
            location = GPSLocation.objects.get(id=location_id)
            
            event = GPSEvent.objects.create(
                device=device,
                event_type=f"GEOFENCE_{event_type.upper()}",
                location=location,
                timestamp=location.timestamp,
                data={
                    'geofence_id': geofence_id,
                    'geofence_name': geofence.name,
                    'event_type': event_type
                }
            )
            
            return event
            
        except (GPSDevice.DoesNotExist, GeoFence.DoesNotExist, GPSLocation.DoesNotExist):
            raise ValueError("Dispositivo, cerca geográfica o ubicación no encontrada")
    
    @staticmethod
    def get_geofences_by_route(route_id: int) -> List[GeoFence]:
        """
        Obtiene todas las cercas geográficas de una ruta
        
        Args:
            route_id: ID de la ruta
        """
        return GeoFence.objects.filter(route_id=route_id)
    
    @staticmethod
    def get_geofences_by_owner(owner_id: int) -> List[GeoFence]:
        """
        Obtiene todas las cercas geográficas de un propietario
        
        Args:
            owner_id: ID del propietario
        """
        return GeoFence.objects.filter(owner_id=owner_id)
    
    @staticmethod
    def update_geofence(geofence_id: int, name: Optional[str] = None, 
                       coordinates: Optional[List[tuple]] = None) -> GeoFence:
        """
        Actualiza una cerca geográfica
        
        Args:
            geofence_id: ID de la cerca geográfica
            name: Nuevo nombre (opcional)
            coordinates: Nuevas coordenadas (opcional)
        """
        try:
            geofence = GeoFence.objects.get(id=geofence_id)
            
            if name:
                geofence.name = name
            
            if coordinates:
                polygon = Polygon(coordinates)
                geofence.fence = polygon
            
            geofence.save()
            return geofence
            
        except GeoFence.DoesNotExist:
            raise ValueError(f"Cerca geográfica con ID {geofence_id} no encontrada")
    
    @staticmethod
    def delete_geofence(geofence_id: int) -> bool:
        """
        Elimina una cerca geográfica
        
        Args:
            geofence_id: ID de la cerca geográfica
        """
        try:
            geofence = GeoFence.objects.get(id=geofence_id)
            geofence.delete()
            return True
            
        except GeoFence.DoesNotExist:
            return False
    
    @staticmethod
    def get_geofence_statistics(geofence_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Obtiene estadísticas de una cerca geográfica
        
        Args:
            geofence_id: ID de la cerca geográfica
            start_date: Fecha de inicio
            end_date: Fecha de fin
        """
        try:
            geofence = GeoFence.objects.get(id=geofence_id)
            
            # Obtener eventos
            events = GeofencingService.get_geofence_events(geofence_id, start_date, end_date)
            
            # Calcular estadísticas
            enter_events = [e for e in events if e['event_type'] == 'enter']
            exit_events = [e for e in events if e['event_type'] == 'exit']
            
            # Dispositivos únicos
            unique_devices = set(e['device'].id for e in events)
            
            # Dispositivos actualmente dentro
            devices_currently_inside = GeofencingService.get_devices_in_geofence(geofence_id)
            
            return {
                'geofence': geofence,
                'date_range': f"{start_date.date()} - {end_date.date()}",
                'total_events': len(events),
                'enter_events': len(enter_events),
                'exit_events': len(exit_events),
                'unique_devices': len(unique_devices),
                'devices_currently_inside': len(devices_currently_inside),
                'events': events
            }
            
        except GeoFence.DoesNotExist:
            return {}
    
    @staticmethod
    def monitor_geofences() -> List[Dict[str, Any]]:
        """
        Monitorea todas las cercas geográficas activas
        """
        geofences = GeoFence.objects.all()
        monitoring_data = []
        
        for geofence in geofences:
            try:
                devices_inside = GeofencingService.get_devices_in_geofence(geofence.id)
                
                monitoring_data.append({
                    'geofence': geofence,
                    'devices_inside': len(devices_inside),
                    'devices_list': devices_inside,
                    'last_checked': timezone.now()
                })
                
            except Exception as e:
                monitoring_data.append({
                    'geofence': geofence,
                    'error': str(e),
                    'last_checked': timezone.now()
                })
        
        return monitoring_data 