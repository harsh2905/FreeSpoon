from allauth.socialaccount.providers.weixin.views import WeixinOAuth2Adapter
from allauth.socialaccount.providers.weixin.client import WeixinOAuth2Client as BaseWeixinOAuth2Client
from rest_auth.registration.views import SocialLoginView

import requests

from django.contrib.auth import login
from django.conf import settings
from rest_auth.app_settings import create_token
from rest_auth.utils import jwt_encode
from rest_auth.models import TokenModel

from rest_framework.exceptions import AuthenticationFailed

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import (
	api_view,
	permission_classes,
)
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
	AllowAny,
	IsAuthenticated,
)
from rest_framework.exceptions import ValidationError

from .serializers import (
	MobUserSerializer,
	BindSerializer,
)

from django.shortcuts import render

# Create your views here.

class WeixinOAuth2Client(BaseWeixinOAuth2Client):

    def get_access_token(self, code):
        data = {'appid': self.consumer_key,
                'redirect_uri': self.callback_url,
                'grant_type': 'authorization_code',
                'secret': self.consumer_secret,
                'scope': self.scope,
                'code': code}
        params = None
        self._strip_empty_keys(data)
        url = self.access_token_url
        if self.access_token_method == 'GET':
            params = data
            data = None
        # TODO: Proper exception handling
        resp = requests.request(self.access_token_method,
                                url,
                                params=params,
                                data=data)
        access_token = None
        if resp.status_code == 200:
            access_token = resp.json()
        if not access_token or 'access_token' not in access_token:
            raise ValidationError('Error retrieving access token: %s'
                              % resp.content)
        return access_token

class WeixinLogin(SocialLoginView):
	adapter_class = WeixinOAuth2Adapter
	client_class = WeixinOAuth2Client
	callback_url = 'localhost:8000' # :(

class BindView(GenericAPIView):

	permission_classes = (IsAuthenticated,)
	serializer_class = BindSerializer

	token_model = TokenModel

	def bind(self):
		mob_user = self.mob_user = self.serializer.validated_data['user']
		temp_mob_user = self.request.user
		if hasattr(temp_mob_user, 'mob') \
			and temp_mob_user.mob \
			and len(temp_mob_user.mob) > 0:
			raise AuthenticationFailed(detail='Duplicate bind')
		social_account = temp_mob_user.wx_socialaccount
		if mob_user and temp_mob_user and social_account:
			social_account.user = mob_user
			social_account.save()
			temp_mob_user.is_active = False
			temp_mob_user.save()

	def login(self):
		self.user = self.serializer.validated_data['user']

		if getattr(settings, 'REST_USE_JWT', False):
		    self.token = jwt_encode(self.user)
		else:
		    self.token = create_token(self.token_model, self.user, self.serializer)

		if getattr(settings, 'REST_SESSION_LOGIN', True):
		    login(self.request, self.user)

	def get_response(self):
		serializer = MobUserSerializer(instance=self.mob_user) # TODO context
		return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
		self.serializer = self.get_serializer(data=self.request.data)
		self.serializer.is_valid(raise_exception=True)
		self.bind()
		self.login()
		return self.get_response()
