#!/usr/bin/env python3
"""
Script maestro para levantar el sistema completo SkyGuard
Incluye todos los servicios: Backend, Frontend, GPS Servers, Celery, etc.
"""

import os
import sys
import subprocess
import time
import threading
import signal
import platform
from datetime import datetime

class SystemManager:
    """Gestor del sistema completo SkyGuard."""
    
    def __init__(self):
        """Inicializar gestor del sistema."""
        self.processes = {}
        self.running = False
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        
    def log(self, message: str, level: str = "INFO"):
        """Registrar mensaje con timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_prerequisites(self) -> bool:
        """Verificar prerequisitos del sistema."""
        self.log("Verificando prerequisitos del sistema...")
        
        # Verificar Python
        if sys.version_info < (3, 7):
            self.log("Python 3.7+ requerido", "ERROR")
            return False
        
        # Verificar archivos principales
        required_files = [
            "manage.py",
            "requirements.txt",
            "skyguard/settings/base.py",
            "frontend/package.json"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                self.log(f"Archivo requerido no encontrado: {file}", "ERROR")
                return False
        
        self.log("✅ Prerequisitos verificados")
        return True
    
    def install_dependencies(self) -> bool:
        """Instalar dependencias Python y Node.js."""
        self.log("Instalando dependencias...")
        
        try:
            # Instalar dependencias Python
            self.log("Instalando dependencias Python...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, capture_output=True)
            
            # Instalar dependencias Node.js
            if os.path.exists("frontend/package.json"):
                self.log("Instalando dependencias Node.js...")
                subprocess.run([
                    "npm", "install"
                ], cwd="frontend", check=True, capture_output=True)
            
            self.log("✅ Dependencias instaladas")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Error instalando dependencias: {e}", "ERROR")
            return False
        except FileNotFoundError:
            self.log("npm no encontrado. Instala Node.js", "ERROR")
            return False
    
    def setup_database(self) -> bool:
        """Configurar base de datos."""
        self.log("Configurando base de datos...")
        
        try:
            # Ejecutar migraciones
            subprocess.run([
                sys.executable, "manage.py", "migrate"
            ], check=True, capture_output=True)
            
            # Crear superusuario si no existe
            subprocess.run([
                sys.executable, "manage.py", "shell", "-c",
                "from django.contrib.auth.models import User; "
                "User.objects.filter(username='admin').exists() or "
                "User.objects.create_superuser('admin', 'admin@skyguard.com', 'admin123')"
            ], capture_output=True)
            
            self.log("✅ Base de datos configurada")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Error configurando base de datos: {e}", "ERROR")
            return False
    
    def start_service(self, name: str, command: list, cwd: str = None) -> bool:
        """Iniciar un servicio."""
        try:
            self.log(f"Iniciando {name}...")
            
            # Configurar variables de entorno
            env = os.environ.copy()
            env['PYTHONPATH'] = self.project_root
            env['DJANGO_SETTINGS_MODULE'] = 'skyguard.settings'
            
            process = subprocess.Popen(
                command,
                cwd=cwd or self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.processes[name] = process
            self.log(f"✅ {name} iniciado (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.log(f"Error iniciando {name}: {e}", "ERROR")
            return False
    
    def start_redis(self) -> bool:
        """Iniciar Redis si está disponible."""
        try:
            # Verificar si Redis está corriendo
            result = subprocess.run(
                ["redis-cli", "ping"], 
                capture_output=True, 
                timeout=5
            )
            
            if result.returncode == 0:
                self.log("✅ Redis ya está corriendo")
                return True
            else:
                self.log("Iniciando Redis...")
                return self.start_service("Redis", ["redis-server"])
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("⚠️ Redis no disponible, usando cache en memoria", "WARNING")
            return True
    
    def start_backend_services(self) -> bool:
        """Iniciar servicios del backend."""
        self.log("Iniciando servicios del backend...")
        
        services = [
            {
                "name": "Django Backend",
                "command": [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"],
                "delay": 2
            },
            {
                "name": "Celery Worker",
                "command": [sys.executable, "-m", "celery", "-A", "skyguard", "worker", "-l", "info"],
                "delay": 3
            },
            {
                "name": "Celery Beat",
                "command": [sys.executable, "-m", "celery", "-A", "skyguard", "beat", "-l", "info"],
                "delay": 2
            }
        ]
        
        for service in services:
            if not self.start_service(service["name"], service["command"]):
                return False
            time.sleep(service["delay"])
        
        return True
    
    def start_gps_servers(self) -> bool:
        """Iniciar servidores GPS."""
        self.log("Iniciando servidores GPS...")
        
        gps_servers = [
            {
                "name": "GPS Server (Wialon)",
                "command": [sys.executable, "start_gps_server.py"],
                "delay": 2
            },
            {
                "name": "Bluetooth Server",
                "command": [sys.executable, "start_bluetooth_server.py"],
                "delay": 2
            },
            {
                "name": "GPS Monitor",
                "command": [sys.executable, "start_gps_monitor.py"],
                "delay": 1
            }
        ]
        
        for server in gps_servers:
            if os.path.exists(server["command"][1]):
                if not self.start_service(server["name"], server["command"]):
                    self.log(f"⚠️ No se pudo iniciar {server['name']}", "WARNING")
                else:
                    time.sleep(server["delay"])
            else:
                self.log(f"⚠️ {server['name']} no encontrado", "WARNING")
        
        return True
    
    def start_frontend(self) -> bool:
        """Iniciar frontend React."""
        if not os.path.exists("frontend/package.json"):
            self.log("⚠️ Frontend no encontrado", "WARNING")
            return True
        
        self.log("Iniciando frontend React...")
        
        # Verificar si está en modo desarrollo o producción
        if os.path.exists("frontend/build"):
            # Modo producción - servir archivos estáticos
            command = [sys.executable, "-m", "http.server", "3000", "--directory", "build"]
            cwd = "frontend"
        else:
            # Modo desarrollo
            command = ["npm", "start"]
            cwd = "frontend"
        
        return self.start_service("React Frontend", command, cwd)
    
    def monitor_services(self):
        """Monitorear servicios en ejecución."""
        self.log("Iniciando monitoreo de servicios...")
        
        while self.running:
            try:
                # Verificar estado de cada proceso
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        self.log(f"⚠️ {name} se detuvo inesperadamente", "WARNING")
                        # Intentar reiniciar servicios críticos
                        if name in ["Django Backend", "GPS Server (Wialon)"]:
                            self.log(f"🔄 Intentando reiniciar {name}...")
                            # Aquí podrías implementar lógica de reinicio
                
                # Mostrar estadísticas cada 30 segundos
                time.sleep(30)
                active_services = len([p for p in self.processes.values() if p.poll() is None])
                self.log(f"📊 Servicios activos: {active_services}/{len(self.processes)}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"Error en monitoreo: {e}", "ERROR")
    
    def stop_all_services(self):
        """Detener todos los servicios."""
        self.log("Deteniendo todos los servicios...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    self.log(f"Deteniendo {name}...")
                    process.terminate()
                    
                    # Esperar terminación graciosa
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        self.log(f"Forzando cierre de {name}...")
                        process.kill()
                        
            except Exception as e:
                self.log(f"Error deteniendo {name}: {e}", "ERROR")
        
        self.log("✅ Todos los servicios detenidos")
    
    def show_system_status(self):
        """Mostrar estado del sistema."""
        print("\n" + "=" * 60)
        print("📊 ESTADO DEL SISTEMA SKYGUARD")
        print("=" * 60)
        
        active_services = []
        inactive_services = []
        
        for name, process in self.processes.items():
            if process.poll() is None:
                active_services.append(f"✅ {name} (PID: {process.pid})")
            else:
                inactive_services.append(f"❌ {name}")
        
        print("🟢 SERVICIOS ACTIVOS:")
        for service in active_services:
            print(f"   {service}")
        
        if inactive_services:
            print("\n🔴 SERVICIOS INACTIVOS:")
            for service in inactive_services:
                print(f"   {service}")
        
        print(f"\n📈 TOTAL: {len(active_services)}/{len(self.processes)} servicios activos")
        
        print("\n🌐 URLS IMPORTANTES:")
        print("   • Backend API: http://localhost:8000")
        print("   • Frontend: http://localhost:3000")
        print("   • Admin Django: http://localhost:8000/admin")
        print("   • GPS Mobile App: http://localhost:8000/mobile_gps_app/")
        
        print("\n🔧 COMANDOS ÚTILES:")
        print("   • Ver logs: tail -f django.log")
        print("   • Probar GPS: python pc_gps_simulator.py")
        print("   • Estado BD: python manage.py shell")
        
        print("=" * 60)
    
    def setup_signal_handlers(self):
        """Configurar manejadores de señales."""
        def signal_handler(signum, frame):
            self.log(f"Señal {signum} recibida, deteniendo sistema...")
            self.stop_all_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_complete_system(self):
        """Iniciar el sistema completo."""
        print("🚀 SKYGUARD - SISTEMA COMPLETO")
        print("🌍 Iniciando todos los servicios...")
        print("=" * 60)
        
        # Configurar manejadores de señales
        self.setup_signal_handlers()
        
        # Verificar prerequisitos
        if not self.check_prerequisites():
            self.log("❌ Prerequisitos no cumplidos", "ERROR")
            return False
        
        # Instalar dependencias (opcional)
        install_deps = input("¿Instalar/actualizar dependencias? (y/N): ").lower() == 'y'
        if install_deps:
            if not self.install_dependencies():
                self.log("⚠️ Error con dependencias, continuando...", "WARNING")
        
        # Configurar base de datos
        if not self.setup_database():
            self.log("⚠️ Error con base de datos, continuando...", "WARNING")
        
        # Iniciar servicios
        self.running = True
        
        # 1. Redis (si está disponible)
        self.start_redis()
        time.sleep(2)
        
        # 2. Servicios del backend
        if not self.start_backend_services():
            self.log("❌ Error iniciando backend", "ERROR")
            return False
        
        # 3. Servidores GPS
        self.start_gps_servers()
        time.sleep(3)
        
        # 4. Frontend
        self.start_frontend()
        time.sleep(2)
        
        # Mostrar estado
        self.show_system_status()
        
        # Iniciar monitoreo
        self.log("🎯 Sistema iniciado completamente")
        self.log("🔄 Presiona Ctrl+C para detener todos los servicios")
        
        try:
            # Iniciar monitoreo en hilo separado
            monitor_thread = threading.Thread(target=self.monitor_services)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Mantener el proceso principal vivo
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.log("🛑 Deteniendo sistema por solicitud del usuario...")
        finally:
            self.stop_all_services()
        
        return True


def main():
    """Función principal."""
    try:
        manager = SystemManager()
        success = manager.start_complete_system()
        
        if success:
            print("✅ Sistema completado exitosamente")
        else:
            print("❌ Error iniciando sistema")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 