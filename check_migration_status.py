#!/usr/bin/env python3
"""
Script simple para verificar el estado actual de la migración.
Verifica qué datos existen en ambos sistemas (legacy y nuevo).
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

def check_migration_status():
    """Verifica el estado actual de la migración."""
    
    print("="*80)
    print("VERIFICACIÓN DEL ESTADO DE MIGRACIÓN")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar modelos legacy
    print("🔍 VERIFICANDO DATOS LEGACY...")
    try:
        from skyguard.gps.tracker.models import (
            SGAvl, GeoFence, SimCard, SGHarness, 
            AccelLog, AlarmLog, Overlays, Stats
        )
        
        legacy_counts = {
            'Dispositivos GPS (SGAvl)': SGAvl.objects.count(),
            'Geocercas': GeoFence.objects.count(),
            'Tarjetas SIM': SimCard.objects.count(),
            'Configuraciones Harness': SGHarness.objects.count(),
            'Logs de Aceleración': AccelLog.objects.count(),
            'Logs de Alarmas': AlarmLog.objects.count(),
            'Overlays': Overlays.objects.count(),
            'Estadísticas': Stats.objects.count(),
        }
        
        print("DATOS LEGACY ENCONTRADOS:")
        for item, count in legacy_counts.items():
            status = "✅" if count > 0 else "⚪"
            print(f"  {status} {item}: {count:,}")
        
    except Exception as e:
        print(f"❌ Error accediendo a datos legacy: {e}")
        legacy_counts = {}
    
    print()
    
    # Verificar modelos nuevos
    print("🔍 VERIFICANDO DATOS NUEVOS...")
    try:
        from skyguard.apps.gps.models import (
            GPSDevice, GeoFence as NewGeoFence, SimCard as NewSimCard, 
            DeviceHarness, AccelerationLog, GPSEvent, Overlay, DeviceStats
        )
        
        new_counts = {
            'Dispositivos GPS': GPSDevice.objects.count(),
            'Geocercas': NewGeoFence.objects.count(),
            'Tarjetas SIM': NewSimCard.objects.count(),
            'Configuraciones Harness': DeviceHarness.objects.count(),
            'Logs de Aceleración': AccelerationLog.objects.count(),
            'Eventos GPS': GPSEvent.objects.count(),
            'Overlays': Overlay.objects.count(),
            'Estadísticas de Dispositivos': DeviceStats.objects.count(),
        }
        
        print("DATOS NUEVOS ENCONTRADOS:")
        for item, count in new_counts.items():
            status = "✅" if count > 0 else "⚪"
            print(f"  {status} {item}: {count:,}")
        
    except Exception as e:
        print(f"❌ Error accediendo a datos nuevos: {e}")
        new_counts = {}
    
    print()
    
    # Análisis de migración
    print("📊 ANÁLISIS DE MIGRACIÓN:")
    print("-" * 50)
    
    if legacy_counts and new_counts:
        # Comparar dispositivos GPS
        legacy_devices = legacy_counts.get('Dispositivos GPS (SGAvl)', 0)
        new_devices = new_counts.get('Dispositivos GPS', 0)
        
        if legacy_devices > 0:
            coverage = (new_devices / legacy_devices) * 100
            print(f"Dispositivos GPS: {new_devices}/{legacy_devices} ({coverage:.1f}% migrados)")
            
            if coverage == 100:
                print("  ✅ Migración de dispositivos COMPLETA")
            elif coverage > 0:
                print(f"  ⚠️  Migración de dispositivos PARCIAL ({legacy_devices - new_devices} faltantes)")
            else:
                print("  ❌ Migración de dispositivos NO INICIADA")
        else:
            print("  ⚪ No hay dispositivos legacy para migrar")
        
        # Verificar otros elementos
        migration_items = [
            ('Geocercas', 'Geocercas'),
            ('Tarjetas SIM', 'Tarjetas SIM'),
            ('Configuraciones Harness', 'Configuraciones Harness'),
            ('Overlays', 'Overlays'),
        ]
        
        for legacy_key, new_key in migration_items:
            legacy_count = legacy_counts.get(legacy_key, 0)
            new_count = new_counts.get(new_key, 0)
            
            if legacy_count > 0:
                coverage = (new_count / legacy_count) * 100
                if coverage == 100:
                    print(f"  ✅ {new_key}: {new_count}/{legacy_count} (100% migrados)")
                elif coverage > 0:
                    print(f"  ⚠️  {new_key}: {new_count}/{legacy_count} ({coverage:.1f}% migrados)")
                else:
                    print(f"  ❌ {new_key}: 0/{legacy_count} (no migrados)")
            elif new_count > 0:
                print(f"  ℹ️  {new_key}: {new_count} (datos nuevos)")
            else:
                print(f"  ⚪ {new_key}: sin datos")
    
    print()
    
    # Estado general
    print("🎯 ESTADO GENERAL DE LA MIGRACIÓN:")
    print("-" * 50)
    
    if not legacy_counts:
        print("❌ No se pueden leer datos legacy - verificar configuración")
        return False
    
    if not new_counts:
        print("❌ No se pueden leer datos nuevos - verificar configuración")
        return False
    
    # Determinar si hay datos para migrar
    total_legacy = sum(legacy_counts.values())
    total_new = sum(new_counts.values())
    
    if total_legacy == 0:
        print("ℹ️  No hay datos legacy para migrar - sistema limpio")
        return True
    
    if total_new == 0:
        print("❌ MIGRACIÓN NO INICIADA - no hay datos en el nuevo sistema")
        return False
    
    # Calcular progreso general
    key_items = ['Dispositivos GPS (SGAvl)', 'Configuraciones Harness']
    migrated_key_items = 0
    total_key_items = 0
    
    for item in key_items:
        if item in legacy_counts:
            total_key_items += legacy_counts[item]
            # Buscar equivalente en datos nuevos
            if item == 'Dispositivos GPS (SGAvl)':
                migrated_key_items += new_counts.get('Dispositivos GPS', 0)
            elif item == 'Configuraciones Harness':
                migrated_key_items += new_counts.get('Configuraciones Harness', 0)
    
    if total_key_items > 0:
        progress = (migrated_key_items / total_key_items) * 100
        
        if progress == 100:
            print("✅ MIGRACIÓN PRINCIPAL COMPLETADA")
            print("   - Todos los elementos críticos han sido migrados")
            print("   - Se recomienda validar la integridad de los datos")
        elif progress >= 50:
            print("⚠️  MIGRACIÓN PARCIALMENTE COMPLETADA")
            print(f"   - Progreso: {progress:.1f}%")
            print("   - Algunos elementos críticos faltan por migrar")
        else:
            print("❌ MIGRACIÓN INCOMPLETA")
            print(f"   - Progreso: {progress:.1f}%")
            print("   - La mayoría de elementos críticos no han sido migrados")
    
    print()
    print("📋 PRÓXIMOS PASOS RECOMENDADOS:")
    print("-" * 50)
    
    if total_new == 0:
        print("1. Ejecutar migración completa:")
        print("   python3 migration_scripts/run_migration.py --execute")
    else:
        print("1. Completar migración faltante:")
        print("   python3 migration_scripts/run_migration.py --execute")
        print("2. Validar integridad de datos:")
        print("   python3 migration_scripts/validate_migration.py")
        print("3. Probar funcionalidad del nuevo sistema")
    
    return True

if __name__ == "__main__":
    try:
        check_migration_status()
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        sys.exit(1) 