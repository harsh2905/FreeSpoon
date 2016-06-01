from allauth.socialaccount.providers.weixin.views import WeixinOAuth2Adapter
from allauth.socialaccount.providers.weixin.client import WeixinOAuth2Client
from rest_auth.registration.views import SocialLoginView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import (
	api_view,
	permission_classes,
)
from rest_framework.reverse import reverse
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
	AllowAny,
	IsAuthenticated,
)

from .serializers import (
	MobUserSerializer,
	BindSerializer,
)

from django.shortcuts import render

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
	return Response({
		'login': reverse('login', request=request, format=format),
		'refresh': reverse('refresh', request=request, format=format),
		'user': reverse('details', request=request, format=format),
		'weixin': reverse('sociallogin', request=request, format=format),
		'bind': reverse('bind', request=request, format=format),
	})


class WeixinLogin(SocialLoginView):
	adapter_class = WeixinOAuth2Adapter
	client_class = WeixinOAuth2Client
	callback_url = 'localhost:8000' # :(

class BindView(GenericAPIView):

	permission_classes = (IsAuthenticated,)
	serializer_class = BindSerializer

	def bind(self):
		parent = self.serializer.validated_data['user']
		user = self.request.user
		if parent and user:
			user.parent = parent
			user.save()

	def get_response(self):
		user = self.request.user
		#if user.parent:
		#	user = user.parent
		serializer = MobUserSerializer(instance=user) # TODO context
		return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
		self.serializer = self.get_serializer(data=self.request.data)
		self.serializer.is_valid(raise_exception=True)
		self.bind()
		return self.get_response()
