from rest_framework import serializers
from .models import *

class MobUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = MobUser
		fields = ('id', 'mob', 'name')

class JWTSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = MobUserSerializer()
