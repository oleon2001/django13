#!/usr/bin/env python3
"""
Verificar el estado del dispositivo PC en la base de datos
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from skyguard.apps.gps.models import GPSDevice
from django.utils import timezone
from datetime import timedelta

def check_device():
    """Verificar dispositivo PC"""
    print("=" * 60)
    print("🔍 VERIFICANDO DISPOSITIVO PC EN BASE DE DATOS")
    print("=" * 60)
    
    imei = "123456789012345"
    
    try:
        # Buscar dispositivo
        device = GPSDevice.objects.get(imei=imei)
        
        print(f"✅ Dispositivo encontrado:")
        print(f"   • Nombre: {device.name}")
        print(f"   • IMEI: {device.imei}")
        print(f"   • Protocolo: {device.protocol}")
        print(f"   • Estado: {device.status}")
        
        # Verificar posición
        if hasattr(device, 'position') and device.position:
            print(f"   • Posición: {device.position.coords}")
        else:
            print("   • Posición: No disponible")
        
        # Verificar última actualización
        if hasattr(device, 'last_log') and device.last_log:
            time_diff = timezone.now() - device.last_log
            if time_diff < timedelta(minutes=5):
                print(f"   • Última actualización: {device.last_log} (✅ Activo)")
            else:
                print(f"   • Última actualización: {device.last_log} (⚠️ Inactivo)")
        else:
            print("   • Última actualización: No disponible")
            
        # Verificar eventos recientes
        if hasattr(device, 'events'):
            recent_events = device.events.filter(
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).count()
            print(f"   • Eventos últimos 5 min: {recent_events}")
        
    except GPSDevice.DoesNotExist:
        print(f"❌ Dispositivo con IMEI {imei} NO encontrado")
        print("\n📝 Dispositivos disponibles:")
        
        # Listar todos los dispositivos
        devices = GPSDevice.objects.all()
        if devices:
            for dev in devices:
                print(f"   • {dev.name} (IMEI: {dev.imei})")
        else:
            print("   • No hay dispositivos registrados")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_device() 