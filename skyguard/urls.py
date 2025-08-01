"""
URL Configuration for the Skyguard project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from skyguard.core.views import HomeView, LoginView, RegisterView, UserProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    # Authentication endpoints
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/profile/', UserProfileView.as_view(), name='profile'),
    path('api/auth/user/', UserProfileView.as_view(), name='user'),  # Alias para compatibilidad
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # App URLs
    path('api/gps/', include('skyguard.apps.gps.urls')),
    path('api/tracking/', include('skyguard.apps.tracking.urls')),
    path('api/monitoring/', include('skyguard.apps.monitoring.urls')),
    path('api/reports/', include('skyguard.apps.reports.urls')),
    path('api/', include('skyguard.apps.coordinates.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 