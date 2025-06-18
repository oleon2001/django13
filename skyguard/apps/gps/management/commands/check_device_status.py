"""
Management command to check device status and update offline devices.
Usage: python manage.py check_device_status
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from skyguard.apps.gps.models.device import GPSDevice
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check device status and mark devices as offline if they have not sent heartbeat recently'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='Heartbeat timeout in seconds (default: 300 = 5 minutes)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show verbose output'
        )

    def handle(self, *args, **options):
        timeout_seconds = options['timeout']
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(f'Checking device status (timeout: {timeout_seconds}s, dry-run: {dry_run})')
        )
        
        # Calcular el tiempo límite
        timeout_time = timezone.now() - timedelta(seconds=timeout_seconds)
        
        # Obtener dispositivos que están marcados como ONLINE
        online_devices = GPSDevice.objects.filter(connection_status='ONLINE')
        
        devices_to_update = []
        online_count = 0
        
        for device in online_devices:
            # Verificar si el dispositivo tiene heartbeat reciente
            if device.last_heartbeat is None:
                # Sin heartbeat registrado, marcar como offline
                devices_to_update.append(device)
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Device {device.imei} ({device.name}): No heartbeat recorded'
                        )
                    )
            elif device.last_heartbeat < timeout_time:
                # Heartbeat muy antiguo, marcar como offline
                time_since_heartbeat = timezone.now() - device.last_heartbeat
                devices_to_update.append(device)
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Device {device.imei} ({device.name}): Last heartbeat {time_since_heartbeat.total_seconds():.0f}s ago'
                        )
                    )
            else:
                # Dispositivo está realmente online
                online_count += 1
                if verbose:
                    time_since_heartbeat = timezone.now() - device.last_heartbeat
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Device {device.imei} ({device.name}): Online (heartbeat {time_since_heartbeat.total_seconds():.0f}s ago)'
                        )
                    )
        
        # Actualizar dispositivos que deben marcarse como offline
        updated_count = 0
        if devices_to_update:
            if not dry_run:
                for device in devices_to_update:
                    try:
                        device.update_connection_status('OFFLINE')
                        updated_count += 1
                        logger.info(f'Marked device {device.imei} as OFFLINE due to missing heartbeat')
                    except Exception as e:
                        logger.error(f'Error updating device {device.imei}: {e}')
                        self.stdout.write(
                            self.style.ERROR(f'Error updating device {device.imei}: {e}')
                        )
            else:
                updated_count = len(devices_to_update)
        
        # Mostrar resumen
        total_devices = online_devices.count()
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total devices checked: {total_devices}')
        self.stdout.write(f'Devices still online: {online_count}')
        self.stdout.write(f'Devices marked as offline: {updated_count}')
        
        if dry_run and devices_to_update:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would have updated {len(devices_to_update)} devices')
            )
        
        # Mostrar estadísticas generales
        all_devices = GPSDevice.objects.all()
        total_all = all_devices.count()
        online_all = all_devices.filter(connection_status='ONLINE').count()
        offline_all = all_devices.filter(connection_status='OFFLINE').count()
        
        self.stdout.write('\nCurrent device status:')
        self.stdout.write(f'Total devices: {total_all}')
        self.stdout.write(self.style.SUCCESS(f'Online: {online_all}'))
        self.stdout.write(self.style.ERROR(f'Offline: {offline_all}'))
        self.stdout.write(f'Other: {total_all - online_all - offline_all}')
        
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully updated {updated_count} device(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nNo devices needed status update')
            ) 