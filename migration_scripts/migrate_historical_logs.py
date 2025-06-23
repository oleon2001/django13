#!/usr/bin/env python3
"""
Script para migrar logs históricos (aceleración y alarmas) del sistema legacy.
Estos datos son voluminosos y requieren procesamiento especial.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.db import transaction, connection
from django.utils import timezone
import logging
from typing import Optional, List, Dict

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

# Legacy models
from skyguard.gps.tracker.models import (
    AccelLog as LegacyAccelLog,
    AlarmLog as LegacyAlarmLog,
    Stats as LegacyStats,
    PsiCal as LegacyPsiCal
)

# New models
from skyguard.apps.gps.models import (
    GPSDevice, AccelerationLog, GPSEvent, DeviceStats
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('historical_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HistoricalLogMigrator:
    """Migrador especializado para logs históricos."""
    
    def __init__(self, dry_run=True, batch_size=5000, date_range_days=None):
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.date_range_days = date_range_days
        self.stats = {
            'acceleration_logs': {'migrated': 0, 'errors': 0, 'skipped': 0},
            'alarm_logs': {'migrated': 0, 'errors': 0, 'skipped': 0},
            'device_stats': {'migrated': 0, 'errors': 0, 'skipped': 0}
        }
        
        # Cache de dispositivos para evitar consultas repetidas
        self.device_cache = {}
        self._load_device_cache()
    
    def _load_device_cache(self):
        """Carga el cache de dispositivos GPS."""
        logger.info("Cargando cache de dispositivos...")
        for device in GPSDevice.objects.all():
            self.device_cache[device.imei] = device
        logger.info(f"Cache cargado: {len(self.device_cache)} dispositivos")
    
    def get_date_filter(self):
        """Obtiene el filtro de fechas si está configurado."""
        if self.date_range_days:
            cutoff_date = timezone.now() - timedelta(days=self.date_range_days)
            return {'date__gte': cutoff_date}
        return {}
    
    def migrate_acceleration_logs(self):
        """Migra los logs de aceleración."""
        logger.info("🔄 Migrando logs de aceleración...")
        
        # Filtros de fecha
        date_filter = self.get_date_filter()
        
        # Contar total
        total = LegacyAccelLog.objects.filter(**date_filter).count()
        if total == 0:
            logger.info("No hay logs de aceleración para migrar")
            return True
        
        logger.info(f"Total de logs de aceleración a migrar: {total:,}")
        
        # Procesar en lotes
        processed = 0
        batch_start = 0
        
        while batch_start < total:
            batch_end = min(batch_start + self.batch_size, total)
            
            # Obtener lote
            legacy_logs = LegacyAccelLog.objects.filter(**date_filter)[batch_start:batch_end]
            
            try:
                with transaction.atomic():
                    batch_objects = []
                    
                    for legacy_log in legacy_logs:
                        try:
                            # Verificar que el dispositivo existe
                            device = self.device_cache.get(legacy_log.imei)
                            if not device:
                                logger.warning(f"Dispositivo {legacy_log.imei} no encontrado, saltando log")
                                self.stats['acceleration_logs']['skipped'] += 1
                                continue
                            
                            # Verificar si ya existe (evitar duplicados)
                            if not self.dry_run:
                                if AccelerationLog.objects.filter(
                                    device=device,
                                    timestamp=legacy_log.date,
                                    x_axis=legacy_log.x,
                                    y_axis=legacy_log.y,
                                    z_axis=legacy_log.z
                                ).exists():
                                    self.stats['acceleration_logs']['skipped'] += 1
                                    continue
                            
                            # Crear nuevo log
                            new_log = AccelerationLog(
                                device=device,
                                timestamp=legacy_log.date,
                                x_axis=legacy_log.x,
                                y_axis=legacy_log.y,
                                z_axis=legacy_log.z,
                                magnitude=legacy_log.mag if hasattr(legacy_log, 'mag') else None,
                                # Nuevos campos con valores por defecto
                                event_type='ACCELERATION',
                                severity='MEDIUM'
                            )
                            
                            if not self.dry_run:
                                batch_objects.append(new_log)
                            
                            self.stats['acceleration_logs']['migrated'] += 1
                            
                        except Exception as e:
                            logger.error(f"Error procesando log de aceleración: {e}")
                            self.stats['acceleration_logs']['errors'] += 1
                    
                    # Guardar lote
                    if not self.dry_run and batch_objects:
                        AccelerationLog.objects.bulk_create(batch_objects, ignore_conflicts=True)
                
                processed += len(legacy_logs)
                batch_start = batch_end
                
                # Log de progreso
                percentage = (processed / total) * 100
                logger.info(f"Logs de aceleración: {processed:,}/{total:,} ({percentage:.1f}%)")
                
            except Exception as e:
                logger.error(f"Error en lote de logs de aceleración: {e}")
                return False
        
        logger.info(f"✅ Logs de aceleración: {self.stats['acceleration_logs']['migrated']:,} migrados, "
                   f"{self.stats['acceleration_logs']['errors']} errores, "
                   f"{self.stats['acceleration_logs']['skipped']} saltados")
        return True
    
    def migrate_alarm_logs(self):
        """Migra los logs de alarmas."""
        logger.info("🔄 Migrando logs de alarmas...")
        
        # Filtros de fecha
        date_filter = self.get_date_filter()
        
        # Contar total
        total = LegacyAlarmLog.objects.filter(**date_filter).count()
        if total == 0:
            logger.info("No hay logs de alarmas para migrar")
            return True
        
        logger.info(f"Total de logs de alarmas a migrar: {total:,}")
        
        # Procesar en lotes
        processed = 0
        batch_start = 0
        
        while batch_start < total:
            batch_end = min(batch_start + self.batch_size, total)
            
            # Obtener lote
            legacy_logs = LegacyAlarmLog.objects.filter(**date_filter)[batch_start:batch_end]
            
            try:
                with transaction.atomic():
                    batch_objects = []
                    
                    for legacy_log in legacy_logs:
                        try:
                            # Verificar que el dispositivo existe
                            device = self.device_cache.get(legacy_log.imei)
                            if not device:
                                logger.warning(f"Dispositivo {legacy_log.imei} no encontrado, saltando alarma")
                                self.stats['alarm_logs']['skipped'] += 1
                                continue
                            
                            # Verificar si ya existe
                            if not self.dry_run:
                                if GPSEvent.objects.filter(
                                    device=device,
                                    timestamp=legacy_log.date,
                                    event_type='ALARM',
                                    alarm_code=legacy_log.alarm
                                ).exists():
                                    self.stats['alarm_logs']['skipped'] += 1
                                    continue
                            
                            # Mapear tipo de alarma
                            event_type = self._map_alarm_type(legacy_log.alarm)
                            severity = self._get_alarm_severity(legacy_log.alarm)
                            
                            # Crear nuevo evento
                            new_event = GPSEvent(
                                device=device,
                                timestamp=legacy_log.date,
                                event_type=event_type,
                                alarm_code=legacy_log.alarm,
                                latitude=legacy_log.lat if hasattr(legacy_log, 'lat') else None,
                                longitude=legacy_log.lng if hasattr(legacy_log, 'lng') else None,
                                speed=legacy_log.speed if hasattr(legacy_log, 'speed') else None,
                                course=legacy_log.course if hasattr(legacy_log, 'course') else None,
                                severity=severity,
                                description=f"Alarma migrada: {legacy_log.alarm}",
                                # Nuevos campos
                                is_acknowledged=False,
                                requires_action=severity in ['HIGH', 'CRITICAL']
                            )
                            
                            if not self.dry_run:
                                batch_objects.append(new_event)
                            
                            self.stats['alarm_logs']['migrated'] += 1
                            
                        except Exception as e:
                            logger.error(f"Error procesando log de alarma: {e}")
                            self.stats['alarm_logs']['errors'] += 1
                    
                    # Guardar lote
                    if not self.dry_run and batch_objects:
                        GPSEvent.objects.bulk_create(batch_objects, ignore_conflicts=True)
                
                processed += len(legacy_logs)
                batch_start = batch_end
                
                # Log de progreso
                percentage = (processed / total) * 100
                logger.info(f"Logs de alarmas: {processed:,}/{total:,} ({percentage:.1f}%)")
                
            except Exception as e:
                logger.error(f"Error en lote de logs de alarmas: {e}")
                return False
        
        logger.info(f"✅ Logs de alarmas: {self.stats['alarm_logs']['migrated']:,} migrados, "
                   f"{self.stats['alarm_logs']['errors']} errores, "
                   f"{self.stats['alarm_logs']['skipped']} saltados")
        return True
    
    def migrate_device_stats(self):
        """Migra las estadísticas de dispositivos."""
        logger.info("🔄 Migrando estadísticas de dispositivos...")
        
        legacy_stats = LegacyStats.objects.all()
        total = legacy_stats.count()
        
        if total == 0:
            logger.info("No hay estadísticas para migrar")
            return True
        
        for i, legacy_stat in enumerate(legacy_stats):
            try:
                with transaction.atomic():
                    # Verificar que el dispositivo existe
                    device = self.device_cache.get(legacy_stat.imei)
                    if not device:
                        logger.warning(f"Dispositivo {legacy_stat.imei} no encontrado, saltando estadística")
                        self.stats['device_stats']['skipped'] += 1
                        continue
                    
                    if not self.dry_run:
                        # Verificar si ya existe
                        if not DeviceStats.objects.filter(
                            device=device,
                            date=legacy_stat.date
                        ).exists():
                            new_stat = DeviceStats(
                                device=device,
                                date=legacy_stat.date,
                                total_distance=legacy_stat.distance or 0,
                                max_speed=legacy_stat.maxSpeed or 0,
                                avg_speed=legacy_stat.avgSpeed or 0,
                                idle_time=legacy_stat.idleTime or 0,
                                moving_time=legacy_stat.movingTime or 0,
                                fuel_consumed=legacy_stat.fuelConsumed if hasattr(legacy_stat, 'fuelConsumed') else 0,
                                # Nuevos campos con valores por defecto
                                total_events=0,
                                harsh_acceleration_count=0,
                                harsh_braking_count=0,
                                speeding_events=0
                            )
                            new_stat.save()
                            self.stats['device_stats']['migrated'] += 1
                        else:
                            self.stats['device_stats']['skipped'] += 1
                    else:
                        self.stats['device_stats']['migrated'] += 1
                
                if (i + 1) % 100 == 0:
                    percentage = ((i + 1) / total) * 100
                    logger.info(f"Estadísticas: {i + 1}/{total} ({percentage:.1f}%)")
                    
            except Exception as e:
                logger.error(f"Error migrando estadística: {e}")
                self.stats['device_stats']['errors'] += 1
        
        logger.info(f"✅ Estadísticas: {self.stats['device_stats']['migrated']} migradas, "
                   f"{self.stats['device_stats']['errors']} errores, "
                   f"{self.stats['device_stats']['skipped']} saltadas")
        return True
    
    def _map_alarm_type(self, alarm_code):
        """Mapea códigos de alarma legacy a tipos de evento."""
        alarm_mapping = {
            'SOS': 'PANIC',
            'OVERSPEED': 'SPEEDING',
            'GEOFENCE_IN': 'GEOFENCE_ENTRY',
            'GEOFENCE_OUT': 'GEOFENCE_EXIT',
            'POWER_OFF': 'POWER_DISCONNECT',
            'POWER_ON': 'POWER_CONNECT',
            'LOW_BATTERY': 'LOW_BATTERY',
            'HARSH_ACCELERATION': 'HARSH_ACCELERATION',
            'HARSH_BRAKING': 'HARSH_BRAKING',
            'ACCIDENT': 'ACCIDENT'
        }
        return alarm_mapping.get(alarm_code, 'ALARM')
    
    def _get_alarm_severity(self, alarm_code):
        """Determina la severidad de una alarma."""
        high_severity = ['SOS', 'ACCIDENT', 'POWER_OFF']
        medium_severity = ['OVERSPEED', 'HARSH_ACCELERATION', 'HARSH_BRAKING']
        
        if alarm_code in high_severity:
            return 'HIGH'
        elif alarm_code in medium_severity:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def run_historical_migration(self):
        """Ejecuta la migración completa de logs históricos."""
        logger.info("🚀 INICIANDO MIGRACIÓN DE LOGS HISTÓRICOS")
        logger.info(f"Modo: {'DRY RUN' if self.dry_run else 'PRODUCCIÓN'}")
        
        if self.date_range_days:
            logger.info(f"Rango de fechas: últimos {self.date_range_days} días")
        else:
            logger.info("Rango de fechas: TODOS los registros")
        
        start_time = datetime.now()
        
        try:
            # Orden de migración
            migrations = [
                ("Acceleration Logs", self.migrate_acceleration_logs),
                ("Alarm Logs", self.migrate_alarm_logs),
                ("Device Stats", self.migrate_device_stats)
            ]
            
            for name, migration_func in migrations:
                logger.info(f"\n{'='*50}")
                logger.info(f"MIGRANDO: {name}")
                logger.info(f"{'='*50}")
                
                if not migration_func():
                    logger.error(f"❌ Falló la migración de {name}")
                    return False
            
            # Resumen final
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info(f"\n{'='*60}")
            logger.info("RESUMEN FINAL - MIGRACIÓN HISTÓRICA")
            logger.info(f"{'='*60}")
            logger.info(f"Tiempo total: {duration}")
            logger.info(f"Modo: {'DRY RUN' if self.dry_run else 'PRODUCCIÓN'}")
            
            total_migrated = sum(cat['migrated'] for cat in self.stats.values())
            total_errors = sum(cat['errors'] for cat in self.stats.values())
            total_skipped = sum(cat['skipped'] for cat in self.stats.values())
            
            logger.info(f"\nRESULTADOS:")
            for category, stats in self.stats.items():
                if any(stats.values()):
                    logger.info(f"  {category}: {stats['migrated']:,} migrados, "
                               f"{stats['errors']} errores, {stats['skipped']} saltados")
            
            logger.info(f"\nTOTAL: {total_migrated:,} registros migrados, "
                       f"{total_errors} errores, {total_skipped:,} saltados")
            
            if total_errors == 0:
                logger.info("✅ MIGRACIÓN HISTÓRICA COMPLETADA SIN ERRORES")
            else:
                logger.warning(f"⚠️  MIGRACIÓN HISTÓRICA COMPLETADA CON {total_errors} ERRORES")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error crítico durante la migración histórica: {e}")
            return False


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrar logs históricos del backend legacy')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Ejecutar en modo prueba sin modificar datos')
    parser.add_argument('--execute', action='store_true',
                       help='Ejecutar migración real (PELIGROSO)')
    parser.add_argument('--batch-size', type=int, default=5000,
                       help='Tamaño de lote para procesamiento')
    parser.add_argument('--days', type=int,
                       help='Migrar solo los últimos N días (por defecto: todos)')
    
    args = parser.parse_args()
    
    if args.execute:
        response = input("⚠️  ADVERTENCIA: Esto modificará la base de datos con datos históricos. ¿Continuar? (escriba 'SI' para confirmar): ")
        if response != 'SI':
            print("Migración cancelada.")
            return
        dry_run = False
    else:
        dry_run = True
    
    migrator = HistoricalLogMigrator(
        dry_run=dry_run, 
        batch_size=args.batch_size,
        date_range_days=args.days
    )
    
    if migrator.run_historical_migration():
        print("\n✅ Migración histórica completada exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Migración histórica falló")
        sys.exit(1)


if __name__ == '__main__':
    main() 