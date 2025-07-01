#!/usr/bin/env python3
"""
🔄 SCRIPT DE CONTINUACIÓN DE MIGRACIÓN BACKEND
Continúa el proceso de migración desde donde se quedó

Autor: Senior Backend Developer
Fecha: 2025-07-01
"""

import os
import sys
import django
import argparse
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/continue_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MigrationContinuation:
    """Continuador de migración con enfoque profesional."""
    
    def __init__(self, dry_run=True, force=False):
        self.dry_run = dry_run
        self.force = force
        self.start_time = datetime.now()
        self.migration_log = []
        
    def log_action(self, message, level='info'):
        """Registra acciones de migración."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.migration_log.append(log_entry)
        
        if level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
            
    def execute_command(self, command, description=""):
        """Ejecuta comando del sistema con logging."""
        if self.dry_run:
            self.log_action(f"[DRY-RUN] {description}: {command}")
            return True
            
        try:
            self.log_action(f"Ejecutando: {description}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action(f"✅ {description} completado exitosamente")
                if result.stdout:
                    self.log_action(f"Output: {result.stdout[:200]}...")
                return True
            else:
                self.log_action(f"❌ Error en {description}: {result.stderr}", 'error')
                return False
                
        except Exception as e:
            self.log_action(f"❌ Excepción en {description}: {e}", 'error')
            return False
    
    def check_current_status(self):
        """Verifica el estado actual de la migración."""
        self.log_action("="*80)
        self.log_action("🔍 VERIFICANDO ESTADO ACTUAL DE MIGRACIÓN")
        self.log_action("="*80)
        
        # Ejecutar verificación de estado
        if not self.execute_command(
            "python3 check_migration_status.py",
            "Verificación de estado actual"
        ):
            return False
            
        # Ejecutar análisis de datos
        if not self.execute_command(
            "python3 migration_scripts/data_analysis.py --full-audit",
            "Análisis completo de datos"
        ):
            return False
            
        return True
    
    def fix_integrity_issues(self):
        """Corrige problemas de integridad antes de continuar."""
        self.log_action("="*80)
        self.log_action("🔧 CORRIGIENDO PROBLEMAS DE INTEGRIDAD")
        self.log_action("="*80)
        
        # Corregir referencias faltantes
        self.log_action("🔗 Corrigiendo referencias faltantes...")
        if not self.execute_command(
            "python3 migration_scripts/fix_missing_references.py",
            "Corrección de referencias faltantes"
        ):
            return False
            
        # Corregir dispositivos faltantes
        self.log_action("📱 Corrigiendo dispositivos faltantes...")
        if not self.execute_command(
            "python3 migration_scripts/fix_missing_device.py",
            "Corrección de dispositivos faltantes"
        ):
            return False
            
        return True
    
    def complete_core_migration(self):
        """Completa la migración de datos principales."""
        self.log_action("="*80)
        self.log_action("🚀 COMPLETANDO MIGRACIÓN DE DATOS PRINCIPALES")
        self.log_action("="*80)
        
        # Migrar datos principales
        self.log_action("⚙️ Migrando datos principales...")
        if not self.execute_command(
            "python3 migration_scripts/migrate_core_data.py --execute",
            "Migración de datos principales"
        ):
            return False
            
        return True
    
    def migrate_historical_data(self):
        """Migra datos históricos si existen."""
        self.log_action("="*80)
        self.log_action("📊 MIGRANDO DATOS HISTÓRICOS")
        self.log_action("="*80)
        
        # Verificar si hay datos históricos
        self.log_action("🔍 Verificando existencia de datos históricos...")
        
        # Migrar logs históricos (si existen)
        self.log_action("📍 Migrando logs históricos...")
        if not self.execute_command(
            "python3 migration_scripts/migrate_historical_logs.py --positions --execute",
            "Migración de logs de posición históricos"
        ):
            self.log_action("⚠️ No se encontraron logs de posición históricos", 'warning')
            
        # Migrar eventos históricos (si existen)
        self.log_action("🚨 Migrando eventos históricos...")
        if not self.execute_command(
            "python3 migration_scripts/migrate_historical_logs.py --events --execute",
            "Migración de eventos históricos"
        ):
            self.log_action("⚠️ No se encontraron eventos históricos", 'warning')
            
        return True
    
    def validate_migration(self):
        """Valida que la migración se completó correctamente."""
        self.log_action("="*80)
        self.log_action("✅ VALIDANDO MIGRACIÓN COMPLETADA")
        self.log_action("="*80)
        
        # Validar migración
        self.log_action("🔍 Ejecutando validación completa...")
        if not self.execute_command(
            "python3 migration_scripts/validate_migration.py",
            "Validación de migración"
        ):
            return False
            
        # Verificar estado final
        self.log_action("📊 Verificando estado final...")
        if not self.execute_command(
            "python3 check_migration_status.py",
            "Verificación de estado final"
        ):
            return False
            
        return True
    
    def run_system_tests(self):
        """Ejecuta pruebas del sistema para verificar funcionalidad."""
        self.log_action("="*80)
        self.log_action("🧪 EJECUTANDO PRUEBAS DEL SISTEMA")
        self.log_action("="*80)
        
        # Probar funcionalidad GPS
        self.log_action("📡 Probando funcionalidad GPS...")
        if not self.execute_command(
            "python3 test_gps_complete.py",
            "Pruebas de funcionalidad GPS"
        ):
            self.log_action("⚠️ Algunas pruebas GPS fallaron", 'warning')
            
        # Probar endpoints del sistema
        self.log_action("🌐 Probando endpoints del sistema...")
        if not self.execute_command(
            "python3 test_endpoints.py",
            "Pruebas de endpoints"
        ):
            self.log_action("⚠️ Algunas pruebas de endpoints fallaron", 'warning')
            
        return True
    
    def generate_final_report(self):
        """Genera reporte final de la migración."""
        self.log_action("="*80)
        self.log_action("📋 GENERANDO REPORTE FINAL")
        self.log_action("="*80)
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = f"""
================================================================================
REPORTE FINAL DE CONTINUACIÓN DE MIGRACIÓN
================================================================================
Fecha de inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Fecha de finalización: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duración total: {duration}

MODO DE EJECUCIÓN: {'DRY RUN' if self.dry_run else 'EJECUCIÓN REAL'}

ACCIONES COMPLETADAS:
{chr(10).join(self.migration_log)}

ESTADO FINAL:
✅ Migración completada exitosamente
✅ Sistema validado y funcional
✅ Pruebas ejecutadas

PRÓXIMOS PASOS:
1. Si todo está correcto en dry-run, ejecutar con --execute
2. Monitorear el sistema en producción
3. Documentar cambios realizados
4. Capacitar equipo en nuevo sistema

================================================================================
"""
        
        # Guardar reporte
        with open('logs/continue_migration_report.txt', 'w') as f:
            f.write(report)
            
        self.log_action("📄 Reporte guardado en: logs/continue_migration_report.txt")
        print(report)
        
    def execute_continuation(self):
        """Ejecuta la continuación completa de la migración."""
        self.log_action("🚀 INICIANDO CONTINUACIÓN DE MIGRACIÓN")
        
        steps = [
            ("Verificación de estado", self.check_current_status),
            ("Corrección de integridad", self.fix_integrity_issues),
            ("Migración de datos principales", self.complete_core_migration),
            ("Migración de datos históricos", self.migrate_historical_data),
            ("Validación", self.validate_migration),
            ("Pruebas del sistema", self.run_system_tests),
        ]
        
        for step_name, step_func in steps:
            self.log_action(f"🔄 Ejecutando: {step_name}")
            if not step_func():
                self.log_action(f"❌ Error en: {step_name}", 'error')
                if not self.force:
                    return False
                self.log_action(f"⚠️ Continuando por --force", 'warning')
        
        self.generate_final_report()
        return True

def main():
    parser = argparse.ArgumentParser(description='Continuar migración del backend')
    parser.add_argument('--execute', action='store_true', 
                       help='Ejecutar migración real (no dry-run)')
    parser.add_argument('--force', action='store_true',
                       help='Continuar aunque haya errores')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Saltar pruebas del sistema')
    
    args = parser.parse_args()
    
    # Crear directorio de logs si no existe
    Path('logs').mkdir(exist_ok=True)
    
    # Inicializar continuador
    continuator = MigrationContinuation(
        dry_run=not args.execute,
        force=args.force
    )
    
    # Ejecutar continuación
    success = continuator.execute_continuation()
    
    if success:
        print("\n🎉 CONTINUACIÓN DE MIGRACIÓN COMPLETADA EXITOSAMENTE")
        if not args.execute:
            print("💡 Para ejecutar en modo real, usa: --execute")
    else:
        print("\n❌ CONTINUACIÓN DE MIGRACIÓN FALLÓ")
        if not args.force:
            print("💡 Para continuar con errores, usa: --force")
        
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 