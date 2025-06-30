from django.conf import settings
from django.utils.functional import lazy, memoize, SimpleLazyObject
from django.contrib import messages
import random

random.seed()

def tracker_globals(request):
	return {
		'logo': 	settings.TRACKER_LOGO,
		'apikey':	settings.TRACKER_API_KEY,
		'HOME_URL':	settings.LOGIN_REDIRECT_URL,
		'random3':	random.randrange(3),
	}
	