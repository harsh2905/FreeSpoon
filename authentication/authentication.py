from django.core.exceptions import ObjectDoesNotExist
from .models import *

import pdb

class SmsBackend(object):

	def authenticate(self, mob=None, code=None):
		pdb.set_trace()
		# TODO Check mobile phone format
		
		# TODO Check Sms verificate code
		if code is not None and code == '123456':
			try:
				user = MobUser.objects.get(mob=mob)
				return user
			except ObjectDoesNotExist:
				print('User not found')
		return None

	def get_user(self, user_id):
		try:
			return MobUser.objects.get(pk=user_id)
		except ObjectDoesNotExist:
			return None
