#!/usr/bin/env python
import os
import django
import sys

# Configurar el entorno de Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
django.setup()

# Importar después de configurar Django
from skyguard.apps.gps.models.device import GPSDevice
from django.contrib.auth.models import User

def create_my_device():
    """Crear mi dispositivo GPS personal."""
    print("🔧 Registrando tu celular como dispositivo GPS...")
    
    try:
        # Buscar o crear usuario por defecto
        user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@skyguard.com', 'is_staff': True}
        )
        
        # Crear tu dispositivo con el IMEI real
        device, created = GPSDevice.objects.get_or_create(
            imei='352749380148144',  # TU IMEI REAL
            defaults={
                'name': 'Mi Celular GPS',
                'owner': user,
                'protocol': 'wialon',  # Protocolo recomendado
                'connection_status': 'OFFLINE',
                'is_active': True,
                'route': 92,  # Ruta ejemplo
                'economico': 1001,  # Número económico
                'model': 1,  # Modelo móvil
                'software_version': '1.0',
            }
        )
        
        if created:
            print(f"✅ ¡Tu dispositivo fue registrado exitosamente!")
        else:
            print(f"ℹ️ Tu dispositivo ya estaba registrado")
            
        print(f"""
📱 DETALLES DE TU DISPOSITIVO:
   • Nombre: {device.name}
   • IMEI: {device.imei} (Clave primaria)
   • Protocolo: {device.protocol}
   • Estado: {device.connection_status}
   • Activo: {'Sí' if device.is_active else 'No'}
   • Última actualización: {device.last_log or 'Nunca'}
   
🎯 Tu celular está listo para conectarse al servidor GPS!
        """)
        
    except Exception as e:
        print(f"❌ Error al registrar el dispositivo: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    create_my_device()
    print("🚀 ¡Listo! Ahora puedes conectar tu celular.") 