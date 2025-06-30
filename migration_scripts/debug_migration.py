#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas en la migración de dispositivos GPS.
"""

import os
import sys
import django
from datetime import datetime
from django.db import transaction
import logging

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

# Legacy models
from skyguard.gps.tracker.models import (
    SGAvl as LegacySGAvl,
    SimCard as LegacySimCard,
    SGHarness as LegacySGHarness
)

# New models
from skyguard.apps.gps.models import (
    GPSDevice, SimCard, DeviceHarness
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MigrationDebugger:
    """Debugger para problemas de migración."""
    
    def __init__(self):
        self.issues = []
    
    def analyze_legacy_devices(self):
        """Analiza los dispositivos legacy para identificar problemas."""
        logger.info("🔍 ANALIZANDO DISPOSITIVOS LEGACY")
        logger.info("="*50)
        
        legacy_devices = LegacySGAvl.objects.all()
        logger.info(f"Total dispositivos legacy: {legacy_devices.count()}")
        
        for device in legacy_devices:
            logger.info(f"\n📱 Dispositivo: {device.imei} - {device.name}")
            logger.info(f"   Propietario: {device.owner}")
            logger.info(f"   SIM: {device.sim}")
            logger.info(f"   Harness: {device.harness}")
            logger.info(f"   Posición: {device.position}")
            logger.info(f"   Último log: {device.lastLog}")
            logger.info(f"   Fecha: {device.date}")
            
            # Verificar si ya existe en el nuevo sistema
            new_device = GPSDevice.objects.filter(imei=device.imei).first()
            if new_device:
                logger.info(f"   ✅ Ya migrado al nuevo sistema")
            else:
                logger.info(f"   ❌ NO migrado al nuevo sistema")
                self.issues.append({
                    'imei': device.imei,
                    'name': device.name,
                    'issue': 'not_migrated'
                })
    
    def analyze_new_devices(self):
        """Analiza los dispositivos del nuevo sistema."""
        logger.info("\n🔍 ANALIZANDO DISPOSITIVOS NUEVOS")
        logger.info("="*50)
        
        new_devices = GPSDevice.objects.all()
        logger.info(f"Total dispositivos nuevos: {new_devices.count()}")
        
        for device in new_devices:
            logger.info(f"\n📱 Dispositivo: {device.imei} - {device.name}")
            logger.info(f"   Propietario: {device.owner}")
            logger.info(f"   SIM: {device.sim_card}")
            logger.info(f"   Harness: {device.harness}")
            logger.info(f"   Posición: {device.position}")
            logger.info(f"   Último log: {device.last_log}")
            logger.info(f"   Última conexión: {device.last_connection}")
            
            # Verificar si existe en el sistema legacy
            legacy_device = LegacySGAvl.objects.filter(imei=device.imei).first()
            if legacy_device:
                logger.info(f"   ✅ Existe en sistema legacy")
            else:
                logger.info(f"   ❌ NO existe en sistema legacy")
                self.issues.append({
                    'imei': device.imei,
                    'name': device.name,
                    'issue': 'orphaned_new_device'
                })
    
    def check_references(self):
        """Verifica las referencias entre dispositivos y SIM/harness."""
        logger.info("\n🔍 VERIFICANDO REFERENCIAS")
        logger.info("="*50)
        
        # Verificar SIM cards
        logger.info("\n📞 SIM CARDS:")
        legacy_sims = LegacySimCard.objects.all()
        new_sims = SimCard.objects.all()
        logger.info(f"Legacy: {legacy_sims.count()}, Nuevas: {new_sims.count()}")
        
        for sim in legacy_sims:
            new_sim = SimCard.objects.filter(iccid=sim.iccid).first()
            if new_sim:
                logger.info(f"   ✅ SIM {sim.iccid} migrada")
            else:
                logger.info(f"   ❌ SIM {sim.iccid} NO migrada")
        
        # Verificar Harnesses
        logger.info("\n🔧 HARNESSES:")
        legacy_harnesses = LegacySGHarness.objects.all()
        new_harnesses = DeviceHarness.objects.all()
        logger.info(f"Legacy: {legacy_harnesses.count()}, Nuevos: {new_harnesses.count()}")
        
        for harness in legacy_harnesses:
            new_harness = DeviceHarness.objects.filter(name=harness.name).first()
            if new_harness:
                logger.info(f"   ✅ Harness {harness.name} migrado")
            else:
                logger.info(f"   ❌ Harness {harness.name} NO migrado")
    
    def check_orphaned_references(self):
        """Identifica dispositivos con referencias faltantes (SIM o harness)."""
        logger.info("\n🔍 BUSCANDO DISPOSITIVOS CON REFERENCIAS FALTANTES")
        logger.info("="*50)
        orphaned = []
        for new_device in GPSDevice.objects.all():
            legacy_device = LegacySGAvl.objects.filter(imei=new_device.imei).first()
            if legacy_device:
                if legacy_device.sim and not new_device.sim_card:
                    logger.warning(f"   ⚠️  Dispositivo {new_device.imei} - {new_device.name} SIN SIM (legacy tenía SIM)")
                    orphaned.append({'imei': new_device.imei, 'name': new_device.name, 'missing': 'sim_card'})
                if legacy_device.harness and not new_device.harness:
                    logger.warning(f"   ⚠️  Dispositivo {new_device.imei} - {new_device.name} SIN HARNESS (legacy tenía harness)")
                    orphaned.append({'imei': new_device.imei, 'name': new_device.name, 'missing': 'harness'})
        if not orphaned:
            logger.info("✅ No se encontraron dispositivos con referencias faltantes")
        else:
            logger.info(f"❌ Se encontraron {len(orphaned)} dispositivos con referencias faltantes")
        self.issues.extend([{'imei': o['imei'], 'name': o['name'], 'issue': f"missing_{o['missing']}"} for o in orphaned])
    
    def test_migration_logic(self):
        """Prueba la lógica de migración para un dispositivo específico."""
        logger.info("\n🧪 PROBANDO LÓGICA DE MIGRACIÓN")
        logger.info("="*50)
        
        # Encontrar un dispositivo que no se migró
        legacy_devices = LegacySGAvl.objects.all()
        for legacy_device in legacy_devices:
            if not GPSDevice.objects.filter(imei=legacy_device.imei).exists():
                logger.info(f"Probando migración para dispositivo: {legacy_device.imei}")
                
                try:
                    # Simular la lógica de migración
                    sim_card = None
                    if legacy_device.sim:
                        sim_card = SimCard.objects.filter(iccid=legacy_device.sim.iccid).first()
                        logger.info(f"   SIM encontrada: {sim_card}")
                    
                    harness = None
                    if legacy_device.harness:
                        harness = DeviceHarness.objects.filter(name=legacy_device.harness.name).first()
                        logger.info(f"   Harness encontrado: {harness}")
                    
                    # Verificar campos problemáticos
                    logger.info(f"   IMEI: {legacy_device.imei}")
                    logger.info(f"   Nombre: {legacy_device.name}")
                    logger.info(f"   Propietario: {legacy_device.owner}")
                    logger.info(f"   Posición: {legacy_device.position}")
                    logger.info(f"   Último log: {legacy_device.lastLog}")
                    logger.info(f"   Fecha: {legacy_device.date}")
                    
                    # Intentar crear el dispositivo (sin guardar)
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
                        connection_status='OFFLINE',
                        is_active=True,
                        protocol='concox'
                    )
                    
                    logger.info("   ✅ Objeto GPSDevice creado exitosamente")
                    
                    # Intentar guardar
                    with transaction.atomic():
                        new_device.save()
                        logger.info("   ✅ Dispositivo guardado exitosamente")
                        # Rollback para no afectar la base de datos
                        transaction.set_rollback(True)
                    
                except Exception as e:
                    logger.error(f"   ❌ Error en migración: {e}")
                    self.issues.append({
                        'imei': legacy_device.imei,
                        'name': legacy_device.name,
                        'issue': 'migration_error',
                        'error': str(e)
                    })
                
                break  # Solo probar el primer dispositivo no migrado
    
    def generate_report(self):
        """Genera un reporte de diagnóstico."""
        logger.info("\n📊 REPORTE DE DIAGNÓSTICO")
        logger.info("="*50)
        
        if self.issues:
            logger.info(f"❌ Se encontraron {len(self.issues)} problemas:")
            for issue in self.issues:
                logger.info(f"   - {issue['imei']} ({issue['name']}): {issue['issue']}")
                if 'error' in issue:
                    logger.info(f"     Error: {issue['error']}")
        else:
            logger.info("✅ No se encontraron problemas evidentes")
    
    def run_full_diagnosis(self):
        """Ejecuta el diagnóstico completo."""
        logger.info("🚀 INICIANDO DIAGNÓSTICO DE MIGRACIÓN")
        logger.info("="*60)
        
        self.analyze_legacy_devices()
        self.analyze_new_devices()
        self.check_references()
        self.check_orphaned_references()
        self.test_migration_logic()
        self.generate_report()
        
        logger.info("\n✅ Diagnóstico completado")


def main():
    """Función principal."""
    debugger = MigrationDebugger()
    debugger.run_full_diagnosis()


if __name__ == '__main__':
    main() 