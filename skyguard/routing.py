"""
ASGI routing configuration for WebSocket endpoints.
"""
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from skyguard.apps.gps.consumers import GPSRealtimeConsumer, GPSAnalyticsConsumer

websocket_urlpatterns = [
    re_path(r'ws/gps/realtime/$', GPSRealtimeConsumer.as_asgi()),
    re_path(r'ws/gps/analytics/$', GPSAnalyticsConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
}) 