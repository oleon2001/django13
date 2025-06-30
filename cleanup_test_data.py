#!/usr/bin/env python3
"""
Script para limpiar datos de prueba del sistema GPS.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent

def cleanup_test_data():
    """Limpia datos de prueba del sistema."""
    print("🧹 Limpiando datos de prueba...")
    
    try:
        # Eliminar dispositivos de prueba
        test_devices = GPSDevice.objects.filter(
            name__startswith='Device_') | GPSDevice.objects.filter(
            name__startswith='test_') | GPSDevice.objects.filter(
            imei__in=[123456789012345, 123456789012346, 999999999999999]
        )
        
        device_count = test_devices.count()
        if device_count > 0:
            # Eliminar ubicaciones relacionadas
            for device in test_devices:
                GPSLocation.objects.filter(device=device).delete()
                GPSEvent.objects.filter(device=device).delete()
            
            # Eliminar dispositivos
            test_devices.delete()
            print(f"✅ Eliminados {device_count} dispositivos de prueba")
        else:
            print("✅ No se encontraron dispositivos de prueba para eliminar")
        
        # Limpiar ubicaciones huérfanas
        orphan_locations = GPSLocation.objects.filter(device__isnull=True)
        orphan_count = orphan_locations.count()
        if orphan_count > 0:
            orphan_locations.delete()
            print(f"✅ Eliminadas {orphan_count} ubicaciones huérfanas")
        
        # Limpiar eventos huérfanos
        orphan_events = GPSEvent.objects.filter(device__isnull=True)
        event_count = orphan_events.count()
        if event_count > 0:
            orphan_events.delete()
            print(f"✅ Eliminados {event_count} eventos huérfanos")
        
        print("✅ Limpieza completada")
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return False
    
    return True

def show_current_status():
    """Muestra el estado actual del sistema."""
    print("\n📊 Estado actual del sistema:")
    print("-" * 30)
    
    try:
        device_count = GPSDevice.objects.count()
        location_count = GPSLocation.objects.count()
        event_count = GPSEvent.objects.count()
        online_count = GPSDevice.objects.filter(connection_status='ONLINE').count()
        
        print(f"Dispositivos totales: {device_count}")
        print(f"Dispositivos online: {online_count}")
        print(f"Ubicaciones totales: {location_count}")
        print(f"Eventos totales: {event_count}")
        
        # Mostrar últimos dispositivos
        recent_devices = GPSDevice.objects.order_by('-id')[:5]
        if recent_devices:
            print("\nÚltimos dispositivos:")
            for device in recent_devices:
                print(f"  - {device.name} (IMEI: {device.imei}, Protocolo: {device.protocol})")
        
    except Exception as e:
        print(f"❌ Error obteniendo estado: {e}")

def main():
    """Función principal."""
    print("🚀 LIMPIEZA DE DATOS DE PRUEBA")
    print("=" * 40)
    
    # Confirmar limpieza
    response = input("¿Estás seguro de que quieres limpiar los datos de prueba? (s/N): ")
    if response.lower() != 's':
        print("Limpieza cancelada.")
        return
    
    # Ejecutar limpieza
    if cleanup_test_data():
        show_current_status()
        print("\n✅ Sistema listo para nuevas pruebas")
    else:
        print("\n❌ Error durante la limpieza")

if __name__ == '__main__':
    main() 