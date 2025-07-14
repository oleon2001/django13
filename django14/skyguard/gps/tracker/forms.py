# -*- coding: utf-8 -*-
# DEPRECATED: Custom user forms - NO LONGER IN USE
# These forms were designed for custom User model but the model was never implemented
# The system uses standard Django authentication forms
# KEPT FOR HISTORICAL REFERENCE ONLY

from django.contrib.auth.forms import UserCreationForm as oldUserCreationForm, UserChangeForm as oldUserChangeForm
from django.forms import widgets
from models import User

class UserChangeForm(oldUserChangeForm):
    """
    DEPRECATED: Custom user change form.
    
    This form was intended for a custom User model that was never implemented.
    The system currently uses standard Django authentication forms.
    
    STATUS: DISCONTINUED - NOT IN USE
    """
    class Meta:
        model = User
        widgets = {
            'password': widgets.TextInput(attrs={"readonly": "readonly" }),
        }

class UserCreationForm(oldUserCreationForm):
    """
    DEPRECATED: Custom user creation form.
    
    This form was intended for a custom User model that was never implemented.
    The system currently uses standard Django authentication forms.
    
    STATUS: DISCONTINUED - NOT IN USE
    """
    class Meta:
        model = User
        fields = ("username",)

