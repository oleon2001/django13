"""
URLs para el sistema de geofencing SkyGuard
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import GeofencingViewSet

router = DefaultRouter()
router.register(r'geofences', GeofencingViewSet, basename='geofence')

urlpatterns = [
    path('', include(router.urls)),
] 