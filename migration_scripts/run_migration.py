#!/usr/bin/env python3
"""
Script maestro para coordinar todo el proceso de migración.
Ejecuta análisis, migración y validación en el orden correcto.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MigrationOrchestrator:
    """Orquestador principal del proceso de migración."""
    
    def __init__(self, dry_run=True, skip_analysis=False, skip_historical=False):
        self.dry_run = dry_run
        self.skip_analysis = skip_analysis
        self.skip_historical = skip_historical
        self.start_time = datetime.now()
        
        # Rutas de scripts
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.scripts = {
            'analysis': os.path.join(self.script_dir, 'data_analysis.py'),
            'core_migration': os.path.join(self.script_dir, 'migrate_core_data.py'),
            'historical_migration': os.path.join(self.script_dir, 'migrate_historical_logs.py'),
            'validation': os.path.join(self.script_dir, 'validate_migration.py')
        }
        
        # Verificar que todos los scripts existen
        self._verify_scripts()
    
    def _verify_scripts(self):
        """Verifica que todos los scripts necesarios existen."""
        missing_scripts = []
        for name, path in self.scripts.items():
            if not os.path.exists(path):
                missing_scripts.append(f"{name}: {path}")
        
        if missing_scripts:
            logger.error("❌ Scripts faltantes:")
            for script in missing_scripts:
                logger.error(f"   - {script}")
            sys.exit(1)
        
        logger.info("✅ Todos los scripts de migración encontrados")
    
    def _run_script(self, script_name, args=None):
        """Ejecuta un script de migración."""
        script_path = self.scripts[script_name]
        
        # Construir comando
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        logger.info(f"🚀 Ejecutando: {script_name}")
        logger.info(f"   Comando: {' '.join(cmd)}")
        
        try:
            # Ejecutar script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(script_path)
            )
            
            # Log de salida
            if result.stdout:
                logger.info(f"Salida de {script_name}:")
                for line in result.stdout.strip().split('\n'):
                    logger.info(f"   {line}")
            
            if result.stderr:
                logger.warning(f"Errores de {script_name}:")
                for line in result.stderr.strip().split('\n'):
                    logger.warning(f"   {line}")
            
            # Verificar código de salida
            if result.returncode == 0:
                logger.info(f"✅ {script_name} completado exitosamente")
                return True
            else:
                logger.error(f"❌ {script_name} falló con código {result.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando {script_name}: {e}")
            return False
    
    def run_data_analysis(self):
        """Ejecuta el análisis de datos existentes."""
        logger.info("\n" + "="*60)
        logger.info("FASE 1: ANÁLISIS DE DATOS EXISTENTES")
        logger.info("="*60)
        
        if self.skip_analysis:
            logger.info("⏭️  Saltando análisis de datos (--skip-analysis)")
            return True
        
        return self._run_script('analysis')
    
    def run_core_migration(self):
        """Ejecuta la migración de datos principales."""
        logger.info("\n" + "="*60)
        logger.info("FASE 2: MIGRACIÓN DE DATOS PRINCIPALES")
        logger.info("="*60)
        
        args = []
        if self.dry_run:
            args.append('--dry-run')
        else:
            args.append('--execute')
        
        return self._run_script('core_migration', args)
    
    def run_historical_migration(self):
        """Ejecuta la migración de logs históricos."""
        logger.info("\n" + "="*60)
        logger.info("FASE 3: MIGRACIÓN DE LOGS HISTÓRICOS")
        logger.info("="*60)
        
        if self.skip_historical:
            logger.info("⏭️  Saltando migración histórica (--skip-historical)")
            return True
        
        args = []
        if self.dry_run:
            args.append('--dry-run')
        else:
            args.append('--execute')
        
        # Migrar solo los últimos 90 días por defecto para acelerar
        args.extend(['--days', '90'])
        
        return self._run_script('historical_migration', args)
    
    def run_validation(self):
        """Ejecuta la validación de la migración."""
        logger.info("\n" + "="*60)
        logger.info("FASE 4: VALIDACIÓN DE MIGRACIÓN")
        logger.info("="*60)
        
        return self._run_script('validation')
    
    def create_backup_reminder(self):
        """Crea recordatorio sobre backup."""
        logger.info("\n" + "⚠️ "*20)
        logger.info("RECORDATORIO IMPORTANTE: BACKUP DE BASE DE DATOS")
        logger.info("⚠️ "*20)
        logger.info("Antes de ejecutar la migración en producción:")
        logger.info("1. Hacer backup completo de la base de datos")
        logger.info("2. Verificar que el backup se puede restaurar")
        logger.info("3. Tener plan de rollback preparado")
        logger.info("4. Ejecutar primero en ambiente de pruebas")
        logger.info("⚠️ "*20)
    
    def generate_final_report(self, success):
        """Genera reporte final del proceso."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        logger.info("\n" + "="*80)
        logger.info("REPORTE FINAL DE MIGRACIÓN")
        logger.info("="*80)
        logger.info(f"Inicio: {self.start_time}")
        logger.info(f"Fin: {end_time}")
        logger.info(f"Duración total: {duration}")
        logger.info(f"Modo: {'DRY RUN' if self.dry_run else 'PRODUCCIÓN'}")
        
        if self.skip_analysis:
            logger.info("Análisis: SALTADO")
        
        if self.skip_historical:
            logger.info("Migración histórica: SALTADA")
        
        if success:
            logger.info("\n🎉 PROCESO DE MIGRACIÓN COMPLETADO EXITOSAMENTE")
            logger.info("\nPróximos pasos:")
            if self.dry_run:
                logger.info("1. Revisar logs de migración")
                logger.info("2. Ejecutar en modo real: --execute")
                logger.info("3. Validar resultados")
            else:
                logger.info("1. Revisar logs de validación")
                logger.info("2. Probar funcionalidad del nuevo sistema")
                logger.info("3. Monitorear rendimiento")
        else:
            logger.info("\n❌ PROCESO DE MIGRACIÓN FALLÓ")
            logger.info("\nAcciones recomendadas:")
            logger.info("1. Revisar logs de error")
            logger.info("2. Corregir problemas identificados")
            logger.info("3. Re-ejecutar migración")
            if not self.dry_run:
                logger.info("4. Considerar rollback si es necesario")
    
    def run_full_migration(self):
        """Ejecuta el proceso completo de migración."""
        logger.info("🚀 INICIANDO PROCESO MAESTRO DE MIGRACIÓN")
        logger.info(f"Modo: {'DRY RUN' if self.dry_run else 'PRODUCCIÓN'}")
        
        # Recordatorio de backup
        if not self.dry_run:
            self.create_backup_reminder()
            
            response = input("\n¿Has hecho backup de la base de datos? (escriba 'SI' para continuar): ")
            if response != 'SI':
                logger.info("Proceso cancelado. Haz backup antes de continuar.")
                return False
        
        try:
            # Fase 1: Análisis
            if not self.run_data_analysis():
                logger.error("❌ Falló el análisis de datos")
                return False
            
            # Fase 2: Migración principal
            if not self.run_core_migration():
                logger.error("❌ Falló la migración de datos principales")
                return False
            
            # Fase 3: Migración histórica
            if not self.run_historical_migration():
                logger.error("❌ Falló la migración histórica")
                return False
            
            # Fase 4: Validación
            if not self.run_validation():
                logger.error("❌ Falló la validación")
                return False
            
            # Reporte final
            self.generate_final_report(True)
            return True
            
        except KeyboardInterrupt:
            logger.info("\n⏹️  Proceso interrumpido por el usuario")
            self.generate_final_report(False)
            return False
        except Exception as e:
            logger.error(f"❌ Error crítico en el proceso maestro: {e}")
            self.generate_final_report(False)
            return False


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Proceso maestro de migración del backend legacy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Ejecutar análisis completo (dry run)
  python run_migration.py

  # Ejecutar migración real (PELIGROSO)
  python run_migration.py --execute

  # Saltar análisis inicial
  python run_migration.py --skip-analysis

  # Saltar migración histórica (solo datos principales)
  python run_migration.py --skip-historical

  # Migración rápida (solo datos principales, sin análisis)
  python run_migration.py --skip-analysis --skip-historical
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Ejecutar en modo prueba sin modificar datos (por defecto)')
    parser.add_argument('--execute', action='store_true',
                       help='Ejecutar migración real (PELIGROSO)')
    parser.add_argument('--skip-analysis', action='store_true',
                       help='Saltar análisis inicial de datos')
    parser.add_argument('--skip-historical', action='store_true',
                       help='Saltar migración de logs históricos')
    
    args = parser.parse_args()
    
    # Determinar modo
    if args.execute:
        dry_run = False
        print("\n" + "⚠️ "*20)
        print("ADVERTENCIA: MIGRACIÓN EN MODO PRODUCCIÓN")
        print("⚠️ "*20)
        response = input("¿Estás seguro de continuar? (escriba 'SI' para confirmar): ")
        if response != 'SI':
            print("Migración cancelada.")
            return
    else:
        dry_run = True
    
    # Crear orquestador
    orchestrator = MigrationOrchestrator(
        dry_run=dry_run,
        skip_analysis=args.skip_analysis,
        skip_historical=args.skip_historical
    )
    
    # Ejecutar migración
    if orchestrator.run_full_migration():
        print("\n✅ Proceso maestro completado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Proceso maestro falló")
        sys.exit(1)


if __name__ == '__main__':
    main() 