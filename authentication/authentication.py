from django.core.exceptions import ObjectDoesNotExist
from .models import *

class SmsBackend(object):

	def authenticate(self, mob=None, code=None):
		# TODO Check mobile phone format
		
		# TODO Check Sms verificate code

		user = None

		if code is not None and code == '123456':
			try:
				user = MobUser.objects.get(mob=mob)
			except ObjectDoesNotExist:
				# TODO register
				print('User not found')
		if user:
			return user

	def get_user(self, user_id):
		try:
			return MobUser.objects.get(pk=user_id)
		except ObjectDoesNotExist:
			return None
