"""
Development settings for the Skyguard project.
"""
from .base import *
from datetime import timedelta

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key'

# Hosts - Corregido para incluir testserver para testing
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '0.0.0.0',
    'testserver',  # Necesario para tests de Django
    '*',  # Solo para desarrollo - REMOVER EN PRODUCCIÓN
]

# Channels Configuration - Corregido para WebSockets
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'skyguard',
        'USER': 'skyguard',
        'PASSWORD': 'skyguard123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']
CORS_ORIGIN_ALLOW_ALL = True  # Solo para desarrollo

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'skyguard.apps.gps.services.hardware_gps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Celery Beat Schedule (tareas periódicas)
CELERY_BEAT_SCHEDULE = {
    'check-devices-heartbeat': {
        'task': 'skyguard.apps.gps.tasks.check_devices_heartbeat',
        'schedule': 60.0,  # Cada 60 segundos
        'kwargs': {'timeout_minutes': 1}
    },
    'monitor-hardware-gps-connections': {
        'task': 'skyguard.apps.gps.tasks.monitor_hardware_gps_connections',
        'schedule': 300.0,  # Cada 5 minutos
    },
    'update-device-connection-quality': {
        'task': 'skyguard.apps.gps.tasks.update_device_connection_quality',
        'schedule': 600.0,  # Cada 10 minutos
    },
    'generate-device-statistics': {
        'task': 'skyguard.apps.gps.tasks.generate_device_statistics',
        'schedule': 3600.0,  # Cada hora
    },
    'cleanup-old-gps-locations': {
        'task': 'skyguard.apps.gps.tasks.cleanup_old_gps_locations',
        'schedule': 86400.0,  # Diario
        'kwargs': {'days_old': 30}
    },
    'validate-gps-data-integrity': {
        'task': 'skyguard.apps.gps.tasks.validate_gps_data_integrity',
        'schedule': 7200.0,  # Cada 2 horas
    },
}

# Celery Task Routes
CELERY_TASK_ROUTES = {
    'skyguard.apps.gps.tasks.*': {'queue': 'gps_tasks'},
}

# Celery Task Annotations
CELERY_TASK_ANNOTATIONS = {
    'skyguard.apps.gps.tasks.check_devices_heartbeat': {
        'rate_limit': '60/m',  # Máximo 60 por minuto
        'time_limit': 120,     # 2 minutos máximo
    },
    'skyguard.apps.gps.tasks.monitor_hardware_gps_connections': {
        'rate_limit': '12/h',  # Máximo 12 por hora
        'time_limit': 60,      # 1 minuto máximo
    },
}

# Hardware GPS Configuration
HARDWARE_GPS_CONFIG = {
    'enabled': True,
    'tcp_server': {
        'host': '0.0.0.0',
        'port': 8001,
        'enabled': True,
    },
    'serial_monitoring': {
        'enabled': False,  # Cambiar a True si tienes GPS serial
        'port': '/dev/ttyS0',
        'baudrate': 9600,
        'timeout': 1,
    },
    'protocols': {
        'concox': {
            'enabled': True,
            'header': b'\x78\x78',
        },
        'meiligao': {
            'enabled': True,
            'header': b'\x79\x79',
        },
        'nmea': {
            'enabled': True,
            'sentences': ['$GPRMC', '$GPGGA', '$GPGLL'],
        },
        'wialon': {
            'enabled': True,
        },
    },
    'auto_create_devices': True,
    'connection_timeout': 30,  # segundos
    'max_connections': 100,
}

# GPS Device Token (para autenticación de dispositivos)
GPS_DEVICE_TOKEN = 'skyguard-gps-device-token-2024'

# GPS Command Security
GPS_COMMAND_SECRET_KEY = 'skyguard-gps-command-secret-key-2024-dev' 