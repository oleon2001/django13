# -*- coding: utf-8 -*-
# DEPRECATED: Custom authentication backend - NO LONGER IN USE
# This backend was designed for custom user model but was never properly implemented
# The system uses django.contrib.auth.backends.ModelBackend instead
# KEPT FOR HISTORICAL REFERENCE ONLY

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model

class TrackerUserBackend(ModelBackend):
    """
    DEPRECATED: Custom authentication backend for tracker users.
    
    This backend was intended to work with a custom User model defined in
    settings.TRACKER_USER_MODEL, but the custom User model was never implemented.
    
    The system currently uses the standard Django authentication backend.
    
    STATUS: DISCONTINUED - NOT IN USE
    """
    def authenticate(self, username=None, password=None):
        try:
            user = self.user_class.objects.get(username=username)
            if user.check_password(password):
                return user
        except self.user_class.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            return None

    @property
    def user_class(self):
        if not hasattr(self, '_user_class'):
            self._user_class = get_model(*settings.TRACKER_USER_MODEL.split('.', 2))
            if not self._user_class:
                raise ImproperlyConfigured('Could not get custom user model')
        return self._user_class
