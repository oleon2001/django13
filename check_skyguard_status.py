#!/usr/bin/env python3
"""
📊 SKYGUARD STATUS CHECKER
Script para verificar el estado de todos los servicios del backend SkyGuard
"""

import os
import sys
import socket
import subprocess
import psutil
import time
from pathlib import Path
from typing import Dict, List, Tuple

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

class SkyGuardStatusChecker:
    """Verificador de estado del sistema SkyGuard."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.pid_file = self.project_root / "skyguard_backend.pid"
        
        # Configuración de servicios a verificar
        self.services = {
            'Redis': {
                'port': 6379,
                'check_cmd': ['redis-cli', 'ping'],
                'expected_response': 'PONG'
            },
            'PostgreSQL': {
                'port': 5432,
                'check_cmd': ['sudo', 'systemctl', 'is-active', 'postgresql'],
                'expected_response': 'active'
            },
            'Django HTTP': {
                'port': 8000,
                'url': 'http://localhost:8000',
                'process_pattern': 'manage.py runserver'
            },
            'Django WebSocket': {
                'port': 8001,
                'process_pattern': 'daphne'
            },
            'Celery Worker': {
                'process_pattern': 'celery -A skyguard worker'
            },
            'Celery Beat': {
                'process_pattern': 'celery -A skyguard beat'
            },
            'GPS Servers': {
                'ports': [20332, 55300, 62000, 15557],
                'process_pattern': 'runserver_gps'
            }
        }
        
    def log(self, message: str, color: str = None):
        """Log con colores."""
        colored_message = f"{color}{message}{Colors.ENDC}" if color else message
        print(colored_message)
    
    def check_port(self, port: int, host: str = 'localhost') -> bool:
        """Verificar si un puerto está en uso."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    def check_process_running(self, pattern: str) -> List[Dict]:
        """Buscar procesos que coincidan con un patrón."""
        matching_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if pattern.lower() in cmdline.lower():
                    matching_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': cmdline,
                        'cpu': proc.info['cpu_percent'],
                        'memory': proc.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return matching_processes
    
    def run_command(self, cmd: List[str]) -> Tuple[bool, str]:
        """Ejecutar comando y retornar resultado."""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    def check_service_status(self, service_name: str, config: Dict) -> Dict:
        """Verificar estado de un servicio específico."""
        status = {
            'name': service_name,
            'running': False,
            'details': [],
            'processes': [],
            'ports': [],
            'issues': []
        }
        
        # Verificar puertos
        if 'port' in config:
            port_open = self.check_port(config['port'])
            status['ports'].append({
                'port': config['port'],
                'open': port_open
            })
            if port_open:
                status['running'] = True
            else:
                status['issues'].append(f"Puerto {config['port']} no está en uso")
        
        if 'ports' in config:
            for port in config['ports']:
                port_open = self.check_port(port)
                status['ports'].append({
                    'port': port,
                    'open': port_open
                })
                if port_open:
                    status['running'] = True
        
        # Verificar procesos
        if 'process_pattern' in config:
            processes = self.check_process_running(config['process_pattern'])
            status['processes'] = processes
            if processes:
                status['running'] = True
            else:
                status['issues'].append(f"No se encontró proceso con patrón: {config['process_pattern']}")
        
        # Verificar comando específico
        if 'check_cmd' in config:
            success, output = self.run_command(config['check_cmd'])
            if success and config.get('expected_response', '') in output:
                status['running'] = True
                status['details'].append(f"Comando exitoso: {output}")
            else:
                status['issues'].append(f"Comando falló: {output}")
        
        return status
    
    def get_system_resources(self) -> Dict:
        """Obtener información de recursos del sistema."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory(),
            'disk': psutil.disk_usage('/'),
            'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    
    def check_pid_file(self) -> Dict:
        """Verificar archivo PID del proceso principal."""
        if not self.pid_file.exists():
            return {'exists': False, 'pid': None, 'running': False}
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                process = psutil.Process(pid)
                return {
                    'exists': True,
                    'pid': pid,
                    'running': process.is_running(),
                    'process': process
                }
            except psutil.NoSuchProcess:
                return {'exists': True, 'pid': pid, 'running': False}
                
        except Exception as e:
            return {'exists': True, 'pid': None, 'running': False, 'error': str(e)}
    
    def print_header(self):
        """Imprimir header del reporte."""
        header = f"""
{Colors.HEADER}{'='*80}
📊 SKYGUARD BACKEND STATUS REPORT
🌍 Estado completo del sistema de rastreo GPS
{'='*80}{Colors.ENDC}

{Colors.OKCYAN}🕐 Verificación realizada: {time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}
"""
        print(header)
    
    def print_service_status(self, status: Dict):
        """Imprimir estado de un servicio."""
        name = status['name']
        running = status['running']
        
        # Icono y color según estado
        if running:
            icon = "✅"
            color = Colors.OKGREEN
            status_text = "CORRIENDO"
        else:
            icon = "❌"
            color = Colors.FAIL
            status_text = "DETENIDO"
        
        print(f"\n{color}{icon} {name:<20} {status_text}{Colors.ENDC}")
        
        # Mostrar puertos
        if status['ports']:
            for port_info in status['ports']:
                port = port_info['port']
                open_status = "ABIERTO" if port_info['open'] else "CERRADO"
                port_color = Colors.OKGREEN if port_info['open'] else Colors.FAIL
                print(f"   🌐 Puerto {port}: {port_color}{open_status}{Colors.ENDC}")
        
        # Mostrar procesos
        if status['processes']:
            for proc in status['processes']:
                print(f"   🔄 PID {proc['pid']} - CPU: {proc['cpu']:.1f}% - RAM: {proc['memory']:.1f}%")
                print(f"      📝 {proc['cmdline'][:70]}...")
        
        # Mostrar detalles
        if status['details']:
            for detail in status['details']:
                print(f"   ℹ️  {detail}")
        
        # Mostrar problemas
        if status['issues']:
            for issue in status['issues']:
                print(f"   ⚠️  {Colors.WARNING}{issue}{Colors.ENDC}")
    
    def print_system_resources(self, resources: Dict):
        """Imprimir recursos del sistema."""
        memory = resources['memory']
        disk = resources['disk']
        
        print(f"\n{Colors.OKBLUE}📊 RECURSOS DEL SISTEMA{Colors.ENDC}")
        print("-" * 40)
        
        # CPU
        cpu_color = Colors.OKGREEN if resources['cpu_percent'] < 80 else Colors.WARNING
        print(f"💻 CPU: {cpu_color}{resources['cpu_percent']:.1f}%{Colors.ENDC}")
        
        # Memoria
        memory_percent = memory.percent
        memory_color = Colors.OKGREEN if memory_percent < 80 else Colors.WARNING
        print(f"🧠 RAM: {memory_color}{memory_percent:.1f}%{Colors.ENDC} "
              f"({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)")
        
        # Disco
        disk_percent = disk.percent
        disk_color = Colors.OKGREEN if disk_percent < 90 else Colors.WARNING
        print(f"💾 Disco: {disk_color}{disk_percent:.1f}%{Colors.ENDC} "
              f"({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)")
        
        # Load average (si está disponible)
        if resources['load_avg']:
            load_1, load_5, load_15 = resources['load_avg']
            print(f"⚡ Load: {load_1:.2f}, {load_5:.2f}, {load_15:.2f}")
    
    def print_summary(self, all_status: List[Dict], pid_info: Dict):
        """Imprimir resumen del estado."""
        running_services = sum(1 for s in all_status if s['running'])
        total_services = len(all_status)
        
        print(f"\n{Colors.HEADER}📋 RESUMEN{Colors.ENDC}")
        print("-" * 40)
        
        # Estado general
        if running_services == total_services:
            overall_color = Colors.OKGREEN
            overall_status = "🟢 TODOS LOS SERVICIOS FUNCIONANDO"
        elif running_services > 0:
            overall_color = Colors.WARNING
            overall_status = "🟡 ALGUNOS SERVICIOS DETENIDOS"
        else:
            overall_color = Colors.FAIL
            overall_status = "🔴 SISTEMA DETENIDO"
        
        print(f"{overall_color}{overall_status}{Colors.ENDC}")
        print(f"Servicios activos: {running_services}/{total_services}")
        
        # Estado del proceso principal
        if pid_info['exists']:
            if pid_info['running']:
                print(f"🎯 Proceso principal: {Colors.OKGREEN}CORRIENDO (PID: {pid_info['pid']}){Colors.ENDC}")
            else:
                print(f"🎯 Proceso principal: {Colors.FAIL}DETENIDO{Colors.ENDC}")
        else:
            print(f"🎯 Proceso principal: {Colors.WARNING}NO INICIADO{Colors.ENDC}")
        
        # URLs importantes
        django_running = any(s['name'] == 'Django HTTP' and s['running'] for s in all_status)
        websocket_running = any(s['name'] == 'Django WebSocket' and s['running'] for s in all_status)
        
        print(f"\n{Colors.OKCYAN}🌐 ENDPOINTS DISPONIBLES:{Colors.ENDC}")
        if django_running:
            print(f"  ✅ API REST: http://localhost:8000")
            print(f"  ✅ Admin: http://localhost:8000/admin")
        else:
            print(f"  ❌ API REST: No disponible")
            
        if websocket_running:
            print(f"  ✅ WebSocket: ws://localhost:8001")
        else:
            print(f"  ❌ WebSocket: No disponible")
    
    def check_all_services(self):
        """Verificar todos los servicios."""
        self.print_header()
        
        # Verificar archivo PID
        pid_info = self.check_pid_file()
        
        # Verificar cada servicio
        all_status = []
        for service_name, config in self.services.items():
            status = self.check_service_status(service_name, config)
            all_status.append(status)
            self.print_service_status(status)
        
        # Mostrar recursos del sistema
        resources = self.get_system_resources()
        self.print_system_resources(resources)
        
        # Mostrar resumen
        self.print_summary(all_status, pid_info)
        
        print(f"\n{Colors.OKCYAN}💡 Para iniciar servicios: ./start_skyguard_backend.py{Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Para detener servicios: ./stop_skyguard_backend.py{Colors.ENDC}")

def main():
    """Función principal."""
    try:
        checker = SkyGuardStatusChecker()
        checker.check_all_services()
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error verificando estado: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main() 