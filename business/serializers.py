from rest_framework import exceptions

from rest_framework import serializers
from authentication.serializers import LoginSerializer as BaseLoginSerializer
from rest_auth.registration.serializers import SocialLoginSerializer as BaseSocialLoginSerializer

from .models import User, Reseller, Dispatcher
from .fields import TimestampField

class UserSerializer(serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.mob')
	create_time = TimestampField()
	class Meta:
		model = User
		fields = ('id', 'name', 'create_time', 'mob')

class UserJWTSerializer(serializers.Serializer):
	token = serializers.CharField()
	user = UserSerializer()

class ResellerSerializer(serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.mob')
	create_time = TimestampField()
	class Meta:
		model = Reseller
		fields = ('id', 'name', 'tail', 'create_time', 'mob')

class ResellerJWTSerializer(serializers.Serializer):
	token = serializers.CharField()
	user = ResellerSerializer()

class DispatcherSerializer(serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.mob')
	create_time = TimestampField()
	class Meta:
		model = Dispatcher
		fields = ('id', 'name', 'tail', 'address', 'create_time', 'mob')

class DispatcherJWTSerializer(serializers.Serializer):
	token = serializers.CharField()
	user = DispatcherSerializer()

class LoginSerializerMixIn(serializers.Serializer):
	name = serializers.CharField(required=False, allow_blank=True)

	mainModel = None # Must implement it in sub class
	parentClass = None # Must implement it in sub class
	defaultFieldNames = [] # Must implement it in sub class

	def validate(self, attrs):
		attrs = self.parentClass.validate(self, attrs)
		mob_user = attrs['user']
		if mob_user:
			defaults = {}
			for fieldName in self.defaultFieldNames:
				fieldValue = attrs.get(fieldName)
				if fieldValue:
					defaults[fieldName] = fieldValue
			user, created = self.mainModel.objects.get_or_create(
				mob_user=mob_user,
				defaults=defaults
			)
			attrs['wrap_user'] = user
		else:
			msg = _('Unable to log in with provided credentials.')
			raise exceptions.ValidationError(msg)
		return attrs

class UserLoginSerializer(
	LoginSerializerMixIn, 
	BaseLoginSerializer):
	parentClass = BaseLoginSerializer
	defaultFieldNames = ['name']
	mainModel = User

class UserSocialLoginSerializer(
	LoginSerializerMixIn, 
	BaseSocialLoginSerializer):
	parentClass = BaseSocialLoginSerializer
	defaultFieldNames = ['name']
	mainModel = User

class ResellerLoginSerializer(
	LoginSerializerMixIn, 
	BaseLoginSerializer):
	parentClass = BaseLoginSerializer
	defaultFieldNames = ['name', 'tail']
	mainModel = Reseller

class ResellerSocialLoginSerializer(
	LoginSerializerMixIn, 
	BaseSocialLoginSerializer):
	parentClass = BaseSocialLoginSerializer
	defaultFieldNames = ['name', 'tail']
	mainModel = Reseller

class DispatcherLoginSerializer(
	LoginSerializerMixIn, 
	BaseLoginSerializer):
	parentClass = BaseLoginSerializer
	defaultFieldNames = ['name', 'tail', 'address']
	mainModel = Dispatcher

class DispatcherSocialLoginSerializer(
	LoginSerializerMixIn, 
	BaseSocialLoginSerializer):
	parentClass = BaseSocialLoginSerializer
	defaultFieldNames = ['name', 'tail', 'address']
	mainModel = Dispatcher





