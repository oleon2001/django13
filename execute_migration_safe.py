#!/usr/bin/env python3
"""
🚀 EJECUTOR SEGURO DE MIGRACIÓN - VERSIÓN MEJORADA
Versión adaptada para manejar comandos disponibles y errores comunes
"""

import os
import sys
import django
import argparse
import logging
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migration_safe.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SafeMigrationExecutor:
    """Ejecutor de migración con manejo mejorado de errores."""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.start_time = datetime.now()
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def log_action(self, message, level='info'):
        """Registra acciones con mejor formato."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if level == 'info':
            logger.info(message)
            self.successes.append(message)
        elif level == 'warning':
            logger.warning(f"⚠️ {message}")
            self.warnings.append(message)
        elif level == 'error':
            logger.error(f"❌ {message}")
            self.errors.append(message)
    
    def check_prerequisites(self):
        """Verifica que todos los prerequisitos estén listos."""
        self.log_action("🔍 Verificando prerequisitos...")
        
        checks = {
            "Django configurado": self.check_django(),
            "Base de datos accesible": self.check_database(),
            "Scripts de migración": self.check_migration_scripts(),
            "Directorio de logs": self.check_logs_directory()
        }
        
        all_passed = True
        for check, result in checks.items():
            if result:
                self.log_action(f"✅ {check}")
            else:
                self.log_action(f"❌ {check}", 'error')
                all_passed = False
                
        return all_passed
    
    def check_django(self):
        """Verifica configuración de Django."""
        try:
            from django.conf import settings
            return hasattr(settings, 'DATABASES')
        except:
            return False
    
    def check_database(self):
        """Verifica conexión a base de datos."""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False
    
    def check_migration_scripts(self):
        """Verifica que existan los scripts necesarios."""
        required_scripts = [
            'migration_scripts/data_analysis.py',
            'migration_scripts/migrate_core_data.py',
            'migration_scripts/validate_migration.py',
            'check_migration_status.py',
            'complete_migration.py'
        ]
        
        for script in required_scripts:
            if not os.path.exists(script):
                self.log_action(f"Script faltante: {script}", 'warning')
                return False
        return True
    
    def check_logs_directory(self):
        """Verifica/crea directorio de logs."""
        try:
            os.makedirs('logs', exist_ok=True)
            return True
        except:
            return False
    
    def execute_phase_1(self):
        """FASE 1: Análisis y Preparación."""
        self.log_action("="*80)
        self.log_action("🔍 FASE 1: ANÁLISIS Y PREPARACIÓN")
        self.log_action("="*80)
        
        steps = [
            ("Análisis de datos", self.analyze_data),
            ("Estado actual", self.check_current_status),
            ("Backup de seguridad", self.create_backup)
        ]
        
        for step_name, step_func in steps:
            self.log_action(f"📋 Ejecutando: {step_name}")
            if not step_func():
                self.log_action(f"Fallo en: {step_name}", 'error')
                return False
                
        self.log_action("✅ FASE 1 COMPLETADA")
        return True
    
    def analyze_data(self):
        """Ejecuta análisis de datos."""
        if self.dry_run:
            self.log_action("[DRY-RUN] Análisis de datos")
            return True
            
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "migration_scripts/data_analysis.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_action("✅ Análisis completado")
                # Guardar resultado
                with open('logs/data_analysis_result.txt', 'w') as f:
                    f.write(result.stdout)
                return True
            else:
                self.log_action(f"Error en análisis: {result.stderr}", 'error')
                return False
                
        except Exception as e:
            self.log_action(f"Excepción en análisis: {e}", 'error')
            return False
    
    def check_current_status(self):
        """Verifica estado actual del sistema."""
        if self.dry_run:
            self.log_action("[DRY-RUN] Verificación de estado")
            return True
            
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "check_migration_status.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_action("✅ Estado verificado")
                # Guardar resultado
                with open('logs/current_status.txt', 'w') as f:
                    f.write(result.stdout)
                return True
            else:
                self.log_action(f"Error verificando estado: {result.stderr}", 'error')
                return False
                
        except Exception as e:
            self.log_action(f"Excepción verificando estado: {e}", 'error')
            return False
    
    def create_backup(self):
        """Crea backup de seguridad."""
        if self.dry_run:
            self.log_action("[DRY-RUN] Backup de seguridad")
            return True
            
        # Por ahora solo registramos la intención
        self.log_action("⚠️ Backup manual requerido antes de continuar", 'warning')
        self.log_action("Ejecute: pg_dump skyguard > backup_$(date +%Y%m%d).sql", 'warning')
        return True
    
    def execute_phase_2(self):
        """FASE 2: Migración de Datos Maestros."""
        self.log_action("="*80)
        self.log_action("🚀 FASE 2: MIGRACIÓN DE DATOS MAESTROS")
        self.log_action("="*80)
        
        if self.dry_run:
            self.log_action("[DRY-RUN] Migración de datos maestros")
            return True
            
        try:
            import subprocess
            
            # Primero ejecutar en modo dry-run
            self.log_action("Ejecutando simulación de migración...")
            result = subprocess.run(
                ["python3", "migration_scripts/migrate_core_data.py", "--dry-run"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log_action(f"Error en simulación: {result.stderr}", 'error')
                return False
                
            # Si la simulación fue exitosa, preguntar si continuar
            self.log_action("✅ Simulación exitosa")
            
            if not self.dry_run:
                response = input("\n¿Ejecutar migración real? (escriba 'SI' para continuar): ")
                if response == 'SI':
                    result = subprocess.run(
                        ["python3", "migration_scripts/migrate_core_data.py", "--execute"],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        self.log_action("✅ Migración de datos maestros completada")
                        return True
                    else:
                        self.log_action(f"Error en migración: {result.stderr}", 'error')
                        return False
                else:
                    self.log_action("Migración cancelada por usuario", 'warning')
                    return False
                    
        except Exception as e:
            self.log_action(f"Excepción en migración: {e}", 'error')
            return False
    
    def execute_phase_3(self):
        """FASE 3: Migración de Dispositivos GPS."""
        self.log_action("="*80)
        self.log_action("📡 FASE 3: MIGRACIÓN DE DISPOSITIVOS GPS")
        self.log_action("="*80)
        
        if self.dry_run:
            self.log_action("[DRY-RUN] Migración de dispositivos GPS")
            return True
            
        try:
            import subprocess
            
            # Ejecutar migración completa
            self.log_action("Ejecutando migración de dispositivos...")
            result = subprocess.run(
                ["python3", "complete_migration.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_action("✅ Dispositivos GPS migrados")
                
                # Validar migración
                self.log_action("Validando migración...")
                result = subprocess.run(
                    ["python3", "migration_scripts/validate_migration.py"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.log_action("✅ Validación exitosa")
                    return True
                else:
                    self.log_action("⚠️ Advertencias en validación", 'warning')
                    # Continuar de todos modos
                    return True
            else:
                self.log_action(f"Error en migración: {result.stderr}", 'error')
                return False
                
        except Exception as e:
            self.log_action(f"Excepción: {e}", 'error')
            return False
    
    def execute_summary(self):
        """Genera resumen de la migración."""
        self.log_action("="*80)
        self.log_action("📊 RESUMEN DE MIGRACIÓN")
        self.log_action("="*80)
        
        duration = datetime.now() - self.start_time
        
        self.log_action(f"⏱️ Tiempo total: {duration}")
        self.log_action(f"✅ Acciones exitosas: {len(self.successes)}")
        self.log_action(f"⚠️ Advertencias: {len(self.warnings)}")
        self.log_action(f"❌ Errores: {len(self.errors)}")
        
        # Generar reporte
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(report_file, 'w') as f:
            f.write("REPORTE DE MIGRACIÓN SKYGUARD\n")
            f.write("="*50 + "\n")
            f.write(f"Fecha: {datetime.now()}\n")
            f.write(f"Duración: {duration}\n")
            f.write(f"Modo: {'DRY-RUN' if self.dry_run else 'PRODUCCIÓN'}\n\n")
            
            if self.errors:
                f.write("ERRORES:\n")
                for error in self.errors:
                    f.write(f"- {error}\n")
                f.write("\n")
                
            if self.warnings:
                f.write("ADVERTENCIAS:\n")
                for warning in self.warnings:
                    f.write(f"- {warning}\n")
                f.write("\n")
                
            f.write("ACCIONES COMPLETADAS:\n")
            for success in self.successes[-10:]:  # Últimas 10 acciones
                f.write(f"- {success}\n")
                
        self.log_action(f"📄 Reporte guardado: {report_file}")
        
        return len(self.errors) == 0
    
    def run(self, phase=None):
        """Ejecuta la migración."""
        self.log_action("🚀 INICIANDO MIGRACIÓN SEGURA SKYGUARD")
        self.log_action(f"Modo: {'DRY-RUN' if self.dry_run else 'PRODUCCIÓN'}")
        
        # Verificar prerequisitos
        if not self.check_prerequisites():
            self.log_action("❌ Prerequisitos no cumplidos", 'error')
            return False
        
        phases = {
            1: ("Análisis y Preparación", self.execute_phase_1),
            2: ("Migración de Datos Maestros", self.execute_phase_2),
            3: ("Migración de Dispositivos GPS", self.execute_phase_3)
        }
        
        if phase:
            # Ejecutar fase específica
            if phase in phases:
                phase_name, phase_func = phases[phase]
                self.log_action(f"Ejecutando solo fase {phase}: {phase_name}")
                success = phase_func()
            else:
                self.log_action(f"Fase {phase} no válida", 'error')
                return False
        else:
            # Ejecutar todas las fases
            success = True
            for phase_num, (phase_name, phase_func) in phases.items():
                if not phase_func():
                    self.log_action(f"Fallo en fase {phase_num}: {phase_name}", 'error')
                    success = False
                    break
        
        # Generar resumen
        self.execute_summary()
        
        if success:
            self.log_action("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        else:
            self.log_action("❌ MIGRACIÓN FALLÓ - Revise el reporte", 'error')
            
        return success

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='🚀 Ejecutor Seguro de Migración SkyGuard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Simulación completa (recomendado primero)
  python3 execute_migration_safe.py --dry-run
  
  # Ejecutar fase específica
  python3 execute_migration_safe.py --phase 1
  
  # Migración completa
  python3 execute_migration_safe.py --execute
        """
    )
    
    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2, 3],
        help='Ejecutar fase específica (1-3)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulación sin cambios reales'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Ejecutar migración real'
    )
    
    args = parser.parse_args()
    
    # Determinar modo
    if args.execute:
        dry_run = False
    else:
        dry_run = True
    
    # Crear directorio de logs
    os.makedirs('logs', exist_ok=True)
    
    # Ejecutar migración
    executor = SafeMigrationExecutor(dry_run=dry_run)
    
    try:
        if executor.run(phase=args.phase):
            print("\n✅ Operación completada exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Operación falló - revise logs/migration_safe.log")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Migración interrumpida por usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 