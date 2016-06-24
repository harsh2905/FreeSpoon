from allauth.socialaccount.adapter import \
	DefaultSocialAccountAdapter as BaseDefaultSocialAccountAdapter
from allauth.account.utils import user_username

from allauth.account.adapter import \
	DefaultAccountAdapter as BaseDefaultAccountAdapter

from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth import get_backends
from django.middleware.csrf import rotate_token
from django.contrib.auth.signals import user_logged_in

from django.conf import settings
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from rest_framework.exceptions import AuthenticationFailed

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

	def add_message(self, request, level, message_template,
					message_context=None, extra_tags=''):
		"""
		Wrapper of `django.contrib.messages.add_message`, that reads
		the message text from a template.
		"""
		if 'django.contrib.messages' in settings.INSTALLED_APPS and \
			not request.path.startswith('/api/'):
			try:
				if message_context is None:
					message_context = {}
				message = render_to_string(message_template,
										message_context).strip()
				if message:
					messages.add_message(request, level, message,
										extra_tags=extra_tags)
			except TemplateDoesNotExist:
				pass

	def respond_user_inactive(self, request, user):
		raise AuthenticationFailed(detail='Account inactive')

	def unstash_verified_email(self, request):
		return None
