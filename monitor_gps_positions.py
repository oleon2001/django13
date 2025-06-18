#!/usr/bin/env python

import os
import sys
import django
import time
from datetime import datetime

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
sys.path.insert(0, '/mnt/c/Users/oswaldo/Desktop/django13')
django.setup()

from skyguard.apps.gps.models.device import GPSDevice
from django.utils import timezone

def monitor_positions():
    """Monitorear posiciones GPS en tiempo real"""
    imei = 123456789012345
    
    print("🛰️  MONITOR DE POSICIONES GPS")
    print("="*50)
    print(f"Dispositivo IMEI: {imei}")
    print("Presiona Ctrl+C para detener")
    print("="*50)
    
    last_position = None
    last_heartbeat = None
    last_speed = None
    
    try:
        while True:
            try:
                device = GPSDevice.objects.get(imei=imei)
                now = timezone.now()
                
                # Verificar cambios en heartbeat
                if device.last_heartbeat != last_heartbeat:
                    time_str = datetime.now().strftime('%H:%M:%S')
                    print(f"\n🔄 [{time_str}] HEARTBEAT ACTUALIZADO")
                    print(f"   Anterior: {last_heartbeat}")
                    print(f"   Nuevo: {device.last_heartbeat}")
                    
                    if device.last_heartbeat:
                        time_since = (now - device.last_heartbeat).total_seconds()
                        status = "🟢 ONLINE" if time_since < 120 else "🔴 OFFLINE"
                        print(f"   Estado: {status} (hace {time_since:.0f}s)")
                    
                    last_heartbeat = device.last_heartbeat
                
                # Verificar cambios en posición
                if device.position != last_position:
                    time_str = datetime.now().strftime('%H:%M:%S')
                    print(f"\n📍 [{time_str}] POSICIÓN ACTUALIZADA")
                    
                    if last_position:
                        print(f"   Anterior: {last_position.y:.6f}, {last_position.x:.6f}")
                    
                    if device.position:
                        print(f"   Nueva: {device.position.y:.6f}, {device.position.x:.6f}")
                        print(f"   Google Maps: https://maps.google.com/?q={device.position.y},{device.position.x}")
                    else:
                        print(f"   Nueva: Sin posición")
                    
                    last_position = device.position
                
                # Verificar cambios en velocidad
                if device.speed != last_speed:
                    time_str = datetime.now().strftime('%H:%M:%S')
                    print(f"\n🚗 [{time_str}] VELOCIDAD ACTUALIZADA")
                    print(f"   Anterior: {last_speed} km/h")
                    print(f"   Nueva: {device.speed} km/h")
                    last_speed = device.speed
                
                # Mostrar estado actual cada 10 segundos
                if int(time.time()) % 10 == 0:
                    time_str = datetime.now().strftime('%H:%M:%S')
                    status = "🟢 ONLINE" if device.last_heartbeat and (now - device.last_heartbeat).total_seconds() < 120 else "🔴 OFFLINE"
                    
                    print(f"\n📊 [{time_str}] ESTADO ACTUAL")
                    print(f"   Estado: {status}")
                    print(f"   IP:Puerto: {device.current_ip}:{device.current_port}")
                    if device.position:
                        print(f"   Posición: {device.position.y:.6f}, {device.position.x:.6f}")
                        print(f"   Velocidad: {device.speed} km/h")
                    else:
                        print(f"   Sin posición GPS")
                    
                    time.sleep(1)  # Evitar mostrar múltiples veces en el mismo segundo
                
            except GPSDevice.DoesNotExist:
                print("❌ Dispositivo no encontrado")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(2)
            
            time.sleep(1)  # Verificar cada segundo
            
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido")

if __name__ == "__main__":
    monitor_positions() 