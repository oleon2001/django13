"""
WSGI config for skyguard project.
"""

import os
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path de Python
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.sites.settings')

# Importar la aplicación WSGI de Django
from django.core.wsgi import get_wsgi_application

# Configurar la aplicación WSGI
application = get_wsgi_application() 