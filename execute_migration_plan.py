#!/usr/bin/env python3
"""
 SCRIPT MAESTRO DE MIGRACIÓN BACKEND LEGACY → NUEVO
Ejecutor principal del plan de migración completo de SkyGuard

Autor: El mejor desarrollador de software de la historia

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
        logging.FileHandler('logs/migration_master.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MigrationExecutor:
    """Ejecutor principal de la migración."""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
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
                return True
            else:
                self.log_action(f"❌ Error en {description}: {result.stderr}", 'error')
                return False
                
        except Exception as e:
            self.log_action(f"❌ Excepción en {description}: {e}", 'error')
            return False
    
    def phase_1_analysis_preparation(self):
        """🔍 FASE 1: ANÁLISIS Y PREPARACIÓN"""
        self.log_action("="*80)
        self.log_action("🔍 INICIANDO FASE 1: ANÁLISIS Y PREPARACIÓN")
        self.log_action("="*80)
        
        # 1.1 Auditoría de datos legacy
        self.log_action("📊 1.1 Ejecutando auditoría completa de datos legacy...")
        if not self.execute_command(
            "python3 migration_scripts/data_analysis.py --full-audit",
            "Auditoría de datos legacy"
        ):
            return False
            
        # 1.2 Generar inventario
        self.log_action("📋 1.2 Generando inventario detallado...")
        if not self.execute_command(
            "python3 check_migration_status.py > migration_inventory_$(date +%Y%m%d_%H%M).txt",
            "Generación de inventario"
        ):
            return False
            
        # 1.3 Backup completo
        self.log_action("💾 1.3 Creando backup completo del sistema legacy...")
        if not self.execute_command(
            "pg_dump skyguard > backup_legacy_$(date +%Y%m%d_%H%M).sql",
            "Backup de base de datos legacy"
        ):
            return False
            
        # 1.4 Preparar entorno
        self.log_action("🛠️ 1.4 Preparando entorno de migración...")
        commands = [
            ("python3 manage.py migrate", "Migración de esquema de BD"),
            ("python3 manage.py collectstatic --noinput", "Recolección de archivos estáticos"),
        ]
        
        for command, description in commands:
            if not self.execute_command(command, description):
                return False
                
        self.log_action("✅ FASE 1 COMPLETADA EXITOSAMENTE")
        return True
    
    def phase_2_master_data_migration(self):
        """🚀 FASE 2: MIGRACIÓN DE DATOS MAESTROS"""
        self.log_action("="*80)
        self.log_action("🚀 INICIANDO FASE 2: MIGRACIÓN DE DATOS MAESTROS")
        self.log_action("="*80)
        
        # Migrar todos los datos maestros con un solo comando
        self.log_action("⚙️ Migrando datos maestros (SIM Cards, Harnesses, Dispositivos, Geocercas)...")
        if not self.execute_command(
            "python3 migration_scripts/migrate_core_data.py --execute",
            "Migración de datos maestros completa"
        ):
            return False
            
        self.log_action("✅ FASE 2 COMPLETADA EXITOSAMENTE")
        return True
    
    def phase_3_gps_devices_migration(self):
        """📡 FASE 3: MIGRACIÓN DE DISPOSITIVOS GPS"""
        self.log_action("="*80)
        self.log_action("📡 INICIANDO FASE 3: MIGRACIÓN DE DISPOSITIVOS GPS")
        self.log_action("="*80)
        
        # 3.1 Migrar dispositivos GPS
        self.log_action("🚗 3.1 Migrando dispositivos GPS...")
        if not self.execute_command(
            "python3 complete_migration.py",
            "Migración de dispositivos GPS"
        ):
            return False
            
        # 3.2 Validar migración de dispositivos
        self.log_action("🔧 3.2 Validando migración de dispositivos...")
        if not self.execute_command(
            "python3 migration_scripts/validate_migration.py",
            "Validación de dispositivos migrados"
        ):
            return False
            
        self.log_action("✅ FASE 3 COMPLETADA EXITOSAMENTE")
        return True
    
    def phase_4_historical_data_migration(self):
        """📊 FASE 4: MIGRACIÓN DE DATOS HISTÓRICOS"""
        self.log_action("="*80)
        self.log_action("📊 INICIANDO FASE 4: MIGRACIÓN DE DATOS HISTÓRICOS")
        self.log_action("="*80)
        
        # 4.1 Migrar logs históricos
        self.log_action("📍 4.1 Migrando logs de posición históricos...")
        if not self.execute_command(
            "python3 migration_scripts/migrate_historical_logs.py --positions",
            "Migración de logs de posición"
        ):
            return False
            
        # 4.2 Migrar eventos y alarmas
        self.log_action("🚨 4.2 Migrando eventos y alarmas...")
        if not self.execute_command(
            "python3 migration_scripts/migrate_historical_logs.py --events",
            "Migración de eventos y alarmas"
        ):
            return False
            
        # 4.3 Migrar reportes
        self.log_action("📈 4.3 Migrando reportes y estadísticas...")
        if not self.execute_command(
            "python3 migration_scripts/migrate_historical_logs.py --reports",
            "Migración de reportes"
        ):
            return False
            
        self.log_action("✅ FASE 4 COMPLETADA EXITOSAMENTE")
        return True
    
    def phase_5_validation_testing(self):
        """✅ FASE 5: VALIDACIÓN Y PRUEBAS"""
        self.log_action("="*80)
        self.log_action("✅ INICIANDO FASE 5: VALIDACIÓN Y PRUEBAS")
        self.log_action("="*80)
        
        # 5.1 Validación de integridad
        self.log_action("🔍 5.1 Ejecutando validación de integridad...")
        if not self.execute_command(
            "python3 migration_scripts/validate_migration.py --full",
            "Validación completa de integridad"
        ):
            return False
            
        # 5.2 Pruebas funcionales
        self.log_action("🧪 5.2 Ejecutando pruebas funcionales...")
        if not self.execute_command(
            "python3 manage.py test skyguard.apps.gps.tests",
            "Pruebas funcionales"
        ):
            return False
            
        # 5.3 Verificar estado final
        self.log_action("⚡ 5.3 Verificando estado final del sistema...")
        if not self.execute_command(
            "python3 check_migration_status.py",
            "Verificación del estado final"
        ):
            return False
            
        self.log_action("✅ FASE 5 COMPLETADA EXITOSAMENTE")
        return True
    
    def phase_6_transition_production(self):
        """🎯 FASE 6: TRANSICIÓN Y PUESTA EN PRODUCCIÓN"""
        self.log_action("="*80)
        self.log_action("🎯 INICIANDO FASE 6: TRANSICIÓN Y PRODUCCIÓN")
        self.log_action("="*80)
        
        # 6.1 Configurar servicios
        self.log_action("🔧 6.1 Configurando servicios de producción...")
        commands = [
            ("sudo systemctl restart nginx", "Reinicio de Nginx"),
            ("sudo systemctl restart gunicorn", "Reinicio de Gunicorn"),
            ("sudo systemctl restart celery", "Reinicio de Celery"),
        ]
        
        for command, description in commands:
            if not self.execute_command(command, description):
                return False
                
        # 6.2 Verificación final del sistema
        self.log_action("📊 6.2 Ejecutando verificación final completa...")
        if not self.execute_command(
            "python3 check_migration_status.py",
            "Verificación final del sistema"
        ):
            return False
            
        self.log_action("✅ FASE 6 COMPLETADA EXITOSAMENTE")
        return True
    
    def execute_full_migration(self):
        """Ejecuta la migración completa."""
        self.log_action("🚀 INICIANDO MIGRACIÓN COMPLETA BACKEND LEGACY → NUEVO")
        self.log_action(f"Modo: {'DRY-RUN' if self.dry_run else 'EJECUCIÓN REAL'}")
        self.log_action("="*80)
        
        phases = [
            ("FASE 1", self.phase_1_analysis_preparation),
            ("FASE 2", self.phase_2_master_data_migration),
            ("FASE 3", self.phase_3_gps_devices_migration),
            ("FASE 4", self.phase_4_historical_data_migration),
            ("FASE 5", self.phase_5_validation_testing),
            ("FASE 6", self.phase_6_transition_production),
        ]
        
        for phase_name, phase_function in phases:
            try:
                if not phase_function():
                    self.log_action(f"❌ FALLA EN {phase_name} - DETENIENDO MIGRACIÓN", 'error')
                    return False
            except Exception as e:
                self.log_action(f"❌ EXCEPCIÓN EN {phase_name}: {e}", 'error')
                return False
        
        # Resumen final
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        self.log_action("="*80)
        self.log_action("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        self.log_action("="*80)
        self.log_action(f"⏱️ Tiempo total: {duration}")
        self.log_action(f"📊 Total de acciones: {len(self.migration_log)}")
        
        # Generar reporte final
        self.generate_final_report()
        
        return True
    
    def execute_phase(self, phase_number):
        """Ejecuta una fase específica."""
        phases = {
            1: ("ANÁLISIS Y PREPARACIÓN", self.phase_1_analysis_preparation),
            2: ("MIGRACIÓN DE DATOS MAESTROS", self.phase_2_master_data_migration),
            3: ("MIGRACIÓN DE DISPOSITIVOS GPS", self.phase_3_gps_devices_migration),
            4: ("MIGRACIÓN DE DATOS HISTÓRICOS", self.phase_4_historical_data_migration),
            5: ("VALIDACIÓN Y PRUEBAS", self.phase_5_validation_testing),
            6: ("TRANSICIÓN Y PRODUCCIÓN", self.phase_6_transition_production),
        }
        
        if phase_number not in phases:
            self.log_action(f"❌ Fase {phase_number} no válida", 'error')
            return False
            
        phase_name, phase_function = phases[phase_number]
        self.log_action(f"🚀 EJECUTANDO FASE {phase_number}: {phase_name}")
        
        try:
            return phase_function()
        except Exception as e:
            self.log_action(f"❌ Error en Fase {phase_number}: {e}", 'error')
            return False
    
    def execute_rollback(self):
        """Ejecuta rollback de la migración."""
        self.log_action("🔄 INICIANDO ROLLBACK DE MIGRACIÓN")
        self.log_action("="*80)
        
        # Encontrar backup más reciente
        backup_files = list(Path('.').glob('backup_legacy_*.sql'))
        if not backup_files:
            self.log_action("❌ No se encontraron archivos de backup", 'error')
            return False
            
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        
        # Restaurar backup
        if not self.execute_command(
            f"psql skyguard < {latest_backup}",
            f"Restauración desde {latest_backup}"
        ):
            return False
            
        # Revertir configuraciones
        rollback_commands = [
            ("git checkout HEAD -- skyguard/settings/", "Revertir configuraciones"),
            ("python3 manage.py migrate --fake-initial", "Revertir migraciones"),
        ]
        
        for command, description in rollback_commands:
            if not self.execute_command(command, description):
                return False
                
        self.log_action("✅ ROLLBACK COMPLETADO EXITOSAMENTE")
        return True
    
    def generate_final_report(self):
        """Genera reporte final de migración."""
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        
        with open(report_file, 'w') as f:
            f.write("🚀 REPORTE FINAL DE MIGRACIÓN SKYGUARD\n")
            f.write("="*80 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duración: {datetime.now() - self.start_time}\n")
            f.write(f"Modo: {'DRY-RUN' if self.dry_run else 'EJECUCIÓN REAL'}\n")
            f.write("\n")
            
            f.write("📋 LOG DE ACCIONES:\n")
            f.write("-" * 50 + "\n")
            for log_entry in self.migration_log:
                f.write(f"{log_entry}\n")
                
        self.log_action(f"📄 Reporte generado: {report_file}")

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='🚀 Ejecutor Maestro de Migración SkyGuard Legacy → Nuevo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Migración completa
  python3 execute_migration_plan.py
  
  # Ejecutar fase específica
  python3 execute_migration_plan.py --phase 1
  
  # Simulación (dry-run)
  python3 execute_migration_plan.py --dry-run
  
  # Rollback
  python3 execute_migration_plan.py --rollback
        """
    )
    
    parser.add_argument(
        '--phase', 
        type=int, 
        choices=[1, 2, 3, 4, 5, 6],
        help='Ejecutar fase específica (1-6)'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Simular migración sin ejecutar cambios reales'
    )
    
    parser.add_argument(
        '--rollback', 
        action='store_true',
        help='Revertir migración al estado anterior'
    )
    
    args = parser.parse_args()
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Inicializar ejecutor
    executor = MigrationExecutor(dry_run=args.dry_run)
    
    try:
        if args.rollback:
            success = executor.execute_rollback()
        elif args.phase:
            success = executor.execute_phase(args.phase)
        else:
            success = executor.execute_full_migration()
            
        if success:
            print("✅ Operación completada exitosamente")
            sys.exit(0)
        else:
            print("❌ Operación falló - revisar logs para detalles")
            sys.exit(1)
            
    except KeyboardInterrupt:
        executor.log_action("⚠️ Migración interrumpida por usuario", 'warning')
        print("\n⚠️ Migración interrumpida")
        sys.exit(130)
    except Exception as e:
        executor.log_action(f"❌ Error inesperado: {e}", 'error')
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()