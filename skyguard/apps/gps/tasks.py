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
def check_devices_heartbeat(self, timeout_minutes=5):
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
        ).order_by('protocol')
        
        # Dispositivos activos en las últimas 24 horas
        last_24h = timezone.now() - timedelta(hours=24)
        active_24h = GPSDevice.objects.filter(
            last_heartbeat__gte=last_24h
        ).count()
        
        result = {
            'timestamp': timezone.now().isoformat(),
            'general_stats': stats,
            'protocol_distribution': list(protocol_stats),
            'active_last_24h': active_24h
        }
        
        logger.info(f"Generated device statistics: {stats}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_device_statistics task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3) 