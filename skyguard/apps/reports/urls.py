"""
URLs para el sistema de reportes SkyGuard
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    RouteViewSet, DriverViewSet, TicketViewSet, TimeSheetViewSet,
    GeoFenceViewSet, StatisticsViewSet, ReportAPIViewSet
)

router = DefaultRouter()
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'timesheets', TimeSheetViewSet, basename='timesheet')
router.register(r'geofences', GeoFenceViewSet, basename='geofence')
router.register(r'statistics', StatisticsViewSet, basename='statistics')
router.register(r'summary', ReportAPIViewSet, basename='summary')

urlpatterns = [
    path('', include(router.urls)),
] 