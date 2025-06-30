from django.utils.http import urlquote
from django.core.exceptions import ImproperlyConfigured
from django import http
from gps.tracker.models import GeoFence

class RedirectToUserSite(object):
	"""
	Middleware for redirecting to proper user's site.

	If request.user is authenticated, and the user is in the wrong site,
	this middleware will redirect to the right one.
	"""

	def process_request(self, request):
		# AuthenticationMiddleware is required so that request.user exists.
		if not hasattr(request, 'user'):
			raise ImproperlyConfigured(
				"The Tracker Redirection middleware requires the"
				" authentication middleware to be installed.  Edit your"
				" MIDDLEWARE_CLASSES setting to insert"
				" 'django.contrib.auth.middleware.AuthenticationMiddleware'"
				" before the RedirectToUserSite class.")
		# Works only on authenticated users
		# getting passed in the headers, then the correct user is already
		# persisted in the session and we don't need to continue.
		if request.user.is_authenticated():
			host = request.get_host()
			if host == request.user.site.domain:
				request.user.hasFences = len(GeoFence.objects.filter(owner = request.user)) != 0
				return
			newurl = "{0}://{1}{2}".format(request.is_secure() and 'https' or 'http',
					request.user.site.domain,
					urlquote(request.path))
			if request.GET:
				newurl += '?' + request.META['QUERY_STRING']
			return http.HttpResponsePermanentRedirect(newurl)

