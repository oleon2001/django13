#!/usr/bin/env python3
"""
🚀 SKYGUARD BACKEND MASTER STARTER
Script maestro para iniciar todo el backend del sistema SkyGuard
Incluye: Django, Celery, GPS Servers, WebSockets, Monitoring
"""

import os
import sys
import subprocess
import time
import threading
import signal
import platform
import psutil
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

class Colors:
    """Códigos de colores para terminal."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class SkyGuardBackendManager:
    """Gestor completo del backend SkyGuard."""
    
    def __init__(self):
        """Inicializar el gestor del backend."""
        self.processes = {}
        self.running = False
        self.project_root = Path(__file__).parent.absolute()
        self.log_dir = self.project_root / "logs"
        self.pid_file = self.project_root / "skyguard_backend.pid"
        
        # Crear directorio de logs
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar logging
        self.setup_logging()
        
        # Configuración de servicios
        self.services_config = {
            'redis': {
                'name': 'Redis Server',
                'command': ['redis-server'],
                'port': 6379,
                'check_cmd': ['redis-cli', 'ping'],
                'required': True,
                'startup_delay': 2,
                'log_file': 'redis.log'
            },
            'postgresql': {
                'name': 'PostgreSQL',
                'command': ['sudo', 'systemctl', 'start', 'postgresql'],
                'port': 5432,
                'check_cmd': ['sudo', 'systemctl', 'is-active', 'postgresql'],
                'required': True,
                'startup_delay': 3,
                'log_file': 'postgresql.log'
            },
            'django': {
                'name': 'Django HTTP Server',
                'command': [sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'],
                'port': 8000,
                'required': True,
                'startup_delay': 5,
                'log_file': 'django.log',
                'env_vars': {'DJANGO_SETTINGS_MODULE': 'skyguard.settings.dev'}
            },
            'daphne': {
                'name': 'Django WebSocket Server (Daphne)',
                'command': [sys.executable, '-m', 'daphne', '-b', '0.0.0.0', '-p', '8001', 'skyguard.asgi:application'],
                'port': 8001,
                'required': True,
                'startup_delay': 3,
                'log_file': 'daphne.log',
                'env_vars': {'DJANGO_SETTINGS_MODULE': 'skyguard.settings.dev'}
            },
            'celery_worker': {
                'name': 'Celery Worker',
                'command': [sys.executable, '-m', 'celery', '-A', 'skyguard', 'worker', '-l', 'info', '--concurrency=12'],
                'required': True,
                'startup_delay': 5,
                'log_file': 'celery_worker.log',
                'env_vars': {'DJANGO_SETTINGS_MODULE': 'skyguard.settings.dev'}
            },
            'celery_beat': {
                'name': 'Celery Beat Scheduler',
                'command': [sys.executable, '-m', 'celery', '-A', 'skyguard', 'beat', '-l', 'info'],
                'required': True,
                'startup_delay': 3,
                'log_file': 'celery_beat.log',
                'env_vars': {'DJANGO_SETTINGS_MODULE': 'skyguard.settings.dev'}
            },
            'gps_servers': {
                'name': 'GPS Protocol Servers',
                'command': [sys.executable, 'manage.py', 'runserver_gps'],
                'required': True,
                'startup_delay': 4,
                'log_file': 'gps_servers.log',
                'env_vars': {'DJANGO_SETTINGS_MODULE': 'skyguard.settings.dev'}
            },
            'device_monitor': {
                'name': 'Device Monitor',
                'command': [sys.executable, 'manage.py', 'start_device_monitor', '--timeout', '2', '--interval', '60'],
                'required': False,
                'startup_delay': 2,
                'log_file': 'device_monitor.log',
                'env_vars': {'DJANGO_SETTINGS_MODULE': 'skyguard.settings.dev'}
            }
        }
        
    def setup_logging(self):
        """Configurar sistema de logging."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.log_dir / 'backend_manager.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def print_banner(self):
        """Mostrar banner del sistema."""
        banner = f"""
{Colors.HEADER}{'='*80}
🚀 SKYGUARD BACKEND SYSTEM MANAGER
🌍 Sistema completo de rastreo GPS y análisis en tiempo real
{'='*80}{Colors.ENDC}

{Colors.OKBLUE}📊 Servicios a iniciar:{Colors.ENDC}
  1. Redis Server (Cache & Message Broker)
  2. PostgreSQL Database 
  3. Django HTTP Server (API REST)
  4. Daphne WebSocket Server (Real-time)
  5. Celery Worker (Background Tasks)
  6. Celery Beat (Scheduled Tasks)
  7. GPS Protocol Servers (Wialon, Concox, etc.)
  8. Device Monitor (Optional)

{Colors.WARNING}💡 Presiona Ctrl+C para detener todos los servicios{Colors.ENDC}
"""
        print(banner)
        
    def log(self, message: str, level: str = "INFO", color: str = None):
        """Registrar mensaje con timestamp y color."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colored_message = f"{color}{message}{Colors.ENDC}" if color else message
        print(f"[{timestamp}] {level}: {colored_message}")
        
        # También log a archivo
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def check_prerequisites(self) -> bool:
        """Verificar prerequisitos del sistema."""
        self.log("🔍 Verificando prerequisitos del sistema...", color=Colors.OKCYAN)
        
        # Verificar Python version
        if sys.version_info < (3, 7):
            self.log("❌ Python 3.7+ requerido", "ERROR", Colors.FAIL)
            return False
        
        # Verificar archivos principales
        required_files = [
            "manage.py",
            "requirements.txt",
            "skyguard/settings/dev.py",
            "skyguard/asgi.py",
            "skyguard/celery.py"
        ]
        
        for file in required_files:
            if not (self.project_root / file).exists():
                self.log(f"❌ Archivo requerido no encontrado: {file}", "ERROR", Colors.FAIL)
                return False
        
        # Verificar que Django esté instalado
        try:
            import django
            self.log(f"✅ Django {django.get_version()} encontrado", color=Colors.OKGREEN)
        except ImportError:
            self.log("❌ Django no está instalado", "ERROR", Colors.FAIL)
            return False
            
        # Verificar que Celery esté instalado
        try:
            import celery
            self.log(f"✅ Celery {celery.__version__} encontrado", color=Colors.OKGREEN)
        except ImportError:
            self.log("❌ Celery no está instalado", "ERROR", Colors.FAIL)
            return False
            
        # Verificar que Daphne esté instalado
        try:
            import daphne
            self.log("✅ Daphne encontrado", color=Colors.OKGREEN)
        except ImportError:
            self.log("❌ Daphne no está instalado", "ERROR", Colors.FAIL)
            return False
        
        self.log("✅ Todos los prerequisitos verificados", color=Colors.OKGREEN)
        return True
    
    def check_port_available(self, port: int) -> bool:
        """Verificar si un puerto está disponible."""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) != 0
        except:
            return True
    
    def check_service_health(self, service_name: str) -> bool:
        """Verificar salud de un servicio."""
        config = self.services_config.get(service_name, {})
        check_cmd = config.get('check_cmd')
        port = config.get('port')
        
        if check_cmd:
            try:
                result = subprocess.run(check_cmd, capture_output=True, timeout=5)
                return result.returncode == 0
            except:
                return False
        elif port:
            return not self.check_port_available(port)
        
        # Si no hay forma de verificar, asumir que está corriendo si el proceso existe
        return service_name in self.processes and self.processes[service_name].poll() is None
    
    def start_service(self, service_name: str) -> bool:
        """Iniciar un servicio específico."""
        config = self.services_config[service_name]
        
        # Verificar si el servicio ya está corriendo antes de intentar iniciarlo
        if self.check_service_health(service_name):
            self.log(f"✅ {config['name']} ya está corriendo", color=Colors.OKGREEN)
            return True
        
        try:
            self.log(f"🚀 Iniciando {config['name']}...", color=Colors.OKCYAN)
            
            # Configurar variables de entorno
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root)
            
            # Agregar variables específicas del servicio
            if 'env_vars' in config:
                env.update(config['env_vars'])
            
            # Configurar archivo de log
            log_file_path = self.log_dir / config.get('log_file', f'{service_name}.log')
            
            # Iniciar proceso
            with open(log_file_path, 'w') as log_file:
                process = subprocess.Popen(
                    config['command'],
                    cwd=self.project_root,
                    env=env,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
            
            self.processes[service_name] = process
            
            # Esperar delay de inicio
            time.sleep(config.get('startup_delay', 2))
            
            # Verificar que el servicio esté corriendo
            if process.poll() is None:
                # Verificar salud si es posible
                if self.check_service_health(service_name):
                    self.log(f"✅ {config['name']} iniciado correctamente (PID: {process.pid})", color=Colors.OKGREEN)
                    return True
                else:
                    self.log(f"⚠️ {config['name']} iniciado pero verificación de salud falló", "WARNING", Colors.WARNING)
                    return True  # Asumir que está bien, puede tomar tiempo en estar listo
            else:
                self.log(f"❌ {config['name']} falló al iniciar", "ERROR", Colors.FAIL)
                return False
                
        except Exception as e:
            self.log(f"❌ Error iniciando {config['name']}: {e}", "ERROR", Colors.FAIL)
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Detener un servicio específico."""
        if service_name not in self.processes:
            return True
            
        process = self.processes[service_name]
        config = self.services_config[service_name]
        
        try:
            self.log(f"🛑 Deteniendo {config['name']}...")
            
            # Intentar terminación graceful
            process.terminate()
            
            # Esperar hasta 10 segundos para terminación graceful
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Forzar terminación
                self.log(f"⚠️ Forzando terminación de {config['name']}", "WARNING")
                process.kill()
                process.wait()
            
            del self.processes[service_name]
            self.log(f"✅ {config['name']} detenido", color=Colors.OKGREEN)
            return True
            
        except Exception as e:
            self.log(f"❌ Error deteniendo {config['name']}: {e}", "ERROR", Colors.FAIL)
            return False
    
    def start_all_services(self) -> bool:
        """Iniciar todos los servicios en orden."""
        self.log("🚀 Iniciando todos los servicios del backend...", color=Colors.HEADER)
        
        failed_services = []
        
        for service_name, config in self.services_config.items():
            if not self.start_service(service_name):
                if config.get('required', False):
                    failed_services.append(config['name'])
                    self.log(f"❌ Servicio requerido {config['name']} falló", "ERROR", Colors.FAIL)
                else:
                    self.log(f"⚠️ Servicio opcional {config['name']} falló", "WARNING", Colors.WARNING)
        
        if failed_services:
            self.log(f"❌ Fallos en servicios críticos: {', '.join(failed_services)}", "ERROR", Colors.FAIL)
            return False
        
        self.log("🎯 Todos los servicios iniciados correctamente", color=Colors.OKGREEN)
        return True
    
    def stop_all_services(self):
        """Detener todos los servicios."""
        self.log("🛑 Deteniendo todos los servicios...", color=Colors.WARNING)
        
        # Detener en orden inverso
        service_names = list(self.services_config.keys())
        service_names.reverse()
        
        for service_name in service_names:
            self.stop_service(service_name)
        
        # Limpiar archivo PID
        if self.pid_file.exists():
            self.pid_file.unlink()
        
        self.log("✅ Todos los servicios detenidos", color=Colors.OKGREEN)
    
    def show_system_status(self):
        """Mostrar estado actual del sistema."""
        self.log("📊 Estado actual del sistema:", color=Colors.HEADER)
        
        print(f"\n{Colors.OKBLUE}{'Servicio':<30} {'Estado':<15} {'PID':<10} {'Puerto':<8}{Colors.ENDC}")
        print("-" * 65)
        
        for service_name, config in self.services_config.items():
            if service_name in self.processes:
                process = self.processes[service_name]
                if process.poll() is None:
                    status = f"{Colors.OKGREEN}✅ Corriendo{Colors.ENDC}"
                    pid = str(process.pid)
                else:
                    status = f"{Colors.FAIL}❌ Detenido{Colors.ENDC}"
                    pid = "N/A"
            else:
                status = f"{Colors.WARNING}⚠️ No iniciado{Colors.ENDC}"
                pid = "N/A"
            
            port = str(config.get('port', 'N/A'))
            print(f"{config['name']:<30} {status:<24} {pid:<10} {port:<8}")
        
        # Mostrar URLs importantes
        print(f"\n{Colors.OKCYAN}🌐 URLs importantes:{Colors.ENDC}")
        print(f"  • API REST:      http://localhost:8000")
        print(f"  • WebSocket:     ws://localhost:8001")
        print(f"  • Admin:         http://localhost:8000/admin")
        print(f"  • API Docs:      http://localhost:8000/api/docs/")
        
        # Mostrar puertos GPS
        print(f"\n{Colors.OKCYAN}📡 Puertos GPS:{Colors.ENDC}")
        print(f"  • Wialon:        20332 (TCP)")
        print(f"  • Concox:        55300 (TCP)")
        print(f"  • Meiligao:      62000 (UDP)")
        print(f"  • Satellite:     15557 (TCP)")
        
    def monitor_services(self):
        """Monitorear servicios en ejecución."""
        self.log("👁️ Iniciando monitoreo de servicios...", color=Colors.OKCYAN)
        
        check_interval = 30  # segundos
        
        while self.running:
            try:
                time.sleep(check_interval)
                
                failed_services = []
                
                for service_name, config in self.services_config.items():
                    if service_name in self.processes:
                        process = self.processes[service_name]
                        if process.poll() is not None:
                            failed_services.append(config['name'])
                            self.log(f"⚠️ {config['name']} se detuvo inesperadamente", "WARNING", Colors.WARNING)
                            
                            # Intentar reiniciar servicios críticos
                            if config.get('required', False):
                                self.log(f"🔄 Intentando reiniciar {config['name']}...", color=Colors.WARNING)
                                if self.start_service(service_name):
                                    self.log(f"✅ {config['name']} reiniciado exitosamente", color=Colors.OKGREEN)
                                else:
                                    self.log(f"❌ No se pudo reiniciar {config['name']}", "ERROR", Colors.FAIL)
                
                # Mostrar estadísticas periódicas
                active_services = len([p for p in self.processes.values() if p.poll() is None])
                total_services = len(self.services_config)
                
                if failed_services:
                    self.log(f"📊 Servicios activos: {active_services}/{total_services} - Fallos: {', '.join(failed_services)}", 
                           "WARNING", Colors.WARNING)
                else:
                    self.log(f"📊 Servicios activos: {active_services}/{total_services} - Todo funcionando correctamente", 
                           color=Colors.OKGREEN)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"❌ Error en monitoreo: {e}", "ERROR", Colors.FAIL)
    
    def setup_signal_handlers(self):
        """Configurar manejadores de señales."""
        def signal_handler(signum, frame):
            self.log("\n🛑 Señal de interrupción recibida, deteniendo servicios...", "WARNING", Colors.WARNING)
            self.running = False
            self.stop_all_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def save_pid(self):
        """Guardar PID del proceso principal."""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    def run_django_migrations(self) -> bool:
        """Ejecutar migraciones de Django."""
        self.log("🔄 Ejecutando migraciones de Django...", color=Colors.OKCYAN)
        
        try:
            env = os.environ.copy()
            env['DJANGO_SETTINGS_MODULE'] = 'skyguard.settings.dev'
            
            result = subprocess.run(
                [sys.executable, 'manage.py', 'migrate'],
                cwd=self.project_root,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("✅ Migraciones ejecutadas correctamente", color=Colors.OKGREEN)
                return True
            else:
                self.log(f"❌ Error en migraciones: {result.stderr}", "ERROR", Colors.FAIL)
                return False
                
        except Exception as e:
            self.log(f"❌ Error ejecutando migraciones: {e}", "ERROR", Colors.FAIL)
            return False
    
    def collect_static_files(self) -> bool:
        """Recopilar archivos estáticos."""
        self.log("📦 Recopilando archivos estáticos...", color=Colors.OKCYAN)
        
        try:
            env = os.environ.copy()
            env['DJANGO_SETTINGS_MODULE'] = 'skyguard.settings.dev'
            
            result = subprocess.run(
                [sys.executable, 'manage.py', 'collectstatic', '--noinput'],
                cwd=self.project_root,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("✅ Archivos estáticos recopilados", color=Colors.OKGREEN)
                return True
            else:
                self.log(f"⚠️ Error en collectstatic: {result.stderr}", "WARNING", Colors.WARNING)
                return True  # No es crítico
                
        except Exception as e:
            self.log(f"⚠️ Error recopilando estáticos: {e}", "WARNING", Colors.WARNING)
            return True  # No es crítico
    
    def start_complete_backend(self):
        """Iniciar el backend completo."""
        self.print_banner()
        
        # Guardar PID
        self.save_pid()
        
        # Configurar manejadores de señales
        self.setup_signal_handlers()
        
        # Verificar prerequisitos
        if not self.check_prerequisites():
            self.log("❌ Prerequisitos no cumplidos", "ERROR", Colors.FAIL)
            return False
        
        # Ejecutar migraciones
        if not self.run_django_migrations():
            self.log("⚠️ Error con migraciones, continuando...", "WARNING", Colors.WARNING)
        
        # Recopilar archivos estáticos
        self.collect_static_files()
        
        # Iniciar servicios
        self.running = True
        
        if not self.start_all_services():
            self.log("❌ Error iniciando servicios críticos", "ERROR", Colors.FAIL)
            self.stop_all_services()
            return False
        
        # Mostrar estado
        self.show_system_status()
        
        self.log("🎯 Backend SkyGuard iniciado completamente", color=Colors.OKGREEN)
        self.log("🔄 Presiona Ctrl+C para detener todos los servicios", color=Colors.WARNING)
        
        try:
            # Iniciar monitoreo en hilo separado
            monitor_thread = threading.Thread(target=self.monitor_services)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Mantener el proceso principal vivo
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all_services()
        
        return True

def main():
    """Función principal."""
    try:
        manager = SkyGuardBackendManager()
        success = manager.start_complete_backend()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error crítico: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main() 