#!/usr/bin/env python3
"""
🛑 SKYGUARD BACKEND STOPPER
Script para detener todos los servicios del backend SkyGuard de manera segura
"""

import os
import sys
import signal
import psutil
import time
from pathlib import Path

class Colors:
    """Códigos de colores para terminal."""
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKCYAN = '\033[96m'

class SkyGuardStopper:
    """Clase para detener servicios SkyGuard."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.pid_file = self.project_root / "skyguard_backend.pid"
        
    def log(self, message: str, color: str = None):
        """Log con colores."""
        colored_message = f"{color}{message}{Colors.ENDC}" if color else message
        print(f"[{time.strftime('%H:%M:%S')}] {colored_message}")
    
    def stop_by_pid_file(self) -> bool:
        """Detener usando archivo PID."""
        if not self.pid_file.exists():
            self.log("❌ Archivo PID no encontrado", Colors.FAIL)
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                main_pid = int(f.read().strip())
            
            self.log(f"🔍 Encontrado PID principal: {main_pid}", Colors.OKCYAN)
            
            # Obtener proceso principal
            try:
                main_process = psutil.Process(main_pid)
                self.log(f"🛑 Deteniendo proceso principal y sus hijos...", Colors.WARNING)
                
                # Detener todos los procesos hijos primero
                children = main_process.children(recursive=True)
                for child in children:
                    try:
                        child.terminate()
                        self.log(f"  ├─ Terminando proceso hijo PID: {child.pid}")
                    except:
                        pass
                
                # Esperar que terminen gracefully
                _, alive = psutil.wait_procs(children, timeout=10)
                
                # Forzar terminación de procesos que no terminaron
                for p in alive:
                    try:
                        p.kill()
                        self.log(f"  ├─ Forzando terminación PID: {p.pid}")
                    except:
                        pass
                
                # Terminar proceso principal
                main_process.terminate()
                main_process.wait(timeout=10)
                
                self.log("✅ Proceso principal terminado", Colors.OKGREEN)
                
            except psutil.NoSuchProcess:
                self.log("⚠️ Proceso principal ya no existe", Colors.WARNING)
            
            # Limpiar archivo PID
            self.pid_file.unlink()
            return True
            
        except Exception as e:
            self.log(f"❌ Error deteniendo por PID: {e}", Colors.FAIL)
            return False
    
    def stop_by_process_name(self) -> bool:
        """Detener procesos por nombre."""
        self.log("🔍 Buscando procesos SkyGuard por nombre...", Colors.OKCYAN)
        
        # Procesos a buscar
        process_patterns = [
            'python',  # Buscaremos por comando específico
            'celery',
            'daphne',
            'manage.py',
            'redis-server'
        ]
        
        skyguard_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                
                # Buscar procesos relacionados con SkyGuard
                if any(pattern in cmdline.lower() for pattern in [
                    'skyguard', 'manage.py', 'celery -A skyguard', 
                    'daphne', 'runserver', 'runserver_gps'
                ]):
                    skyguard_processes.append(proc)
                    self.log(f"  📦 Encontrado: PID {proc.info['pid']} - {cmdline[:60]}...")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not skyguard_processes:
            self.log("ℹ️ No se encontraron procesos SkyGuard", Colors.WARNING)
            return True
        
        # Detener procesos
        self.log(f"🛑 Deteniendo {len(skyguard_processes)} procesos...", Colors.WARNING)
        
        for proc in skyguard_processes:
            try:
                proc.terminate()
                self.log(f"  ├─ Terminando PID: {proc.pid}")
            except:
                pass
        
        # Esperar terminación graceful
        _, alive = psutil.wait_procs(skyguard_processes, timeout=10)
        
        # Forzar terminación si es necesario
        for proc in alive:
            try:
                proc.kill()
                self.log(f"  ├─ Forzando terminación PID: {proc.pid}")
            except:
                pass
        
        self.log("✅ Procesos detenidos", Colors.OKGREEN)
        return True
    
    def stop_all(self):
        """Detener todos los servicios."""
        self.log("🛑 DETENIENDO BACKEND SKYGUARD", Colors.WARNING)
        self.log("=" * 50, Colors.WARNING)
        
        # Intentar detener por PID file primero
        stopped_by_pid = self.stop_by_pid_file()
        
        # Si no funcionó, buscar por nombre de proceso
        if not stopped_by_pid:
            self.stop_by_process_name()
        
        # Verificar que no queden procesos
        remaining = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'skyguard' in cmdline.lower() and 'stop_skyguard' not in cmdline.lower():
                    remaining.append(f"PID {proc.info['pid']}: {cmdline[:50]}...")
            except:
                continue
        
        if remaining:
            self.log("⚠️ Procesos que aún están corriendo:", Colors.WARNING)
            for proc in remaining:
                self.log(f"  - {proc}")
            self.log("\n💡 Puedes detenerlos manualmente con: kill -9 <PID>")
        else:
            self.log("✅ Todos los servicios SkyGuard han sido detenidos", Colors.OKGREEN)
        
        self.log("=" * 50)

def main():
    """Función principal."""
    stopper = SkyGuardStopper()
    stopper.stop_all()

if __name__ == "__main__":
    main() 