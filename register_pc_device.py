#!/usr/bin/env python3
"""
Script simple para registrar el PC como dispositivo GPS
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
django.setup()

from skyguard.apps.gps.models.device import GPSDevice
from django.contrib.auth.models import User

def main():
    print("🔧 Registrando PC como dispositivo GPS...")
    
    try:
        # Crear usuario admin si no existe
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@skyguard.com', 
                'is_staff': True, 
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            print("✅ Usuario admin creado")
        
        # Crear dispositivo PC
        device, created = GPSDevice.objects.get_or_create(
            imei='123456789012345',
            defaults={
                'name': 'PC-DESKTOP-5V9VDBR',
                'owner': user,
                'protocol': 'wialon',
                'connection_status': 'OFFLINE',
                'is_active': True,
                'route': 99,
                'economico': 9999,
                'model': 99,
                'software_version': '1.0',
                'current_ip': '127.0.1.1',
                'current_port': 20332
            }
        )
        
        if created:
            print(f"✅ Dispositivo PC creado: {device.name}")
            print(f"   IMEI: {device.imei}")
            print(f"   Propietario: {device.owner.username}")
        else:
            print(f"ℹ️ Dispositivo PC ya existe: {device.name}")
            print(f"   IMEI: {device.imei}")
        
        print("\n🎯 ¡Listo! Tu PC está registrado como dispositivo GPS")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 