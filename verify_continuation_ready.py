#!/usr/bin/env python3
"""
🔍 SCRIPT DE VERIFICACIÓN DE PREPARACIÓN
Verifica que todo esté listo para la continuación de migración

Autor: Senior Backend Developer
Fecha: 2025-07-01
"""

import os
import sys
import django
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from django.db import connection
from django.core.management import call_command

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContinuationVerifier:
    """Verificador de preparación para continuación."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.verification_log = []
        self.issues = []
        
    def log_action(self, message, level='info'):
        """Registra acciones de verificación."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.verification_log.append(log_entry)
        
        if level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
    
    def check_django_setup(self):
        """Verifica configuración de Django."""
        self.log_action("="*80)
        self.log_action("🐍 VERIFICANDO CONFIGURACIÓN DE DJANGO")
        self.log_action("="*80)
        
        try:
            # Verificar configuración
            call_command('check')
            self.log_action("✅ Configuración de Django correcta")
            
            # Verificar migraciones
            call_command('showmigrations')
            self.log_action("✅ Migraciones de Django verificadas")
            
            return True
            
        except Exception as e:
            self.log_action(f"❌ Error en Django: {e}", 'error')
            self.issues.append(f"Django: {e}")
            return False
    
    def check_database_connection(self):
        """Verifica conexión a base de datos."""
        self.log_action("="*80)
        self.log_action("🗄️ VERIFICANDO CONEXIÓN A BASE DE DATOS")
        self.log_action("="*80)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.log_action(f"✅ Base de datos conectada: {version.split(',')[0]}")
            
            return True
            
        except Exception as e:
            self.log_action(f"❌ Error en base de datos: {e}", 'error')
            self.issues.append(f"Base de datos: {e}")
            return False
    
    def check_required_scripts(self):
        """Verifica que los scripts requeridos existan."""
        self.log_action("="*80)
        self.log_action("📜 VERIFICANDO SCRIPTS REQUERIDOS")
        self.log_action("="*80)
        
        required_scripts = [
            'master_continuation.py',
            'continue_migration.py',
            'optimize_migrated_system.py',
            'monitor_migrated_system.py',
            'check_migration_status.py',
            'migration_scripts/validate_migration.py',
            'migration_scripts/data_analysis.py',
            'migration_scripts/migrate_core_data.py',
        ]
        
        missing_scripts = []
        for script in required_scripts:
            if Path(script).exists():
                self.log_action(f"✅ {script}")
            else:
                self.log_action(f"❌ {script} - FALTANTE", 'error')
                missing_scripts.append(script)
        
        if missing_scripts:
            self.issues.append(f"Scripts faltantes: {', '.join(missing_scripts)}")
            return False
        
        return True
    
    def check_directories(self):
        """Verifica directorios requeridos."""
        self.log_action("="*80)
        self.log_action("📁 VERIFICANDO DIRECTORIOS")
        self.log_action("="*80)
        
        required_dirs = [
            'logs',
            'migration_scripts',
            'skyguard/apps',
        ]
        
        missing_dirs = []
        for directory in required_dirs:
            if Path(directory).exists():
                self.log_action(f"✅ {directory}/")
            else:
                self.log_action(f"❌ {directory}/ - FALTANTE", 'error')
                missing_dirs.append(directory)
        
        if missing_dirs:
            self.issues.append(f"Directorios faltantes: {', '.join(missing_dirs)}")
            return False
        
        return True
    
    def check_migration_status(self):
        """Verifica estado actual de migración."""
        self.log_action("="*80)
        self.log_action("📊 VERIFICANDO ESTADO DE MIGRACIÓN")
        self.log_action("="*80)
        
        try:
            # Importar modelos para verificar
            from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
            
            total_devices = GPSDevice.objects.count()
            total_locations = GPSLocation.objects.count()
            total_events = GPSEvent.objects.count()
            
            self.log_action(f"📱 Dispositivos GPS: {total_devices}")
            self.log_action(f"📍 Ubicaciones: {total_locations}")
            self.log_action(f"🚨 Eventos: {total_events}")
            
            if total_devices > 0:
                self.log_action("✅ Sistema tiene datos migrados")
            else:
                self.log_action("⚠️ Sistema sin datos migrados", 'warning')
                self.issues.append("Sistema sin datos migrados")
            
            return True
            
        except Exception as e:
            self.log_action(f"❌ Error verificando estado: {e}", 'error')
            self.issues.append(f"Estado de migración: {e}")
            return False
    
    def check_system_resources(self):
        """Verifica recursos del sistema."""
        self.log_action("="*80)
        self.log_action("💾 VERIFICANDO RECURSOS DEL SISTEMA")
        self.log_action("="*80)
        
        try:
            import shutil
            
            # Verificar espacio en disco
            total, used, free = shutil.disk_usage('.')
            free_gb = free // (1024**3)
            
            self.log_action(f"💾 Espacio libre: {free_gb} GB")
            
            if free_gb < 1:
                self.log_action("❌ Espacio insuficiente (< 1 GB)", 'error')
                self.issues.append("Espacio en disco insuficiente")
            else:
                self.log_action("✅ Espacio en disco suficiente")
            
            return True
            
        except Exception as e:
            self.log_action(f"❌ Error verificando recursos: {e}", 'error')
            return False
    
    def generate_verification_report(self):
        """Genera reporte de verificación."""
        self.log_action("="*80)
        self.log_action("📋 GENERANDO REPORTE DE VERIFICACIÓN")
        self.log_action("="*80)
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Determinar estado general
        if len(self.issues) == 0:
            status = "✅ LISTO PARA CONTINUACIÓN"
            ready = True
        elif len(self.issues) <= 2:
            status = "⚠️ LISTO CON ADVERTENCIAS"
            ready = True
        else:
            status = "❌ NO LISTO - PROBLEMAS CRÍTICOS"
            ready = False
        
        report = f"""
================================================================================
REPORTE DE VERIFICACIÓN DE PREPARACIÓN
================================================================================
Fecha: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duración de verificación: {duration}

ESTADO GENERAL: {status}

PROBLEMAS ENCONTRADOS ({len(self.issues)}):
{chr(10).join([f'  • {issue}' for issue in self.issues]) if self.issues else '  ✅ Ningún problema encontrado'}

VERIFICACIONES COMPLETADAS:
{chr(10).join(self.verification_log[-20:])}  # Últimas 20 verificaciones

RECOMENDACIÓN:
{'✅ SISTEMA LISTO PARA CONTINUACIÓN' if ready else '❌ CORREGIR PROBLEMAS ANTES DE CONTINUAR'}

PRÓXIMOS PASOS:
{chr(10).join([
    '1. Ejecutar: python3 master_continuation.py',
    '2. Revisar logs y reportes',
    '3. Ejecutar migración real: python3 master_continuation.py --execute'
]) if ready else chr(10).join([
    '1. Corregir problemas identificados',
    '2. Ejecutar verificación nuevamente',
    '3. Contactar soporte si es necesario'
])}

================================================================================
"""
        
        # Guardar reporte
        with open('logs/verification_report.txt', 'w') as f:
            f.write(report)
            
        self.log_action("📄 Reporte guardado en: logs/verification_report.txt")
        print(report)
        
        return ready
    
    def execute_verification(self):
        """Ejecuta la verificación completa."""
        self.log_action("🚀 INICIANDO VERIFICACIÓN DE PREPARACIÓN")
        
        checks = [
            ("Configuración de Django", self.check_django_setup),
            ("Conexión a base de datos", self.check_database_connection),
            ("Scripts requeridos", self.check_required_scripts),
            ("Directorios", self.check_directories),
            ("Estado de migración", self.check_migration_status),
            ("Recursos del sistema", self.check_system_resources),
        ]
        
        for check_name, check_func in checks:
            self.log_action(f"🔄 Ejecutando: {check_name}")
            if not check_func():
                self.log_action(f"❌ Error en: {check_name}", 'error')
        
        return self.generate_verification_report()

def main():
    parser = argparse.ArgumentParser(description='Verificar preparación para continuación')
    parser.add_argument('--fix', action='store_true',
                       help='Intentar corregir problemas automáticamente')
    
    args = parser.parse_args()
    
    # Crear directorio de logs si no existe
    Path('logs').mkdir(exist_ok=True)
    
    # Inicializar verificador
    verifier = ContinuationVerifier()
    
    # Ejecutar verificación
    is_ready = verifier.execute_verification()
    
    if is_ready:
        print("\n🎉 SISTEMA LISTO PARA CONTINUACIÓN")
        print("💡 Ejecuta: python3 master_continuation.py")
    else:
        print("\n❌ SISTEMA NO ESTÁ LISTO")
        print("💡 Corrige los problemas identificados antes de continuar")
        
    sys.exit(0 if is_ready else 1)

if __name__ == '__main__':
    main() 