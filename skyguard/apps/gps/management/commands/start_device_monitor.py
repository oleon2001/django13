"""
Management command to start automatic device monitoring.
Usage: python manage.py start_device_monitor
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
    help = 'Start automatic monitoring of GPS devices and mark them offline when inactive'

    def __init__(self):
        super().__init__()
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        self.stdout.write(self.style.WARNING('Received signal to stop monitoring...'))
        self.running = False

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=5,
            help='Heartbeat timeout in minutes (default: 5 minutes)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Check interval in seconds (default: 60 seconds)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show verbose output'
        )

    def handle(self, *args, **options):
        timeout_minutes = options['timeout']
        check_interval = options['interval']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting GPS device monitor (timeout: {timeout_minutes}min, interval: {check_interval}s)'
            )
        )
        
        iteration = 0
        
        try:
            while self.running:
                iteration += 1
                
                if verbose:
                    self.stdout.write(f'\n--- Check #{iteration} at {timezone.now()} ---')
                
                # Verificar dispositivos
                result = self.check_devices(timeout_minutes, verbose)
                
                if result['devices_marked_offline'] > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Marked {result["devices_marked_offline"]} devices as OFFLINE'
                        )
                    )
                elif verbose:
                    self.stdout.write(
                        self.style.SUCCESS('All devices are up to date')
                    )
                
                if verbose:
                    self.stdout.write(
                        f'Status: {result["total_online"]} online, {result["total_offline"]} offline'
                    )
                
                # Esperar hasta la siguiente verificación
                for i in range(check_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error in monitoring loop: {e}')
            )
            logger.error(f'Error in device monitoring: {e}', exc_info=True)
        finally:
            self.stdout.write(
                self.style.SUCCESS(f'\nDevice monitoring stopped after {iteration} checks')
            )

    def check_devices(self, timeout_minutes, verbose=False):
        """
        Verifica el estado de los dispositivos y marca como offline los que no tienen heartbeat.
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
                    device.connection_status = 'OFFLINE'
                    device.save()
                    
                    updated_count += 1
                    
                    # Log del cambio
                    if device.last_heartbeat:
                        time_since = timezone.now() - device.last_heartbeat
                        message = (
                            f"Device {device.imei} ({device.name}) → OFFLINE "
                            f"(last heartbeat {time_since.total_seconds():.0f}s ago)"
                        )
                    else:
                        message = (
                            f"Device {device.imei} ({device.name}) → OFFLINE "
                            f"(no heartbeat recorded)"
                        )
                    
                    if verbose:
                        self.stdout.write(self.style.WARNING(message))
                    
                    logger.info(message)
                    
                except Exception as e:
                    error_msg = f"Error updating device {device.imei}: {e}"
                    self.stdout.write(self.style.ERROR(error_msg))
                    logger.error(error_msg)
            
            # Estadísticas finales
            total_online = GPSDevice.objects.filter(connection_status='ONLINE').count()
            total_offline = GPSDevice.objects.filter(connection_status='OFFLINE').count()
            
            return {
                'devices_checked': stale_devices.count(),
                'devices_marked_offline': updated_count,
                'total_online': total_online,
                'total_offline': total_offline,
                'timeout_minutes': timeout_minutes
            }
            
        except Exception as e:
            logger.error(f"Error in check_devices: {e}")
            return {
                'devices_checked': 0,
                'devices_marked_offline': 0,
                'total_online': 0,
                'total_offline': 0,
                'timeout_minutes': timeout_minutes
            } 