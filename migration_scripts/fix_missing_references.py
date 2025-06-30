#!/usr/bin/env python3
"""
Script para corregir referencias faltantes en dispositivos GPS migrados.
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
        logging.FileHandler('fix_missing_references.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ReferenceFixer:
    """Clase para arreglar referencias faltantes."""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.fixed_count = 0
        self.error_count = 0
    
    def find_missing_references(self):
        """Encuentra dispositivos con referencias faltantes."""
        logger.info("🔍 Buscando dispositivos con referencias faltantes...")
        
        missing_refs = []
        for new_device in GPSDevice.objects.all():
            legacy_device = LegacySGAvl.objects.filter(imei=new_device.imei).first()
            if legacy_device:
                issues = []
                
                # Verificar SIM faltante
                if legacy_device.sim and not new_device.sim_card:
                    sim_card = SimCard.objects.filter(iccid=legacy_device.sim.iccid).first()
                    if sim_card:
                        issues.append(('sim_card', sim_card))
                        logger.info(f"   ⚠️  Dispositivo {new_device.imei} - {new_device.name} SIN SIM (legacy tenía SIM)")
                    else:
                        logger.warning(f"   ❌ SIM {legacy_device.sim.iccid} no encontrada en nuevo sistema")
                
                # Verificar Harness faltante
                if legacy_device.harness and not new_device.harness:
                    harness = DeviceHarness.objects.filter(name=legacy_device.harness.name).first()
                    if harness:
                        issues.append(('harness', harness))
                        logger.info(f"   ⚠️  Dispositivo {new_device.imei} - {new_device.name} SIN HARNESS (legacy tenía harness)")
                    else:
                        logger.warning(f"   ❌ Harness {legacy_device.harness.name} no encontrado en nuevo sistema")
                
                if issues:
                    missing_refs.append({
                        'device': new_device,
                        'legacy_device': legacy_device,
                        'issues': issues
                    })
        
        logger.info(f"Total dispositivos con referencias faltantes: {len(missing_refs)}")
        return missing_refs
    
    def fix_device_references(self, device_info):
        """Corrige las referencias faltantes de un dispositivo."""
        device = device_info['device']
        issues = device_info['issues']
        
        logger.info(f"🔄 Corrigiendo referencias para dispositivo: {device.imei} - {device.name}")
        
        try:
            if not self.dry_run:
                with transaction.atomic():
                    for ref_type, ref_object in issues:
                        if ref_type == 'sim_card':
                            device.sim_card = ref_object
                            logger.info(f"   ✅ SIM asignada: {ref_object}")
                        elif ref_type == 'harness':
                            device.harness = ref_object
                            logger.info(f"   ✅ Harness asignado: {ref_object}")
                    
                    device.save()
                    logger.info(f"   ✅ Dispositivo actualizado exitosamente")
                    self.fixed_count += 1
            else:
                logger.info(f"   ✅ Referencias corregidas (dry-run):")
                for ref_type, ref_object in issues:
                    logger.info(f"      - {ref_type}: {ref_object}")
                self.fixed_count += 1
                
        except Exception as e:
            logger.error(f"   ❌ Error corrigiendo referencias para dispositivo {device.imei}: {e}")
            self.error_count += 1
            return False
        
        return True
    
    def run_fix(self):
        """Ejecuta la corrección de referencias faltantes."""
        logger.info("🚀 INICIANDO CORRECCIÓN DE REFERENCIAS FALTANTES")
        logger.info(f"Modo: {'DRY RUN' if self.dry_run else 'PRODUCCIÓN'}")
        logger.info("="*60)
        
        # Encontrar dispositivos con referencias faltantes
        missing_refs = self.find_missing_references()
        
        if not missing_refs:
            logger.info("✅ No hay dispositivos con referencias faltantes")
            return True
        
        # Corregir cada dispositivo
        for device_info in missing_refs:
            self.fix_device_references(device_info)
        
        # Reporte final
        logger.info("\n" + "="*60)
        logger.info("REPORTE DE CORRECCIÓN DE REFERENCIAS")
        logger.info("="*60)
        logger.info(f"Dispositivos corregidos: {self.fixed_count}")
        logger.info(f"Errores: {self.error_count}")
        
        if self.error_count == 0:
            logger.info("✅ CORRECCIÓN DE REFERENCIAS COMPLETADA EXITOSAMENTE")
            return True
        else:
            logger.error("❌ CORRECCIÓN DE REFERENCIAS CON ERRORES")
            return False


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Corregir referencias faltantes en dispositivos GPS')
    parser.add_argument('--dry-run', action='store_true', default=False,
                       help='Ejecutar en modo prueba sin guardar')
    parser.add_argument('--execute', action='store_true',
                       help='Ejecutar corrección real')
    
    args = parser.parse_args()
    
    # Determinar modo
    if args.execute:
        dry_run = False
        print("\n⚠️  ADVERTENCIA: Ejecutando corrección real de referencias")
        response = input("¿Continuar? (escriba 'SI' para confirmar): ")
        if response != 'SI':
            print("Corrección cancelada.")
            return
    else:
        dry_run = True
    
    # Ejecutar corrección
    fixer = ReferenceFixer(dry_run=dry_run)
    if fixer.run_fix():
        print("\n✅ Corrección de referencias completada exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Corrección de referencias falló")
        sys.exit(1)


if __name__ == '__main__':
    main() 