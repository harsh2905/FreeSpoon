from allauth.socialaccount.adapter import \
	DefaultSocialAccountAdapter as BaseDefaultSocialAccountAdapter
from allauth.account.utils import user_username

from allauth.account.adapter import \
	DefaultAccountAdapter as BaseDefaultAccountAdapter

class DefaultSocialAccountAdapter(BaseDefaultSocialAccountAdapter):
	def populate_user(self,
			request,
			sociallogin,
			data):
		user = sociallogin.user
		#user_username(user, None)
		return user

class DefaultAccountAdapter(BaseDefaultAccountAdapter):
	def populate_username(self, request, user):
		pass
