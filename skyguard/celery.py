"""
Celery configuration for SkyGuard project.
"""

import os
import django
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')

# Ensure Django is setup before importing any Django modules
django.setup()

app = Celery('skyguard')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    # Verificar heartbeat de dispositivos cada minuto
    'check-devices-heartbeat': {
        'task': 'skyguard.apps.gps.tasks.check_devices_heartbeat',
        'schedule': crontab(minute='*'),  # Cada minuto
        'kwargs': {'timeout_minutes': 1}
    },
    
    # Limpiar sesiones antiguas diariamente a las 2:00 AM
    'cleanup-old-sessions': {
        'task': 'skyguard.apps.gps.tasks.cleanup_old_device_sessions',
        'schedule': crontab(hour=2, minute=0),  # Diario a las 2:00 AM
        'kwargs': {'days_old': 7}
    },
    
    # Actualizar calidad de conexión cada hora
    'update-connection-quality': {
        'task': 'skyguard.apps.gps.tasks.update_device_connection_quality',
        'schedule': crontab(minute=0),  # Cada hora en punto
    },
    
    # Generar estadísticas cada 6 horas
    'generate-device-stats': {
        'task': 'skyguard.apps.gps.tasks.generate_device_statistics',
        'schedule': crontab(minute=0, hour='*/6'),  # Cada 6 horas
    },
    
    # === TAREAS DE GEOCERCAS ===
    
    # Verificar geocercas para todos los dispositivos cada 2 minutos
    'check-all-devices-geofences': {
        'task': 'skyguard.apps.gps.tasks.check_all_devices_geofences',
        'schedule': crontab(minute='*/2'),  # Cada 2 minutos
    },
    
    # Limpiar eventos de geocercas antiguos diariamente a las 3:00 AM
    'cleanup-old-geofence-events': {
        'task': 'skyguard.apps.gps.tasks.cleanup_old_geofence_events',
        'schedule': crontab(hour=3, minute=0),  # Diario a las 3:00 AM
        'kwargs': {'days_old': 30}
    },
    
    # Generar estadísticas de geocercas cada 4 horas
    'generate-geofence-statistics': {
        'task': 'skyguard.apps.gps.tasks.generate_geofence_statistics',
        'schedule': crontab(minute=0, hour='*/4'),  # Cada 4 horas
    },
    
    # Enviar reporte diario de geocercas a las 8:00 AM
    'send-geofence-daily-report': {
        'task': 'skyguard.apps.gps.tasks.send_geofence_daily_report',
        'schedule': crontab(hour=8, minute=0),  # Diario a las 8:00 AM
    },
}

# Configuración adicional
app.conf.update(
    timezone='UTC',
    enable_utc=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_routes={
        'skyguard.apps.gps.tasks.*': {'queue': 'gps_tasks'},
    },
    task_annotations={
        'skyguard.apps.gps.tasks.check_devices_heartbeat': {
            'rate_limit': '60/m',  # Máximo 60 por minuto (1 por segundo)
            'time_limit': 120,     # 2 minutos máximo
        },
        'skyguard.apps.gps.tasks.cleanup_old_device_sessions': {
            'rate_limit': '1/h',   # Máximo 1 por hora
            'time_limit': 600,     # 10 minutos máximo
        },
    }
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 