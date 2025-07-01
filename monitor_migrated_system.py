#!/usr/bin/env python3
"""
📊 SCRIPT DE MONITOREO DEL SISTEMA MIGRADO
Monitorea la salud y funcionalidad del sistema después de la migración

Autor: Senior Backend Developer
Fecha: 2025-07-01
"""

import os
import sys
import django
import argparse
import logging
import subprocess
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.db.models import Count, Q, Max, Min
from django.utils import timezone

# Importar modelos
from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
from skyguard.apps.monitoring.models import DeviceStatus
from skyguard.apps.reports.models import DeviceReport

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor del sistema migrado."""
    
    def __init__(self, continuous=False, interval=300):
        self.continuous = continuous
        self.interval = interval
        self.start_time = datetime.now()
        self.monitoring_log = []
        self.alerts = []
        
    def log_action(self, message, level='info'):
        """Registra acciones de monitoreo."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.monitoring_log.append(log_entry)
        
        if level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
    
    def check_database_health(self):
        """Verifica la salud de la base de datos."""
        self.log_action("="*80)
        self.log_action("🗄️ VERIFICANDO SALUD DE BASE DE DATOS")
        self.log_action("="*80)
        
        try:
            # Verificar conexión
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.log_action(f"✅ Base de datos conectada: {version.split(',')[0]}")
            
            # Verificar tablas principales
            tables = ['gps_gpsdevice', 'gps_gpslocation', 'gps_gpsevent']
            for table in tables:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    self.log_action(f"📊 {table}: {count} registros")
            
            return True
            
        except Exception as e:
            self.log_action(f"❌ Error en base de datos: {e}", 'error')
            self.alerts.append(f"Base de datos: {e}")
            return False
    
    def check_gps_functionality(self):
        """Verifica la funcionalidad GPS."""
        self.log_action("="*80)
        self.log_action("📡 VERIFICANDO FUNCIONALIDAD GPS")
        self.log_action("="*80)
        
        try:
            # Verificar dispositivos activos
            total_devices = GPSDevice.objects.count()
            active_devices = GPSDevice.objects.filter(is_active=True).count()
            
            self.log_action(f"📱 Dispositivos totales: {total_devices}")
            self.log_action(f"📱 Dispositivos activos: {active_devices}")
            
            # Verificar dispositivos con actividad reciente (últimas 24h)
            yesterday = timezone.now() - timedelta(days=1)
            recent_activity = GPSLocation.objects.filter(
                timestamp__gte=yesterday
            ).values('device').distinct().count()
            
            self.log_action(f"📱 Dispositivos con actividad reciente: {recent_activity}")
            
            # Verificar eventos recientes
            recent_events = GPSEvent.objects.filter(
                timestamp__gte=yesterday
            ).count()
            
            self.log_action(f"🚨 Eventos en las últimas 24h: {recent_events}")
            
            # Alertas si no hay actividad
            if recent_activity == 0:
                self.log_action("⚠️ No hay actividad GPS reciente", 'warning')
                self.alerts.append("No hay actividad GPS reciente")
            
            return True
            
        except Exception as e:
            self.log_action(f"❌ Error en funcionalidad GPS: {e}", 'error')
            self.alerts.append(f"GPS: {e}")
            return False
    
    def check_system_performance(self):
        """Verifica el rendimiento del sistema."""
        self.log_action("="*80)
        self.log_action("⚡ VERIFICANDO RENDIMIENTO DEL SISTEMA")
        self.log_action("="*80)
        
        try:
            # Verificar tamaño de tablas
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    AND tablename LIKE 'gps_%'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
                """)
                
                tables = cursor.fetchall()
                self.log_action("📊 Tamaño de tablas GPS:")
                for table, size in tables:
                    self.log_action(f"  {table}: {size}")
            
            # Verificar consultas lentas
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        query,
                        mean_time,
                        calls
                    FROM pg_stat_statements 
                    WHERE query LIKE '%gps%'
                    ORDER BY mean_time DESC
                    LIMIT 5;
                """)
                
                slow_queries = cursor.fetchall()
                if slow_queries:
                    self.log_action("🐌 Consultas más lentas:")
                    for query, mean_time, calls in slow_queries:
                        self.log_action(f"  {mean_time:.2f}ms ({calls} llamadas)")
            
            return True
            
        except Exception as e:
            self.log_action(f"❌ Error en rendimiento: {e}", 'error')
            return False
    
    def check_data_integrity(self):
        """Verifica la integridad de los datos."""
        self.log_action("="*80)
        self.log_action("🔍 VERIFICANDO INTEGRIDAD DE DATOS")
        self.log_action("="*80)
        
        try:
            # Verificar dispositivos sin ubicaciones
            devices_without_locations = GPSDevice.objects.filter(
                gpslocation__isnull=True
            ).count()
            
            if devices_without_locations > 0:
                self.log_action(f"⚠️ {devices_without_locations} dispositivos sin ubicaciones", 'warning')
                self.alerts.append(f"{devices_without_locations} dispositivos sin ubicaciones")
            
            # Verificar ubicaciones duplicadas
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM (
                        SELECT device_id, latitude, longitude, timestamp, COUNT(*)
                        FROM gps_gpslocation
                        GROUP BY device_id, latitude, longitude, timestamp
                        HAVING COUNT(*) > 1
                    ) as duplicates;
                """)
                
                duplicates = cursor.fetchone()[0]
                if duplicates > 0:
                    self.log_action(f"⚠️ {duplicates} grupos de ubicaciones duplicadas", 'warning')
                    self.alerts.append(f"{duplicates} grupos de ubicaciones duplicadas")
            
            # Verificar datos inconsistentes
            invalid_locations = GPSLocation.objects.filter(
                Q(latitude__lt=-90) | Q(latitude__gt=90) |
                Q(longitude__lt=-180) | Q(longitude__gt=180)
            ).count()
            
            if invalid_locations > 0:
                self.log_action(f"❌ {invalid_locations} ubicaciones con coordenadas inválidas", 'error')
                self.alerts.append(f"{invalid_locations} ubicaciones con coordenadas inválidas")
            
            return True
            
        except Exception as e:
            self.log_action(f"❌ Error en integridad: {e}", 'error')
            return False
    
    def check_system_services(self):
        """Verifica los servicios del sistema."""
        self.log_action("="*80)
        self.log_action("🔧 VERIFICANDO SERVICIOS DEL SISTEMA")
        self.log_action("="*80)
        
        try:
            # Verificar servidor GPS
            gps_server_running = False
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "start_hardware_gps_server.py"],
                    capture_output=True,
                    text=True
                )
                gps_server_running = result.returncode == 0
            except:
                pass
            
            if gps_server_running:
                self.log_action("✅ Servidor GPS ejecutándose")
            else:
                self.log_action("❌ Servidor GPS no está ejecutándose", 'error')
                self.alerts.append("Servidor GPS no está ejecutándose")
            
            # Verificar Django
            try:
                from django.core.management import execute_from_command_line
                self.log_action("✅ Django funcionando correctamente")
            except Exception as e:
                self.log_action(f"❌ Error en Django: {e}", 'error')
                self.alerts.append(f"Django: {e}")
            
            return True
            
        except Exception as e:
            self.log_action(f"❌ Error en servicios: {e}", 'error')
            return False
    
    def generate_health_report(self):
        """Genera reporte de salud del sistema."""
        self.log_action("="*80)
        self.log_action("📋 GENERANDO REPORTE DE SALUD")
        self.log_action("="*80)
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Obtener estadísticas finales
        total_devices = GPSDevice.objects.count()
        total_locations = GPSLocation.objects.count()
        total_events = GPSEvent.objects.count()
        
        # Determinar estado general
        if len(self.alerts) == 0:
            status = "✅ SALUDABLE"
        elif len(self.alerts) <= 2:
            status = "⚠️ ADVERTENCIA"
        else:
            status = "❌ CRÍTICO"
        
        report = f"""
================================================================================
REPORTE DE SALUD DEL SISTEMA
================================================================================
Fecha: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duración del monitoreo: {duration}

ESTADO GENERAL: {status}

ESTADÍSTICAS DEL SISTEMA:
  📱 Dispositivos GPS: {total_devices}
  📍 Ubicaciones: {total_locations}
  🚨 Eventos: {total_events}

ALERTAS DETECTADAS ({len(self.alerts)}):
{chr(10).join([f'  • {alert}' for alert in self.alerts]) if self.alerts else '  ✅ Ninguna alerta'}

ACCIONES DE MONITOREO:
{chr(10).join(self.monitoring_log[-20:])}  # Últimas 20 acciones

RECOMENDACIONES:
{chr(10).join([
    '1. Revisar alertas críticas inmediatamente',
    '2. Monitorear actividad GPS continuamente',
    '3. Ejecutar optimización si es necesario',
    '4. Verificar logs de errores'
]) if self.alerts else '✅ Sistema funcionando correctamente'}

================================================================================
"""
        
        # Guardar reporte
        timestamp = end_time.strftime('%Y%m%d_%H%M%S')
        report_file = f'logs/health_report_{timestamp}.txt'
        with open(report_file, 'w') as f:
            f.write(report)
            
        self.log_action(f"📄 Reporte guardado en: {report_file}")
        
        # Guardar alertas en JSON para integración
        alert_data = {
            'timestamp': end_time.isoformat(),
            'status': status,
            'alerts': self.alerts,
            'stats': {
                'devices': total_devices,
                'locations': total_locations,
                'events': total_events
            }
        }
        
        with open(f'logs/alerts_{timestamp}.json', 'w') as f:
            json.dump(alert_data, f, indent=2)
        
        print(report)
        return len(self.alerts) == 0
    
    def execute_monitoring(self):
        """Ejecuta el monitoreo completo del sistema."""
        self.log_action("🚀 INICIANDO MONITOREO DEL SISTEMA")
        
        steps = [
            ("Salud de base de datos", self.check_database_health),
            ("Funcionalidad GPS", self.check_gps_functionality),
            ("Rendimiento del sistema", self.check_system_performance),
            ("Integridad de datos", self.check_data_integrity),
            ("Servicios del sistema", self.check_system_services),
        ]
        
        for step_name, step_func in steps:
            self.log_action(f"🔄 Ejecutando: {step_name}")
            if not step_func():
                self.log_action(f"❌ Error en: {step_name}", 'error')
        
        is_healthy = self.generate_health_report()
        
        if self.continuous:
            self.log_action(f"🔄 Monitoreo continuo - próxima verificación en {self.interval} segundos")
            time.sleep(self.interval)
            return self.execute_monitoring()
        
        return is_healthy

def main():
    parser = argparse.ArgumentParser(description='Monitorear sistema migrado')
    parser.add_argument('--continuous', action='store_true',
                       help='Monitoreo continuo')
    parser.add_argument('--interval', type=int, default=300,
                       help='Intervalo de monitoreo en segundos (default: 300)')
    parser.add_argument('--json', action='store_true',
                       help='Salida en formato JSON')
    
    args = parser.parse_args()
    
    # Crear directorio de logs si no existe
    Path('logs').mkdir(exist_ok=True)
    
    # Inicializar monitor
    monitor = SystemMonitor(
        continuous=args.continuous,
        interval=args.interval
    )
    
    # Ejecutar monitoreo
    is_healthy = monitor.execute_monitoring()
    
    if args.json:
        # Salida JSON para integración
        output = {
            'timestamp': datetime.now().isoformat(),
            'healthy': is_healthy,
            'alerts': monitor.alerts,
            'status': 'healthy' if is_healthy else 'unhealthy'
        }
        print(json.dumps(output))
    else:
        if is_healthy:
            print("\n🎉 SISTEMA SALUDABLE")
        else:
            print(f"\n⚠️ SISTEMA CON {len(monitor.alerts)} ALERTAS")
        
    sys.exit(0 if is_healthy else 1)

if __name__ == '__main__':
    main() 