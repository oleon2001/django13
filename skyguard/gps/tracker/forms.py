from django.contrib.auth.forms import UserCreationForm as oldUserCreationForm, UserChangeForm as oldUserChangeForm
from django.forms import widgets
from django.contrib.auth.models import User

class UserChangeForm(oldUserChangeForm):
	class Meta:
		model = User
		fields = ("username",)
		widgets = {
			'password': widgets.TextInput(attrs={"readonly": "readonly" }),
		}

class UserCreationForm(oldUserCreationForm):
    class Meta:
        model = User
        fields = ("username",)

