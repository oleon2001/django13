"""
Production settings for SkyGuard GPS Tracking System
Optimized for high-performance, scalability, and security.
"""

from .base import *
import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security Settings
DEBUG = False
ALLOWED_HOSTS = [
    'your-domain.com',
    'api.your-domain.com',
    'ws.your-domain.com',
    '10.0.0.0/8',  # Private networks
    '172.16.0.0/12',
    '192.168.0.0/16'
]

# Security headers and HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# GPS Command Security
GPS_COMMAND_SECRET_KEY = os.environ.get('GPS_COMMAND_SECRET_KEY', 'your-very-long-secret-key-here')

# Database Configuration (High Performance)
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME', 'skyguard_prod'),
        'USER': os.environ.get('DB_USER', 'skyguard'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 600,  # Connection pooling
        'CONN_HEALTH_CHECKS': True,
    }
}

# Redis Configuration for Cache and Channels
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'{REDIS_URL}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'skyguard',
        'TIMEOUT': 3600,  # 1 hour default
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'{REDIS_URL}/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'skyguard_sessions',
        'TIMEOUT': 86400,  # 24 hours
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400  # 24 hours

# Channels Configuration for WebSockets
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'capacity': 1500,
            'expiry': 60,
        },
    },
}

# Celery Configuration for Background Tasks
CELERY_BROKER_URL = f'{REDIS_URL}/3'
CELERY_RESULT_BACKEND = f'{REDIS_URL}/4'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Celery optimizations for GPS data
CELERY_TASK_ROUTES = {
    'skyguard.apps.gps.tasks.process_gps_data': {'queue': 'gps_processing'},
    'skyguard.apps.gps.tasks.send_notifications': {'queue': 'notifications'},
    'skyguard.apps.gps.analytics.*': {'queue': 'analytics'},
}

CELERY_WORKER_CONCURRENCY = 8
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Static and Media Files (CDN Configuration)
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# AWS S3 Configuration (Optional)
if os.environ.get('USE_S3') == 'True':
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/skyguard/django.log',
            'maxBytes': 15728640,  # 15MB
            'backupCount': 10,
            'formatter': 'detailed',
        },
        'gps_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/skyguard/gps.log',
            'maxBytes': 52428800,  # 50MB
            'backupCount': 20,
            'formatter': 'detailed',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/skyguard/security.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 15,
            'formatter': 'detailed',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'detailed',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'skyguard.apps.gps': {
            'handlers': ['gps_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'skyguard.apps.gps.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'skyguard.apps.gps.analytics': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'channels': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@your-domain.com')

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Push Notifications (FCM)
FCM_SERVER_KEY = os.environ.get('FCM_SERVER_KEY')
APNS_CERTIFICATE_PATH = os.environ.get('APNS_CERTIFICATE_PATH')

# GPS Server Configuration
GPS_SERVERS = {
    'concox': {
        'enabled': True,
        'host': '0.0.0.0',
        'port': 55300,
        'protocol': 'tcp',
        'max_connections': 1000,
    },
    'meiligao': {
        'enabled': True,
        'host': '0.0.0.0',
        'port': 62000,
        'protocol': 'udp',
        'max_connections': 500,
    },
    'satellite': {
        'enabled': True,
        'host': '0.0.0.0',
        'port': 15557,
        'protocol': 'tcp',
        'max_connections': 200,
    },
    'wialon': {
        'enabled': True,
        'host': '0.0.0.0',
        'port': 20332,
        'protocol': 'tcp',
        'max_connections': 300,
    }
}

# API Rate Limiting
REST_FRAMEWORK.update({
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'gps_data': '10000/hour',  # Higher limit for GPS data ingestion
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
})

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'SkyGuard GPS API',
    'DESCRIPTION': 'Enterprise GPS Tracking and Fleet Management API',
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}],
}

# CORS Configuration for Mobile Apps
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "https://app.your-domain.com",
    "http://localhost:3000",  # React development
    "http://localhost:8080",  # Vue development
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Never True in production

# Mobile App specific headers
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
    'x-device-id',  # Custom header for device identification
    'x-app-version',  # Custom header for app version
]

# WebSocket Configuration
ASGI_APPLICATION = 'skyguard.routing.application'

# Analytics and ML Configuration
ANALYTICS_SETTINGS = {
    'enable_real_time': True,
    'enable_ml_analytics': True,
    'cache_metrics_duration': 300,  # 5 minutes
    'anomaly_detection_threshold': 0.1,
    'ml_model_update_interval': 86400,  # 24 hours
    'batch_processing_size': 1000,
}

# Monitoring and Health Checks
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,    # MB
}

# Performance Optimizations
DATABASE_CONNECTION_POOLING = True
USE_L10N = True
USE_I18N = True
USE_TZ = True

# Security enhancements
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
PERMISSIONS_POLICY = {
    'geolocation': ['self'],
    'camera': [],
    'microphone': [],
}

# Custom settings for GPS processing
GPS_DATA_RETENTION_DAYS = 365  # Keep GPS data for 1 year
GPS_PROCESSING_BATCH_SIZE = 500
GPS_REAL_TIME_UPDATES = True
GPS_ENABLE_GEOCODING = True

# Machine Learning settings
ML_MODELS_PATH = '/var/lib/skyguard/ml_models/'
ML_ENABLE_PATTERN_DETECTION = True
ML_ENABLE_PREDICTIVE_MAINTENANCE = True

# Backup and archival
BACKUP_SETTINGS = {
    'enable_auto_backup': True,
    'backup_interval_hours': 6,
    'backup_retention_days': 30,
    'backup_location': '/var/backups/skyguard/',
}

# Integration settings
EXTERNAL_APIS = {
    'google_maps': {
        'api_key': os.environ.get('GOOGLE_MAPS_API_KEY'),
        'enable_geocoding': True,
        'enable_routing': True,
    },
    'weather_api': {
        'api_key': os.environ.get('WEATHER_API_KEY'),
        'provider': 'openweathermap',
    }
}

# Feature flags
FEATURE_FLAGS = {
    'enable_websockets': True,
    'enable_push_notifications': True,
    'enable_advanced_analytics': True,
    'enable_ml_predictions': True,
    'enable_geofencing': True,
    'enable_route_optimization': True,
    'enable_driver_behavior_analysis': True,
    'enable_fuel_monitoring': True,
    'enable_maintenance_scheduling': True,
    'enable_fleet_efficiency_reports': True,
}

# Mobile API specific settings
MOBILE_API_SETTINGS = {
    'enable_offline_sync': True,
    'max_offline_days': 7,
    'sync_batch_size': 100,
    'enable_background_location': True,
    'location_update_interval': 30,  # seconds
    'enable_push_notifications': True,
    'max_cached_routes': 50,
    'enable_voice_commands': True,
    'enable_ar_navigation': False,  # Augmented reality features
}

# Additional security for production
SILKY_PYTHON_PROFILER = False  # Disable profiling in production
SILKY_AUTHENTICATION = True
SILKY_AUTHORISATION = True 