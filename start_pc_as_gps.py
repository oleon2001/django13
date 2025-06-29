#!/usr/bin/env python3
"""
Script completo para iniciar PC como dispositivo GPS
Incluye registro, servidor GPS y simulador
"""
import os
import sys
import subprocess
import time
import threading
import signal

def log(message):
    """Imprimir mensaje con timestamp."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def register_device():
    """Registrar dispositivo PC en la base de datos."""
    log("🔧 Registrando dispositivo PC...")
    try:
        result = subprocess.run([sys.executable, "register_pc_device.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            log("✅ Dispositivo registrado exitosamente")
            return True
        else:
            log(f"❌ Error registrando dispositivo: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ Error: {e}")
        return False

def start_gps_server():
    """Iniciar servidor GPS en hilo separado."""
    log("🌐 Iniciando servidor GPS...")
    try:
        process = subprocess.Popen([sys.executable, "start_django_gps_server.py"],
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        log("✅ Servidor GPS iniciado")
        return process
    except Exception as e:
        log(f"❌ Error iniciando servidor GPS: {e}")
        return None

def start_pc_simulator():
    """Iniciar simulador PC."""
    log("🖥️ Iniciando simulador PC...")
    try:
        process = subprocess.Popen([sys.executable, "pc_gps_simulator.py"],
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        log("✅ Simulador PC iniciado")
        return process
    except Exception as e:
        log(f"❌ Error iniciando simulador PC: {e}")
        return None

def main():
    """Función principal."""
    print("=" * 60)
    print("🚀 PC GPS SYSTEM - SkyGuard")
    print("🌍 Iniciando PC como dispositivo GPS completo")
    print("=" * 60)
    
    processes = []
    
    try:
        # Paso 1: Verificar IMEI
        log("🔍 Verificando IMEI...")
        result = subprocess.run([sys.executable, "verify_imei.py"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            log("❌ IMEI inválido")
            return
        
        # Paso 2: Registrar dispositivo
        if not register_device():
            log("⚠️ Error registrando dispositivo, continuando...")
        
        # Paso 3: Iniciar servidor GPS
        gps_server = start_gps_server()
        if gps_server:
            processes.append(("Servidor GPS", gps_server))
            time.sleep(3)  # Esperar que el servidor esté listo
        
        # Paso 4: Iniciar simulador PC
        pc_simulator = start_pc_simulator()
        if pc_simulator:
            processes.append(("Simulador PC", pc_simulator))
        
        if not processes:
            log("❌ No se pudo iniciar ningún servicio")
            return
        
        log("🎯 Sistema iniciado correctamente")
        log("📊 Servicios activos:")
        for name, process in processes:
            log(f"   • {name} (PID: {process.pid})")
        
        log("🌐 URLs importantes:")
        log("   • Frontend: http://localhost:3000")
        log("   • Backend: http://localhost:8000")
        log("   • Admin: http://localhost:8000/admin")
        
        log("🔄 Presiona Ctrl+C para detener todos los servicios")
        
        # Mantener vivo hasta Ctrl+C
        while True:
            time.sleep(1)
            # Verificar que los procesos sigan vivos
            for name, process in processes:
                if process.poll() is not None:
                    log(f"⚠️ {name} se detuvo inesperadamente")
    
    except KeyboardInterrupt:
        log("🛑 Deteniendo servicios...")
    
    except Exception as e:
        log(f"❌ Error: {e}")
    
    finally:
        # Detener todos los procesos
        for name, process in processes:
            try:
                log(f"Deteniendo {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                log(f"Forzando cierre de {name}...")
                process.kill()
            except Exception as e:
                log(f"Error deteniendo {name}: {e}")
        
        log("✅ Todos los servicios detenidos")

if __name__ == "__main__":
    main() 