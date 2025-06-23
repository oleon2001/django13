#!/usr/bin/env python3
"""
Script para analizar datos existentes antes de la migración.
Ejecutar desde el directorio raíz del proyecto Django.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from collections import defaultdict

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from skyguard.gps.tracker.models import (
    SGAvl, GeoFence, SimCard, SGHarness, ServerSMS,
    AccelLog, Overlays, Stats, PsiCal, AlarmLog
)
from django.contrib.auth.models import User


def analyze_legacy_data():
    """Analiza los datos del sistema legacy."""
    
    print("=" * 60)
    print("ANÁLISIS DE DATOS LEGACY")
    print("=" * 60)
    
    # Análisis de dispositivos GPS
    devices = SGAvl.objects.all()
    print(f"\n📱 DISPOSITIVOS GPS:")
    print(f"   Total: {devices.count()}")
    print(f"   Activos (últimos 7 días): {devices.filter(lastLog__gte=datetime.now()-timedelta(days=7)).count()}")
    print(f"   Por ruta:")
    
    route_stats = defaultdict(int)
    for device in devices:
        if device.ruta:
            route_stats[device.get_ruta_display()] += 1
        else:
            route_stats['Sin ruta'] += 1
    
    for route, count in sorted(route_stats.items()):
        print(f"     {route}: {count}")
    
    # Análisis de geocercas
    geofences = GeoFence.objects.all()
    print(f"\n🗺️  GEOCERCAS:")
    print(f"   Total: {geofences.count()}")
    print(f"   Por propietario:")
    
    owner_stats = defaultdict(int)
    for fence in geofences:
        owner_stats[fence.owner.username] += 1
    
    for owner, count in sorted(owner_stats.items()):
        print(f"     {owner}: {count}")
    
    # Análisis de SIM cards
    sim_cards = SimCard.objects.all()
    print(f"\n📞 TARJETAS SIM:")
    print(f"   Total: {sim_cards.count()}")
    print(f"   Asignadas a dispositivos: {sim_cards.filter(avl__isnull=False).count()}")
    
    # Análisis de configuraciones harness
    harnesses = SGHarness.objects.all()
    print(f"\n🔧 CONFIGURACIONES HARNESS:")
    print(f"   Total: {harnesses.count()}")
    print(f"   En uso: {harnesses.filter(sgavl__isnull=False).distinct().count()}")
    
    # Análisis de logs de aceleración
    accel_logs = AccelLog.objects.all()
    print(f"\n📊 LOGS DE ACELERACIÓN:")
    print(f"   Total: {accel_logs.count()}")
    recent_logs = accel_logs.filter(date__gte=datetime.now()-timedelta(days=30))
    print(f"   Últimos 30 días: {recent_logs.count()}")
    
    # Análisis de alarmas
    alarm_logs = AlarmLog.objects.all()
    print(f"\n🚨 LOGS DE ALARMAS:")
    print(f"   Total: {alarm_logs.count()}")
    recent_alarms = alarm_logs.filter(date__gte=datetime.now()-timedelta(days=30))
    print(f"   Últimos 30 días: {recent_alarms.count()}")
    
    # Análisis de overlays
    overlays = Overlays.objects.all()
    print(f"\n🗺️  OVERLAYS:")
    print(f"   Total: {overlays.count()}")
    
    # Análisis de estadísticas
    stats = Stats.objects.all()
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   Total: {stats.count()}")
    recent_stats = stats.filter(dateEnd__gte=datetime.now()-timedelta(days=30))
    print(f"   Últimos 30 días: {recent_stats.count()}")
    
    # Análisis de sensores PSI
    psi_cals = PsiCal.objects.all()
    print(f"\n⚖️  CALIBRACIONES PSI:")
    print(f"   Total: {psi_cals.count()}")
    
    # Análisis de usuarios
    users = User.objects.all()
    print(f"\n👥 USUARIOS:")
    print(f"   Total: {users.count()}")
    print(f"   Activos: {users.filter(is_active=True).count()}")
    print(f"   Staff: {users.filter(is_staff=True).count()}")
    print(f"   Superusuarios: {users.filter(is_superuser=True).count()}")
    
    return {
        'devices': devices.count(),
        'geofences': geofences.count(),
        'sim_cards': sim_cards.count(),
        'harnesses': harnesses.count(),
        'accel_logs': accel_logs.count(),
        'alarm_logs': alarm_logs.count(),
        'overlays': overlays.count(),
        'stats': stats.count(),
        'psi_cals': psi_cals.count(),
        'users': users.count()
    }


def check_data_integrity():
    """Verifica la integridad de los datos."""
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE INTEGRIDAD")
    print("=" * 60)
    
    issues = []
    
    # Verificar dispositivos sin harness
    devices_without_harness = SGAvl.objects.filter(harness__isnull=True)
    if devices_without_harness.exists():
        issues.append(f"⚠️  {devices_without_harness.count()} dispositivos sin configuración harness")
    
    # Verificar dispositivos sin propietario
    devices_without_owner = SGAvl.objects.filter(owner__isnull=True)
    if devices_without_owner.exists():
        issues.append(f"⚠️  {devices_without_owner.count()} dispositivos sin propietario")
    
    # Verificar geocercas sin propietario
    fences_without_owner = GeoFence.objects.filter(owner__isnull=True)
    if fences_without_owner.exists():
        issues.append(f"⚠️  {fences_without_owner.count()} geocercas sin propietario")
    
    # Verificar SIM cards duplicadas
    sim_phones = SimCard.objects.values_list('phone', flat=True)
    duplicate_phones = set([phone for phone in sim_phones if sim_phones.count(phone) > 1])
    if duplicate_phones:
        issues.append(f"⚠️  {len(duplicate_phones)} números de teléfono duplicados en SIM cards")
    
    # Verificar dispositivos con posición nula
    devices_no_position = SGAvl.objects.filter(position__isnull=True)
    if devices_no_position.exists():
        issues.append(f"⚠️  {devices_no_position.count()} dispositivos sin posición registrada")
    
    if issues:
        print("\n🔍 PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ No se encontraron problemas de integridad")
    
    return issues


def generate_migration_report():
    """Genera un reporte completo para la migración."""
    
    print("\n" + "=" * 60)
    print("GENERANDO REPORTE DE MIGRACIÓN")
    print("=" * 60)
    
    stats = analyze_legacy_data()
    issues = check_data_integrity()
    
    # Calcular estimaciones de tiempo
    total_records = sum(stats.values())
    estimated_time_hours = max(2, total_records / 10000)  # Estimación: 10k registros por hora
    
    print(f"\n📋 RESUMEN EJECUTIVO:")
    print(f"   Total de registros a migrar: {total_records:,}")
    print(f"   Tiempo estimado de migración: {estimated_time_hours:.1f} horas")
    print(f"   Problemas de integridad: {len(issues)}")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if total_records > 100000:
        print("   - Usar migración gradual por lotes")
        print("   - Implementar monitoreo de progreso")
    
    if len(issues) > 0:
        print("   - Resolver problemas de integridad antes de migrar")
        print("   - Crear scripts de limpieza de datos")
    
    if stats['devices'] > 100:
        print("   - Migrar dispositivos en grupos por ruta")
        print("   - Validar conectividad post-migración")
    
    print("\n✅ Análisis completado")
    
    return {
        'stats': stats,
        'issues': issues,
        'estimated_time_hours': estimated_time_hours,
        'total_records': total_records
    }


if __name__ == '__main__':
    try:
        report = generate_migration_report()
        
        # Guardar reporte en archivo
        with open('migration_analysis_report.txt', 'w') as f:
            f.write(f"REPORTE DE ANÁLISIS DE MIGRACIÓN\n")
            f.write(f"Generado: {datetime.now()}\n")
            f.write(f"Total registros: {report['total_records']:,}\n")
            f.write(f"Tiempo estimado: {report['estimated_time_hours']:.1f} horas\n")
            f.write(f"Problemas encontrados: {len(report['issues'])}\n")
            
            if report['issues']:
                f.write("\nProblemas:\n")
                for issue in report['issues']:
                    f.write(f"- {issue}\n")
        
        print(f"\n📄 Reporte guardado en: migration_analysis_report.txt")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        sys.exit(1) 