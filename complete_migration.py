#!/usr/bin/env python3
"""
Script para completar la migración faltante de dispositivos GPS y configuraciones harness.
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
django.setup()

def complete_missing_migration():
    """Completa la migración de elementos faltantes."""
    print("=" * 80)
    print("COMPLETANDO MIGRACIÓN FALTANTE")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar modelos legacy y nuevos
        from skyguard.gps.tracker.models import SGAvl, SGHarness
        from skyguard.apps.gps.models import GPSDevice, DeviceHarness
        print("✅ Modelos importados correctamente")
        print()
        
    except ImportError as e:
        print(f"❌ Error importando modelos: {e}")
        return False
    
    # Migrar configuraciones harness faltantes
    print("🔧 MIGRANDO CONFIGURACIONES HARNESS FALTANTES...")
    harness_migrated = 0
    harness_errors = 0
    
    try:
        legacy_harnesses = SGHarness.objects.all()
        for legacy_harness in legacy_harnesses:
            # Verificar si ya existe
            if DeviceHarness.objects.filter(name=legacy_harness.name).exists():
                print(f"  ⏭️  Harness '{legacy_harness.name}' ya existe, saltando...")
                continue
                
            try:
                # Crear nuevo harness con los campos correctos
                new_harness = DeviceHarness(
                    name=legacy_harness.name,
                    in00=legacy_harness.in00 or "PANIC",
                    in01=legacy_harness.in01 or "IGNITION",
                    in02=legacy_harness.in02 or "",
                    in03=legacy_harness.in03 or "",
                    in04=legacy_harness.in04 or "",
                    in05=legacy_harness.in05 or "",
                    in06=legacy_harness.in06 or "BAT_DOK",
                    in07=legacy_harness.in07 or "BAT_CHG",
                    in08=legacy_harness.in08 or "BAT_FLT",
                    in09=legacy_harness.in09 or "",
                    in10=legacy_harness.in10 or "",
                    in11=legacy_harness.in11 or "",
                    in12=legacy_harness.in12 or "",
                    in13=legacy_harness.in13 or "",
                    in14=legacy_harness.in14 or "",
                    in15=legacy_harness.in15 or "",
                    out00=legacy_harness.out00 or "MOTOR",
                    out01=legacy_harness.out01 or "",
                    out02=legacy_harness.out02 or "",
                    out03=legacy_harness.out03 or "",
                    out04=legacy_harness.out04 or "",
                    out05=legacy_harness.out05 or "",
                    out06=legacy_harness.out06 or "",
                    out07=legacy_harness.out07 or "",
                    out08=legacy_harness.out08 or "",
                    out09=legacy_harness.out09 or "",
                    out10=legacy_harness.out10 or "",
                    out11=legacy_harness.out11 or "",
                    out12=legacy_harness.out12 or "",
                    out13=legacy_harness.out13 or "",
                    out14=legacy_harness.out14 or "",
                    out15=legacy_harness.out15 or "",
                    input_config=getattr(legacy_harness, 'inputCfg', '') or ""
                )
                new_harness.save()
                print(f"  ✅ Harness '{legacy_harness.name}' migrado correctamente")
                harness_migrated += 1
                
            except Exception as e:
                print(f"  ❌ Error migrando harness '{legacy_harness.name}': {e}")
                harness_errors += 1
                
    except Exception as e:
        print(f"  ❌ Error general migrando harnesses: {e}")
        harness_errors += 1
    
    print(f"Configuraciones harness: {harness_migrated} migradas, {harness_errors} errores")
    print()
    
    # Migrar dispositivos GPS faltantes
    print("🚗 MIGRANDO DISPOSITIVOS GPS FALTANTES...")
    device_migrated = 0
    device_errors = 0
    
    try:
        legacy_devices = SGAvl.objects.all()
        for legacy_device in legacy_devices:
            # Verificar si ya existe
            if GPSDevice.objects.filter(imei=legacy_device.imei).exists():
                print(f"  ⏭️  Dispositivo {legacy_device.imei} ya existe, saltando...")
                continue
                
            try:
                # Buscar harness correspondiente
                harness_obj = None
                if hasattr(legacy_device, 'harness') and legacy_device.harness:
                    try:
                        harness_obj = DeviceHarness.objects.get(name=legacy_device.harness.name)
                    except DeviceHarness.DoesNotExist:
                        print(f"  ⚠️  Harness '{legacy_device.harness.name}' no encontrado para dispositivo {legacy_device.imei}")
                
                # Crear nuevo dispositivo con los campos correctos
                new_device = GPSDevice(
                    imei=legacy_device.imei,
                    name=legacy_device.name,
                    position=legacy_device.position,
                    speed=legacy_device.speed or 0,
                    course=legacy_device.course or 0,
                    altitude=legacy_device.altitude or 0,
                    last_log=legacy_device.lastLog,
                    owner=legacy_device.owner,
                    icon=legacy_device.icon or 'default.png',
                    odometer=legacy_device.odom or 0,
                    # Campos específicos de GPS
                    serial=str(legacy_device.serial) if hasattr(legacy_device, 'serial') else "",
                    model=getattr(legacy_device, 'model', 0),
                    software_version=getattr(legacy_device, 'swversion', ''),
                    route=getattr(legacy_device, 'ruta', None),
                    economico=getattr(legacy_device, 'economico', None),
                    harness=harness_obj,
                    new_outputs=getattr(legacy_device, 'newOutputs', None),
                    new_input_flags=getattr(legacy_device, 'newInflags', ''),
                    is_active=True,
                    connection_status='OFFLINE'
                )
                new_device.save()
                print(f"  ✅ Dispositivo {legacy_device.imei} - {legacy_device.name} migrado correctamente")
                device_migrated += 1
                
            except Exception as e:
                print(f"  ❌ Error migrando dispositivo {legacy_device.imei}: {e}")
                device_errors += 1
                
    except Exception as e:
        print(f"  ❌ Error general migrando dispositivos: {e}")
        device_errors += 1
    
    print(f"Dispositivos GPS: {device_migrated} migrados, {device_errors} errores")
    print()
    
    # Resumen final
    print("=" * 80)
    print("RESUMEN DE MIGRACIÓN COMPLETADA")
    print("=" * 80)
    total_migrated = harness_migrated + device_migrated
    total_errors = harness_errors + device_errors
    
    print(f"✅ Total migrado: {total_migrated} elementos")
    if total_errors > 0:
        print(f"❌ Total errores: {total_errors}")
    
    if total_errors == 0:
        print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("📋 Acciones recomendadas:")
        print("   1. Ejecutar validación completa")
        print("   2. Verificar integridad de datos")
        print("   3. Realizar pruebas funcionales")
        return True
    else:
        print("⚠️  MIGRACIÓN COMPLETADA CON {} ERRORES".format(total_errors))
        print("📋 Acciones recomendadas:")
        print("   1. Revisar errores reportados")
        print("   2. Corregir problemas manualmente si es necesario")
        print("   3. Ejecutar validación para verificar integridad")
        return False

if __name__ == "__main__":
    success = complete_missing_migration()
    if success:
        print("✅ Script completado exitosamente")
        sys.exit(0)
    else:
        print("⚠️  Script completado con advertencias")
        sys.exit(1) 