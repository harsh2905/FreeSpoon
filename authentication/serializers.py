from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework import exceptions

from rest_framework.fields import empty

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from .models import *

class MobUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = MobUser
		fields = ('id', 'mob', 'name')

	def __init__(self, instance=None, data=empty, **kwargs):
		if instance and instance.parent:
			instance = instance.parent
		super(MobUserSerializer, self).__init__(instance, data, **kwargs)

class JWTSerializer(serializers.Serializer):
	token = serializers.CharField()
	user = MobUserSerializer()

class LoginSerializer(serializers.Serializer):
	mob = serializers.CharField(required=True, allow_blank=False)
	code = serializers.CharField(required=True, allow_blank=False)

	def validate(self, attrs):
		mob = attrs.get('mob')
		code = attrs.get('code')

		user = None

		if mob and code:
			user = authenticate(mob=mob, code=code)
		else:
			msg = _('Must include "mob" and "code".')
			raise exceptions.ValidationError(msg)

		if user:
			if not user.is_active:
				msg = _('User account is disabled.')
				raise exceptions.ValidationError(msg)
		else:
			msg = _('Unable to log in with provided credentials.')
			raise exceptions.ValidationError(msg)
		
		attrs['user'] = user
		return attrs

class BindSerializer(serializers.Serializer):
	mob = serializers.CharField(required=True, allow_blank=False)
	code = serializers.CharField(required=True, allow_blank=False)

	def validate(self, attrs):
		mob = attrs.get('mob')
		code = attrs.get('code')
		
		user = None

		if mob and code:
			user = authenticate(mob=mob, code=code)
		else:
			msg = _('Must include "mob" and "code".')
			raise exceptions.ValidationError(msg)

		if user:
			attrs['user'] = user
		else:
			msg = _('Unable to log in with provided credentials.')
			raise exceptions.ValidationError(msg)

		return attrs






	
