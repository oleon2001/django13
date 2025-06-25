#!/usr/bin/env python3
"""
Script principal para migrar datos del sistema legacy al nuevo backend.
IMPORTANTE: Ejecutar con backup completo de la base de datos.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.db import transaction, connection
from django.contrib.gis.geos import Point, Polygon, LineString
import logging

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

# Legacy models
from skyguard.gps.tracker.models import (
    SGAvl as LegacySGAvl,
    GeoFence as LegacyGeoFence,
    SimCard as LegacySimCard,
    SGHarness as LegacySGHarness,
    ServerSMS as LegacyServerSMS,
    AccelLog as LegacyAccelLog,
    Overlays as LegacyOverlays,
    Stats as LegacyStats,
    PsiCal as LegacyPsiCal,
    AlarmLog as LegacyAlarmLog
)

# New models
from skyguard.apps.gps.models import (
    GPSDevice, GeoFence, SimCard, DeviceHarness, ServerSMS,
    AccelerationLog, Overlay, DeviceStats, GPSLocation, GPSEvent
)

from django.contrib.auth.models import User

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataMigrator:
    """Clase principal para manejar la migración de datos."""
    
    def __init__(self, dry_run=True, batch_size=1000):
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.stats = {
            'devices': {'migrated': 0, 'errors': 0},
            'geofences': {'migrated': 0, 'errors': 0},
            'sim_cards': {'migrated': 0, 'errors': 0},
            'harnesses': {'migrated': 0, 'errors': 0},
            'sms_commands': {'migrated': 0, 'errors': 0},
            'acceleration_logs': {'migrated': 0, 'errors': 0},
            'overlays': {'migrated': 0, 'errors': 0},
            'device_stats': {'migrated': 0, 'errors': 0}
        }
    
    def log_progress(self, category, processed, total):
        """Log del progreso de migración."""
        percentage = (processed / total) * 100 if total > 0 else 0
        logger.info(f"{category}: {processed}/{total} ({percentage:.1f}%)")
    
    def migrate_sim_cards(self):
        """Migra las tarjetas SIM (sin dependencias)."""
        logger.info("🔄 Migrando tarjetas SIM...")
        
        legacy_sims = LegacySimCard.objects.all()
        total = legacy_sims.count()
        
        if total == 0:
            logger.info("No hay tarjetas SIM para migrar")
            return True
        
        for i, legacy_sim in enumerate(legacy_sims):
            try:
                with transaction.atomic():
                    if not self.dry_run:
                        # Verificar si ya existe
                        if not SimCard.objects.filter(iccid=legacy_sim.iccid).exists():
                            new_sim = SimCard(
                                iccid=legacy_sim.iccid,
                                imsi=legacy_sim.imsi,
                                provider=legacy_sim.provider,
                                phone=legacy_sim.phone
                            )
                            new_sim.save()
                            self.stats['sim_cards']['migrated'] += 1
                        else:
                            logger.debug(f"SIM {legacy_sim.iccid} ya existe, saltando...")
                    else:
                        self.stats['sim_cards']['migrated'] += 1
                
                if (i + 1) % 100 == 0:
                    self.log_progress("SIM Cards", i + 1, total)
                    
            except Exception as e:
                logger.error(f"Error migrando SIM {legacy_sim.iccid}: {e}")
                self.stats['sim_cards']['errors'] += 1
        
        logger.info(f"✅ SIM Cards: {self.stats['sim_cards']['migrated']} migradas, {self.stats['sim_cards']['errors']} errores")
        return True
    
    def migrate_device_harnesses(self):
        """Migra las configuraciones de harness."""
        logger.info("🔄 Migrando configuraciones harness...")
        
        legacy_harnesses = LegacySGHarness.objects.all()
        total = legacy_harnesses.count()
        
        if total == 0:
            logger.info("No hay configuraciones harness para migrar")
            return True
        
        for i, legacy_harness in enumerate(legacy_harnesses):
            try:
                with transaction.atomic():
                    if not self.dry_run:
                        if not DeviceHarness.objects.filter(name=legacy_harness.name).exists():
                            new_harness = DeviceHarness(
                                name=legacy_harness.name,
                                in00=legacy_harness.in00,
                                in01=legacy_harness.in01,
                                in02=legacy_harness.in02,
                                in03=legacy_harness.in03,
                                in04=legacy_harness.in04,
                                in05=legacy_harness.in05,
                                in06=legacy_harness.in06,
                                in07=legacy_harness.in07,
                                in08=legacy_harness.in08,
                                in09=legacy_harness.in09,
                                in10=legacy_harness.in10,
                                in11=legacy_harness.in11,
                                in12=legacy_harness.in12,
                                in13=legacy_harness.in13,
                                in14=legacy_harness.in14,
                                in15=legacy_harness.in15,
                                out00=legacy_harness.out00,
                                out01=legacy_harness.out01,
                                out02=legacy_harness.out02,
                                out03=legacy_harness.out03,
                                out04=legacy_harness.out04,
                                out05=legacy_harness.out05,
                                out06=legacy_harness.out06,
                                out07=legacy_harness.out07,
                                out08=legacy_harness.out08,
                                out09=legacy_harness.out09,
                                out10=legacy_harness.out10,
                                out11=legacy_harness.out11,
                                out12=legacy_harness.out12,
                                out13=legacy_harness.out13,
                                out14=legacy_harness.out14,
                                out15=legacy_harness.out15,
                                input_config=legacy_harness.inputCfg
                            )
                            new_harness.save()
                            self.stats['harnesses']['migrated'] += 1
                        else:
                            logger.debug(f"Harness {legacy_harness.name} ya existe, saltando...")
                    else:
                        self.stats['harnesses']['migrated'] += 1
                
                if (i + 1) % 10 == 0:
                    self.log_progress("Harnesses", i + 1, total)
                    
            except Exception as e:
                logger.error(f"Error migrando harness {legacy_harness.name}: {e}")
                self.stats['harnesses']['errors'] += 1
        
        logger.info(f"✅ Harnesses: {self.stats['harnesses']['migrated']} migrados, {self.stats['harnesses']['errors']} errores")
        return True
    
    def migrate_gps_devices(self):
        """Migra los dispositivos GPS."""
        logger.info("🔄 Migrando dispositivos GPS...")
        
        legacy_devices = LegacySGAvl.objects.all()
        total = legacy_devices.count()
        
        if total == 0:
            logger.info("No hay dispositivos GPS para migrar")
            return True
        
        for i, legacy_device in enumerate(legacy_devices):
            try:
                with transaction.atomic():
                    if not self.dry_run:
                        if not GPSDevice.objects.filter(imei=legacy_device.imei).exists():
                            # Obtener referencias
                            sim_card = None
                            if legacy_device.sim:
                                sim_card = SimCard.objects.filter(iccid=legacy_device.sim.iccid).first()
                            
                            harness = None
                            if legacy_device.harness:
                                harness = DeviceHarness.objects.filter(name=legacy_device.harness.name).first()
                            
                            new_device = GPSDevice(
                                imei=legacy_device.imei,
                                name=legacy_device.name,
                                position=legacy_device.position,
                                speed=legacy_device.speed,
                                course=legacy_device.course,
                                last_connection=legacy_device.date,
                                last_log=legacy_device.lastLog,
                                owner=legacy_device.owner,
                                icon=legacy_device.icon,
                                odometer=legacy_device.odom or 0,
                                altitude=legacy_device.altitude or 0,
                                serial=legacy_device.serial,
                                model=legacy_device.model,
                                software_version=legacy_device.swversion,
                                inputs=legacy_device.inputs,
                                outputs=legacy_device.outputs,
                                alarm_mask=legacy_device.alarmMask,
                                alarms=legacy_device.alarms,
                                firmware_file=legacy_device.fwFile,
                                last_firmware_update=legacy_device.lastFwUpdate,
                                comments=legacy_device.comments,
                                sim_card=sim_card,
                                route=legacy_device.ruta,
                                economico=legacy_device.economico,
                                harness=harness,
                                new_outputs=legacy_device.newOutputs,
                                new_input_flags=legacy_device.newInflags or '',
                                # Nuevos campos con valores por defecto
                                connection_status='OFFLINE',
                                is_active=True,
                                protocol='concox'  # Valor por defecto
                            )
                            new_device.save()
                            self.stats['devices']['migrated'] += 1
                        else:
                            logger.debug(f"Dispositivo {legacy_device.imei} ya existe, saltando...")
                    else:
                        self.stats['devices']['migrated'] += 1
                
                if (i + 1) % 50 == 0:
                    self.log_progress("GPS Devices", i + 1, total)
                    
            except Exception as e:
                logger.error(f"Error migrando dispositivo {legacy_device.imei}: {e}")
                self.stats['devices']['errors'] += 1
        
        logger.info(f"✅ Dispositivos GPS: {self.stats['devices']['migrated']} migrados, {self.stats['devices']['errors']} errores")
        return True
    
    def migrate_geofences(self):
        """Migra las geocercas."""
        logger.info("🔄 Migrando geocercas...")
        
        legacy_fences = LegacyGeoFence.objects.all()
        total = legacy_fences.count()
        
        if total == 0:
            logger.info("No hay geocercas para migrar")
            return True
        
        for i, legacy_fence in enumerate(legacy_fences):
            try:
                with transaction.atomic():
                    if not self.dry_run:
                        if not GeoFence.objects.filter(name=legacy_fence.name, owner=legacy_fence.owner).exists():
                            new_fence = GeoFence(
                                name=legacy_fence.name,
                                geometry=legacy_fence.fence,
                                owner=legacy_fence.owner,
                                base=legacy_fence.base,
                                # Nuevos campos con valores por defecto
                                is_active=True,
                                notify_on_entry=True,
                                notify_on_exit=True
                            )
                            new_fence.save()
                            self.stats['geofences']['migrated'] += 1
                        else:
                            logger.debug(f"Geocerca {legacy_fence.name} ya existe, saltando...")
                    else:
                        self.stats['geofences']['migrated'] += 1
                
                if (i + 1) % 20 == 0:
                    self.log_progress("Geofences", i + 1, total)
                    
            except Exception as e:
                logger.error(f"Error migrando geocerca {legacy_fence.name}: {e}")
                self.stats['geofences']['errors'] += 1
        
        logger.info(f"✅ Geocercas: {self.stats['geofences']['migrated']} migradas, {self.stats['geofences']['errors']} errores")
        return True
    
    def migrate_overlays(self):
        """Migra los overlays de mapa."""
        logger.info("🔄 Migrando overlays...")
        
        legacy_overlays = LegacyOverlays.objects.all()
        total = legacy_overlays.count()
        
        if total == 0:
            logger.info("No hay overlays para migrar")
            return True
        
        for i, legacy_overlay in enumerate(legacy_overlays):
            try:
                with transaction.atomic():
                    if not self.dry_run:
                        if not Overlay.objects.filter(name=legacy_overlay.name).exists():
                            new_overlay = Overlay(
                                name=legacy_overlay.name,
                                geometry=legacy_overlay.geometry,
                                owner=legacy_overlay.owner,
                                base=legacy_overlay.base
                            )
                            new_overlay.save()
                            self.stats['overlays']['migrated'] += 1
                        else:
                            logger.debug(f"Overlay {legacy_overlay.name} ya existe, saltando...")
                    else:
                        self.stats['overlays']['migrated'] += 1
                
                if (i + 1) % 20 == 0:
                    self.log_progress("Overlays", i + 1, total)
                    
            except Exception as e:
                logger.error(f"Error migrando overlay {legacy_overlay.name}: {e}")
                self.stats['overlays']['errors'] += 1
        
        logger.info(f"✅ Overlays: {self.stats['overlays']['migrated']} migrados, {self.stats['overlays']['errors']} errores")
        return True
    
    def run_full_migration(self):
        """Ejecuta la migración completa en el orden correcto."""
        logger.info("🚀 INICIANDO MIGRACIÓN COMPLETA")
        logger.info(f"Modo: {'DRY RUN' if self.dry_run else 'PRODUCCIÓN'}")
        
        start_time = datetime.now()
        
        try:
            # Orden de migración (respetando dependencias)
            migrations = [
                ("SIM Cards", self.migrate_sim_cards),
                ("Device Harnesses", self.migrate_device_harnesses),
                ("GPS Devices", self.migrate_gps_devices),
                ("Geofences", self.migrate_geofences),
                ("Overlays", self.migrate_overlays)
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
            logger.info("RESUMEN FINAL DE MIGRACIÓN")
            logger.info(f"{'='*60}")
            logger.info(f"Tiempo total: {duration}")
            logger.info(f"Modo: {'DRY RUN' if self.dry_run else 'PRODUCCIÓN'}")
            
            total_migrated = sum(cat['migrated'] for cat in self.stats.values())
            total_errors = sum(cat['errors'] for cat in self.stats.values())
            
            logger.info(f"\nRESULTADOS:")
            for category, stats in self.stats.items():
                if stats['migrated'] > 0 or stats['errors'] > 0:
                    logger.info(f"  {category}: {stats['migrated']} migrados, {stats['errors']} errores")
            
            logger.info(f"\nTOTAL: {total_migrated} registros migrados, {total_errors} errores")
            
            if total_errors == 0:
                logger.info("✅ MIGRACIÓN COMPLETADA SIN ERRORES")
            else:
                logger.warning(f"⚠️  MIGRACIÓN COMPLETADA CON {total_errors} ERRORES")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error crítico durante la migración: {e}")
            return False


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrar datos del backend legacy al nuevo')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Ejecutar en modo prueba sin modificar datos')
    parser.add_argument('--execute', action='store_true',
                       help='Ejecutar migración real (PELIGROSO)')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Tamaño de lote para procesamiento')
    
    args = parser.parse_args()
    
    if args.execute:
        response = input("⚠️  ADVERTENCIA: Esto modificará la base de datos. ¿Continuar? (escriba 'SI' para confirmar): ")
        if response != 'SI':
            print("Migración cancelada.")
            return
        dry_run = False
    else:
        dry_run = True
    
    migrator = DataMigrator(dry_run=dry_run, batch_size=args.batch_size)
    
    if migrator.run_full_migration():
        print("\n✅ Migración completada exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Migración falló")
        sys.exit(1)


if __name__ == '__main__':
    main() 