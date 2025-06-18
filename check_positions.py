#!/usr/bin/env python

import os
import sys
import django
from datetime import datetime

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
sys.path.insert(0, '/mnt/c/Users/oswaldo/Desktop/django13')
django.setup()

from skyguard.apps.gps.models.device import GPSDevice
from skyguard.gps.tracker.models import SGAvl
from django.utils import timezone

def check_positions():
    """Verificar posiciones GPS en la base de datos"""
    imei = 123456789012345
    
    print("🛰️  VERIFICACIÓN DE POSICIONES GPS")
    print("="*60)
    
    try:
        # Verificar GPSDevice
        print("\n📱 DISPOSITIVO GPS (GPSDevice):")
        try:
            device = GPSDevice.objects.get(imei=imei)
            print(f"   ✅ Encontrado: {device.name}")
            print(f"   📍 Posición: {device.position}")
            print(f"   🚗 Velocidad: {device.speed} km/h")
            print(f"   📡 Estado: {device.connection_status}")
            print(f"   💓 Último heartbeat: {device.last_heartbeat}")
            print(f"   🔗 IP:Puerto: {device.current_ip}:{device.current_port}")
            print(f"   📊 Total conexiones: {device.total_connections}")
            
            if device.position:
                print(f"   🗺️  Google Maps: https://maps.google.com/?q={device.position.y},{device.position.x}")
            
        except GPSDevice.DoesNotExist:
            print("   ❌ No encontrado")
        
        # Verificar SGAvl (modelo legacy)
        print("\n📡 DISPOSITIVO LEGACY (SGAvl):")
        try:
            avl = SGAvl.objects.get(imei=imei)
            print(f"   ✅ Encontrado: {avl.name}")
            print(f"   📍 Posición: {avl.position}")
            print(f"   🚗 Velocidad: {avl.speed} km/h")
            print(f"   📅 Última fecha: {avl.date}")
            print(f"   📝 Último log: {avl.lastLog}")
            print(f"   🔌 Inputs: {avl.inputs}")
            print(f"   🔧 Outputs: {avl.outputs}")
            
            if avl.position:
                print(f"   🗺️  Google Maps: https://maps.google.com/?q={avl.position.y},{avl.position.x}")
                
        except SGAvl.DoesNotExist:
            print("   ❌ No encontrado")
            
        # Verificar sesiones UDP
        print("\n🔗 SESIONES UDP:")
        from skyguard.apps.gps.models.protocols import UDPSession
        sessions = UDPSession.objects.filter(device__imei=imei)
        if sessions.exists():
            for session in sessions:
                print(f"   📡 Sesión {session.session}: {session.host}:{session.port}")
                print(f"      ⏰ Expira: {session.expires}")
                print(f"      🔗 Dispositivo: {session.device.name}")
        else:
            print("   ❌ No hay sesiones activas")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_positions() 