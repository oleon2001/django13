#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la conexión GPS
"""
import socket
import subprocess
import json
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
django.setup()

from skyguard.apps.gps.models.device import GPSDevice

def check_port_20332():
    """Verificar si el puerto 20332 está en uso."""
    print("🔍 Verificando puerto 20332...")
    try:
        # Intentar conectar al puerto
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 20332))
        sock.close()
        
        if result == 0:
            print("✅ Puerto 20332 está disponible y escuchando")
            return True
        else:
            print("❌ Puerto 20332 no está disponible")
            return False
    except Exception as e:
        print(f"❌ Error verificando puerto: {e}")
        return False

def check_device_in_db():
    """Verificar dispositivo en base de datos."""
    print("\n🔍 Verificando dispositivo en base de datos...")
    try:
        device = GPSDevice.objects.filter(imei='123456789012345').first()
        if device:
            print(f"✅ Dispositivo encontrado:")
            print(f"   • Nombre: {device.name}")
            print(f"   • IMEI: {device.imei}")
            print(f"   • Estado: {device.connection_status}")
            print(f"   • Activo: {device.is_active}")
            print(f"   • Protocolo: {device.protocol}")
            print(f"   • IP actual: {device.current_ip}")
            print(f"   • Puerto actual: {device.current_port}")
            return device
        else:
            print("❌ Dispositivo no encontrado en BD")
            return None
    except Exception as e:
        print(f"❌ Error verificando dispositivo: {e}")
        return None

def check_config_file():
    """Verificar archivo de configuración."""
    print("\n🔍 Verificando configuración...")
    try:
        with open('pc_gps_config.json', 'r') as f:
            config = json.load(f)
        
        print(f"✅ Configuración encontrada:")
        print(f"   • Host: {config.get('host', 'N/A')}")
        print(f"   • Puerto: {config.get('port', 'N/A')}")
        print(f"   • IMEI: {config.get('imei', 'N/A')}")
        print(f"   • Protocolo: {config.get('protocol', 'N/A')}")
        print(f"   • Intervalo: {config.get('interval', 'N/A')}s")
        
        # Verificar IMEI
        imei = config.get('imei', '')
        if len(imei) == 15 and imei.isdigit():
            print("✅ IMEI válido")
        else:
            print("❌ IMEI inválido")
        
        return config
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return None

def test_gps_connection():
    """Probar conexión GPS directamente."""
    print("\n🔍 Probando conexión GPS...")
    try:
        # Leer configuración
        with open('pc_gps_config.json', 'r') as f:
            config = json.load(f)
        
        host = config.get('host', 'localhost')
        port = config.get('port', 20332)
        imei = config.get('imei', '123456789012345')
        password = config.get('password', '123456')
        
        print(f"Conectando a {host}:{port}...")
        
        # Crear socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # Enviar login
        login_packet = f"#L#{imei};{password}\r\n"
        print(f"Enviando login: {login_packet.strip()}")
        sock.send(login_packet.encode('ascii'))
        
        # Esperar respuesta
        try:
            response = sock.recv(1024)
            if response:
                response_str = response.decode('ascii').strip()
                print(f"Respuesta del servidor: {response_str}")
                
                if "#AL#1" in response_str:
                    print("✅ Login exitoso!")
                    return True
                else:
                    print("⚠️ Login con respuesta inesperada")
                    return False
            else:
                print("⚠️ Sin respuesta del servidor")
                return False
        except socket.timeout:
            print("⏰ Timeout esperando respuesta")
            return False
        finally:
            sock.close()
            
    except ConnectionRefusedError:
        print("❌ Conexión rechazada - servidor GPS no está corriendo")
        return False
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
        return False

def provide_solutions():
    """Proporcionar soluciones basadas en el diagnóstico."""
    print("\n" + "="*60)
    print("💡 SOLUCIONES RECOMENDADAS")
    print("="*60)
    
    print("\n🔧 Para conectar el dispositivo:")
    print("1. Asegúrate que el servidor GPS esté corriendo:")
    print("   python start_gps_server.py")
    print()
    print("2. En otra terminal, ejecuta el simulador:")
    print("   python pc_gps_simulator.py")
    print()
    print("3. O usa el script automático:")
    print("   python start_pc_as_gps.py")

def main():
    """Función principal de diagnóstico."""
    print("🔍 DIAGNÓSTICO GPS - SkyGuard")
    print("="*50)
    
    # Verificaciones
    port_ok = check_port_20332()
    device_ok = check_device_in_db() is not None
    config_ok = check_config_file() is not None
    connection_ok = test_gps_connection() if port_ok else False
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("="*50)
    print(f"• Puerto 20332:     {'✅' if port_ok else '❌'}")
    print(f"• Dispositivo en BD: {'✅' if device_ok else '❌'}")
    print(f"• Configuración:    {'✅' if config_ok else '❌'}")
    print(f"• Conexión GPS:     {'✅' if connection_ok else '❌'}")
    
    if all([port_ok, device_ok, config_ok, connection_ok]):
        print("\n🎉 ¡Todo está funcionando correctamente!")
        print("El dispositivo debería estar enviando ubicación.")
    else:
        provide_solutions()

if __name__ == "__main__":
    main() 