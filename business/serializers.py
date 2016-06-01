from rest_framework import exceptions

from rest_framework import serializers
from authentication.serializers import LoginSerializer as BaseLoginSerializer
from rest_auth.registration.serializers import SocialLoginSerializer as BaseSocialLoginSerializer

from .models import User

class UserSerializer(serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.mob')
	class Meta:
		model = User
		fields = ('id', 'name', 'mob')

class JWTSerializer(serializers.Serializer):
	token = serializers.CharField()
	user = UserSerializer()

#class UserLoginSerializer(BaseLoginSerializer):
class UserLoginSerializerMixIn(serializers.Serializer):
	name = serializers.CharField(required=False, allow_blank=True)

	parentClass = None # ! You must implement it in sub class

	def validate(self, attrs):
		attrs = self.parentClass.validate(self, attrs)
		mob_user = attrs['user']
		if mob_user:
			name = attrs.get('name')
			user, created = User.objects.get_or_create(
				mob_user=mob_user,
				defaults={
					'name': name
				},
			)
			attrs['wrap_user'] = user
		else:
			msg = _('Unable to log in with provided credentials.')
			raise exceptions.ValidationError(msg)
		return attrs

class UserLoginSerializer(
	UserLoginSerializerMixIn, 
	BaseLoginSerializer):
	parentClass = BaseLoginSerializer

class UserSocialLoginSerializer(
	UserLoginSerializerMixIn, 
	BaseSocialLoginSerializer):
	parentClass = BaseSocialLoginSerializer
