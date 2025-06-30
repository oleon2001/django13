# -*- coding: utf-8 -*-
import os
# Configuracion local para desarrollo

# Obtener la ruta del proyecto actual
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SKYGUARD_DIR = os.path.join(BASE_DIR, 'skyguard')

# Importar configuración base
from settings import *

# Configuración de base de datos para Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'falkun',
        'USER': 'falkun_user',
        'PASSWORD': 'falkun_password',
        'HOST': 'localhost',  # Cambiar a 'db' si usas Docker para Django también
        'PORT': '5433',
    },
}

# Configuración de desarrollo
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Sobrescribir rutas para el entorno local
FIXTURE_DIRS = (SKYGUARD_DIR,)
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'media')
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

TEMPLATE_DIRS = (
    os.path.join(SKYGUARD_DIR, 'sites', 'www', 'templates'),
    os.path.join(SKYGUARD_DIR, 'templates'),
)

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(SKYGUARD_DIR, 'static'),
)

# Configuración de logging para desarrollo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'django.log'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'gps': {
            'handlers': ['console', 'file'],
            'propagate': False,
            'level': 'DEBUG',
        },
    }
}

# Crear directorios si no existen
import os
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)
if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT) 