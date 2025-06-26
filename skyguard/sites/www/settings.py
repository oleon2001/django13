# Django settings for gps_site project.

SKYGUARD_DOMAIN = 'www.ensambles.net'
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
    ('Bernardo Cantu', 'bcantu@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'skyguard',              # Or path to database file if using sqlite3.
        'USER': 'django13',              # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    'feria': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'feria',              # Or path to database file if using sqlite3.
        'USER': 'link_eisa',          # Not used with sqlite3.
        'PASSWORD': 'link_eisa',      # Not used with sqlite3.
        'HOST': 'conteo.gpomag.com',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',               # Set to empty string for default. Not used with sqlite3.
        #'OPTIONS': {'options': '-c search_path=oreja' },
    }
}

DATABASE_ROUTERS = [ 'gps.tracker.routers.FeriaRouter' ]

#Paths and URLs
FIXTURE_DIRS = ('/home/django13/skyguard',)
MEDIA_ROOT = '/home/django13/www/media/'
STATIC_ROOT = '/home/django13/www/static'
#MEDIA_URL = '//'+SKYGUARD_DOMAIN+'/media/'
#STATIC_URL = '//'+SKYGUARD_DOMAIN+'/static/'
#ADMIN_MEDIA_PREFIX = '//'+SKYGUARD_DOMAIN+'/static/admin/'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

ROOT_URLCONF = 'sites.www.urls'
TEMPLATE_DIRS = (
    '/home/django13/skyguard/sites/www/templates',
    '/home/django13/skyguard/templates',
    )

# Additional locations of static files
STATICFILES_DIRS = (
    '/home/django13/skyguard/static',
)

LOGIN_URL='/login'
LOGIN_REDIRECT_URL='/'
X_FRAME_OPTIONS = 'SAMEORIGIN'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
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


# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT settings
from datetime import timedelta
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

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'channels',  # For WebSocket support
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.gis',
    'gps.tracker',
    'gps.gprs',
	'gps.udp',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose'
        },
        'file':{
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'formatter': 'simple',
            'filename': '/var/log/uwsgi/django/django.log'
        },
        'file_gps':{
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'formatter': 'simple',
            'filename': '/var/log/uwsgi/django/gps.log'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': False,
            'level':'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'gps': {
            'handlers':['file_gps'],
            'propagate': False,
            'level':'DEBUG',
        },
        'fastkml.config': {
            'handlers':['file_gps'],
            'propagate': False,
            'level':'DEBUG',
        },
    }
}
