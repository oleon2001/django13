"""
Configuración de Celery Beat para tareas periódicas de GPS.
"""

from celery.schedules import crontab

# Configuración de tareas periódicas
CELERYBEAT_SCHEDULE = {
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

# Configuración de zona horaria para Celery
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Configuración del broker (Redis)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Configuración adicional
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_ROUTES = {
    'skyguard.apps.gps.tasks.*': {'queue': 'gps_tasks'},
    'skyguard.apps.gps.tasks.process_geofence_detection': {'queue': 'geofence_tasks'},
    'skyguard.apps.gps.tasks.check_all_devices_geofences': {'queue': 'geofence_tasks'},
}

# Configuración de retry
CELERY_TASK_ANNOTATIONS = {
    'skyguard.apps.gps.tasks.check_devices_heartbeat': {
        'rate_limit': '60/m',  # Máximo 60 por minuto (1 por segundo)
        'time_limit': 120,     # 2 minutos máximo
    },
    'skyguard.apps.gps.tasks.cleanup_old_device_sessions': {
        'rate_limit': '1/h',   # Máximo 1 por hora
        'time_limit': 600,     # 10 minutos máximo
    },
    'skyguard.apps.gps.tasks.check_all_devices_geofences': {
        'rate_limit': '30/m',  # Máximo 30 por minuto (cada 2 segundos)
        'time_limit': 300,     # 5 minutos máximo
    },
    'skyguard.apps.gps.tasks.process_geofence_detection': {
        'rate_limit': '200/m', # Máximo 200 por minuto (alta frecuencia para dispositivos individuales)
        'time_limit': 60,      # 1 minuto máximo
    },
    'skyguard.apps.gps.tasks.cleanup_old_geofence_events': {
        'rate_limit': '1/d',   # Máximo 1 por día
        'time_limit': 1800,    # 30 minutos máximo
    },
    'skyguard.apps.gps.tasks.generate_geofence_statistics': {
        'rate_limit': '6/d',   # Máximo 6 por día (cada 4 horas)
        'time_limit': 600,     # 10 minutos máximo
    },
    'skyguard.apps.gps.tasks.send_geofence_daily_report': {
        'rate_limit': '1/d',   # Máximo 1 por día
        'time_limit': 900,     # 15 minutos máximo
    },
} 