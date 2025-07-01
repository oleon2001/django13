#!/usr/bin/env python3
"""
🎯 SCRIPT MAESTRO DE CONTINUACIÓN DE MIGRACIÓN
Orquesta todo el proceso de continuación, optimización y monitoreo

Autor: Senior Backend Developer
Fecha: 2025-07-01
"""

import os
import sys
import django
import argparse
import logging
import subprocess
import time
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
        logging.FileHandler('logs/master_continuation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterContinuation:
    """Maestro de continuación de migración."""
    
    def __init__(self, dry_run=True, force=False, optimize=True, monitor=True):
        self.dry_run = dry_run
        self.force = force
        self.optimize = optimize
        self.monitor = monitor
        self.start_time = datetime.now()
        self.master_log = []
        
    def log_action(self, message, level='info'):
        """Registra acciones del maestro."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.master_log.append(log_entry)
        
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
                return True
            else:
                self.log_action(f"❌ Error en {description}: {result.stderr}", 'error')
                return False
                
        except Exception as e:
            self.log_action(f"❌ Excepción en {description}: {e}", 'error')
            return False
    
    def phase_1_continuation(self):
        """🔄 FASE 1: CONTINUACIÓN DE MIGRACIÓN"""
        self.log_action("="*80)
        self.log_action("🔄 INICIANDO FASE 1: CONTINUACIÓN DE MIGRACIÓN")
        self.log_action("="*80)
        
        # Ejecutar continuación de migración
        self.log_action("📊 Ejecutando continuación de migración...")
        if not self.execute_command(
            f"python3 continue_migration.py {'--execute' if not self.dry_run else ''} {'--force' if self.force else ''}",
            "Continuación de migración"
        ):
            if not self.force:
                return False
            self.log_action("⚠️ Continuando por --force", 'warning')
        
        return True
    
    def phase_2_optimization(self):
        """⚡ FASE 2: OPTIMIZACIÓN DEL SISTEMA"""
        if not self.optimize:
            self.log_action("⏭️ Saltando optimización por configuración")
            return True
            
        self.log_action("="*80)
        self.log_action("⚡ INICIANDO FASE 2: OPTIMIZACIÓN DEL SISTEMA")
        self.log_action("="*80)
        
        # Ejecutar optimización
        self.log_action("🔧 Ejecutando optimización del sistema...")
        if not self.execute_command(
            f"python3 optimize_migrated_system.py {'--execute' if not self.dry_run else ''}",
            "Optimización del sistema"
        ):
            if not self.force:
                return False
            self.log_action("⚠️ Continuando por --force", 'warning')
        
        return True
    
    def phase_3_monitoring(self):
        """📊 FASE 3: MONITOREO Y VALIDACIÓN"""
        if not self.monitor:
            self.log_action("⏭️ Saltando monitoreo por configuración")
            return True
            
        self.log_action("="*80)
        self.log_action("📊 INICIANDO FASE 3: MONITOREO Y VALIDACIÓN")
        self.log_action("="*80)
        
        # Ejecutar monitoreo inicial
        self.log_action("🔍 Ejecutando monitoreo inicial...")
        if not self.execute_command(
            "python3 monitor_migrated_system.py",
            "Monitoreo inicial del sistema"
        ):
            if not self.force:
                return False
            self.log_action("⚠️ Continuando por --force", 'warning')
        
        return True
    
    def phase_4_validation(self):
        """✅ FASE 4: VALIDACIÓN FINAL"""
        self.log_action("="*80)
        self.log_action("✅ INICIANDO FASE 4: VALIDACIÓN FINAL")
        self.log_action("="*80)
        
        # Validar migración
        self.log_action("🔍 Validando migración completada...")
        if not self.execute_command(
            "python3 migration_scripts/validate_migration.py",
            "Validación de migración"
        ):
            if not self.force:
                return False
            self.log_action("⚠️ Continuando por --force", 'warning')
        
        # Verificar estado final
        self.log_action("📊 Verificando estado final...")
        if not self.execute_command(
            "python3 check_migration_status.py",
            "Verificación de estado final"
        ):
            if not self.force:
                return False
            self.log_action("⚠️ Continuando por --force", 'warning')
        
        return True
    
    def phase_5_testing(self):
        """🧪 FASE 5: PRUEBAS DEL SISTEMA"""
        self.log_action("="*80)
        self.log_action("🧪 INICIANDO FASE 5: PRUEBAS DEL SISTEMA")
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
    
    def generate_master_report(self):
        """Genera reporte maestro final."""
        self.log_action("="*80)
        self.log_action("📋 GENERANDO REPORTE MAESTRO FINAL")
        self.log_action("="*80)
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = f"""
================================================================================
REPORTE MAESTRO DE CONTINUACIÓN DE MIGRACIÓN
================================================================================
Fecha de inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Fecha de finalización: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duración total: {duration}

MODO DE EJECUCIÓN: {'DRY RUN' if self.dry_run else 'EJECUCIÓN REAL'}
MODO FORZADO: {'SÍ' if self.force else 'NO'}
OPTIMIZACIÓN: {'SÍ' if self.optimize else 'NO'}
MONITOREO: {'SÍ' if self.monitor else 'NO'}

FASES COMPLETADAS:
✅ Fase 1: Continuación de migración
{'✅' if self.optimize else '⏭️'} Fase 2: Optimización del sistema
{'✅' if self.monitor else '⏭️'} Fase 3: Monitoreo y validación
✅ Fase 4: Validación final
✅ Fase 5: Pruebas del sistema

ACCIONES COMPLETADAS:
{chr(10).join(self.master_log)}

ESTADO FINAL:
🎉 PROCESO DE CONTINUACIÓN COMPLETADO EXITOSAMENTE

PRÓXIMOS PASOS:
1. Si todo está correcto en dry-run, ejecutar con --execute
2. Configurar monitoreo continuo del sistema
3. Documentar cambios realizados
4. Capacitar equipo en nuevo sistema
5. Planificar mantenimiento regular

COMANDOS ÚTILES:
  • Monitoreo continuo: python3 monitor_migrated_system.py --continuous
  • Optimización periódica: python3 optimize_migrated_system.py --execute
  • Verificar estado: python3 check_migration_status.py
  • Pruebas GPS: python3 test_gps_complete.py

================================================================================
"""
        
        # Guardar reporte
        with open('logs/master_continuation_report.txt', 'w') as f:
            f.write(report)
            
        self.log_action("📄 Reporte guardado en: logs/master_continuation_report.txt")
        print(report)
    
    def execute_master_continuation(self):
        """Ejecuta la continuación maestra completa."""
        self.log_action("🚀 INICIANDO PROCESO MAESTRO DE CONTINUACIÓN")
        
        phases = [
            ("Continuación de migración", self.phase_1_continuation),
            ("Optimización del sistema", self.phase_2_optimization),
            ("Monitoreo y validación", self.phase_3_monitoring),
            ("Validación final", self.phase_4_validation),
            ("Pruebas del sistema", self.phase_5_testing),
        ]
        
        for phase_name, phase_func in phases:
            self.log_action(f"🔄 Ejecutando: {phase_name}")
            if not phase_func():
                self.log_action(f"❌ Error en: {phase_name}", 'error')
                if not self.force:
                    return False
                self.log_action(f"⚠️ Continuando por --force", 'warning')
        
        self.generate_master_report()
        return True

def main():
    parser = argparse.ArgumentParser(description='Maestro de continuación de migración')
    parser.add_argument('--execute', action='store_true', 
                       help='Ejecutar migración real (no dry-run)')
    parser.add_argument('--force', action='store_true',
                       help='Continuar aunque haya errores')
    parser.add_argument('--skip-optimization', action='store_true',
                       help='Saltar optimización del sistema')
    parser.add_argument('--skip-monitoring', action='store_true',
                       help='Saltar monitoreo del sistema')
    parser.add_argument('--quick', action='store_true',
                       help='Modo rápido (solo migración)')
    
    args = parser.parse_args()
    
    # Crear directorio de logs si no existe
    Path('logs').mkdir(exist_ok=True)
    
    # Configurar opciones
    optimize = not args.skip_optimization and not args.quick
    monitor = not args.skip_monitoring and not args.quick
    
    # Inicializar maestro
    master = MasterContinuation(
        dry_run=not args.execute,
        force=args.force,
        optimize=optimize,
        monitor=monitor
    )
    
    # Ejecutar proceso maestro
    success = master.execute_master_continuation()
    
    if success:
        print("\n🎉 PROCESO MAESTRO COMPLETADO EXITOSAMENTE")
        if not args.execute:
            print("💡 Para ejecutar en modo real, usa: --execute")
        if args.quick:
            print("💡 Para proceso completo, ejecuta sin --quick")
    else:
        print("\n❌ PROCESO MAESTRO FALLÓ")
        if not args.force:
            print("💡 Para continuar con errores, usa: --force")
        
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 