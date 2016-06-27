from django.core.exceptions import ObjectDoesNotExist

from authentication.models import *
from .sms import SmsApp

class SmsBackend(object):

	def authenticate(self, mob=None, code=None):
		# TODO Check mobile phone format
		
		# TODO Check Sms verificate code

		user = None

		if SmsApp.check(mob, code):
			user, created = MobUser.objects.get_or_create(
				mob=mob,
				defaults={},
			)
		return user

	def get_user(self, user_id):
		try:
			return MobUser.objects.get(pk=user_id)
		except ObjectDoesNotExist:
			return None
