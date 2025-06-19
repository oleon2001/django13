#!/usr/bin/env python
"""
Script para probar el sistema de detección de dispositivos offline.
"""

import os
import sys
import time
import requests
import subprocess
from datetime import datetime, timedelta

# Configuración
API_BASE_URL = "http://localhost:8000/api/gps"
FRONTEND_URL = "http://localhost:3000"
TEST_IMEI = "123456789012345"

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n🔹 Paso {step}: {description}")

def check_device_status():
    """Verificar el estado actual de los dispositivos."""
    try:
        response = requests.get(f"{API_BASE_URL}/devices/activity-status/")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Estadísticas: {data['stats']}")
            
            for device in data['devices']:
                status_icon = "🟢" if device['connection_status_real'] == 'ONLINE' else "🔴"
                heartbeat_info = ""
                if device['heartbeat_age_seconds']:
                    heartbeat_info = f" (hace {device['heartbeat_age_seconds']:.0f}s)"
                
                print(f"   {status_icon} {device['imei']} ({device['name']}) - {device['connection_status_real']}{heartbeat_info}")
                
                if device['needs_update']:
                    print(f"      ⚠️  Estado en BD: {device['connection_status_db']} (necesita actualización)")
            
            return data
        else:
            print(f"❌ Error al obtener estado: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def force_check_devices():
    """Forzar verificación de todos los dispositivos."""
    try:
        response = requests.post(f"{API_BASE_URL}/devices/check-status/", json={'timeout': 60})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Verificación completada:")
            print(f"   - Dispositivos verificados: {data['devices_checked']}")
            print(f"   - Marcados como offline: {data['devices_updated_to_offline']}")
            print(f"   - Aún online: {data['devices_still_online']}")
            return data
        else:
            print(f"❌ Error en verificación: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_device_connection(imei):
    """Probar conexión de un dispositivo específico."""
    try:
        response = requests.post(f"{API_BASE_URL}/devices/{imei}/test-connection/")
        if response.status_code == 200:
            data = response.json()
            status_icon = "✅" if data['success'] else "❌"
            print(f"{status_icon} Test de conexión: {data['message']}")
            return data
        else:
            print(f"❌ Error en test de conexión: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def run_device_monitor_command():
    """Ejecutar el comando de monitoreo de dispositivos."""
    print("🚀 Iniciando monitor de dispositivos (presiona Ctrl+C para detener)...")
    try:
        # Ejecutar el comando en background por 60 segundos para demostración
        process = subprocess.Popen([
            'python', 'manage.py', 'start_device_monitor', 
            '--timeout', '1',  # 1 minuto para prueba rápida
            '--interval', '60',  # Verificar cada 60 segundos (1 minuto)
            '--verbose'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Leer salida por 60 segundos
        start_time = time.time()
        while time.time() - start_time < 60:
            if process.poll() is not None:
                break
            time.sleep(1)
        
        # Terminar el proceso
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        
        print("📝 Salida del monitor:")
        print(stdout)
        if stderr:
            print("⚠️  Errores:")
            print(stderr)
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("⏰ Monitor detenido después de 60 segundos")
    except Exception as e:
        print(f"❌ Error ejecutando monitor: {e}")

def main():
    print_header("PRUEBA DEL SISTEMA DE DETECCIÓN DE DISPOSITIVOS OFFLINE")
    
    print("Este script probará el sistema automático para marcar dispositivos como offline")
    print("cuando no reciben peticiones o conexiones.")
    
    # Paso 1: Verificar estado inicial
    print_step(1, "Verificando estado inicial de dispositivos")
    initial_status = check_device_status()
    
    if not initial_status:
        print("❌ No se pudo obtener el estado inicial. Verifica que el servidor esté ejecutándose.")
        return
    
    # Paso 2: Forzar verificación manual
    print_step(2, "Ejecutando verificación manual de dispositivos")
    force_check_devices()
    
    # Paso 3: Verificar estado después de la verificación
    print_step(3, "Verificando estado después de la verificación manual")
    check_device_status()
    
    # Paso 4: Probar conexión de dispositivo específico
    if TEST_IMEI:
        print_step(4, f"Probando conexión del dispositivo {TEST_IMEI}")
        test_device_connection(TEST_IMEI)
    
    # Paso 5: Ejecutar monitor automático
    print_step(5, "Ejecutando monitor automático de dispositivos")
    run_device_monitor_command()
    
    # Paso 6: Verificar estado final
    print_step(6, "Verificando estado final después del monitoreo")
    final_status = check_device_status()
    
    print_header("RESUMEN DE LA PRUEBA")
    
    if initial_status and final_status:
        initial_stats = initial_status['stats']
        final_stats = final_status['stats']
        
        print(f"📊 Estado inicial: {initial_stats['online']} online, {initial_stats['offline']} offline")
        print(f"📊 Estado final:   {final_stats['online']} online, {final_stats['offline']} offline")
        
        if final_stats['offline'] > initial_stats['offline']:
            print("✅ El sistema detectó y marcó dispositivos como offline correctamente")
        else:
            print("ℹ️  No se detectaron cambios (puede ser normal si todos los dispositivos están activos)")
    
    print("\n🔗 URLs útiles:")
    print(f"   - API de estado: {API_BASE_URL}/devices/activity-status/")
    print(f"   - Frontend:      {FRONTEND_URL}/devices")
    print(f"   - Verificación:  {API_BASE_URL}/devices/check-status/")
    
    print("\n📝 Comandos útiles:")
    print("   - python manage.py quick_device_monitor --quiet     # Monitor cada minuto (recomendado)")
    print("   - python manage.py start_device_monitor --verbose   # Monitor configurable")
    print("   - python manage.py check_device_status --dry-run    # Verificación única")
    print("   - python gps_simulator.py                           # Simular actividad de dispositivo")

if __name__ == "__main__":
    main() 