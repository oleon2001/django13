"""
Quick device monitor for development and testing.
Usage: python manage.py quick_device_monitor
"""

import time
import signal
import sys
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from skyguard.apps.gps.models.device import GPSDevice
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Quick GPS device monitor - checks every minute for development/testing'

    def __init__(self):
        super().__init__()
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        self.stdout.write(self.style.WARNING('\n🛑 Recibida señal para detener monitoreo...'))
        self.running = False

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=1,
            help='Heartbeat timeout in minutes (default: 1 minute)'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Solo mostrar cambios importantes'
        )

    def handle(self, *args, **options):
        timeout_minutes = options['timeout']
        quiet_mode = options['quiet']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🚀 Iniciando monitor rápido GPS (timeout: {timeout_minutes}min, verificación cada minuto)'
            )
        )
        
        if not quiet_mode:
            self.stdout.write('💡 Usa --quiet para mostrar solo cambios importantes')
            self.stdout.write('⏹️  Presiona Ctrl+C para detener\n')
        
        iteration = 0
        last_stats = None
        
        try:
            while self.running:
                iteration += 1
                current_time = timezone.now()
                
                if not quiet_mode:
                    self.stdout.write(f'⏰ Verificación #{iteration} - {current_time.strftime("%H:%M:%S")}')
                
                # Verificar dispositivos
                result = self.check_devices_fast(timeout_minutes, quiet_mode)
                
                # Mostrar cambios importantes
                if result['devices_marked_offline'] > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'📴 {result["devices_marked_offline"]} dispositivos marcados como OFFLINE'
                        )
                    )
                    for device_info in result.get('updated_devices', []):
                        self.stdout.write(f'   • {device_info["imei"]} ({device_info["name"]}) - {device_info["reason"]}')
                
                # Mostrar estadísticas si cambiaron o en modo verbose
                current_stats = f'{result["total_online"]} online, {result["total_offline"]} offline'
                if not quiet_mode or current_stats != last_stats:
                    status_color = self.style.SUCCESS if result["total_online"] > 0 else self.style.WARNING
                    self.stdout.write(f'📊 Estado: {status_color(current_stats)}')
                    last_stats = current_stats
                
                if not quiet_mode:
                    self.stdout.write('')  # Línea en blanco
                
                # Esperar 60 segundos (1 minuto)
                for i in range(60):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error en el bucle de monitoreo: {e}')
            )
            logger.error(f'Error en monitoreo rápido: {e}', exc_info=True)
        finally:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Monitor detenido después de {iteration} verificaciones')
            )

    def check_devices_fast(self, timeout_minutes, quiet_mode=False):
        """
        Verificación rápida del estado de dispositivos.
        """
        try:
            timeout_time = timezone.now() - timedelta(minutes=timeout_minutes)
            
            # Buscar dispositivos que necesitan ser marcados como offline
            stale_devices = GPSDevice.objects.filter(
                connection_status='ONLINE'
            ).filter(
                Q(last_heartbeat__isnull=True) | 
                Q(last_heartbeat__lt=timeout_time)
            )
            
            updated_devices = []
            updated_count = 0
            
            for device in stale_devices:
                try:
                    device.connection_status = 'OFFLINE'
                    device.save()
                    
                    updated_count += 1
                    
                    # Información del dispositivo actualizado
                    if device.last_heartbeat:
                        time_since = timezone.now() - device.last_heartbeat
                        reason = f"Sin heartbeat por {time_since.total_seconds():.0f}s"
                    else:
                        reason = "Sin heartbeat registrado"
                    
                    updated_devices.append({
                        'imei': device.imei,
                        'name': device.name,
                        'reason': reason
                    })
                    
                    if not quiet_mode:
                        logger.info(f"Dispositivo {device.imei} marcado como OFFLINE: {reason}")
                    
                except Exception as e:
                    error_msg = f"Error actualizando dispositivo {device.imei}: {e}"
                    self.stdout.write(self.style.ERROR(f'❌ {error_msg}'))
                    logger.error(error_msg)
            
            # Estadísticas actuales
            total_online = GPSDevice.objects.filter(connection_status='ONLINE').count()
            total_offline = GPSDevice.objects.filter(connection_status='OFFLINE').count()
            
            return {
                'devices_checked': stale_devices.count(),
                'devices_marked_offline': updated_count,
                'updated_devices': updated_devices,
                'total_online': total_online,
                'total_offline': total_offline,
                'timeout_minutes': timeout_minutes
            }
            
        except Exception as e:
            logger.error(f"Error en check_devices_fast: {e}")
            return {
                'devices_checked': 0,
                'devices_marked_offline': 0,
                'updated_devices': [],
                'total_online': 0,
                'total_offline': 0,
                'timeout_minutes': timeout_minutes
            } 