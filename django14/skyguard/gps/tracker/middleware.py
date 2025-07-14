# -*- coding: utf-8 -*-
# DEPRECATED: Custom redirection middleware - NO LONGER IN USE
# This middleware was designed for multi-site user redirection but is not used
# The system uses standard Django authentication middleware
# KEPT FOR HISTORICAL REFERENCE ONLY

from django.utils.http import urlquote
from django.core.exceptions import ImproperlyConfigured
from django import http
from gps.tracker.models import GeoFence

class RedirectToUserSite(object):
    """
    DEPRECATED: Middleware for redirecting to proper user's site.
    
    This middleware was intended to redirect authenticated users to their
    assigned site domain, but the multi-site functionality was never fully
    implemented.
    
    The system currently uses standard Django authentication middleware.
    
    STATUS: DISCONTINUED - NOT IN USE
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

