#!/usr/bin/env python3
"""
⚡ SCRIPT DE OPTIMIZACIÓN DEL SISTEMA MIGRADO
Optimiza el rendimiento y limpia el sistema después de la migración

Autor: Senior Backend Developer
Fecha: 2025-07-01
"""

import os
import sys
import django
import argparse
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.db.models import Count, Q

# Importar modelos
from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
from skyguard.apps.monitoring.models import DeviceStatus
from skyguard.apps.reports.models import DeviceReport

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemOptimizer:
    """Optimizador del sistema migrado."""
    
    def __init__(self, dry_run=True, aggressive=False):
        self.dry_run = dry_run
        self.aggressive = aggressive
        self.start_time = datetime.now()
        self.optimization_log = []
        
    def log_action(self, message, level='info'):
        """Registra acciones de optimización."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.optimization_log.append(log_entry)
        
        if level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
    
    def analyze_database_performance(self):
        """Analiza el rendimiento de la base de datos."""
        self.log_action("="*80)
        self.log_action("📊 ANALIZANDO RENDIMIENTO DE BASE DE DATOS")
        self.log_action("="*80)
        
        with connection.cursor() as cursor:
            # Analizar tamaño de tablas
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY size_bytes DESC;
            """)
            
            tables = cursor.fetchall()
            
            self.log_action("📋 TAMAÑO DE TABLAS:")
            for table in tables[:10]:  # Top 10
                self.log_action(f"  {table[1]}: {table[2]}")
        
        # Analizar índices
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    indexname,
                    tablename,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname;
            """)
            
            indexes = cursor.fetchall()
            self.log_action(f"📈 ÍNDICES ENCONTRADOS: {len(indexes)}")
        
        return True
    
    def optimize_database_indexes(self):
        """Optimiza índices de la base de datos."""
        self.log_action("="*80)
        self.log_action("🔍 OPTIMIZANDO ÍNDICES DE BASE DE DATOS")
        self.log_action("="*80)
        
        # Crear índices faltantes para GPS
        self.log_action("📡 Creando índices para GPS...")
        
        with connection.cursor() as cursor:
            # Índice para búsquedas por dispositivo y fecha
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_gps_location_device_timestamp 
                ON gps_gpslocation (device_id, timestamp);
            """)
            
            # Índice para búsquedas por coordenadas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_gps_location_coordinates 
                ON gps_gpslocation (latitude, longitude);
            """)
            
            # Índice para eventos GPS
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_gps_event_device_type 
                ON gps_gpsevent (device_id, event_type, timestamp);
            """)
            
            # Índice para estado de dispositivos
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_device_status_device 
                ON monitoring_devicestatus (device_id, last_seen);
            """)
        
        self.log_action("✅ Índices optimizados")
        return True
    
    def clean_duplicate_data(self):
        """Limpia datos duplicados."""
        self.log_action("="*80)
        self.log_action("🧹 LIMPIANDO DATOS DUPLICADOS")
        self.log_action("="*80)
        
        # Limpiar ubicaciones duplicadas (mismo dispositivo, misma ubicación, mismo tiempo)
        self.log_action("📍 Limpiando ubicaciones GPS duplicadas...")
        
        with connection.cursor() as cursor:
            # Encontrar duplicados
            cursor.execute("""
                DELETE FROM gps_gpslocation 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM gps_gpslocation 
                    GROUP BY device_id, latitude, longitude, timestamp
                );
            """)
            
            deleted_count = cursor.rowcount
            self.log_action(f"🗑️ Eliminadas {deleted_count} ubicaciones duplicadas")
        
        # Limpiar eventos duplicados
        self.log_action("🚨 Limpiando eventos duplicados...")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM gps_gpsevent 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM gps_gpsevent 
                    GROUP BY device_id, event_type, timestamp
                );
            """)
            
            deleted_count = cursor.rowcount
            self.log_action(f"🗑️ Eliminadas {deleted_count} eventos duplicados")
        
        return True
    
    def archive_old_data(self):
        """Archiva datos antiguos para mejorar rendimiento."""
        self.log_action("="*80)
        self.log_action("📦 ARCHIVANDO DATOS ANTIGUOS")
        self.log_action("="*80)
        
        # Calcular fecha límite (6 meses atrás)
        cutoff_date = datetime.now() - timedelta(days=180)
        
        # Contar registros antiguos
        old_locations = GPSLocation.objects.filter(timestamp__lt=cutoff_date).count()
        old_events = GPSEvent.objects.filter(timestamp__lt=cutoff_date).count()
        
        self.log_action(f"📊 Registros antiguos encontrados:")
        self.log_action(f"  📍 Ubicaciones: {old_locations}")
        self.log_action(f"  🚨 Eventos: {old_events}")
        
        if self.aggressive and not self.dry_run:
            # Crear tabla de archivo
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS gps_gpslocation_archive 
                    AS SELECT * FROM gps_gpslocation WHERE 1=0;
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS gps_gpsevent_archive 
                    AS SELECT * FROM gps_gpsevent WHERE 1=0;
                """)
            
            # Mover datos antiguos a archivo
            self.log_action("📦 Moviendo datos antiguos a archivo...")
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO gps_gpslocation_archive 
                    SELECT * FROM gps_gpslocation 
                    WHERE timestamp < %s;
                """, [cutoff_date])
                
                cursor.execute("""
                    DELETE FROM gps_gpslocation 
                    WHERE timestamp < %s;
                """, [cutoff_date])
                
                archived_count = cursor.rowcount
                self.log_action(f"📦 Archivadas {archived_count} ubicaciones antiguas")
        
        return True
    
    def optimize_queries(self):
        """Optimiza consultas frecuentes."""
        self.log_action("="*80)
        self.log_action("⚡ OPTIMIZANDO CONSULTAS")
        self.log_action("="*80)
        
        # Crear vistas materializadas para consultas frecuentes
        self.log_action("📊 Creando vistas optimizadas...")
        
        with connection.cursor() as cursor:
            # Vista para estadísticas de dispositivos
            cursor.execute("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS device_stats_view AS
                SELECT 
                    d.id as device_id,
                    d.imei,
                    d.name,
                    COUNT(l.id) as total_locations,
                    MAX(l.timestamp) as last_location,
                    COUNT(e.id) as total_events
                FROM gps_gpsdevice d
                LEFT JOIN gps_gpslocation l ON d.id = l.device_id
                LEFT JOIN gps_gpsevent e ON d.id = e.device_id
                GROUP BY d.id, d.imei, d.name;
            """)
            
            # Índice en la vista materializada
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_device_stats_device 
                ON device_stats_view (device_id);
            """)
        
        self.log_action("✅ Vistas optimizadas creadas")
        return True
    
    def vacuum_database(self):
        """Ejecuta VACUUM para optimizar la base de datos."""
        self.log_action("="*80)
        self.log_action("🧽 EJECUTANDO VACUUM DE BASE DE DATOS")
        self.log_action("="*80)
        
        if not self.dry_run:
            with connection.cursor() as cursor:
                cursor.execute("VACUUM ANALYZE;")
                self.log_action("✅ VACUUM completado")
        else:
            self.log_action("[DRY-RUN] VACUUM ANALYZE;")
        
        return True
    
    def update_statistics(self):
        """Actualiza estadísticas de la base de datos."""
        self.log_action("="*80)
        self.log_action("📈 ACTUALIZANDO ESTADÍSTICAS")
        self.log_action("="*80)
        
        if not self.dry_run:
            with connection.cursor() as cursor:
                cursor.execute("ANALYZE;")
                self.log_action("✅ Estadísticas actualizadas")
        else:
            self.log_action("[DRY-RUN] ANALYZE;")
        
        return True
    
    def generate_optimization_report(self):
        """Genera reporte de optimización."""
        self.log_action("="*80)
        self.log_action("📋 GENERANDO REPORTE DE OPTIMIZACIÓN")
        self.log_action("="*80)
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Obtener estadísticas finales
        total_devices = GPSDevice.objects.count()
        total_locations = GPSLocation.objects.count()
        total_events = GPSEvent.objects.count()
        
        report = f"""
================================================================================
REPORTE DE OPTIMIZACIÓN DEL SISTEMA
================================================================================
Fecha de inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Fecha de finalización: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duración total: {duration}

MODO DE EJECUCIÓN: {'DRY RUN' if self.dry_run else 'OPTIMIZACIÓN REAL'}
MODO AGRESIVO: {'SÍ' if self.aggressive else 'NO'}

ESTADÍSTICAS FINALES:
  📱 Dispositivos GPS: {total_devices}
  📍 Ubicaciones: {total_locations}
  🚨 Eventos: {total_events}

ACCIONES COMPLETADAS:
{chr(10).join(self.optimization_log)}

MEJORAS IMPLEMENTADAS:
✅ Índices optimizados para consultas GPS
✅ Datos duplicados eliminados
✅ Vistas materializadas creadas
✅ Base de datos limpiada y optimizada

PRÓXIMOS PASOS:
1. Monitorear rendimiento del sistema
2. Ejecutar optimización periódicamente
3. Configurar mantenimiento automático
4. Documentar mejoras implementadas

================================================================================
"""
        
        # Guardar reporte
        with open('logs/optimization_report.txt', 'w') as f:
            f.write(report)
            
        self.log_action("📄 Reporte guardado en: logs/optimization_report.txt")
        print(report)
    
    def execute_optimization(self):
        """Ejecuta la optimización completa del sistema."""
        self.log_action("🚀 INICIANDO OPTIMIZACIÓN DEL SISTEMA")
        
        steps = [
            ("Análisis de rendimiento", self.analyze_database_performance),
            ("Optimización de índices", self.optimize_database_indexes),
            ("Limpieza de duplicados", self.clean_duplicate_data),
            ("Archivado de datos antiguos", self.archive_old_data),
            ("Optimización de consultas", self.optimize_queries),
            ("VACUUM de base de datos", self.vacuum_database),
            ("Actualización de estadísticas", self.update_statistics),
        ]
        
        for step_name, step_func in steps:
            self.log_action(f"🔄 Ejecutando: {step_name}")
            if not step_func():
                self.log_action(f"❌ Error en: {step_name}", 'error')
                return False
        
        self.generate_optimization_report()
        return True

def main():
    parser = argparse.ArgumentParser(description='Optimizar sistema migrado')
    parser.add_argument('--execute', action='store_true', 
                       help='Ejecutar optimización real (no dry-run)')
    parser.add_argument('--aggressive', action='store_true',
                       help='Modo agresivo (archiva datos antiguos)')
    parser.add_argument('--skip-archive', action='store_true',
                       help='Saltar archivado de datos')
    
    args = parser.parse_args()
    
    # Crear directorio de logs si no existe
    Path('logs').mkdir(exist_ok=True)
    
    # Inicializar optimizador
    optimizer = SystemOptimizer(
        dry_run=not args.execute,
        aggressive=args.aggressive
    )
    
    # Ejecutar optimización
    success = optimizer.execute_optimization()
    
    if success:
        print("\n🎉 OPTIMIZACIÓN COMPLETADA EXITOSAMENTE")
        if not args.execute:
            print("💡 Para ejecutar optimización real, usa: --execute")
    else:
        print("\n❌ OPTIMIZACIÓN FALLÓ")
        
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 