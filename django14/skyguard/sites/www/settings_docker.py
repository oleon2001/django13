# Django settings for gps_site project con Docker

import os

SKYGUARD_DOMAIN = 'localhost:8000'
DEBUG = True 
TEMPLATE_DEBUG = DEBUG

#Location settings
TIME_ZONE = 'America/Guatemala'
LANGUAGE_CODE = 'es-mx'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
DECIMAL_SEPARATOR = '.'
USE_TZ = True

FILE_CHARSET="UTF-8"
ADMINS = (
    ('Admin', 'admin@falkun.com'),
)

MANAGERS = ADMINS

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

#Paths and URLs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FIXTURE_DIRS = (BASE_DIR,)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

ROOT_URLCONF = 'sites.www.urls'
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'sites', 'www', 'templates'),
    os.path.join(BASE_DIR, 'templates'),
)

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

LOGIN_URL='/login'
LOGIN_REDIRECT_URL='/'
X_FRAME_OPTIONS = 'SAMEORIGIN'

# DEPRECATED: Custom authentication backend configuration
# The TrackerUserBackend was never properly implemented and is not used
# The system uses the standard Django authentication backend
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# DEPRECATED: Custom user model setting - NOT IMPLEMENTED
# The custom User model was never created, so this setting is ignored
# The system uses the standard Django User model
TRACKER_USER_MODEL = 'tracker.User'

TRACKER_LOGO = 'logo64.png'
TRACKER_API_KEY = 'AIzaSyDAJgTMNvIGnRCrnqH6Ok8kayI-shZhRPI'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=f44JAdfgsfdADShgu786513278gx_af3q_rlvhc_-9hv*pwz$'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "gps.tracker.context_processors.tracker_globals"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.gis',
    'gps.tracker',
    'gps.gprs',
    'gps.udp',
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