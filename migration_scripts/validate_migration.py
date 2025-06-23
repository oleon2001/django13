#!/usr/bin/env python3
"""
Script para validar la migración de datos del sistema legacy al nuevo.
Compara conteos y verifica integridad de datos.
"""

import os
import sys
import django
from datetime import datetime
from django.db import connection
from django.db.models import Count, Q
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
    AccelLog as LegacyAccelLog,
    AlarmLog as LegacyAlarmLog,
    Overlays as LegacyOverlays,
    Stats as LegacyStats
)

# New models
from skyguard.apps.gps.models import (
    GPSDevice, GeoFence, SimCard, DeviceHarness,
    AccelerationLog, GPSEvent, Overlay, DeviceStats
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MigrationValidator:
    """Validador de migración de datos."""
    
    def __init__(self):
        self.validation_results = {
            'sim_cards': {'status': 'PENDING', 'details': {}},
            'harnesses': {'status': 'PENDING', 'details': {}},
            'devices': {'status': 'PENDING', 'details': {}},
            'geofences': {'status': 'PENDING', 'details': {}},
            'overlays': {'status': 'PENDING', 'details': {}},
            'acceleration_logs': {'status': 'PENDING', 'details': {}},
            'alarm_logs': {'status': 'PENDING', 'details': {}},
            'device_stats': {'status': 'PENDING', 'details': {}}
        }
        self.total_issues = 0
    
    def validate_sim_cards(self):
        """Valida la migración de tarjetas SIM."""
        logger.info("🔍 Validando tarjetas SIM...")
        
        try:
            # Conteos
            legacy_count = LegacySimCard.objects.count()
            new_count = SimCard.objects.count()
            
            # Verificar integridad
            missing_sims = []
            for legacy_sim in LegacySimCard.objects.all():
                if not SimCard.objects.filter(iccid=legacy_sim.iccid).exists():
                    missing_sims.append(legacy_sim.iccid)
            
            # Verificar duplicados
            duplicates = SimCard.objects.values('iccid').annotate(
                count=Count('iccid')
            ).filter(count__gt=1)
            
            # Resultados
            self.validation_results['sim_cards'] = {
                'status': 'PASS' if len(missing_sims) == 0 and duplicates.count() == 0 else 'FAIL',
                'details': {
                    'legacy_count': legacy_count,
                    'migrated_count': new_count,
                    'missing_count': len(missing_sims),
                    'missing_items': missing_sims[:10],  # Solo los primeros 10
                    'duplicates_count': duplicates.count(),
                    'coverage_percentage': (new_count / legacy_count * 100) if legacy_count > 0 else 0
                }
            }
            
            if missing_sims:
                self.total_issues += len(missing_sims)
                logger.warning(f"❌ {len(missing_sims)} tarjetas SIM no migradas")
            else:
                logger.info("✅ Todas las tarjetas SIM migradas correctamente")
            
        except Exception as e:
            logger.error(f"Error validando SIM cards: {e}")
            self.validation_results['sim_cards']['status'] = 'ERROR'
    
    def validate_harnesses(self):
        """Valida la migración de configuraciones harness."""
        logger.info("🔍 Validando configuraciones harness...")
        
        try:
            legacy_count = LegacySGHarness.objects.count()
            new_count = DeviceHarness.objects.count()
            
            missing_harnesses = []
            for legacy_harness in LegacySGHarness.objects.all():
                if not DeviceHarness.objects.filter(name=legacy_harness.name).exists():
                    missing_harnesses.append(legacy_harness.name)
            
            self.validation_results['harnesses'] = {
                'status': 'PASS' if len(missing_harnesses) == 0 else 'FAIL',
                'details': {
                    'legacy_count': legacy_count,
                    'migrated_count': new_count,
                    'missing_count': len(missing_harnesses),
                    'missing_items': missing_harnesses,
                    'coverage_percentage': (new_count / legacy_count * 100) if legacy_count > 0 else 0
                }
            }
            
            if missing_harnesses:
                self.total_issues += len(missing_harnesses)
                logger.warning(f"❌ {len(missing_harnesses)} configuraciones harness no migradas")
            else:
                logger.info("✅ Todas las configuraciones harness migradas correctamente")
            
        except Exception as e:
            logger.error(f"Error validando harnesses: {e}")
            self.validation_results['harnesses']['status'] = 'ERROR'
    
    def validate_devices(self):
        """Valida la migración de dispositivos GPS."""
        logger.info("🔍 Validando dispositivos GPS...")
        
        try:
            legacy_count = LegacySGAvl.objects.count()
            new_count = GPSDevice.objects.count()
            
            missing_devices = []
            orphaned_devices = 0
            
            for legacy_device in LegacySGAvl.objects.all():
                if not GPSDevice.objects.filter(imei=legacy_device.imei).exists():
                    missing_devices.append(legacy_device.imei)
            
            # Verificar dispositivos sin SIM o harness cuando deberían tenerlos
            for new_device in GPSDevice.objects.all():
                legacy_device = LegacySGAvl.objects.filter(imei=new_device.imei).first()
                if legacy_device:
                    if legacy_device.sim and not new_device.sim_card:
                        orphaned_devices += 1
                    if legacy_device.harness and not new_device.harness:
                        orphaned_devices += 1
            
            self.validation_results['devices'] = {
                'status': 'PASS' if len(missing_devices) == 0 and orphaned_devices == 0 else 'FAIL',
                'details': {
                    'legacy_count': legacy_count,
                    'migrated_count': new_count,
                    'missing_count': len(missing_devices),
                    'missing_items': missing_devices[:10],
                    'orphaned_references': orphaned_devices,
                    'coverage_percentage': (new_count / legacy_count * 100) if legacy_count > 0 else 0
                }
            }
            
            issues = len(missing_devices) + orphaned_devices
            if issues > 0:
                self.total_issues += issues
                logger.warning(f"❌ {len(missing_devices)} dispositivos no migrados, {orphaned_devices} con referencias faltantes")
            else:
                logger.info("✅ Todos los dispositivos GPS migrados correctamente")
            
        except Exception as e:
            logger.error(f"Error validando devices: {e}")
            self.validation_results['devices']['status'] = 'ERROR'
    
    def validate_geofences(self):
        """Valida la migración de geocercas."""
        logger.info("🔍 Validando geocercas...")
        
        try:
            legacy_count = LegacyGeoFence.objects.count()
            new_count = GeoFence.objects.count()
            
            missing_fences = []
            for legacy_fence in LegacyGeoFence.objects.all():
                if not GeoFence.objects.filter(
                    name=legacy_fence.name, 
                    owner=legacy_fence.owner
                ).exists():
                    missing_fences.append(f"{legacy_fence.name} ({legacy_fence.owner})")
            
            self.validation_results['geofences'] = {
                'status': 'PASS' if len(missing_fences) == 0 else 'FAIL',
                'details': {
                    'legacy_count': legacy_count,
                    'migrated_count': new_count,
                    'missing_count': len(missing_fences),
                    'missing_items': missing_fences[:10],
                    'coverage_percentage': (new_count / legacy_count * 100) if legacy_count > 0 else 0
                }
            }
            
            if missing_fences:
                self.total_issues += len(missing_fences)
                logger.warning(f"❌ {len(missing_fences)} geocercas no migradas")
            else:
                logger.info("✅ Todas las geocercas migradas correctamente")
            
        except Exception as e:
            logger.error(f"Error validando geofences: {e}")
            self.validation_results['geofences']['status'] = 'ERROR'
    
    def validate_overlays(self):
        """Valida la migración de overlays."""
        logger.info("🔍 Validando overlays...")
        
        try:
            legacy_count = LegacyOverlays.objects.count()
            new_count = Overlay.objects.count()
            
            missing_overlays = []
            for legacy_overlay in LegacyOverlays.objects.all():
                if not Overlay.objects.filter(name=legacy_overlay.name).exists():
                    missing_overlays.append(legacy_overlay.name)
            
            self.validation_results['overlays'] = {
                'status': 'PASS' if len(missing_overlays) == 0 else 'FAIL',
                'details': {
                    'legacy_count': legacy_count,
                    'migrated_count': new_count,
                    'missing_count': len(missing_overlays),
                    'missing_items': missing_overlays,
                    'coverage_percentage': (new_count / legacy_count * 100) if legacy_count > 0 else 0
                }
            }
            
            if missing_overlays:
                self.total_issues += len(missing_overlays)
                logger.warning(f"❌ {len(missing_overlays)} overlays no migrados")
            else:
                logger.info("✅ Todos los overlays migrados correctamente")
            
        except Exception as e:
            logger.error(f"Error validando overlays: {e}")
            self.validation_results['overlays']['status'] = 'ERROR'
    
    def validate_acceleration_logs(self):
        """Valida la migración de logs de aceleración."""
        logger.info("🔍 Validando logs de aceleración...")
        
        try:
            legacy_count = LegacyAccelLog.objects.count()
            new_count = AccelerationLog.objects.count()
            
            # Verificación por muestreo (los logs son muchos)
            sample_size = min(1000, legacy_count)
            missing_logs = 0
            
            if sample_size > 0:
                legacy_sample = LegacyAccelLog.objects.all()[:sample_size]
                for legacy_log in legacy_sample:
                    device = GPSDevice.objects.filter(imei=legacy_log.imei).first()
                    if device:
                        if not AccelerationLog.objects.filter(
                            device=device,
                            timestamp=legacy_log.date,
                            x_axis=legacy_log.x,
                            y_axis=legacy_log.y,
                            z_axis=legacy_log.z
                        ).exists():
                            missing_logs += 1
            
            estimated_missing = (missing_logs / sample_size * legacy_count) if sample_size > 0 else 0
            
            self.validation_results['acceleration_logs'] = {
                'status': 'PASS' if missing_logs == 0 else 'WARN',
                'details': {
                    'legacy_count': legacy_count,
                    'migrated_count': new_count,
                    'sample_size': sample_size,
                    'missing_in_sample': missing_logs,
                    'estimated_missing': int(estimated_missing),
                    'coverage_percentage': (new_count / legacy_count * 100) if legacy_count > 0 else 0
                }
            }
            
            if missing_logs > 0:
                logger.warning(f"⚠️  {missing_logs}/{sample_size} logs de aceleración faltantes en muestra")
            else:
                logger.info("✅ Muestra de logs de aceleración validada correctamente")
            
        except Exception as e:
            logger.error(f"Error validando acceleration logs: {e}")
            self.validation_results['acceleration_logs']['status'] = 'ERROR'
    
    def validate_alarm_logs(self):
        """Valida la migración de logs de alarmas."""
        logger.info("🔍 Validando logs de alarmas...")
        
        try:
            legacy_count = LegacyAlarmLog.objects.count()
            new_count = GPSEvent.objects.filter(type__in=[
                'ALARM', 'PANIC', 'SPEEDING', 'GEOFENCE_ENTRY', 'GEOFENCE_EXIT',
                'POWER_DISCONNECT', 'POWER_CONNECT', 'LOW_BATTERY',
                'HARSH_ACCELERATION', 'HARSH_BRAKING', 'ACCIDENT'
            ]).count()
            
            # Verificación por muestreo
            sample_size = min(1000, legacy_count)
            missing_logs = 0
            
            if sample_size > 0:
                legacy_sample = LegacyAlarmLog.objects.all()[:sample_size]
                for legacy_log in legacy_sample:
                    device = GPSDevice.objects.filter(imei=legacy_log.imei).first()
                    if device:
                        if not GPSEvent.objects.filter(
                            device=device,
                            timestamp=legacy_log.date,
                            type='ALARM'
                        ).exists():
                            missing_logs += 1
            
            estimated_missing = (missing_logs / sample_size * legacy_count) if sample_size > 0 else 0
            
            self.validation_results['alarm_logs'] = {
                'status': 'PASS' if missing_logs == 0 else 'WARN',
                'details': {
                    'legacy_count': legacy_count,
                    'migrated_count': new_count,
                    'sample_size': sample_size,
                    'missing_in_sample': missing_logs,
                    'estimated_missing': int(estimated_missing),
                    'coverage_percentage': (new_count / legacy_count * 100) if legacy_count > 0 else 0
                }
            }
            
            if missing_logs > 0:
                logger.warning(f"⚠️  {missing_logs}/{sample_size} logs de alarmas faltantes en muestra")
            else:
                logger.info("✅ Muestra de logs de alarmas validada correctamente")
            
        except Exception as e:
            logger.error(f"Error validando alarm logs: {e}")
            self.validation_results['alarm_logs']['status'] = 'ERROR'
    
    def validate_device_stats(self):
        """Valida la migración de estadísticas de dispositivos."""
        logger.info("🔍 Validando estadísticas de dispositivos...")
        
        try:
            legacy_count = LegacyStats.objects.count()
            new_count = DeviceStats.objects.count()
            
            missing_stats = []
            for legacy_stat in LegacyStats.objects.all()[:100]:  # Muestra de 100
                device = GPSDevice.objects.filter(imei=legacy_stat.imei).first()
                if device:
                    if not DeviceStats.objects.filter(
                        device=device,
                        date=legacy_stat.date
                    ).exists():
                        missing_stats.append(f"{legacy_stat.imei} - {legacy_stat.date}")
            
            self.validation_results['device_stats'] = {
                'status': 'PASS' if len(missing_stats) == 0 else 'WARN',
                'details': {
                    'legacy_count': legacy_count,
                    'migrated_count': new_count,
                    'missing_in_sample': len(missing_stats),
                    'coverage_percentage': (new_count / legacy_count * 100) if legacy_count > 0 else 0
                }
            }
            
            if missing_stats:
                logger.warning(f"⚠️  {len(missing_stats)} estadísticas faltantes en muestra")
            else:
                logger.info("✅ Muestra de estadísticas validada correctamente")
            
        except Exception as e:
            logger.error(f"Error validando device stats: {e}")
            self.validation_results['device_stats']['status'] = 'ERROR'
    
    def generate_validation_report(self):
        """Genera reporte completo de validación."""
        logger.info("\n" + "="*60)
        logger.info("REPORTE DE VALIDACIÓN DE MIGRACIÓN")
        logger.info("="*60)
        
        passed = 0
        warnings = 0
        failed = 0
        errors = 0
        
        for category, result in self.validation_results.items():
            status = result['status']
            details = result.get('details', {})
            
            logger.info(f"\n📊 {category.upper().replace('_', ' ')}:")
            logger.info(f"   Estado: {status}")
            
            if 'legacy_count' in details:
                logger.info(f"   Legacy: {details['legacy_count']:,}")
                logger.info(f"   Migrados: {details['migrated_count']:,}")
                logger.info(f"   Cobertura: {details['coverage_percentage']:.1f}%")
            
            if 'missing_count' in details and details['missing_count'] > 0:
                logger.info(f"   Faltantes: {details['missing_count']}")
            
            if 'missing_in_sample' in details and details['missing_in_sample'] > 0:
                logger.info(f"   Faltantes en muestra: {details['missing_in_sample']}")
            
            # Contar estados
            if status == 'PASS':
                passed += 1
            elif status == 'WARN':
                warnings += 1
            elif status == 'FAIL':
                failed += 1
            elif status == 'ERROR':
                errors += 1
        
        # Resumen final
        logger.info(f"\n{'='*60}")
        logger.info("RESUMEN FINAL")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Pasaron: {passed}")
        logger.info(f"⚠️  Advertencias: {warnings}")
        logger.info(f"❌ Fallaron: {failed}")
        logger.info(f"🔥 Errores: {errors}")
        logger.info(f"📊 Total de problemas identificados: {self.total_issues}")
        
        # Estado general
        if failed == 0 and errors == 0:
            if warnings == 0:
                logger.info("\n🎉 MIGRACIÓN VALIDADA EXITOSAMENTE")
                return True
            else:
                logger.info("\n⚠️  MIGRACIÓN COMPLETADA CON ADVERTENCIAS")
                return True
        else:
            logger.info("\n❌ MIGRACIÓN TIENE PROBLEMAS CRÍTICOS")
            return False
    
    def run_full_validation(self):
        """Ejecuta validación completa."""
        logger.info("🚀 INICIANDO VALIDACIÓN DE MIGRACIÓN")
        start_time = datetime.now()
        
        try:
            # Ejecutar todas las validaciones
            validations = [
                ("SIM Cards", self.validate_sim_cards),
                ("Harnesses", self.validate_harnesses),
                ("GPS Devices", self.validate_devices),
                ("Geofences", self.validate_geofences),
                ("Overlays", self.validate_overlays),
                ("Acceleration Logs", self.validate_acceleration_logs),
                ("Alarm Logs", self.validate_alarm_logs),
                ("Device Stats", self.validate_device_stats)
            ]
            
            for name, validation_func in validations:
                logger.info(f"\n{'-'*40}")
                logger.info(f"Validando: {name}")
                logger.info(f"{'-'*40}")
                validation_func()
            
            # Generar reporte
            success = self.generate_validation_report()
            
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"\nTiempo total de validación: {duration}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error crítico durante la validación: {e}")
            return False


def main():
    """Función principal."""
    validator = MigrationValidator()
    
    if validator.run_full_validation():
        print("\n✅ Validación completada")
        sys.exit(0)
    else:
        print("\n❌ Validación encontró problemas")
        sys.exit(1)


if __name__ == '__main__':
    main() 