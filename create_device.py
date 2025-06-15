#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
django.setup()

# Importar el modelo después de configurar Django
from skyguard.apps.gps.models.device import GPSDevice

# Crear el dispositivo
device, created = GPSDevice.objects.get_or_create(
    imei='123456789012345',
    defaults={
        'name': 'Test Device',
        'serial': 123456,
        'model': 1,  # SGB4612
        'software_version': '1.0',
        'route': 92,  # Ruta 4
        'economico': 123,
        'connection_status': 'ONLINE',
        'current_ip': '127.0.0.1',
        'current_port': 8000
    }
)

# Mostrar el resultado
if created:
    print(f"✅ Dispositivo creado exitosamente:")
else:
    print(f"ℹ️ El dispositivo ya existe:")
    
print(f"  - Nombre: {device.name}")
print(f"  - IMEI: {device.imei}")
print(f"  - Serial: {device.serial}")
print(f"  - Modelo: {device.get_model_display()}")  # Muestra el nombre del modelo
print(f"  - Estado: {device.connection_status}")
print(f"  - Ruta: {device.get_route_display()}")  # Muestra el nombre de la ruta
print(f"  - Económico: {device.economico}") 