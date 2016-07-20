import time
from importlib import import_module

from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date

from django.utils.functional import SimpleLazyObject
from django.contrib import auth

from django.contrib.messages.storage import default_storage
from django.contrib.auth.models import AnonymousUser


class MessageMiddleware(object):
    """
    Middleware that handles temporary messages.
    """

    def process_request(self, request):
        if request.path.startswith('/v1/'):
            return
        request._messages = default_storage(request)

    def process_response(self, request, response):
        """
        Updates the storage backend (i.e., saves the messages).

        If not all messages could not be stored and ``DEBUG`` is ``True``, a
        ``ValueError`` is raised.
        """
        if request.path.startswith('/v1/'):
            return response
        # A higher middleware layer may return a request which does not contain
        # messages storage, so make no assumption that it will be there.
        if hasattr(request, '_messages'):
            unstored_messages = request._messages.update(response)
            if unstored_messages and settings.DEBUG:
                raise ValueError('Not all temporary messages could be stored.')
        return response

class SessionMiddleware(object):
    def __init__(self):
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    def process_request(self, request):
        if request.path.startswith('/v1/'):
            return
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        request.session = self.SessionStore(session_key)

    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie or delete
        the session cookie if the session has been emptied.
        """
        if request.path.startswith('/v1/'):
            return response
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            pass
        else:
            # First check if we need to delete this cookie.
            # The session should be deleted only if the session is entirely empty
            if settings.SESSION_COOKIE_NAME in request.COOKIES and empty:
                response.delete_cookie(settings.SESSION_COOKIE_NAME,
                    domain=settings.SESSION_COOKIE_DOMAIN)
            else:
                if accessed:
                    patch_vary_headers(response, ('Cookie',))
                if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                    if request.session.get_expire_at_browser_close():
                        max_age = None
                        expires = None
                    else:
                        max_age = request.session.get_expiry_age()
                        expires_time = time.time() + max_age
                        expires = cookie_date(expires_time)
                    # Save the session data and refresh the client cookie.
                    # Skip session save for 500 responses, refs #3881.
                    if response.status_code != 500:
                        request.session.save()
                        response.set_cookie(settings.SESSION_COOKIE_NAME,
                                request.session.session_key, max_age=max_age,
                                expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                                path=settings.SESSION_COOKIE_PATH,
                                secure=settings.SESSION_COOKIE_SECURE or None,
                                httponly=settings.SESSION_COOKIE_HTTPONLY or None)
        return response

def get_user(request):
    if not hasattr(request, '_cached_user'):
        if request.path.startswith('/v1/'):
            request._cached_user = AnonymousUser()
        else:
            request._cached_user = auth.get_user(request)
    return request._cached_user

class AuthenticationMiddleware(object):
    def process_request(self, request):
        if not request.path.startswith('/v1/'):
            assert hasattr(request, 'session'), (
                "The Django authentication middleware requires session middleware "
                "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
                "'django.contrib.sessions.middleware.SessionMiddleware' before "
                "'django.contrib.auth.middleware.AuthenticationMiddleware'."
            )
        request.user = SimpleLazyObject(lambda: get_user(request))