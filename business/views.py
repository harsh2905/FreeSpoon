from django.http import HttpResponseRedirect
from django.views.decorators.http import require_GET

from rest_framework.decorators import (
	api_view,
	permission_classes,
)
from rest_framework.response import Response

from django.shortcuts import render

from . import config
from wx import Auth as wxAuthClass
from .exceptions import *

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

# Web Only

@api_view(['POST'])
def wxConfig(request):
	jsApiList = request.data.get('jsApiList', None)
	if jsApiList is None:
		raise BadRequestException('jsApiList is required')
	url = request.data.get('url', None)
	if url is None:
		raise BadRequestException('url is required')
	wxConfig = wx.createWXConfig(url, jsApiList)
	return Response(wxConfig)
