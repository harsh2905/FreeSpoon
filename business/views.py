import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import mixins
from rest_framework import views
from rest_framework import filters
#from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import (
	AllowAny,
	IsAuthenticated
)
from rest_framework.decorators import (
	api_view,
	permission_classes,
)

from rest_auth.views import LoginView as BaseLoginView
from authentication.views import WeixinLogin as BaseWeixinLogin
from authentication.views import BindView as BaseBindView

from django.shortcuts import render

from . import config
from .exceptions import *
from .models import *
from .serializers import *
from .paginations import *
from .viewsets import *
from .filters import *
from .generics import *

from .wx import *

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
	redirectUrl = WxApp.get_current(request).createAuthorizeBaseRedirectUrl(targetUrl, state)
	return HttpResponseRedirect(redirectUrl)

# REST API

# Authentication

class LoginViewMixIn(object):

	def get_response(self):
		mob_user = self.serializer.validated_data.get('user', None)
		user = self.serializer.validated_data.get('wrap_user', None)
		reseller = self.serializer.validated_data.get('wrap_reseller', None)
		dispatcher = self.serializer.validated_data.get('wrap_dispatcher', None)


		flag = 0
		if user:
			flag = flag | 1
		if reseller:
			flag = flag | (1 << 1)
		if dispatcher:
			flag = flag | (1 << 2)

		data = {
			'mob_user': mob_user,
			'user': user,
			'reseller': reseller,
			'dispatcher': dispatcher,
			'token': self.token,
			'flag': flag
		}
		serializer = JWTSerializer(instance=data, context={'request': self.request})

		return Response(serializer.data, status=status.HTTP_200_OK)

class UserLoginView(
	LoginViewMixIn,
	BaseLoginView):
	serializer_class = LoginSerializer

class WeixinLoginView(
	LoginViewMixIn,
	BaseWeixinLogin):
	serializer_class = SocialLoginSerializer

class BindView(
	BaseBindView):
	serializer_class = BindSerializer

	def get_response(self):
		mob_user = self.serializer.validated_data.get('user', None)
		user = self.serializer.validated_data.get('wrap_user', None)
		reseller = self.serializer.validated_data.get('wrap_reseller', None)
		dispatcher = self.serializer.validated_data.get('wrap_dispatcher', None)

		flag = 0
		if user:
			flag = flag | 1
		if reseller:
			flag = flag | (1 << 1)
		if dispatcher:
			flag = flag | (1 << 2)

		data = {
			'mob_user': self.mob_user,
			'user': user,
			'reseller': reseller,
			'dispatcher': dispatcher,
			'token': self.token,
			'flag': flag
		}
		serializer = JWTSerializer(instance=data, context={'request': self.request})

		return Response(serializer.data, status=status.HTTP_200_OK)

#class LoginViewMixIn(object):
#
#	jwtSerializerClass = None # Must implement it in sub class
#
#	def get_response(self):
#		user = self.serializer.validated_data['wrap_user']
#
#        	data = {
#        	    'user': user,
#        	    'token': self.token
#        	}
#        	serializer = self.jwtSerializerClass(instance=data, context={'request': self.request})
#
#        	return Response(serializer.data, status=status.HTTP_200_OK)
#
#class UserLoginView(
#	LoginViewMixIn,
#	BaseLoginView):
#	serializer_class = UserLoginSerializer
#	jwtSerializerClass = UserJWTSerializer
#
#class WeixinLogin(
#	LoginViewMixIn,
#	BaseWeixinLogin):
#	serializer_class = UserSocialLoginSerializer
#	jwtSerializerClass = UserJWTSerializer
#
#class ResellerLoginView(
#	LoginViewMixIn,
#	BaseLoginView):
#	serializer_class = ResellerLoginSerializer
#	jwtSerializerClass = ResellerJWTSerializer
#
#class ResellerWeixinLogin(
#	LoginViewMixIn,
#	BaseWeixinLogin):
#	serializer_class = ResellerSocialLoginSerializer
#	jwtSerializerClass = ResellerJWTSerializer
#
#class DispatcherLoginView(
#	LoginViewMixIn,
#	BaseLoginView):
#	serializer_class = DispatcherLoginSerializer
#	jwtSerializerClass = DispatcherJWTSerializer
#
#class DispatcherWeixinLogin(
#	LoginViewMixIn,
#	BaseWeixinLogin):
#	serializer_class = DispatcherSocialLoginSerializer
#	jwtSerializerClass = DispatcherJWTSerializer

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
	wxConfig = WxApp.get_current(request).createWXConfig(url, jsApiList)
	return Response(wxConfig)

# General API

@api_view(['POST'])
@permission_classes([AllowAny])
def payNotify(request):
	error = {
		"return_code": "FAIL"
	}
	order_id = WxApp.get_current(request).payNotify(request.body)
	if order_id is None:
		error['return_msg'] = 'Error'
    		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	order_id = int(order_id)
	order = None
	try:
		order = Order.objects.get(pk=order_id)
	except ObjectDoesNotExist:
		raise BadRequestException('Order not found')
	if order is None:
		error['return_msg'] = 'Error'
    		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	if order.status > 0:
		error['return_msg'] = 'Error'
    		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	order.status = 1
	order.save()
	success = {
		"return_code": "SUCCESS",
		"return_msg": ""
	}
	xml = utils.mapToXml(success)
	return HttpResponse(xml,
		content_type='text/xml')

class payRequest(views.APIView):
	permission_classes = [IsAuthenticated]

	lookup_field = 'pk'
	lookup_url_kwarg = None

	def get_pay_request(self, order_id, request):
		ip_address = '127.0.0.1'
		if 'HTTP_X_FORWARDED_FOR' in request.META:
			ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '127.0.0.1')
		if 'REMOTE_ADDR' in request.META:
			ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

		openid = None
		mob_user = request.user
		if mob_user:
			openid = mob_user.real_wx_openid
		user = mob_user.user
		if user is None:
			raise BadRequestException('User not found')
		order = None
		try:
			order = Order.objects.get(pk=order_id)
		except ObjectDoesNotExist:
			raise BadRequestException('Order not found')
		if order is None:
			raise BadRequestException('Order not found')

		time_start = datetime.datetime.now()
		time_expire = time_start + datetime.timedelta(minutes=30)

		prepay_id = WxApp.get_current(request).createPrepayId(
			order_id=order_id,
			total_fee=order.total_fee,
			ip_address=ip_address,
			time_start=time_start,
			time_expire=time_expire,
			openid=openid,
			title=order.bulk.title,
			detail=order.bulk.details,
			notify_url=reverse('payNotify', request=request)
		)
		if prepay_id is None:
			raise BadRequestException('Failed to create pre pay order')
		return WxApp.get_current(request).createPayRequestJson(prepay_id)

	def get(self, request, *args, **kwargs):
		lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

		assert lookup_url_kwarg in self.kwargs, (
				'Expected view %s to be called with a URL keyword argument '
				'named "%s". Fix your URL conf, or set the `.lookup_field` '
				'attribute on the view correctly.' %
				(self.__class__.__name__, lookup_url_kwarg)
		)

		pk = self.kwargs[lookup_url_kwarg]

		result = self.get_pay_request(pk, request)
		return Response(result, status=status.HTTP_200_OK)

class BulkViewSet(ModelViewSet):
	queryset = Bulk.objects.all()
	serializer_class_list = BulkListSerializer
	serializer_class_retrieve = BulkSerializer
	pagination_class = TimestampPagination

	pagination_field_name = 'create_time'
	pagination_lookup_type = 'lt'

	filter_backends = (filters.SearchFilter, FieldOrderBackend,)

	search_fields = ('$products__title',)

	order_fields = ['-dead_time']

class ProductViewSet(ModelViewSet):
	queryset = Product.objects.all()
	serializer_class_retrieve = ProductSerializer

class ShippingAddressViewSet(ModelViewSet):
	queryset = ShippingAddress.objects.all()
	serializer_class = ShippingAddressSerializer
	permission_classes = [IsAuthenticated]
	filter_backends = (IsOwnedByUserFilterBackend,)

class PurchasedProductHistoryViewSet(ReadOnlyModelViewSet):
	queryset = PurchasedProductHistory.objects.all()
	serializer_class = PurchasedProductHistorySerializer
	filter_backends = (FieldFilterBackend,)

	filter_fields = ['product_id']
	filter_field_raise_exception = True
	
class OrderViewSet(ModelViewSet):
	queryset = Order.objects.filter(is_delete=False)
	serializer_class = OrderSerializer
	serializer_class_list = OrderListSerializer
	serializer_class_create = OrderCreateSerializer
	serializer_class_update = OrderUpdateSerializer
	permission_classes = [IsAuthenticated]
	filter_backends = (IsOwnedByUserFilterBackend, FieldOrderBackend,)

	order_fields = ['-create_time']

	def perform_destroy(self, instance):
		if instance.status > 1:
			raise BadRequestException('Refused to destroy order')
		if instance.status > 0:
			instance.user.balance += instance.total_fee
			instance.user.save()
		instance.is_delete = True
		instance.save()





