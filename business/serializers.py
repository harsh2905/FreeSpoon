from django.db.models import Sum
from rest_framework import exceptions

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.reverse import reverse
from authentication.serializers import LoginSerializer as BaseLoginSerializer
from rest_auth.registration.serializers import SocialLoginSerializer as BaseSocialLoginSerializer

from . import config
from .models import *
from .fields import *
from .exceptions import *
from . import utils

from collections import OrderedDict
from rest_framework.relations import PKOnlyObject
from rest_framework.fields import SkipField

from authentication.serializers import MobUserSerializer

from .wx2 import *
from wx import Auth as wxAuthClass
wx = wxAuthClass()

class RemoveNullSerializerMixIn(serializers.Serializer):
	def to_representation(self, instance):
		"""
		Object instance -> Dict of primitive datatypes.
		"""
		ret = OrderedDict()
		fields = self._readable_fields
		
		for field in fields:
			try:
				attribute = field.get_attribute(instance)
			except SkipField:
				continue
			
			# We skip `to_representation` for `None` values so that fields do
			# not have to explicitly deal with that case.
			#
			# For related fields with `use_pk_only_optimization` we need to
			# resolve the pk value.
			check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
			if check_for_none is None:
				#ret[field.field_name] = None
				pass
			else:
				value = field.to_representation(attribute)
				if value is not None:
					ret[field.field_name] = value
		
		return ret

class WeixinSerializerMixIn(RemoveNullSerializerMixIn, serializers.Serializer):
	wx_nickname = serializers.CharField(source='mob_user.real_wx_nickname', read_only=True) # TODO not null
	wx_headimgurl = serializers.CharField(source='mob_user.real_wx_headimgurl', read_only=True)

class UserSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.real_mob')
	create_time = TimestampField()
	class Meta:
		model = User
		fields = ('id', 'name', 'create_time', 'mob', 
			'recent_obtain_name', 'recent_obtain_mob', 
			'wx_nickname', 'wx_headimgurl')

class LoginUserSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	class Meta:
		model = User
		fields = ('create_time',
			'recent_obtain_name', 'recent_obtain_mob')

#class UserJWTSerializer(serializers.Serializer):
#	token = serializers.CharField()
#	user = UserSerializer()

class ResellerSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.real_mob')
	create_time = TimestampField()
	class Meta:
		model = Reseller
		fields = ('id', 'name', 'tail', 'create_time', 
			'mob', 'wx_nickname', 'wx_headimgurl')

class LoginResellerSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	class Meta:
		model = Reseller
		fields = ('tail', 'create_time')

#class ResellerJWTSerializer(serializers.Serializer):
#	token = serializers.CharField()
#	user = ResellerSerializer()

class DispatcherSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.real_mob')
	create_time = TimestampField()
	class Meta:
		model = Dispatcher
		fields = ('id', 'name', 'tail', 'address', 
			'create_time', 'mob', 'opening_time', 
			'closing_time', 'wx_nickname', 'wx_headimgurl')

class LoginDispatcherSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	class Meta:
		model = Dispatcher
		fields = ('tail', 'address', 
			'create_time', 'opening_time', 
			'closing_time')

#class DispatcherJWTSerializer(serializers.Serializer):
#	token = serializers.CharField()
#	user = DispatcherSerializer()

class JWTSerializer(serializers.Serializer):
	flag = serializers.IntegerField()
	token = serializers.CharField()
	mob_user = MobUserSerializer()
	user = LoginUserSerializer()
	reseller = LoginResellerSerializer()
	dispatcher = LoginDispatcherSerializer()

class LoginSerializerMixIn(serializers.Serializer):
	name = serializers.CharField(required=False, allow_blank=True)

	baseClass = None # Must implement it in sub class

	def validate(self, attrs):
		attrs = self.baseClass.validate(self, attrs)
		mob_user = attrs['user']
		if not mob_user:
			msg = _('Unable to log in with provided credentials.')
			raise exceptions.ValidationError(msg)
		user, created = User.objects.get_or_create(
			mob_user=mob_user,
			defaults={}
		)
		attrs['wrap_user'] = user
		try:
			reseller = Reseller.objects.get(mob_user=mob_user)
			attrs['wrap_reseller'] = reseller
		except ObjectDoesNotExist:
			pass
		try:
			dispatcher = Dispatcher.objects.get(mob_user=mob_user)
			attrs['wrap_dispatcher'] = dispatcher
		except ObjectDoesNotExist:
			pass
		return attrs

class LoginSerializer(
	LoginSerializerMixIn, 
	BaseLoginSerializer):
	baseClass = BaseLoginSerializer

class SocialLoginSerializer(
	LoginSerializerMixIn, 
	BaseSocialLoginSerializer):
	baseClass = BaseSocialLoginSerializer

#class LoginSerializerMixIn(serializers.Serializer):
#	name = serializers.CharField(required=False, allow_blank=True)
#
#	mainModel = None # Must implement it in sub class
#	parentClass = None # Must implement it in sub class
#	defaultFieldNames = [] # Must implement it in sub class
#
#	def validate(self, attrs):
#		attrs = self.parentClass.validate(self, attrs)
#		mob_user = attrs['user']
#		if mob_user:
#			defaults = {}
#			for fieldName in self.defaultFieldNames:
#				fieldValue = attrs.get(fieldName)
#				if fieldValue:
#					defaults[fieldName] = fieldValue
#			user, created = self.mainModel.objects.get_or_create(
#				mob_user=mob_user,
#				defaults=defaults
#			)
#			attrs['wrap_user'] = user
#		else:
#			msg = _('Unable to log in with provided credentials.')
#			raise exceptions.ValidationError(msg)
#		return attrs
#
#class UserLoginSerializer(
#	LoginSerializerMixIn, 
#	BaseLoginSerializer):
#	parentClass = BaseLoginSerializer
#	defaultFieldNames = ['name']
#	mainModel = User
#
#class UserSocialLoginSerializer(
#	LoginSerializerMixIn, 
#	BaseSocialLoginSerializer):
#	parentClass = BaseSocialLoginSerializer
#	defaultFieldNames = ['name']
#	mainModel = User
#
#class ResellerLoginSerializer(
#	LoginSerializerMixIn, 
#	BaseLoginSerializer):
#	parentClass = BaseLoginSerializer
#	defaultFieldNames = ['name', 'tail']
#	mainModel = Reseller
#
#class ResellerSocialLoginSerializer(
#	LoginSerializerMixIn, 
#	BaseSocialLoginSerializer):
#	parentClass = BaseSocialLoginSerializer
#	defaultFieldNames = ['name', 'tail']
#	mainModel = Reseller
#
#class DispatcherLoginSerializer(
#	LoginSerializerMixIn, 
#	BaseLoginSerializer):
#	parentClass = BaseLoginSerializer
#	defaultFieldNames = ['name', 'tail', 'address']
#	mainModel = Dispatcher
#
#class DispatcherSocialLoginSerializer(
#	LoginSerializerMixIn, 
#	BaseSocialLoginSerializer):
#	parentClass = BaseSocialLoginSerializer
#	defaultFieldNames = ['name', 'tail', 'address']
#	mainModel = Dispatcher

def jwt_response_payload_handler(token, user=None, request=None):
	mob_user = user
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
        	'token': token,
		'flag': flag
        }
        serializer = JWTSerializer(instance=data, context={'request': request})
	return serializer.data

# Business Serializer model

class BulkListSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	#url = serializers.HyperlinkedIdentityField(
	#	view_name='bulk-detail',
	#	lookup_field='id'
	#)
	reseller = ResellerSerializer()
	covers = serializers.SerializerMethodField(method_name='get_product_covers')
	create_time = TimestampField()
	dead_time = TimestampField()
	arrived_time = TimestampField()
	participant_count = serializers.SerializerMethodField()

	class Meta:
		model = Bulk
		fields = ('url', 'id', 'title', 'category', 'reseller', 'covers',
			'dead_time', 'arrived_time', 'status',
			'create_time', 'location', 'participant_count')
		#extra_kwargs = {
		#	'url': {'view_name': 'bulk', 'lookup_field': 'id'}
		#}

	#def get_reseller_name(self, obj):
	#	obj = obj.reseller
	#	if not hasattr(obj, 'mob_user'):
	#		return ''
	#	obj = obj.mob_user
	#	if not obj:
	#		return ''
	#	return obj.real_wx_nickname

	def get_product_covers(self, obj): # So ugly :(
		request = self.context.get('request', None)
		return map(lambda url: 
			url if not request else
			request.build_absolute_uri(url),
			map(lambda p: p.cover.url 
			if hasattr(p.cover, 'url') 
			else '', obj.products.all()))

	def get_participant_count(self, obj):
		return Order.objects.filter(bulk_id=obj.pk).count()

class ProductDetailsSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = ProductDetails
		fields = ('image', 'plain', 'seq')

class ProductListSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	create_time = TimestampField()
	participant_count = serializers.SerializerMethodField()
	purchased_count = serializers.SerializerMethodField()
	participant_avatars = serializers.SerializerMethodField()
	history = serializers.SerializerMethodField()
	details = ProductDetailsSerializer(source='productdetails_set', many=True)

	class Meta:
		model = Product
		fields = ('url', 'id', 'title', 'desc', 'unit_price', 'market_price',
			'spec', 'spec_desc', 'cover', 'create_time', 'details',
			'participant_count', 'purchased_count', 'tag',
			'participant_avatars', 'history')

	def get_participant_count(self, obj):
		return Goods.objects.filter(product_id=obj.pk).count()

	def get_purchased_count(self, obj):
		result = Goods.objects.filter(product_id=obj.pk).aggregate(Sum('quantity'))
		return result.get('quantity__sum', 0)

	def get_participant_avatars(self, obj):
		request = self.context.get('request', None)
		avatars = dict()

		goods = Goods.objects.filter(product_id=obj.pk)
		for _ in goods:
			user = _.order.user
			if user.avatar:
				url = user.avatar.url
				if request:
					url = request.build_absolute_uri(url)
				avatars[user.pk] = url
		return avatars.values()[:6]

	def get_history(self, obj):
		request = self.context.get('request', None)
		if not request:
			return None
		params = {
			'product_id': obj.id,
		}
		url = reverse('purchasedproducthistory-list', request=request)
		return utils.addQueryParams(url, params)

class ProductSerializer(serializers.HyperlinkedModelSerializer):
	details = ProductDetailsSerializer(source='productdetails_set', many=True)

	class Meta:
		model = Product
		fields = ('url', 'id', 'title', 'desc', 'unit_price', 'market_price',
			'spec', 'spec_desc', 'cover', 'create_time',
			'details')

class BulkSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	reseller = ResellerSerializer()
	dispatchers = DispatcherSerializer(many=True)
	create_time = TimestampField()
	dead_time = TimestampField()
	standard_time = StandardTimeField(source='*')
	arrived_time = TimestampField()
	products = ProductListSerializer(many=True)
	participant_count = serializers.SerializerMethodField()
	recent_obtain_name = serializers.SerializerMethodField()
	recent_obtain_mob = serializers.SerializerMethodField()
	card_url = serializers.SerializerMethodField()

	class Meta:
		model = Bulk
		fields = ('url', 'id', 'title', 'category', 'reseller', 'dispatchers', 
			'products', 'location', 'standard_time', 'dead_time', 
			'arrived_time', 'status', 'card_title', 'card_desc',
			'card_icon', 'card_url', 'create_time', 'participant_count',
			'recent_obtain_name', 'recent_obtain_mob')

	def get_participant_count(self, obj):
		return Order.objects.filter(bulk_id=obj.pk).count()

	def get_recent_obtain_name(self, obj):
		request = self.context.get('request', None)
		if request is None:
			return None
		mob_user = request.user
		if mob_user:
			user = User.first(mob_user)
			if user:
				return user.recent_obtain_name
		return None

	def get_recent_obtain_mob(self, obj):
		request = self.context.get('request', None)
		if request is None:
			return None
		mob_user = request.user
		if mob_user:
			user = User.first(mob_user)
			if user:
				return user.recent_obtain_mob
		return None

	def get_card_url(self, obj):
		return config.CARD_URL % obj.id


class ShippingAddressSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = ShippingAddress
		fields = ('url', 'id', 'name', 'mob', 'address')

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException('Bad Request')
		mob_user = request.user
		if mob_user:
			openid = mob_user.real_wx_openid
		user = User.first(mob_user)
		if user is None:
			raise BadRequestException('User not found')

		name = validated_data.get('name')
		mob = validated_data.get('mob')
		address = validated_data.get('address')

		shippingaddress = ShippingAddress.objects.create(
			name=name,
			mob=mob,
			address=address,
			user=user)
		return shippingaddress

class PurchasedProductHistorySerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	order_id = serializers.ReadOnlyField()
	bulk_id = serializers.ReadOnlyField()
	product_id = serializers.ReadOnlyField()
	name = serializers.ReadOnlyField()
	quantity = serializers.ReadOnlyField()
	spec = serializers.ReadOnlyField()
	create_time = TimestampField(read_only=True)

	class Meta:
		model = PurchasedProductHistory
		fields = ('order_id', 'bulk_id', 'product_id', 
			'name', 'quantity', 'spec', 'create_time',
			'wx_nickname', 'wx_headimgurl')

class GoodsCreateSerializer(serializers.Serializer):
	product_id = serializers.IntegerField()
	quantity = serializers.IntegerField()

class GoodsSerializer(serializers.ModelSerializer):
	title = serializers.CharField(source='product.title')
	unit_price = serializers.IntegerField(source='product.unit_price')
	class Meta:
		model = Goods
		fields = ('title', 'quantity', 'unit_price')

class OrderUpdateSerializer(serializers.Serializer):
	status = serializers.IntegerField()

	def update(self, instance, validated_data):
		status = validated_data.get('status')
		instance.status = status
		instance.save()
		return instance

class OrderCreateSerializer(serializers.Serializer):
	goods = GoodsCreateSerializer(many=True)
	ip_address = serializers.CharField()
	obtain_name = serializers.CharField()
	obtain_mob = serializers.CharField()
	bulk_id = serializers.IntegerField()
	dispatcher_id = serializers.IntegerField()

	def create(self, validated_data):
		openid = None
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException('Bad Request')
		mob_user = request.user
		if mob_user:
			openid = mob_user.real_wx_openid
		user = User.first(mob_user)
		if user is None:
			raise BadRequestException('User not found')
		bulk_id = validated_data.get('bulk_id')
		bulk = None
		try:
			bulk = Bulk.objects.get(pk=bulk_id)
		except ObjectDoesNotExist:
			raise BadRequestException('Bulk not found')
		if bulk is None:
			raise BadRequestException('Bulk not found')
		dispatcher_id = validated_data.get('dispatcher_id')
		dispatcher = None
		try:
			dispatcher = Dispatcher.objects.get(pk=dispatcher_id)
		except ObjectDoesNotExist:
			raise BadRequestException('Dispatcher not found')
		if dispatcher is None:
			raise BadRequestException('Dispatcher not found')
		obtain_name = validated_data.get('obtain_name')
		obtain_mob = validated_data.get('obtain_mob')
		ip_address = validated_data.get('ip_address')
		goods = validated_data.get('goods')
		total_fee = 0
		for _ in goods:
			product_id = _.get('product_id')
			quantity = _.get('quantity')
			try:
				product = Product.objects.get(pk=product_id)
				total_fee = product.unit_price * quantity
			except ObjectDoesNotExist:
				raise BadRequestException('Product not found')
		time_start = datetime.datetime.now()
		time_expire = time_start + datetime.timedelta(minutes=30)
		order_id = utils.createOrderId()
		prepay_id = WxApp.get_current(request).createPrepayId(
			order_id=order_id,
			total_fee=total_fee,
			ip_address=ip_address,
			time_start=time_start,
			time_expire=time_expire,
			openid=openid,
			title=bulk.title,
			detail=bulk.details,
			notify_url=reverse('payNotify', request=request)
		)
		if prepay_id is None:
			raise BadRequestException('Failed to create pre pay order')
		order = Order.objects.create(
			id=order_id,
			status=0,
			prepay_id=prepay_id,
			freight=0,
			total_fee=total_fee,
			bulk_id=bulk_id,
			dispatcher_id=dispatcher_id,
			user_id=user.id,
			obtain_name=obtain_name,
			obtain_mob=obtain_mob
		)
		for _ in goods:
			product_id = _.get('product_id')
			quantity = _.get('quantity')
			Goods.objects.create(
				quantity=quantity,
				order_id=order.id,
				product_id=product_id
			)
		user.recent_obtain_name = obtain_name
		user.recent_obtain_mob = obtain_mob
		user.save()
		return order
			
class OrderListSerializer(serializers.HyperlinkedModelSerializer):
	reseller = ResellerSerializer(source='bulk.reseller')
	create_time = TimestampField()
	covers = serializers.SerializerMethodField(method_name='get_goods_covers')
	count = serializers.SerializerMethodField(method_name='get_goods_count')
	class Meta:
		model = Order
		fields = ('url', 'id', 'create_time', 'reseller', 
			'status', 'total_fee', 'covers', 'count',)

	def get_goods_count(self, obj):
		result = Goods.objects.filter(order_id=obj.pk).aggregate(Sum('quantity'))
		return result.get('quantity__sum', 0)

	def get_goods_covers(self, obj): # So ugly :(
		request = self.context.get('request', None)
		return map(lambda url: 
			url if not request else
			request.build_absolute_uri(url),
			map(lambda g: g.product.cover.url 
			if hasattr(g.product.cover, 'url') 
			else '', obj.goods_set.all()))

class OrderSerializer(serializers.HyperlinkedModelSerializer):
	dispatcher = DispatcherSerializer()
	create_time = TimestampField()
	goods = GoodsSerializer(source='goods_set', many=True)
	pay_request_json = serializers.SerializerMethodField()
	class Meta:
		model = Order
		fields = ('url', 'id', 'create_time', 'dispatcher', 
			'status', 'prepay_id', 'freight', 'total_fee',
			'obtain_name', 'obtain_mob', 'goods',
			'pay_request_json',)

	def get_pay_request_json(self, obj):
		request = self.context.get('request', None)
		return WxApp.get_current(request).createPayRequestJson(obj.prepay_id)



