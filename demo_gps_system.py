#!/usr/bin/env python3
"""
Demostración completa del sistema GPS SkyGuard
Este script muestra el flujo completo de funcionamiento del sistema.
"""

import subprocess
import time
import sys
import threading
import signal
import os

class GPSSystemDemo:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def signal_handler(self, signum, frame):
        print("\n🛑 Deteniendo demostración...")
        self.running = False
        self.cleanup()
        sys.exit(0)
        
    def cleanup(self):
        """Limpiar procesos en ejecución"""
        for proc in self.processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                try:
                    proc.kill()
                except:
                    pass
                    
    def run_command(self, cmd, description, background=False):
        """Ejecutar comando con descripción"""
        print(f"🚀 {description}")
        print(f"   Comando: {' '.join(cmd)}")
        
        if background:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(proc)
            print(f"   ✅ Proceso iniciado en background (PID: {proc.pid})")
            return proc
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Éxito")
                if result.stdout:
                    print(f"   📤 Salida: {result.stdout.strip()}")
            else:
                print(f"   ❌ Error (código: {result.returncode})")
                if result.stderr:
                    print(f"   📤 Error: {result.stderr.strip()}")
            return result
            
    def demo_step_1_check_environment(self):
        """Paso 1: Verificar entorno"""
        print("\n" + "="*60)
        print("📋 PASO 1: VERIFICACIÓN DEL ENTORNO")
        print("="*60)
        
        # Verificar Django
        cmd = ['python', 'manage.py', '--version']
        self.run_command(cmd, "Verificando versión de Django")
        
        # Verificar base de datos
        cmd = ['python', 'manage.py', 'check']
        self.run_command(cmd, "Verificando configuración del sistema")
        
    def demo_step_2_start_servers(self):
        """Paso 2: Iniciar servidores GPS"""
        print("\n" + "="*60)
        print("🌐 PASO 2: INICIANDO SERVIDORES GPS")
        print("="*60)
        
        # Mostrar estado inicial
        cmd = ['python', 'manage.py', 'gps_servers', 'status']
        self.run_command(cmd, "Estado inicial de servidores")
        
        # Iniciar servidores
        cmd = ['python', 'manage.py', 'gps_servers', 'start']
        proc = self.run_command(cmd, "Iniciando todos los servidores GPS", background=True)
        
        # Esperar un momento para que inicien
        time.sleep(3)
        
        # Verificar estado después del inicio
        cmd = ['python', 'manage.py', 'gps_servers', 'status']
        self.run_command(cmd, "Estado después del inicio")
        
    def demo_step_3_simulate_device(self):
        """Paso 3: Simular dispositivo GPS"""
        print("\n" + "="*60)
        print("📱 PASO 3: SIMULANDO DISPOSITIVO GPS")
        print("="*60)
        
        # Mostrar servidores disponibles
        cmd = ['python', 'gps_simulator.py', '--list-servers']
        self.run_command(cmd, "Servidores GPS disponibles")
        
        # Simular dispositivo Wialon Legacy
        print("\n🎯 Simulando dispositivo Wialon Legacy...")
        cmd = ['python', 'gps_simulator.py', '--server', 'wialon_legacy', '--imei', '123456789012345']
        proc = self.run_command(cmd, "Iniciando simulador GPS Wialon Legacy", background=True)
        
        # Simular dispositivo Concox
        print("\n🎯 Simulando dispositivo Concox...")
        cmd = ['python', 'gps_simulator.py', '--server', 'concox', '--imei', '987654321098765']
        proc2 = self.run_command(cmd, "Iniciando simulador GPS Concox", background=True)
        
        return [proc, proc2]
        
    def demo_step_4_monitor_activity(self):
        """Paso 4: Monitorear actividad"""
        print("\n" + "="*60)
        print("📊 PASO 4: MONITOREANDO ACTIVIDAD")
        print("="*60)
        
        # Verificar estadísticas
        cmd = ['python', 'manage.py', 'gps_servers', 'stats']
        self.run_command(cmd, "Estadísticas del sistema")
        
        # Mostrar dispositivos conectados
        print("\n📱 Verificando dispositivos en base de datos...")
        cmd = ['python', 'manage.py', 'shell', '-c', '''
from skyguard.apps.gps.models.device import GPSDevice
devices = GPSDevice.objects.all()
print(f"Total de dispositivos: {devices.count()}")
for device in devices:
    print(f"  - IMEI: {device.imei}, Estado: {device.connection_status}")
    if device.position:
        print(f"    Posición: {device.position.y:.6f}, {device.position.x:.6f}")
''']
        self.run_command(cmd, "Consultando dispositivos registrados")
        
    def demo_step_5_test_apis(self):
        """Paso 5: Probar APIs"""
        print("\n" + "="*60)
        print("🔌 PASO 5: PROBANDO APIs REST")
        print("="*60)
        
        # Probar API de dispositivos (requiere servidor web)
        print("💡 Para probar las APIs REST, ejecuta:")
        print("   python manage.py runserver 8000")
        print("   curl http://localhost:8000/api/gps/devices/")
        
    def run_demo(self):
        """Ejecutar demostración completa"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🎬 DEMOSTRACIÓN DEL SISTEMA GPS SKYGUARD")
        print("=" * 60)
        print("Esta demostración muestra el flujo completo del sistema:")
        print("1. Verificación del entorno")
        print("2. Inicio de servidores GPS")
        print("3. Simulación de dispositivos GPS")
        print("4. Monitoreo de actividad")
        print("5. Prueba de APIs")
        print("\nPresiona Ctrl+C para detener en cualquier momento")
        print("=" * 60)
        
        try:
            # Ejecutar pasos de la demostración
            self.demo_step_1_check_environment()
            time.sleep(2)
            
            self.demo_step_2_start_servers()
            time.sleep(5)
            
            simulators = self.demo_step_3_simulate_device()
            time.sleep(10)  # Dejar que los simuladores envíen datos
            
            self.demo_step_4_monitor_activity()
            time.sleep(2)
            
            self.demo_step_5_test_apis()
            
            print("\n" + "="*60)
            print("✅ DEMOSTRACIÓN COMPLETADA")
            print("="*60)
            print("🔄 Los servidores y simuladores siguen ejecutándose...")
            print("📊 Puedes verificar los datos en:")
            print("   - Admin: http://localhost:8000/admin/")
            print("   - API: http://localhost:8000/api/gps/")
            print("\n🛑 Presiona Ctrl+C para detener todo")
            
            # Mantener demostración activa
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    """Función principal"""
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        print("❌ Error: Este script debe ejecutarse desde el directorio raíz del proyecto Django")
        print("   Asegúrate de estar en el directorio que contiene manage.py")
        sys.exit(1)
        
    # Verificar que el entorno virtual está activado
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Advertencia: No se detectó un entorno virtual activado")
        print("   Recomendamos activar el entorno virtual con: source venv/bin/activate")
        
    demo = GPSSystemDemo()
    demo.run_demo()

if __name__ == "__main__":
    main() 