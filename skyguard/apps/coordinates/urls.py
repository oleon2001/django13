from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoordinateViewSet

router = DefaultRouter()
router.register(r'coordinates', CoordinateViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 