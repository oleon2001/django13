#!/usr/bin/env python3
"""
Script de prueba para verificar que tu celular está registrado correctamente
IMEI: 352749380148144
"""
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

def test_my_device():
    """Verificar que tu dispositivo esté registrado correctamente."""
    print("🔍 Verificando tu dispositivo GPS...")
    print("="*50)
    
    # Buscar tu dispositivo
    imei = '352749380148144'
    
    try:
        device = GPSDevice.objects.get(imei=imei)
        print("✅ ¡DISPOSITIVO ENCONTRADO!")
        print(f"""
📱 INFORMACIÓN DEL DISPOSITIVO:
   • IMEI: {device.imei}
   • Nombre: {device.name}
   • Propietario: {device.owner.username if device.owner else 'Sin propietario'}
   • Protocolo: {device.protocol}
   • Estado: {device.connection_status}
   • Activo: {'✅ Sí' if device.is_active else '❌ No'}
   • Última conexión: {device.last_connection or 'Nunca'}
   • IP actual: {device.current_ip or 'N/A'}
   • Puerto actual: {device.current_port or 'N/A'}
   • Calidad de conexión: {device.connection_quality}%
   • Creado: {device.created_at}
   • Actualizado: {device.updated_at}
        """)
        
        # Verificar configuración
        print("🔧 VERIFICACIÓN DE CONFIGURACIÓN:")
        
        # Protocolo
        if device.protocol == 'wialon':
            print("   ✅ Protocolo Wialon configurado (puerto 20332)")
        else:
            print(f"   ⚠️ Protocolo actual: {device.protocol}")
            print("   💡 Se recomienda usar 'wialon' para conectar celulares")
        
        # Estado activo
        if device.is_active:
            print("   ✅ Dispositivo activo")
        else:
            print("   ❌ Dispositivo INACTIVO - debe activarse")
            
        # Propietario
        if device.owner:
            print(f"   ✅ Propietario: {device.owner.username}")
        else:
            print("   ⚠️ Sin propietario asignado")
            
        print("\n🚀 PRÓXIMOS PASOS:")
        print("   1. Ejecutar: python3 start_my_gps.py")
        print("   2. Usar aplicación web: http://localhost/mobile_gps_app/")
        print("   3. Configurar en tu celular:")
        print("      • Host: [IP_DEL_SERVIDOR]")
        print("      • Puerto: 20332")
        print(f"      • IMEI: {imei}")
        print("      • Protocolo: Wialon")
        
    except GPSDevice.DoesNotExist:
        print("❌ DISPOSITIVO NO ENCONTRADO")
        print(f"   El IMEI {imei} no está registrado en el sistema")
        print("\n💡 SOLUCIÓN:")
        print("   Ejecuta: python3 create_my_device.py")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        
    print("\n" + "="*50)

def test_users():
    """Verificar usuarios del sistema."""
    print("\n👥 USUARIOS DEL SISTEMA:")
    users = User.objects.all()
    if users:
        for user in users:
            print(f"   • {user.username} ({'Admin' if user.is_staff else 'Usuario'})")
    else:
        print("   ❌ No hay usuarios en el sistema")
        print("   💡 Considera crear un superusuario: python3 manage.py createsuperuser")

def test_device_count():
    """Contar dispositivos en el sistema."""
    print("\n📊 ESTADÍSTICAS DE DISPOSITIVOS:")
    total = GPSDevice.objects.count()
    online = GPSDevice.objects.filter(connection_status='ONLINE').count()
    offline = GPSDevice.objects.filter(connection_status='OFFLINE').count()
    active = GPSDevice.objects.filter(is_active=True).count()
    
    print(f"   • Total: {total}")
    print(f"   • Online: {online}")
    print(f"   • Offline: {offline}")
    print(f"   • Activos: {active}")

if __name__ == '__main__':
    test_my_device()
    test_users()
    test_device_count()
    print("\n✅ Verificación completada.") 