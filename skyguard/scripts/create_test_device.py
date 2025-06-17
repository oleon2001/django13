#!/usr/bin/env python
import os
import django
import sys

# Configurar el entorno de Django
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
django.setup()

# Importar después de configurar Django
from django.contrib.contenttypes.models import ContentType
from skyguard.apps.gps.models.device import GPSDevice

def create_test_device():
    """Create a test GPS device."""
    print("Iniciando creación de dispositivo de prueba...")
    try:
        # Verificar si el dispositivo ya existe
        device, created = GPSDevice.objects.get_or_create(
            imei='123456789012345',
            defaults={
                'name': 'Test Device',
                'serial': '12356',
                'model': '60',
                'software_version': '1.0',
                'route': '1',
                'economico': '1234567890',
                'connection_status': 'connected',
                'current_ip': '127.0.0.1',
                'current_port': 8000
            }
        )
        
        if created:
            print(f"✅ Dispositivo creado exitosamente:")
        else:
            print(f"ℹ️ El dispositivo ya existe:")
            
        print(f"  - Nombre: {device.name}")
        print(f"  - IMEI: {device.imei}")
        print(f"  - Modelo: {device.model}")
        print(f"  - Estado: {device.connection_status}")
        print(f"  - ID: {device.id}")
        
    except Exception as e:
        print(f"❌ Error al crear el dispositivo: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    create_test_device()
    print("\nScript completado.") 