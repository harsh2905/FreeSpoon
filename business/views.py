import datetime
import hashlib

from django.utils.timezone import UTC
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, OperationalError
from django.core.files.base import ContentFile
from django.db.models import Q

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
	parser_classes,
)
from rest_framework.parsers import (
	MultiPartParser,
	FileUploadParser
)

from rest_auth.views import LoginView as BaseLoginView
from authentication.views import WeixinLogin as BaseWeixinLogin
from authentication.views import BindView as BaseBindView

from django.shortcuts import render

from . import config
from . import utils
from .exceptions import *
from .models import *
from .serializers import *
from .paginations import *
from .viewsets import *
from .filters import *
from .generics import *
from .sms import *

from .wx import *

# Create your views here.

def error():
	return HttpResponse('Bad Request')

@require_GET
def redirect(request, relativePath):
	state = request.GET.get('state', None)
	if state is None:
		return error()
	targetUrl = '%s%s' % (config.MOBILE_DOMAIN_URL, relativePath)
	redirectUrl = WxApp.get_current(request).createAuthorizeRedirectUrl(targetUrl, state)
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

	def bind(self):
		super(BindView, self).bind()
		mob_user = self.serializer.validated_data.get('user', None)
		user = self.serializer.validated_data.get('wrap_user', None)
		reseller = self.serializer.validated_data.get('wrap_reseller', None)
		dispatcher = self.serializer.validated_data.get('wrap_dispatcher', None)
		if not mob_user:
			return
		if user:
			try:
				user.name = mob_user.real_wx_nickname
				user.save()
			except Exception, e:
				user.name = '#'
				user.save()
		if reseller:
			try:
				reseller.name = mob_user.real_wx_nickname
				reseller.save()
			except Exception, e:
				reseller.name = '#'
				reseller.save()
		if dispatcher:
			try:
				dispatcher.name = mob_user.real_wx_nickname
				dispatcher.save()
			except Exception, e:
				dispatcher.name = '#'
				dispatcher.save()


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

# Web Only

@api_view(['POST'])
@permission_classes([AllowAny])
def wxConfig(request):

	"""
	Web Only"""

	jsApiList = request.data.get('jsApiList', None)
	if jsApiList is None:
		raise BadRequestException(detail='jsApiList is required')
	url = request.data.get('url', None)
	if url is None:
		raise BadRequestException(detail='url is required')
	wxConfig = WxApp.get_current(request).createWXConfig(url, jsApiList)
	return Response(wxConfig)

# General API

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userDetail(request):
	mob_user = request.user
	if mob_user is None:
		raise BadRequestException(detail='Mob user not found')
	user = None
	reseller = None
	dispatcher = None
	try:
		user = User.objects.get(mob_user=mob_user)
	except ObjectDoesNotExist:
		pass
	try:
		reseller = Reseller.objects.get(mob_user=mob_user)
	except ObjectDoesNotExist:
		pass
	try:
		dispatcher = Dispatcher.objects.get(mob_user=mob_user)
	except ObjectDoesNotExist:
		pass

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
		'flag': flag
	}
	serializer = JWTSerializer(instance=data, context={'request': request})
	return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def payNotify(request, appid):
	error = {
		"return_code": "FAIL"
	}
	wxapp = WxApp.get(appid)
	if wxapp is None:
		error['return_msg'] = 'Error'
		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	order_id = wxapp.payNotify(request.body)
	if order_id is None:
		error['return_msg'] = 'Error'
		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	order_id = int(order_id)
	payrequest = None
	try:
		payrequest = PayRequest.objects.get(third_party_order_id=order_id)
	except ObjectDoesNotExist:
		error['return_msg'] = 'Error'
		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	if payrequest is None:
		error['return_msg'] = 'Error'
		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	order = payrequest.order
	user = order.user
	if payrequest.status > 0:
		error['return_msg'] = 'Error'
		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	if order.status > 0:
		error['return_msg'] = 'Error'
		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	payrequest.status = 1
	payrequest.save()
	order.status = 1
	order.save()
	for goods in order.goods_set.all():
		product = goods.product
		product.purchased += goods.quantity
		product.save()
	user.balance -= payrequest.balance_fee
	user.save()
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

	def get_pay_request(self, order_id, balance, request):
		ip_address = '127.0.0.1'
		if 'HTTP_X_FORWARDED_FOR' in request.META:
			ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '127.0.0.1')
		if 'REMOTE_ADDR' in request.META:
			ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

		openid = None
		mob_user = request.user
		if mob_user:
			openid = mob_user.get_wx_openid(request)
		user = mob_user.user
		if user is None:
			raise BadRequestException(detail='User not found')
		order = None
		try:
			order = Order.objects.get(pk=order_id)
		except ObjectDoesNotExist:
			raise BadRequestException(detail='Order not found')
		if order is None:
			raise BadRequestException(detail='Order not found')
		if order.bulk is None:
			raise BadRequestException(detail='Bulk not found')
		if order.bulk.status < 0 or order.bulk.dead_time < datetime.datetime.now(tz=UTC()):
			raise BadRequestException(detail='Order has been expired')
		errs = []
		for goods in order.goods_set.all():
			stock = goods.product.stock
			if stock is not None and stock > 0:
				purchased = goods.product.purchased
				if stock < (purchased + goods.quantity):
					errs.append({
						'product_id': goods.product_id,
						'product_title': goods.product.title
					})
		if len(errs) > 0:
			exception = BadRequestException(errcode=-2, detail=errs)
			exception.status_code = 200
			raise exception
		if hasattr(order, 'payrequest'):
			order.payrequest.delete()
		total_fee = order.total_fee
		balance_fee = 0
		third_party_fee = 0
		require_third_party_payment = True
		if balance:
			if user.balance >= total_fee:
				require_third_party_payment = False
				balance_fee = total_fee
				third_party_fee = 0
			else:
				balance_fee = user.balance
				third_party_fee = total_fee - user.balance
		else:
			third_party_fee = total_fee
		payrequest = PayRequest(
			order=order,
			third_party_order_id=utils.createOrderId(),
			third_party_fee=third_party_fee,
			balance_fee=balance_fee,
			use_balance=balance,
			status=0
		)
		payrequest.save()

		if not require_third_party_payment:
			payrequest.status = 1
			payrequest.save()
			order.status = 1
			order.save()
			user.balance -= payrequest.balance_fee
			user.save()
			for goods in order.goods_set.all():
				product = goods.product
				product.purchased += goods.quantity
				product.save()
			data = {
				'require_third_party_payment': require_third_party_payment,
				'pay_request_json': None,
				'order': order
			}
			serializer = PayRequestSerializer(instance=data, context={'request': self.request})
			return serializer.data

		time_start = datetime.datetime.now()
		time_expire = time_start + datetime.timedelta(minutes=30)

		prepay_id = WxApp.get_current(request).createPrepayId(
			order_id=order.payrequest.third_party_order_id,
			total_fee=third_party_fee,
			ip_address=ip_address,
			time_start=time_start,
			time_expire=time_expire,
			openid=openid,
			title=order.bulk.title,
			detail=order.bulk.details,
			notify_url=reverse('payNotify', request=request, kwargs={'appid': WxApp.get_current(request).appid})
		)
		if prepay_id is None:
			raise BadRequestException(detail='Failed to create pre pay order')
		data = {
			'require_third_party_payment': require_third_party_payment,
			'pay_request_json': WxApp.get_current(request).createPayRequestJson(prepay_id),
			'order': None
		}
		serializer = PayRequestSerializer(instance=data, context={'request': self.request})
		return serializer.data

	def get(self, request, *args, **kwargs):
		lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

		assert lookup_url_kwarg in self.kwargs, (
				'Expected view %s to be called with a URL keyword argument '
				'named "%s". Fix your URL conf, or set the `.lookup_field` '
				'attribute on the view correctly.' %
				(self.__class__.__name__, lookup_url_kwarg)
		)

		pk = self.kwargs[lookup_url_kwarg]
		balance = request.query_params.get('balance', True)
		try:
			balance = int(balance)
			balance = bool(balance)
		except ValueError:
			balance = True

		result = self.get_pay_request(pk, balance, request)
		return Response(result, status=status.HTTP_200_OK)

class BulkViewSet(ModelViewSet):
	queryset = Bulk.objects.all()
	serializer_class_list = BulkListSerializer
	serializer_class_retrieve = BulkSerializer
	serializer_class_create = BulkCreateSerializer
	serializer_class_update = BulkUpdateSerializer
	pagination_class = TimestampPagination

	pagination_field_name = 'dead_time'
	pagination_lookup_type = 'lt'

	filter_backends = (filters.SearchFilter, FieldOrderBackend, FieldFilterBackend, MethodFilterBackend,)

	filter_fields = ['reseller_id']
	filter_field_raise_exception = False

	def retrieve(self, request, pk=None):
		queryset = Bulk.objects.all()
		bulk = get_object_or_404(queryset, pk=pk)
		serializer = BulkSerializer(bulk, 
			context={'request': request, 'pk': pk})
		return Response(serializer.data)

	def update_bulk_status(self, queryset):
		queryset.filter(Q(start_time__lt=datetime.datetime.now(tz=UTC())) & Q(status=-2)).update(status=0)
		queryset.filter(Q(dead_time__lt=datetime.datetime.now(tz=UTC())) & Q(status=0)).update(status=-1)
		return queryset

	filter_method = update_bulk_status

	#search_fields = ('$products__title',)
	search_fields = ('$products__title', '$reseller__name')

	order_fields = ['-dead_time']

class ProductViewSet(ModelViewSet):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	serializer_class_retrieve = ProductSerializer
	filter_backends = (FieldFilterBackend,)

	filter_fields = ['is_snapshot', 'category']
	filter_field_raise_exception = False

class CategoryViewSet(ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = [IsAuthenticated]

class ShippingAddressViewSet(ModelViewSet):
	queryset = ShippingAddress.objects.all()
	serializer_class = ShippingAddressSerializer
	permission_classes = [IsAuthenticated]
	filter_backends = (IsOwnedByUserFilterBackend,)

class StorageViewSet(ModelViewSet):
	queryset = Storage.objects.all()
	serializer_class = StorageSerializer

	class IsOwnedByResellerFilterBackend(filters.BaseFilterBackend):
		def filter_queryset(self, request, queryset, view):
			mob_user = request.user
			if mob_user is None:
				raise BadRequestException(detail='Mob user not found')
			return queryset.filter(Q(reseller=mob_user.reseller) | Q(is_custom=False))

	filter_backends = (FieldFilterBackend, IsOwnedByResellerFilterBackend,)

	filter_fields = ['is_custom']
	filter_field_raise_exception = False

class BulkSummaryViewSet(ReadOnlyModelViewSet):
	queryset = BulkSummary.objects.all()
	serializer_class = BulkSummarySerializer
	filter_backends = (FieldFilterBackend,)

	filter_fields = ['bulk_id']
	filter_field_raise_exception = False

class PurchasedProductHistoryViewSet(ReadOnlyModelViewSet):
	queryset = PurchasedProductHistory.objects.all()
	serializer_class = PurchasedProductHistorySerializer
	filter_backends = (FieldFilterBackend, FieldOrderBackend,)

	filter_fields = ['product_id', 'bulk_id']
	filter_field_raise_exception = True

	order_fields = ['-create_time']
	
class OrderViewSet(ModelViewSet):
	queryset = Order.objects.filter(is_delete=False)
	serializer_class = OrderSerializer
	serializer_class_list = OrderListSerializer
	serializer_class_create = OrderCreateSerializer
	serializer_class_update = OrderUpdateSerializer
	permission_classes = [IsAuthenticated]
	filter_backends = (IsOwnedByUserFilterBackend, FieldOrderBackend, MethodFilterBackend,)
	
	pagination_class = TimestampPagination

	pagination_field_name = 'create_time'
	pagination_lookup_type = 'lt'

	def update_order_status(self, queryset):
		queryset.filter(Q(status=0) & (Q(bulk__status=-1) | Q(bulk__status__lt=0) | Q(bulk__dead_time__lt=datetime.datetime.now(tz=UTC())))).update(status=-1)
		queryset.filter(Q(status=1) & (Q(bulk__status=-1) | Q(bulk__status__lt=0) | Q(bulk__dead_time__lt=datetime.datetime.now(tz=UTC())))).update(status=2)
		return queryset

	filter_method = update_order_status

	order_fields = ['-create_time']

	def perform_destroy(self, instance):
		if instance.status > 1:
			raise BadRequestException(detail='Refused to destroy order')
		if instance.status > 0:
			instance.user.balance += instance.total_fee
			for goods in instance.goods_set.all():
				product = goods.product
				product.purchased -= goods.quantity
				product.save()
			instance.user.save()
		instance.is_delete = True
		instance.save()

class RecipeViewSet(ModelViewSet):
	queryset = Recipe.objects.all()
	serializer_class_update = RecipeUpdateSerializer
	serializer_class_create = RecipeCreateSerializer
	serializer_class = RecipeSerializer
	#permission_classes = [AllowAny]
	pagination_class = TimestampPagination

	pagination_field_name = 'create_time'
	pagination_lookup_type = 'lt'

	filter_backends = (filters.SearchFilter, FieldOrderBackend, FieldFilterBackend, MoreFilterBackend)

	filter_fields = ['user_id']
	filter_field_raise_exception = False

	search_fields = ('$name', '$user__name')

	order_fields = ['-create_time']

class DishViewSet(ModelViewSet):
	queryset = Dish.objects.all()
	serializer_class_update = DishUpdateSerializer
	serializer_class_create = DishCreateSerializer
	serializer_class = DishSerializer
	#permission_classes = [AllowAny]
	pagination_class = TimestampPagination

	pagination_field_name = 'create_time'
	pagination_lookup_type = 'lt'

	filter_backends = (filters.SearchFilter, FieldOrderBackend, FieldFilterBackend, MoreFilterBackend)

	filter_fields = ['user_id']
	filter_field_raise_exception = False

	search_fields = ('$name', '$user__name')

	order_fields = ['-create_time']

@api_view(['GET'])
@permission_classes([AllowAny])
def index(request):
	now = datetime.datetime.now(tz=UTC()) 
	data = Exhibit.objects.filter(
		publish_time__lt=now).order_by('-publish_time').first()
	serializer = ExhibitSerializer(instance=data, context={'request': request})
	return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def recipe_index(request):
	now = datetime.datetime.now(tz=UTC()) 
	data = RecipeExhibit.objects.filter(
		publish_time__lt=now).order_by('-publish_time').first()
	serializer = RecipeExhibitSerializer(instance=data, context={'request': request})
	return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser])
def image_create(request):
	f = request.data.get('file', None)
	if f:
		try:
			f.name = utils.nonceStr()
			md5 = hashlib.md5()
			for chunk in f.chunks():
				md5.update(chunk)
			md5 = md5.hexdigest()
			image, created = Image.objects.get_or_create(
				pk=md5,
				defaults={
					'image': f
				}
			)
			serializer = ImageSerializer(instance=image, context={'request': request})
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		except IntegrityError:
			pass
	return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['GET'])
@permission_classes([AllowAny])
def image_retrieve(request, pk):
	if pk:
		try:
			image = Image.objects.get(pk=pk)
			serializer = ImageSerializer(instance=image, context={'request': request})
			return Response(serializer.data, status=status.HTTP_200_OK)
		except ObjectDoesNotExist:
			pass
	return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def sms(request, mob):
	if mob and SmsApp.send(mob):
		return Response(status=status.HTTP_204_NO_CONTENT)
	raise BadRequestException(detail='SMS sending failure')

	
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_reseller(request):
	mob_user = request.user
	if not mob_user:
		raise BadRequestException(detail='Mob User not found')
	# name = request.data.get('name', None)
	name = mob_user.real_wx_nickname if mob_user.real_wx_nickname else mob_user.mob
	name = utils.filter_emoji(name)
	try:
		reseller = Reseller.objects.create(
			mob_user=mob_user, 
			name=name,
			state=1)
	except IntegrityError:
		raise BadRequestException(detail='Submit duplicate')
	serializer = ResellerSerializer(instance=reseller, context={'request': request})
	return Response(serializer.data, status=status.HTTP_200_OK)
	
