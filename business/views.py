from django.http import HttpResponseRedirect
from django.views.decorators.http import require_GET

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import (
	api_view,
	permission_classes,
)

from rest_auth.views import LoginView as BaseLoginView
from authentication.views import WeixinLogin as BaseWeixinLogin

from django.shortcuts import render

from . import config
from wx import Auth as wxAuthClass
from .exceptions import *
from .serializers import (
	UserLoginSerializer,
	UserSocialLoginSerializer,
	UserJWTSerializer,
	ResellerLoginSerializer,
	ResellerSocialLoginSerializer,
	ResellerJWTSerializer,
	DispatcherLoginSerializer,
	DispatcherSocialLoginSerializer,
	DispatcherJWTSerializer,
)

wx = wxAuthClass()

# Create your views here.

def error():
	return HttpResponse('Bad Request')

def main(request):
	return HttpResponse('FreeSpoon API v0.0.1')

@require_GET
def redirect(request, relativePath):
	state = request.GET.get('state', None)
	if state is None:
		return error()
	targetUrl = '%s%s' % (config.DOMAIN_URL, relativePath)
	redirectUrl = wx.createAuthorizeBaseRedirectUrl(targetUrl, state)
	return HttpResponseRedirect(redirectUrl)

# REST API

# Authentication

class LoginViewMixIn(object):

	jwtSerializerClass = None # Must implement it in sub class

	def get_response(self):
		user = self.serializer.validated_data['wrap_user']

        	data = {
        	    'user': user,
        	    'token': self.token
        	}
        	serializer = self.jwtSerializerClass(instance=data, context={'request': self.request})

        	return Response(serializer.data, status=status.HTTP_200_OK)

class UserLoginView(
	LoginViewMixIn,
	BaseLoginView):
	serializer_class = UserLoginSerializer
	jwtSerializerClass = UserJWTSerializer

class WeixinLogin(
	LoginViewMixIn,
	BaseWeixinLogin):
	serializer_class = UserSocialLoginSerializer
	jwtSerializerClass = UserJWTSerializer

class ResellerLoginView(
	LoginViewMixIn,
	BaseLoginView):
	serializer_class = ResellerLoginSerializer
	jwtSerializerClass = ResellerJWTSerializer

class ResellerWeixinLogin(
	LoginViewMixIn,
	BaseWeixinLogin):
	serializer_class = ResellerLoginSerializer
	jwtSerializerClass = ResellerJWTSerializer

class DispatcherLoginView(
	LoginViewMixIn,
	BaseLoginView):
	serializer_class = DispatcherLoginSerializer
	jwtSerializerClass = DispatcherJWTSerializer

class DispatcherWeixinLogin(
	LoginViewMixIn,
	BaseWeixinLogin):
	serializer_class = DispatcherLoginSerializer
	jwtSerializerClass = DispatcherJWTSerializer

# Web Only

@api_view(['POST'])
def wxConfig(request):

	"""
	Web Only"""

	jsApiList = request.data.get('jsApiList', None)
	if jsApiList is None:
		raise BadRequestException('jsApiList is required')
	url = request.data.get('url', None)
	if url is None:
		raise BadRequestException('url is required')
	wxConfig = wx.createWXConfig(url, jsApiList)
	return Response(wxConfig)

class BatchViewSet(viewsets.ViewSet):
	pass
