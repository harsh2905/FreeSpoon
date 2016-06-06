import datetime

from django.http import HttpResponseRedirect
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import mixins
from rest_framework import views
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
from .models import *
from .serializers import *

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
	serializer_class = ResellerSocialLoginSerializer
	jwtSerializerClass = ResellerJWTSerializer

class DispatcherLoginView(
	LoginViewMixIn,
	BaseLoginView):
	serializer_class = DispatcherLoginSerializer
	jwtSerializerClass = DispatcherJWTSerializer

class DispatcherWeixinLogin(
	LoginViewMixIn,
	BaseWeixinLogin):
	serializer_class = DispatcherSocialLoginSerializer
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

# General API

#class BulkViewSet(viewsets.ModelViewSet):
#	queryset = Bulk.objects.all()
#	serializer_class = BulkListSerializer

class DateTimePaginationMixIn(object):
	pageinationLimitField = 'create_time'
	pageinationLimitQueryParamName = 'time'
	pageinationSizeQueryParamName = 'size'
	pageinationModel = None
	pageinationSerializerClass = None
	
	def list(self, request):
		limitName = request.data.get(self.pageinationLimitQueryParamName, 'time')
		sizeName = request.data.get(self.pageinationLimitQueryParamName, 'size')
		limit = request.query_params.get(limitName, 0)
		limit = int(limit)
		limit = limit / 10**6
		limit = datetime.datetime.fromtimestamp(limit)
		size = request.query_params.get(sizeName, 10)
		size = int(size)
		queryset = self.pageinationModel.objects.filter(**{
			'%s__gt' % self.pageinationLimitField: limit
		}).order_by('-%s' % self.pageinationLimitField)[:size]
		serializer = self.pageinationSerializerClass(queryset,
			many=True, context={'request': request})
		return Response(serializer.data)

class BulkViewSet(DateTimePaginationMixIn, viewsets.ViewSet):

	pageinationLimitField = 'create_time'
	pageinationLimitQueryParamName = 'time'
	pageinationModel = Bulk
	pageinationSerializerClass = BulkListSerializer

	#def list(self, request):
	#	queryset = Bulk.objects.all()
	#	serializer = BulkListSerializer(queryset, 
	#		many=True, context={'request': request})
	#	return Response(serializer.data)

	def retrieve(self, request, pk=None):
		queryset = Bulk.objects.all()
		try:
			bulk = queryset.get(pk=pk)
			serializer = BulkSerializer(bulk, 
				context={'request': request, 'pk': pk})
			return Response(serializer.data)
		except queryset.model.DoesNotExist:
			return Response(status=status.HTTP_204_NO_CONTENT)

class ProductViewSet(viewsets.ViewSet):
	
	def retrieve(self, request, pk=None):
		queryset = Product.objects.all()
		try:
			product = queryset.get(pk=pk)
			serializer = ProductSerializer(product,
				context={'request': request})
			return Response(serializer.data)
		except queryset.model.DoesNotExist:
			return Response(status=status.HTTP_204_NO_CONTENT)

#class PurchasedProductHistoryViewSet(viewsets.ViewSet):
#
#	def list(self, request):
#		product_id = request.query_params.get('product_id', None)
#		if not product_id:
#			raise BadRequestException('Product id is required')
#		order_id = request.query_params.get('order_id', None)
#		if not order_id:
#			raise BadRequestException('Order id is required')
#		queryset = PurchasedProductHistory.objects.filter(
#			product_id=product_id, order_id=order_id)
#		serializer = PurchasedProductHistorySerializer(
#			queryset, many=True, context={'request': request})
#		return Response(serializer.data)

class PurchasedProductHistoryView(views.APIView):
	
	def get(self, request, format=None):
		product_id = request.query_params.get('product_id', None)
		if not product_id:
			raise BadRequestException('Product id is required')
		bulk_id = request.query_params.get('bulk_id', None)
		if not bulk_id:
			raise BadRequestException('Bulk id is required')
		queryset = PurchasedProductHistory.objects.filter(
			product_id=product_id, bulk_id=bulk_id)
		serializer = PurchasedProductHistorySerializer(
			queryset, many=True, context={'request': request})
		return Response(serializer.data)
		




