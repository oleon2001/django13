#!/usr/bin/env python3
"""
Script para iniciar el servidor Bluetooth de SkyGuard
"""

import os
import sys
import subprocess
import time
import signal
import threading

# Agregar el directorio del proyecto al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configurar variables de entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')

class BluetoothServerManager:
    """Gestor del servidor Bluetooth de SkyGuard."""
    
    def __init__(self):
        self.server_process = None
        self.running = False
        
    def start_server(self, port: int = 50100):
        """Iniciar el servidor Bluetooth."""
        try:
            # Ruta al script del servidor Bluetooth
            server_script = os.path.join(project_root, 'skyguard', 'apps', 'tracking', 'BluServer.py')
            
            if not os.path.exists(server_script):
                print(f"Error: No se encontró el script del servidor en {server_script}")
                return False
            
            # Comando para ejecutar el servidor
            cmd = [
                sys.executable,
                server_script
            ]
            
            print(f"Iniciando servidor Bluetooth en puerto {port}...")
            print(f"Comando: {' '.join(cmd)}")
            
            # Iniciar el proceso del servidor
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.running = True
            
            # Thread para monitorear la salida del servidor
            def monitor_output():
                while self.running and self.server_process.poll() is None:
                    output = self.server_process.stdout.readline()
                    if output:
                        print(f"[Servidor] {output.strip()}")
                    error = self.server_process.stderr.readline()
                    if error:
                        print(f"[Error] {error.strip()}")
            
            monitor_thread = threading.Thread(target=monitor_output, daemon=True)
            monitor_thread.start()
            
            # Esperar un momento para verificar que el servidor se inició correctamente
            time.sleep(2)
            
            if self.server_process.poll() is None:
                print("✅ Servidor Bluetooth iniciado exitosamente")
                return True
            else:
                print("❌ Error al iniciar el servidor")
                return False
                
        except Exception as e:
            print(f"Error iniciando servidor: {e}")
            return False
    
    def stop_server(self):
        """Detener el servidor Bluetooth."""
        if self.server_process and self.running:
            print("Deteniendo servidor Bluetooth...")
            self.running = False
            
            # Enviar señal de terminación
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Forzando terminación del servidor...")
                self.server_process.kill()
                self.server_process.wait()
            
            print("✅ Servidor Bluetooth detenido")
    
    def is_running(self) -> bool:
        """Verificar si el servidor está ejecutándose."""
        return self.running and self.server_process and self.server_process.poll() is None
    
    def get_status(self):
        """Obtener estado del servidor."""
        if self.is_running():
            return "Ejecutándose"
        elif self.server_process:
            return f"Detenido (código: {self.server_process.returncode})"
        else:
            return "No iniciado"

def signal_handler(signum, frame):
    """Manejador de señales para detener el servidor."""
    print(f"\nRecibida señal {signum}, deteniendo servidor...")
    if server_manager:
        server_manager.stop_server()
    sys.exit(0)

def main():
    """Función principal."""
    global server_manager
    
    print("=== Gestor del Servidor Bluetooth SkyGuard ===")
    
    # Registrar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Crear gestor del servidor
    server_manager = BluetoothServerManager()
    
    # Iniciar servidor
    if server_manager.start_server(port=50100):
        print("\nServidor iniciado. Presiona Ctrl+C para detener.")
        
        # Mantener el programa ejecutándose
        try:
            while server_manager.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            server_manager.stop_server()
    else:
        print("No se pudo iniciar el servidor")
        sys.exit(1)

if __name__ == "__main__":
    server_manager = None
    main() 