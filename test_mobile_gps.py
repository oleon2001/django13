#!/usr/bin/env python3
"""
Script de prueba para usar celular como GPS con SkyGuard
Este script demuestra cómo conectar tu celular como dispositivo GPS
"""

import os
import sys
import time
import threading
import subprocess
import requests
from datetime import datetime

def print_banner():
    """Imprimir banner del sistema."""
    print("=" * 60)
    print("🚗 SKYGUARD GPS MÓVIL - SISTEMA DE PRUEBA")
    print("=" * 60)
    print("Este sistema permite usar tu celular como dispositivo GPS")
    print("y conectarlo a la aplicación SkyGuard para tracking en tiempo real.")
    print("=" * 60)

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas."""
    print("🔍 Verificando dependencias...")
    
    required_packages = ['flask', 'requests', 'django']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANTE")
    
    if missing_packages:
        print(f"\n⚠️  Paquetes faltantes: {', '.join(missing_packages)}")
        print("Ejecuta: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def get_local_ip():
    """Obtener la IP local del sistema."""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def start_bluetooth_server():
    """Iniciar el servidor Bluetooth de SkyGuard."""
    print("\n🔧 Iniciando servidor Bluetooth SkyGuard...")
    
    try:
        # Verificar si el script del servidor existe
        server_script = os.path.join('skyguard', 'apps', 'tracking', 'BluServer.py')
        if not os.path.exists(server_script):
            print(f"❌ No se encontró el servidor Bluetooth en: {server_script}")
            return None
        
        # Iniciar el servidor en segundo plano
        cmd = [sys.executable, server_script]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar un momento para verificar que se inició
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Servidor Bluetooth iniciado en puerto 50100")
            return process
        else:
            print("❌ Error al iniciar el servidor Bluetooth")
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return None

def start_web_interface():
    """Iniciar la interfaz web para el GPS móvil."""
    print("\n🌐 Iniciando interfaz web GPS móvil...")
    
    try:
        # Importar y ejecutar la interfaz web
        from mobile_gps_web_interface import app
        
        # Obtener IP local
        local_ip = get_local_ip()
        
        print(f"✅ Interfaz web iniciada en: http://{local_ip}:5000")
        print("📱 Abre esta URL en tu celular para controlar el GPS")
        
        # Ejecutar en un thread separado
        def run_web_server():
            app.run(host='0.0.0.0', port=5000, debug=False)
        
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()
        
        return web_thread
        
    except Exception as e:
        print(f"❌ Error iniciando interfaz web: {e}")
        return None

def test_gps_connection():
    """Probar la conexión GPS."""
    print("\n🧪 Probando conexión GPS...")
    
    try:
        # Crear un cliente de prueba
        from mobile_gps_simulator import MobileGPSSimulator
        
        simulator = MobileGPSSimulator()
        
        # Intentar conectar
        if simulator.connect():
            print("✅ Conexión GPS exitosa")
            
            # Enviar una posición de prueba
            simulator.update_position(19.4326, -99.1332, 25.0, 90.0)
            simulator.send_ping()
            
            simulator.disconnect()
            return True
        else:
            print("❌ Error en conexión GPS")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba GPS: {e}")
        return False

def show_instructions():
    """Mostrar instrucciones de uso."""
    local_ip = get_local_ip()
    
    print("\n" + "=" * 60)
    print("📋 INSTRUCCIONES DE USO")
    print("=" * 60)
    print("1. El servidor Bluetooth está ejecutándose en puerto 50100")
    print("2. La interfaz web está disponible en:")
    print(f"   📱 http://{local_ip}:5000")
    print("\n3. En tu celular:")
    print("   - Abre el navegador")
    print("   - Ve a la URL mostrada arriba")
    print("   - Permite acceso a la ubicación cuando se solicite")
    print("   - Haz clic en 'Conectar'")
    print("   - Usa 'Obtener Ubicación Actual' para GPS real")
    print("   - O ingresa coordenadas manualmente")
    print("   - Haz clic en 'Enviar Posición'")
    print("\n4. En SkyGuard:")
    print("   - Ve al panel de dispositivos")
    print("   - Busca el dispositivo con IMEI: 123456789012345")
    print("   - Verás la posición en tiempo real")
    print("\n5. Para envío automático:")
    print("   - Activa 'Envío automático cada 30 segundos'")
    print("   - El GPS se actualizará automáticamente")
    print("=" * 60)

def monitor_system():
    """Monitorear el sistema en ejecución."""
    print("\n🔄 Sistema en ejecución. Presiona Ctrl+C para detener.")
    print("📊 Monitoreando actividad...")
    
    try:
        while True:
            time.sleep(10)
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Sistema activo")
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")

def main():
    """Función principal."""
    print_banner()
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ Faltan dependencias. Instálalas y vuelve a intentar.")
        return
    
    # Iniciar servidor Bluetooth
    bluetooth_process = start_bluetooth_server()
    if not bluetooth_process:
        print("\n❌ No se pudo iniciar el servidor Bluetooth")
        return
    
    # Iniciar interfaz web
    web_thread = start_web_interface()
    if not web_thread:
        print("\n❌ No se pudo iniciar la interfaz web")
        bluetooth_process.terminate()
        return
    
    # Probar conexión GPS
    if test_gps_connection():
        print("✅ Sistema GPS funcionando correctamente")
    else:
        print("⚠️  Advertencia: Problemas con la conexión GPS")
    
    # Mostrar instrucciones
    show_instructions()
    
    # Monitorear sistema
    try:
        monitor_system()
    except KeyboardInterrupt:
        pass
    finally:
        # Limpiar procesos
        print("\n🧹 Limpiando procesos...")
        if bluetooth_process:
            bluetooth_process.terminate()
            print("✅ Servidor Bluetooth detenido")
        print("✅ Sistema detenido correctamente")

if __name__ == "__main__":
    main() 