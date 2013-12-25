# getted from https://djangosnippets.org/snippets/1720/
# with small modifications:
# 1. do not check basic auth for authorised users by default
#
# TODO move to separate small app


from django.conf import settings
from django.http import HttpResponse

from django.contrib.auth import authenticate

import base64
from functools import wraps


class HttpAuthMiddleware(object):
    """
    Some middleware to authenticate all requests at this site.
    """
    def process_request(self, request):
        return _http_auth_helper(request)


def http_auth(func):
    """
    A decorator, that can be used to authenticate some requests at the site.
    """
    @wraps(func)
    def inner(request, *args, **kwargs):
        result = _http_auth_helper(request)
        if result is not None:
            return result
        return func(request, *args, **kwargs)
    return inner


def _http_auth_helper(request):
    "This is the part that does all of the work"

    if not getattr(settings, 'FORCE_HTTP_AUTH', False):
        # If we don't mind if django's session auth is used, see if the
        # user is already logged in, and use that user.
        if request.user.is_authenticated():
            return None

    # At this point, the user is either not logged in, or must log in using
    # http auth.  If they have a header that indicates a login attempt, then
    # use this to try to login.
    if request.META.has_key('HTTP_AUTHORIZATION'):
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == 'basic':
                # Currently, only basic http auth is used.
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user:
                    # If the user successfully logged in, then add/overwrite
                    # the user object of this request.
                    request.user = user
                    return None

    # The username/password combo was incorrect, or not provided.
    # Challenge the user for a username/password.
    resp = HttpResponse()
    resp.status_code = 401
    # If we have a realm in our settings, use this for the challenge.
    realm = getattr(settings, 'HTTP_AUTH_REALM', 'Django')
    resp['WWW-Authenticate'] = 'Basic realm="%s"' % realm

    return resp
