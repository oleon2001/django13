"""
Tareas de Celery para manejo automático de dispositivos GPS.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.db.models import Count, Avg, Q
from celery import shared_task
from skyguard.apps.gps.models.device import GPSDevice

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def check_devices_heartbeat(self, timeout_minutes=1):
    """
    Tarea periódica para verificar el heartbeat de los dispositivos y marcar como offline
    aquellos que no han enviado datos recientemente.
    
    Args:
        timeout_minutes (int): Minutos sin heartbeat para considerar un dispositivo offline
    """
    try:
        timeout_time = timezone.now() - timedelta(minutes=timeout_minutes)
        
        # Buscar dispositivos marcados como ONLINE pero sin heartbeat reciente
        stale_devices = GPSDevice.objects.filter(
            connection_status='ONLINE'
        ).filter(
            Q(last_heartbeat__isnull=True) | 
            Q(last_heartbeat__lt=timeout_time)
        )
        
        updated_count = 0
        for device in stale_devices:
            try:
                old_status = device.connection_status
                device.connection_status = 'OFFLINE'
                device.save()
                
                updated_count += 1
                
                # Log del cambio
                if device.last_heartbeat:
                    time_since = timezone.now() - device.last_heartbeat
                    logger.info(
                        f"Device {device.imei} ({device.name}) marked as OFFLINE - "
                        f"last heartbeat {time_since.total_seconds():.0f}s ago"
                    )
                else:
                    logger.info(
                        f"Device {device.imei} ({device.name}) marked as OFFLINE - "
                        f"no heartbeat recorded"
                    )
                    
            except Exception as e:
                logger.error(f"Error updating device {device.imei}: {e}")
        
        # Estadísticas finales
        total_online = GPSDevice.objects.filter(connection_status='ONLINE').count()
        total_offline = GPSDevice.objects.filter(connection_status='OFFLINE').count()
        
        result = {
            'devices_checked': stale_devices.count(),
            'devices_marked_offline': updated_count,
            'total_online': total_online,
            'total_offline': total_offline,
            'timeout_minutes': timeout_minutes
        }
        
        logger.info(
            f"Heartbeat check completed: {updated_count} devices marked offline, "
            f"{total_online} online, {total_offline} offline"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in check_devices_heartbeat task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def cleanup_old_device_sessions(self, days_old=7):
    """
    Limpia sesiones de dispositivos antiguas.
    
    Args:
        days_old (int): Días de antigüedad para considerar una sesión como antigua
    """
    try:
        from skyguard.apps.gps.models.protocols import UDPSession
        
        cutoff_time = timezone.now() - timedelta(days=days_old)
        
        # Eliminar sesiones expiradas
        old_sessions = UDPSession.objects.filter(expires__lt=cutoff_time)
        count = old_sessions.count()
        old_sessions.delete()
        
        logger.info(f"Cleaned up {count} old device sessions (older than {days_old} days)")
        
        return {
            'sessions_deleted': count,
            'days_old': days_old
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_device_sessions task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def update_device_connection_quality(self):
    """
    Actualiza la calidad de conexión de los dispositivos basada en su historial.
    """
    try:
        devices = GPSDevice.objects.filter(is_active=True)
        updated_count = 0
        
        for device in devices:
            try:
                # Calcular calidad basada en heartbeat reciente y errores
                quality = 0.0
                
                if device.last_heartbeat:
                    time_since_heartbeat = timezone.now() - device.last_heartbeat
                    minutes_since = time_since_heartbeat.total_seconds() / 60
                    
                    # Calidad basada en recencia del heartbeat
                    if minutes_since <= 1:
                        quality += 50  # Excelente
                    elif minutes_since <= 5:
                        quality += 30  # Bueno
                    elif minutes_since <= 15:
                        quality += 10  # Regular
                    # Más de 15 minutos = 0 puntos
                
                # Calidad basada en errores
                if device.error_count == 0:
                    quality += 30
                elif device.error_count <= 5:
                    quality += 20
                elif device.error_count <= 10:
                    quality += 10
                # Más de 10 errores = 0 puntos
                
                # Calidad basada en conexiones totales (experiencia)
                if device.total_connections > 100:
                    quality += 20
                elif device.total_connections > 50:
                    quality += 15
                elif device.total_connections > 10:
                    quality += 10
                elif device.total_connections > 0:
                    quality += 5
                
                # Normalizar a 0-100
                quality = min(100.0, max(0.0, quality))
                
                if device.connection_quality != quality:
                    device.connection_quality = quality
                    device.save()
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Error updating connection quality for device {device.imei}: {e}")
        
        logger.info(f"Updated connection quality for {updated_count} devices")
        
        return {
            'devices_updated': updated_count,
            'total_devices': devices.count()
        }
        
    except Exception as e:
        logger.error(f"Error in update_device_connection_quality task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def generate_device_statistics(self):
    """
    Genera estadísticas periódicas de los dispositivos.
    """
    try:
        # Estadísticas generales
        stats = GPSDevice.objects.aggregate(
            total=Count('id'),
            online=Count('id', filter=Q(connection_status='ONLINE')),
            offline=Count('id', filter=Q(connection_status='OFFLINE')),
            avg_quality=Avg('connection_quality')
        )
        
        # Dispositivos por protocolo
        protocol_stats = GPSDevice.objects.values('protocol').annotate(
            count=Count('id')
        )
        
        # Dispositivos por estado de conexión
        status_stats = GPSDevice.objects.values('connection_status').annotate(
            count=Count('id')
        )
        
        logger.info(f"Device statistics generated: {stats}")
        
        return {
            'general_stats': stats,
            'protocol_stats': list(protocol_stats),
            'status_stats': list(status_stats)
        }
        
    except Exception as e:
        logger.error(f"Error in generate_device_statistics task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def monitor_hardware_gps_connections(self):
    """
    Monitorea conexiones de dispositivos GPS de hardware.
    Basado en la implementación del proyecto django14.
    """
    try:
        from skyguard.apps.gps.services.hardware_gps import hardware_gps_service
        
        # Verificar estado del servicio de hardware GPS
        active_connections = len(hardware_gps_service.active_connections)
        running = hardware_gps_service.running
        active_threads = len([t for t in hardware_gps_service.threads if t.is_alive()])
        
        # Dispositivos conectados recientemente (últimos 5 minutos)
        recent_time = timezone.now() - timedelta(minutes=5)
        recent_devices = GPSDevice.objects.filter(
            last_connection__gte=recent_time,
            connection_status='ONLINE'
        ).count()
        
        # Dispositivos por protocolo de hardware
        hardware_protocols = GPSDevice.objects.filter(
            protocol__in=['concox', 'meiligao', 'nmea']
        ).values('protocol').annotate(
            count=Count('id'),
            online=Count('id', filter=Q(connection_status='ONLINE'))
        )
        
        result = {
            'service_running': running,
            'active_connections': active_connections,
            'active_threads': active_threads,
            'recent_devices': recent_devices,
            'hardware_protocols': list(hardware_protocols),
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Hardware GPS monitoring: {result}")
        
        # Alertar si el servicio no está corriendo
        if not running:
            logger.warning("Hardware GPS service is not running!")
        
        # Alertar si no hay dispositivos recientes
        if recent_devices == 0:
            logger.warning("No recent GPS device connections detected")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in monitor_hardware_gps_connections task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def cleanup_old_gps_locations(self, days_old=30):
    """
    Limpia ubicaciones GPS antiguas para optimizar la base de datos.
    
    Args:
        days_old (int): Días de antigüedad para considerar una ubicación como antigua
    """
    try:
        from skyguard.apps.gps.models import GPSLocation
        
        cutoff_time = timezone.now() - timedelta(days=days_old)
        
        # Eliminar ubicaciones antiguas
        old_locations = GPSLocation.objects.filter(timestamp__lt=cutoff_time)
        count = old_locations.count()
        old_locations.delete()
        
        logger.info(f"Cleaned up {count} old GPS locations (older than {days_old} days)")
        
        return {
            'locations_deleted': count,
            'days_old': days_old
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_gps_locations task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def validate_gps_data_integrity(self):
    """
    Valida la integridad de los datos GPS almacenados.
    """
    try:
        from skyguard.apps.gps.models import GPSLocation, GPSEvent
        
        # Verificar ubicaciones sin coordenadas válidas
        invalid_locations = GPSLocation.objects.filter(
            Q(position__isnull=True) |
            Q(latitude__isnull=True) |
            Q(longitude__isnull=True)
        ).count()
        
        # Verificar eventos sin dispositivo
        orphan_events = GPSEvent.objects.filter(device__isnull=True).count()
        
        # Verificar ubicaciones duplicadas (mismo dispositivo, misma posición, mismo tiempo)
        duplicate_locations = GPSLocation.objects.raw("""
            SELECT id FROM skyguard_apps_gps_gpslocation 
            WHERE (device_id, position, timestamp) IN (
                SELECT device_id, position, timestamp 
                FROM skyguard_apps_gps_gpslocation 
                GROUP BY device_id, position, timestamp 
                HAVING COUNT(*) > 1
            )
        """)
        duplicate_count = len(list(duplicate_locations))
        
        result = {
            'invalid_locations': invalid_locations,
            'orphan_events': orphan_events,
            'duplicate_locations': duplicate_count,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"GPS data integrity check: {result}")
        
        # Alertar sobre problemas encontrados
        if invalid_locations > 0:
            logger.warning(f"Found {invalid_locations} invalid GPS locations")
        
        if orphan_events > 0:
            logger.warning(f"Found {orphan_events} orphan GPS events")
        
        if duplicate_count > 0:
            logger.warning(f"Found {duplicate_count} duplicate GPS locations")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in validate_gps_data_integrity task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3) 


@shared_task(bind=True)
def process_geofence_detection(self, device_imei):
    """
    Procesar detección de geocercas para un dispositivo específico.
    
    Args:
        device_imei (int): IMEI del dispositivo a procesar
    """
    try:
        from skyguard.apps.gps.models import GPSDevice
        from skyguard.apps.gps.services.geofence_service import geofence_detection_service
        
        # Obtener el dispositivo
        try:
            device = GPSDevice.objects.get(imei=device_imei)
        except GPSDevice.DoesNotExist:
            logger.error(f"Device {device_imei} not found for geofence detection")
            return {'success': False, 'error': 'Device not found'}
        
        # Solo procesar dispositivos con posición y que estén online
        if not device.position:
            logger.debug(f"Device {device_imei} has no position, skipping geofence detection")
            return {'success': True, 'skipped': 'No position'}
        
        if device.connection_status != 'ONLINE':
            logger.debug(f"Device {device_imei} is {device.connection_status}, skipping geofence detection")
            return {'success': True, 'skipped': f'Device {device.connection_status}'}
        
        # Procesar geocercas
        events_generated = geofence_detection_service.check_device_geofences(device)
        
        logger.info(
            f"Processed geofence detection for device {device.name} ({device_imei}): "
            f"{len(events_generated)} events generated"
        )
        
        return {
            'success': True,
            'device_imei': device_imei,
            'device_name': device.name,
            'events_generated': len(events_generated),
            'events': events_generated
        }
        
    except Exception as error:
        logger.error(f"Error processing geofence detection for device {device_imei}: {error}")
        return {'success': False, 'error': str(error)}


@shared_task(bind=True)
def check_all_devices_geofences(self):
    """
    Verificar geocercas para todos los dispositivos activos.
    Esta tarea se ejecuta periódicamente para detectar eventos de geocercas.
    """
    try:
        from skyguard.apps.gps.models import GPSDevice
        
        # Obtener todos los dispositivos activos con posición
        active_devices = GPSDevice.objects.filter(
            connection_status='ONLINE',
            position__isnull=False
        ).values_list('imei', flat=True)
        
        if not active_devices:
            logger.info("No active devices found for geofence checking")
            return {'success': True, 'devices_processed': 0}
        
        # Procesar cada dispositivo de forma asíncrona
        results = []
        for device_imei in active_devices:
            try:
                # Llamar a la tarea de procesamiento individual
                result = process_geofence_detection.delay(device_imei)
                results.append({
                    'device_imei': device_imei,
                    'task_id': result.id
                })
            except Exception as e:
                logger.error(f"Error queuing geofence detection for device {device_imei}: {e}")
                results.append({
                    'device_imei': device_imei,
                    'error': str(e)
                })
        
        logger.info(f"Queued geofence detection for {len(active_devices)} devices")
        
        return {
            'success': True,
            'devices_processed': len(active_devices),
            'results': results
        }
        
    except Exception as error:
        logger.error(f"Error in check_all_devices_geofences: {error}")
        return {'success': False, 'error': str(error)}


@shared_task(bind=True)
def cleanup_old_geofence_events(self, days_old=30):
    """
    Limpiar eventos de geocercas antiguos.
    
    Args:
        days_old (int): Días de antigüedad para considerar eventos como antiguos
    """
    try:
        from skyguard.apps.gps.models import GeoFenceEvent
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # Contar eventos antiguos
        old_events = GeoFenceEvent.objects.filter(created_at__lt=cutoff_date)
        events_count = old_events.count()
        
        if events_count == 0:
            logger.info("No old geofence events to clean up")
            return {'success': True, 'events_deleted': 0}
        
        # Eliminar eventos antiguos
        deleted_count, _ = old_events.delete()
        
        logger.info(
            f"Cleaned up {deleted_count} geofence events older than {days_old} days"
        )
        
        return {
            'success': True,
            'events_deleted': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as error:
        logger.error(f"Error cleaning up old geofence events: {error}")
        return {'success': False, 'error': str(error)}


@shared_task(bind=True)
def generate_geofence_statistics(self):
    """
    Generar estadísticas de uso de geocercas.
    """
    try:
        from skyguard.apps.gps.models import GeoFence, GeoFenceEvent
        from django.db.models import Count, Q
        from datetime import timedelta
        
        # Estadísticas básicas
        total_geofences = GeoFence.objects.count()
        active_geofences = GeoFence.objects.filter(is_active=True).count()
        
        # Eventos de las últimas 24 horas
        yesterday = timezone.now() - timedelta(days=1)
        recent_events = GeoFenceEvent.objects.filter(
            timestamp__gte=yesterday
        ).count()
        
        # Eventos por tipo
        entry_events = GeoFenceEvent.objects.filter(
            timestamp__gte=yesterday,
            event_type='ENTRY'
        ).count()
        
        exit_events = GeoFenceEvent.objects.filter(
            timestamp__gte=yesterday,
            event_type='EXIT'
        ).count()
        
        # Geocercas más activas
        most_active_geofences = GeoFence.objects.annotate(
            event_count=Count('events', filter=Q(events__timestamp__gte=yesterday))
        ).filter(event_count__gt=0).order_by('-event_count')[:10]
        
        # Dispositivos más activos en geocercas
        most_active_devices = GeoFenceEvent.objects.filter(
            timestamp__gte=yesterday
        ).values('device__name', 'device__imei').annotate(
            event_count=Count('id')
        ).order_by('-event_count')[:10]
        
        stats = {
            'total_geofences': total_geofences,
            'active_geofences': active_geofences,
            'events_last_24h': recent_events,
            'entry_events_24h': entry_events,
            'exit_events_24h': exit_events,
            'most_active_geofences': [
                {
                    'name': gf.name,
                    'id': gf.id,
                    'event_count': gf.event_count
                }
                for gf in most_active_geofences
            ],
            'most_active_devices': list(most_active_devices),
            'generated_at': timezone.now().isoformat()
        }
        
        # Almacenar estadísticas en cache
        from django.core.cache import cache
        cache.set('geofence_statistics', stats, 3600)  # Cache por 1 hora
        
        logger.info(
            f"Generated geofence statistics: {total_geofences} total geofences, "
            f"{recent_events} events in last 24h"
        )
        
        return {
            'success': True,
            'statistics': stats
        }
        
    except Exception as error:
        logger.error(f"Error generating geofence statistics: {error}")
        return {'success': False, 'error': str(error)}


@shared_task(bind=True)
def send_geofence_daily_report(self, user_id=None):
    """
    Enviar reporte diario de actividad de geocercas.
    
    Args:
        user_id (int): ID del usuario específico, None para todos los usuarios
    """
    try:
        from django.contrib.auth.models import User
        from skyguard.apps.gps.models import GeoFence, GeoFenceEvent
        from skyguard.apps.gps.notifications import geofence_notification_service
        from datetime import timedelta
        
        # Obtener usuarios
        if user_id:
            users = User.objects.filter(id=user_id, is_active=True)
        else:
            # Solo usuarios que tienen geocercas
            users = User.objects.filter(
                geofence_set__isnull=False,
                is_active=True
            ).distinct()
        
        reports_sent = 0
        yesterday = timezone.now() - timedelta(days=1)
        
        for user in users:
            try:
                # Obtener geocercas del usuario
                user_geofences = GeoFence.objects.filter(owner=user)
                
                if not user_geofences.exists():
                    continue
                
                # Obtener eventos de ayer
                events_yesterday = GeoFenceEvent.objects.filter(
                    fence__owner=user,
                    timestamp__gte=yesterday
                ).select_related('fence', 'device')
                
                # Preparar datos del reporte
                report_data = {
                    'user': user,
                    'date': yesterday.date(),
                    'total_geofences': user_geofences.count(),
                    'active_geofences': user_geofences.filter(is_active=True).count(),
                    'total_events': events_yesterday.count(),
                    'entry_events': events_yesterday.filter(event_type='ENTRY').count(),
                    'exit_events': events_yesterday.filter(event_type='EXIT').count(),
                    'events_by_geofence': {},
                    'events_by_device': {}
                }
                
                # Agrupar eventos por geocerca
                for geofence in user_geofences:
                    geofence_events = events_yesterday.filter(fence=geofence)
                    if geofence_events.exists():
                        report_data['events_by_geofence'][geofence.name] = {
                            'total': geofence_events.count(),
                            'entries': geofence_events.filter(event_type='ENTRY').count(),
                            'exits': geofence_events.filter(event_type='EXIT').count()
                        }
                
                # Agrupar eventos por dispositivo
                device_events = events_yesterday.values('device__name').annotate(
                    total=Count('id'),
                    entries=Count('id', filter=Q(event_type='ENTRY')),
                    exits=Count('id', filter=Q(event_type='EXIT'))
                )
                
                for device_data in device_events:
                    device_name = device_data['device__name']
                    report_data['events_by_device'][device_name] = {
                        'total': device_data['total'],
                        'entries': device_data['entries'],
                        'exits': device_data['exits']
                    }
                
                # Enviar reporte por email (implementar template)
                # geofence_notification_service.send_daily_report(report_data)
                
                reports_sent += 1
                logger.info(f"Generated daily geofence report for user {user.username}")
                
            except Exception as e:
                logger.error(f"Error generating report for user {user.username}: {e}")
        
        return {
            'success': True,
            'reports_sent': reports_sent,
            'date': yesterday.date().isoformat()
        }
        
    except Exception as error:
        logger.error(f"Error sending daily geofence reports: {error}")
        return {'success': False, 'error': str(error)} 