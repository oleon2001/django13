#!/usr/bin/env python3
"""
Script para cambiar el protocolo de tu dispositivo GPS
IMEI: 352749380148144
De: concox → A: wialon
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

def cambiar_protocolo():
    """Cambiar protocolo del dispositivo de concox a wialon."""
    print("🔄 Cambiando protocolo de tu dispositivo GPS...")
    print("="*60)
    
    imei = '352749380148144'
    
    try:
        # Buscar el dispositivo
        device = GPSDevice.objects.get(imei=imei)
        
        print(f"📱 DISPOSITIVO ENCONTRADO:")
        print(f"   • IMEI: {device.imei}")
        print(f"   • Nombre: {device.name}")
        print(f"   • Protocolo actual: {device.protocol}")
        
        # Verificar si ya es wialon
        if device.protocol == 'wialon':
            print("✅ El dispositivo ya está configurado con protocolo Wialon")
            print("   No es necesario hacer cambios")
            return
        
        # Cambiar protocolo
        old_protocol = device.protocol
        device.protocol = 'wialon'
        device.save()
        
        print(f"\n🔄 CAMBIO REALIZADO:")
        print(f"   • Protocolo anterior: {old_protocol}")
        print(f"   • Protocolo nuevo: {device.protocol}")
        
        print(f"\n📋 INFORMACIÓN ACTUALIZADA:")
        print(f"   • IMEI: {device.imei}")
        print(f"   • Nombre: {device.name}")
        print(f"   • Protocolo: {device.protocol} ✅")
        print(f"   • Puerto para conectar: 20332")
        print(f"   • Estado: {device.connection_status}")
        
        print(f"\n🎯 CONFIGURACIÓN PARA TU CELULAR:")
        print(f"   • Host/IP: [IP_DEL_SERVIDOR]")
        print(f"   • Puerto: 20332 (Wialon)")
        print(f"   • IMEI: {imei}")
        print(f"   • Protocolo: Wialon")
        print(f"   • Contraseña: 123456")
        
        print(f"\n🚀 PRÓXIMOS PASOS:")
        print(f"   1. Ejecutar: python3 start_my_gps.py")
        print(f"   2. En tu celular, usar puerto 20332 (no 55300)")
        print(f"   3. Protocolo: Wialon (no Concox)")
        
        print("\n✅ ¡Protocolo cambiado exitosamente!")
        
    except GPSDevice.DoesNotExist:
        print("❌ DISPOSITIVO NO ENCONTRADO")
        print(f"   El IMEI {imei} no está registrado en el sistema")
        print("\n💡 SOLUCIÓN:")
        print("   Ejecuta: python3 create_my_device.py")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        
    print("\n" + "="*60)

def mostrar_diferencias_protocolos():
    """Mostrar las diferencias entre protocolos."""
    print("\n📊 DIFERENCIAS ENTRE PROTOCOLOS:")
    print("""
┌─────────────┬─────────┬───────────────────────────────────┐
│ Protocolo   │ Puerto  │ Descripción                       │
├─────────────┼─────────┼───────────────────────────────────┤
│ concox      │ 55300   │ Para dispositivos Concox físicos  │
│ wialon      │ 20332   │ Simple, ideal para celulares ✅   │
│ meiligao    │ 62000   │ Para dispositivos Meiligao        │
│ satellite   │ 15557   │ Comunicación satelital            │
└─────────────┴─────────┴───────────────────────────────────┘

🎯 PARA CELULARES SE RECOMIENDA:
   • Protocolo: wialon
   • Puerto: 20332
   • Razón: Más simple y compatible con apps móviles
    """)

if __name__ == '__main__':
    cambiar_protocolo()
    mostrar_diferencias_protocolos()
    print("\n🔧 Cambio completado. Ahora puedes conectar tu celular.") 