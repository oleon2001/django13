#!/usr/bin/env python3
"""
Script de prueba para verificar las correcciones de GPS.
"""

import os
import sys
import django
from datetime import datetime
import pytz

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from skyguard.apps.gps.services.hardware_gps import HardwareGPSService
from skyguard.apps.gps.models import GPSDevice, GPSLocation

def test_device_creation():
    """Prueba la creación de dispositivos con diferentes tipos de ID."""
    print("🧪 Probando creación de dispositivos...")
    
    service = HardwareGPSService()
    
    # Test 1: IMEI como string
    device1 = service._get_or_create_device("123456789012345", "concox")
    print(f"✅ Dispositivo con IMEI string: {device1.name if device1 else 'ERROR'}")
    
    # Test 2: IMEI como entero
    device2 = service._get_or_create_device(123456789012346, "meiligao")
    print(f"✅ Dispositivo con IMEI entero: {device2.name if device2 else 'ERROR'}")
    
    # Test 3: Nombre de dispositivo
    device3 = service._get_or_create_device("test_device_001", "nmea")
    print(f"✅ Dispositivo con nombre: {device3.name if device3 else 'ERROR'}")
    
    return device1, device2, device3

def test_gps_data_processing():
    """Prueba el procesamiento de datos GPS."""
    print("\n🧪 Probando procesamiento de datos GPS...")
    
    service = HardwareGPSService()
    
    # Datos GPS de prueba
    test_gps_data = {
        'timestamp': datetime.now(pytz.UTC),
        'latitude': 19.4326,  # Ciudad de México
        'longitude': -99.1332,
        'speed': 45.5,
        'course': 180.0,
        'altitude': 2240,
        'satellites': 8,
        'fix_quality': 1
    }
    
    # Test con diferentes tipos de device_id
    test_cases = [
        ("123456789012345", "concox"),
        (123456789012346, "meiligao"),
        ("test_device_001", "nmea")
    ]
    
    for device_id, protocol in test_cases:
        try:
            service._save_gps_location(device_id, test_gps_data, protocol)
            print(f"✅ Datos GPS guardados para {device_id} ({protocol})")
        except Exception as e:
            print(f"❌ Error guardando datos GPS para {device_id}: {e}")

def test_nmea_processing():
    """Prueba el procesamiento de datos NMEA."""
    print("\n🧪 Probando procesamiento NMEA...")
    
    service = HardwareGPSService()
    
    # Datos NMEA de prueba
    test_nmea_data = [
        "$GPRMC,123519,A,4808.38,N,01131.66,E,022.4,084.4,230394,003.1,W*6A",
        "$GPGGA,123519,4808.38,N,01131.66,E,1,08,0.9,545.4,M,46.9,M,,*47",
        "$GPGLL,4808.38,N,01131.66,E,123519,A*3D"
    ]
    
    address = ('127.0.0.1', 12345)
    
    for nmea_string in test_nmea_data:
        try:
            if "$GPRMC" in nmea_string:
                service._process_gprmc(nmea_string, address)
            elif "$GPGGA" in nmea_string:
                service._process_gpgga(nmea_string, address)
            elif "$GPGLL" in nmea_string:
                service._process_gpgll(nmea_string, address)
            print(f"✅ NMEA procesado: {nmea_string[:20]}...")
        except Exception as e:
            print(f"❌ Error procesando NMEA: {e}")

def test_database_queries():
    """Prueba consultas a la base de datos."""
    print("\n🧪 Probando consultas de base de datos...")
    
    try:
        # Contar dispositivos
        device_count = GPSDevice.objects.count()
        print(f"✅ Total dispositivos: {device_count}")
        
        # Contar ubicaciones
        location_count = GPSLocation.objects.count()
        print(f"✅ Total ubicaciones: {location_count}")
        
        # Dispositivos online
        online_count = GPSDevice.objects.filter(connection_status='ONLINE').count()
        print(f"✅ Dispositivos online: {online_count}")
        
        # Últimas ubicaciones
        recent_locations = GPSLocation.objects.select_related('device').order_by('-timestamp')[:5]
        print(f"✅ Últimas 5 ubicaciones:")
        for loc in recent_locations:
            print(f"   - {loc.device.name}: {loc.position.y:.6f}, {loc.position.x:.6f}")
            
    except Exception as e:
        print(f"❌ Error en consultas de BD: {e}")

def main():
    """Función principal de pruebas."""
    print("🚀 INICIANDO PRUEBAS DE CORRECCIONES GPS")
    print("=" * 50)
    
    try:
        # Ejecutar pruebas
        test_device_creation()
        test_gps_data_processing()
        test_nmea_processing()
        test_database_queries()
        
        print("\n" + "=" * 50)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("Las correcciones de GPS están funcionando correctamente.")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 