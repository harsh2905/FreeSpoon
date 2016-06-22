from allauth.socialaccount.adapter import \
	DefaultSocialAccountAdapter as BaseDefaultSocialAccountAdapter
from allauth.account.utils import user_username

from allauth.account.adapter import \
	DefaultAccountAdapter as BaseDefaultAccountAdapter

from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth import get_backends
from django.middleware.csrf import rotate_token
from django.contrib.auth.signals import user_logged_in

class DefaultSocialAccountAdapter(BaseDefaultSocialAccountAdapter):
	def populate_user(self,
			request,
			sociallogin,
			data):
		user = sociallogin.user
		#user_username(user, None)
		return user

class DefaultAccountAdapter(BaseDefaultAccountAdapter):
	def get_login_redirect_url(self, request):
		return ''

	def populate_username(self, request, user):
		pass

	def login(self, request, user):
		# HACK: This is not nice. The proper Django way is to use an
		# authentication backend
		if not hasattr(user, 'backend'):
			backends = get_backends()
			for backend in backends:
				if isinstance(backend, AuthenticationBackend):
					# prefer our own backend
					break
			else:
				# Pick one
				backend = backends[0]
			backend_path = '.'.join([backend.__module__,
										backend.__class__.__name__])
			user.backend = backend_path
		if hasattr(request, 'user'):
			request.user = user
		rotate_token(request)
		user_logged_in.send(sender=user.__class__, request=request, user=user)