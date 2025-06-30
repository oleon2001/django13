from django.contrib.auth.forms import UserCreationForm as oldUserCreationForm, UserChangeForm as oldUserChangeForm
from django.forms import widgets
from models import User

class UserChangeForm(oldUserChangeForm):
	class Meta:
		model = User
		widgets = {
			'password': widgets.TextInput(attrs={"readonly": "readonly" }),
		}

class UserCreationForm(oldUserCreationForm):
    class Meta:
        model = User
        fields = ("username",)

