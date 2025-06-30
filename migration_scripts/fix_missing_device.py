#!/usr/bin/env python3
"""
Script para migrar específicamente el dispositivo GPS faltante.
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
        logging.FileHandler('fix_missing_device.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DeviceFixer:
    """Clase para arreglar dispositivos faltantes."""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.fixed_count = 0
        self.error_count = 0
    
    def find_missing_devices(self):
        """Encuentra dispositivos legacy que no están en el nuevo sistema."""
        logger.info("🔍 Buscando dispositivos faltantes...")
        
        missing_devices = []
        legacy_devices = LegacySGAvl.objects.all()
        
        for legacy_device in legacy_devices:
            if not GPSDevice.objects.filter(imei=legacy_device.imei).exists():
                missing_devices.append(legacy_device)
                logger.info(f"   ❌ Dispositivo faltante: {legacy_device.imei} - {legacy_device.name}")
        
        logger.info(f"Total dispositivos faltantes: {len(missing_devices)}")
        return missing_devices
    
    def migrate_device(self, legacy_device):
        """Migra un dispositivo específico."""
        logger.info(f"🔄 Migrando dispositivo: {legacy_device.imei} - {legacy_device.name}")
        
        try:
            # Obtener referencias
            sim_card = None
            if legacy_device.sim:
                sim_card = SimCard.objects.filter(iccid=legacy_device.sim.iccid).first()
                logger.info(f"   SIM encontrada: {sim_card}")
            
            harness = None
            if legacy_device.harness:
                harness = DeviceHarness.objects.filter(name=legacy_device.harness.name).first()
                logger.info(f"   Harness encontrado: {harness}")
            
            # Crear el dispositivo con manejo de valores None
            new_device = GPSDevice(
                imei=legacy_device.imei,
                name=legacy_device.name or f"Dispositivo {legacy_device.imei}",
                position=legacy_device.position,
                speed=legacy_device.speed or 0,
                course=legacy_device.course or 0,
                last_connection=legacy_device.date,
                last_log=legacy_device.lastLog,
                owner=legacy_device.owner,
                icon=legacy_device.icon or 'default.png',
                odometer=legacy_device.odom or 0,
                altitude=legacy_device.altitude or 0,
                serial=legacy_device.serial or 0,
                model=legacy_device.model or 0,
                software_version=legacy_device.swversion or '----',
                inputs=legacy_device.inputs or 0,
                outputs=legacy_device.outputs or 0,
                alarm_mask=legacy_device.alarmMask or 0x0141,
                alarms=legacy_device.alarms or 0,
                firmware_file=legacy_device.fwFile or '',
                last_firmware_update=legacy_device.lastFwUpdate,
                comments=legacy_device.comments or '',
                sim_card=sim_card,
                route=legacy_device.ruta,
                economico=legacy_device.economico,
                harness=harness,
                new_outputs=legacy_device.newOutputs,
                new_input_flags=legacy_device.newInflags or '',
                # Nuevos campos con valores por defecto
                connection_status='OFFLINE',
                is_active=True,
                protocol='concox'
            )
            
            if not self.dry_run:
                with transaction.atomic():
                    new_device.save()
                    logger.info(f"   ✅ Dispositivo guardado exitosamente")
                    self.fixed_count += 1
            else:
                logger.info(f"   ✅ Dispositivo creado (dry-run)")
                self.fixed_count += 1
                
        except Exception as e:
            logger.error(f"   ❌ Error migrando dispositivo {legacy_device.imei}: {e}")
            self.error_count += 1
            return False
        
        return True
    
    def fix_orphaned_references(self):
        """Corrige dispositivos migrados con referencias faltantes (harness o SIM)."""
        logger.info("\n🔧 Corrigiendo referencias faltantes en dispositivos migrados...")
        fixed = 0
        for new_device in GPSDevice.objects.all():
            legacy_device = LegacySGAvl.objects.filter(imei=new_device.imei).first()
            if not legacy_device:
                continue
            update_needed = False
            # Corregir harness
            if legacy_device.harness and not new_device.harness:
                harness = DeviceHarness.objects.filter(name=legacy_device.harness.name).first()
                if harness:
                    new_device.harness = harness
                    update_needed = True
                    logger.info(f"   ✅ Asignado harness '{harness.name}' a {new_device.imei} - {new_device.name}")
                else:
                    logger.warning(f"   ⚠️  No se encontró harness '{legacy_device.harness.name}' para {new_device.imei}")
            # Corregir SIM
            if legacy_device.sim and not new_device.sim_card:
                sim_card = SimCard.objects.filter(iccid=legacy_device.sim.iccid).first()
                if sim_card:
                    new_device.sim_card = sim_card
                    update_needed = True
                    logger.info(f"   ✅ Asignada SIM '{sim_card.iccid}' a {new_device.imei} - {new_device.name}")
                else:
                    logger.warning(f"   ⚠️  No se encontró SIM '{legacy_device.sim.iccid}' para {new_device.imei}")
            if update_needed and not self.dry_run:
                new_device.save()
                fixed += 1
        logger.info(f"\nReferencias corregidas: {fixed}")
        return fixed

    def run_fix(self):
        """Ejecuta la corrección de dispositivos faltantes."""
        logger.info("🚀 INICIANDO CORRECCIÓN DE DISPOSITIVOS FALTANTES")
        logger.info(f"Modo: {'DRY RUN' if self.dry_run else 'PRODUCCIÓN'}")
        logger.info("="*60)
        
        # Encontrar dispositivos faltantes
        missing_devices = self.find_missing_devices()
        
        if not missing_devices:
            logger.info("✅ No hay dispositivos faltantes")
        else:
            # Migrar cada dispositivo faltante
            for legacy_device in missing_devices:
                self.migrate_device(legacy_device)
        
        # Corregir referencias huérfanas
        self.fix_orphaned_references()
        
        # Reporte final
        logger.info("\n" + "="*60)
        logger.info("REPORTE DE CORRECCIÓN")
        logger.info("="*60)
        logger.info(f"Dispositivos corregidos: {self.fixed_count}")
        logger.info(f"Errores: {self.error_count}")
        
        if self.error_count == 0:
            logger.info("✅ CORRECCIÓN COMPLETADA EXITOSAMENTE")
            return True
        else:
            logger.error("❌ CORRECCIÓN CON ERRORES")
            return False


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Corregir dispositivos GPS faltantes')
    parser.add_argument('--dry-run', action='store_true', default=False,
                       help='Ejecutar en modo prueba sin guardar')
    parser.add_argument('--execute', action='store_true',
                       help='Ejecutar corrección real')
    
    args = parser.parse_args()
    
    # Determinar modo
    if args.execute:
        dry_run = False
        print("\n⚠️  ADVERTENCIA: Ejecutando corrección real")
        response = input("¿Continuar? (escriba 'SI' para confirmar): ")
        if response != 'SI':
            print("Corrección cancelada.")
            return
    else:
        dry_run = True
    
    # Ejecutar corrección
    fixer = DeviceFixer(dry_run=dry_run)
    if fixer.run_fix():
        print("\n✅ Corrección completada exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Corrección falló")
        sys.exit(1)


if __name__ == '__main__':
    main() 