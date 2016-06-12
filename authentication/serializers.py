from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework import exceptions

from rest_framework.fields import empty

from collections import OrderedDict
from rest_framework.relations import PKOnlyObject
from rest_framework.fields import SkipField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from .models import *

class RemoveNullSerializerMixIn(serializers.Serializer):
	def to_representation(self, instance):
		"""
		Object instance -> Dict of primitive datatypes.
		"""
		ret = OrderedDict()
		fields = self._readable_fields
		
		for field in fields:
			try:
				attribute = field.get_attribute(instance)
			except SkipField:
				continue
			
			# We skip `to_representation` for `None` values so that fields do
			# not have to explicitly deal with that case.
			#
			# For related fields with `use_pk_only_optimization` we need to
			# resolve the pk value.
			check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
			if check_for_none is None:
				#ret[field.field_name] = None
				pass
			else:
				value = field.to_representation(attribute)
				if value is not None:
					ret[field.field_name] = value
		
		return ret

class MobUserSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	wx_nickname = serializers.CharField(source='real_wx_nickname')
	wx_headimgurl = serializers.CharField(source='real_wx_headimgurl')
	class Meta:
		model = MobUser
		fields = ('id', 'mob', 'wx_nickname', 'wx_headimgurl')

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






	
