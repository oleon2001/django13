"""
Django settings initialization for SkyGuard project.
Automatically detects environment and loads appropriate settings.
"""
import os

# Detect environment automatically
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
elif environment == 'development':
    from .development import *
else:
    # Default to dev settings
    from .dev import * 