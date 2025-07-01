from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Route(models.Model):
    """Model for GPS routes."""
    name = models.CharField(_('name'), max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gps_routes')
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        app_label = 'gps'
        verbose_name = _('Route')
        verbose_name_plural = _('Routes')
        unique_together = [('name', 'owner')]
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.owner.username}" 