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
} 