"""
ASGI config for skyguard project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')

# Import Django and initialize Django before importing channels
django_asgi_app = get_asgi_application()

# Import channels consumers
from skyguard.apps.gps.consumers import GPSRealtimeConsumer

# WebSocket URL patterns
websocket_urlpatterns = [
    path('ws/gps/', GPSRealtimeConsumer.as_asgi()),
    path('ws/geofences/', GPSRealtimeConsumer.as_asgi()),
    path('ws/alerts/', GPSRealtimeConsumer.as_asgi()),
    path('ws/notifications/', GPSRealtimeConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
}) 