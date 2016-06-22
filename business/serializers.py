import urlparse

from django.db.models import Sum
from rest_framework import exceptions

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.reverse import reverse
from authentication.serializers import LoginSerializer as BaseLoginSerializer
from authentication.serializers import BindSerializer as BaseBindSerializer
from rest_auth.registration.serializers import SocialLoginSerializer as BaseSocialLoginSerializer

from . import config
from .models import *
from .fields import *
from .exceptions import *
from . import utils
from .parsers import *

from collections import OrderedDict
from rest_framework.relations import PKOnlyObject
from rest_framework.fields import SkipField
from rest_framework.parsers import JSONParser

from authentication.serializers import MobUserSerializer

from .wx import *

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
	mob = serializers.CharField(source='mob_user.mob')
	create_time = TimestampField()
	class Meta:
		model = User
		fields = ('id', 'name', 'create_time', 'mob', 
			'recent_obtain_name', 'recent_obtain_mob', 
			'wx_nickname', 'wx_headimgurl', 'balance')

class LoginUserSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	class Meta:
		model = User
		fields = ('create_time', 'balance',
			'recent_obtain_name', 'recent_obtain_mob')

#class UserJWTSerializer(serializers.Serializer):
#	token = serializers.CharField()
#	user = UserSerializer()

class ResellerSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.mob')
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
	mob = serializers.CharField(source='mob_user.mob')
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

class JWTSerializer(RemoveNullSerializerMixIn, serializers.Serializer):
	flag = serializers.IntegerField()
	token = serializers.CharField()
	mob_user = MobUserSerializer()
	user = LoginUserSerializer()
	reseller = LoginResellerSerializer()
	dispatcher = LoginDispatcherSerializer()

class LoginSerializer(BaseLoginSerializer):

	def validate(self, attrs):
		attrs = super(LoginSerializer, self).validate(attrs)
		mob_user = attrs['user']
		if not mob_user:
			msg = _('Unable to log in with provided credentials.')
			raise exceptions.ValidationError(msg)
		user, created = User.objects.get_or_create(
			mob_user=mob_user,
			defaults={
				'name': mob_user.mob,
			}
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

class BindSerializer(BaseBindSerializer):
	
	def validate(self, attrs):
		attrs = super(BindSerializer, self).validate(attrs)
		mob_user = attrs['user']
		if not mob_user:
			msg = _('Unable to log in with provided credentials.')
			raise exceptions.ValidationError(msg)
		user, created = User.objects.get_or_create(
			mob_user=mob_user,
			defaults={
				'name': mob_user.mob,
			}
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

class SocialLoginSerializer(BaseSocialLoginSerializer):

	def validate(self, attrs):
		attrs = super(SocialLoginSerializer, self).validate(attrs)
		mob_user = attrs['user']
		if not mob_user:
			msg = _('Unable to log in with provided credentials.')
			raise exceptions.ValidationError(msg)
		try:
			user = User.objects.get(mob_user=mob_user)
			attrs['wrap_user'] = user
		except ObjectDoesNotExist:
			pass
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
			else '', obj.product_set.all()))

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
	bulk_url = serializers.HyperlinkedRelatedField(
		source='bulk', read_only=True, view_name='bulk-detail')

	class Meta:
		model = Product
		fields = ('url', 'id', 'title', 'desc', 'unit_price', 'market_price',
			'spec', 'spec_desc', 'cover', 'create_time', 'details', 'bulk_url')

class BulkSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	reseller = ResellerSerializer()
	dispatchers = DispatcherSerializer(many=True)
	create_time = TimestampField()
	dead_time = TimestampField()
	standard_time = StandardTimeField(source='*')
	arrived_time = TimestampField()
	products = ProductListSerializer(source='product_set', many=True)
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
		if isinstance(mob_user, MobUser):
			user = mob_user.user
			if user:
				return user.recent_obtain_name
		return None

	def get_recent_obtain_mob(self, obj):
		request = self.context.get('request', None)
		if request is None:
			return None
		mob_user = request.user
		if isinstance(mob_user, MobUser):
			user = mob_user.user
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
		user = mob_user.user
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
	obtain_name = serializers.CharField()
	obtain_mob = serializers.CharField()
	bulk_id = serializers.IntegerField()
	dispatcher_id = serializers.IntegerField()

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException('Bad Request')
		mob_user = request.user
		user = mob_user.user
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
		goods = validated_data.get('goods')
		total_fee = 0
		for _ in goods:
			product_id = _.get('product_id')
			quantity = _.get('quantity')
			try:
				product = Product.objects.get(pk=product_id)
				total_fee += product.unit_price * quantity
			except ObjectDoesNotExist:
				raise BadRequestException('Product not found')
		order_id = utils.createOrderId()
		order = Order.objects.create(
			id=order_id,
			status=0,
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
	wx_pay_request = serializers.SerializerMethodField()
	
	class Meta:
		model = Order
		fields = ('url', 'id', 'create_time', 'dispatcher', 
			'status', 'freight', 'total_fee',
			'obtain_name', 'obtain_mob', 'goods',
			'wx_pay_request',)

	def get_wx_pay_request(self, obj):
		request = self.context.get('request', None)
		if not request:
			return None
		return reverse('payRequest', request=request, kwargs={'pk':obj.pk})

class PayRequestSerializer(RemoveNullSerializerMixIn, serializers.Serializer):
	require_third_party_payment = serializers.BooleanField()
	pay_request_json = serializers.JSONField()
	order = OrderSerializer()

class SlideSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()

	class Meta:
		model = Slide
		fields = ('link', 'image', 'category', 'seq', 'create_time')

class BulkExhibitSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	covers = serializers.SerializerMethodField(method_name='get_product_covers')

	class Meta:
		model = Bulk
		fields = ('url', 'id', 'title', 'category', 'covers',)

	def get_product_covers(self, obj): # So ugly :(
		request = self.context.get('request', None)
		return map(lambda url: 
			url if not request else
			request.build_absolute_uri(url),
			map(lambda p: p.cover.url 
			if hasattr(p.cover, 'url') 
			else '', obj.product_set.all()))

class ProductExhibitSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	create_time = TimestampField()
	participant_count = serializers.SerializerMethodField()
	purchased_count = serializers.SerializerMethodField()
	details = ProductDetailsSerializer(source='productdetails_set', many=True)
	bulk_url = serializers.HyperlinkedRelatedField(
		source='bulk', read_only=True, view_name='bulk-detail')

	class Meta:
		model = Product
		fields = ('url', 'id', 'title', 'desc', 'unit_price', 'market_price',
			'spec', 'spec_desc', 'cover', 'create_time', 'details',
			'participant_count', 'purchased_count', 'tag', 'bulk_url')

	def get_participant_count(self, obj):
		return Goods.objects.filter(product_id=obj.pk).count()

	def get_purchased_count(self, obj):
		result = Goods.objects.filter(product_id=obj.pk).aggregate(Sum('quantity'))
		return result.get('quantity__sum', 0)

class ExhibitedProductSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	product = ProductExhibitSerializer()

	class Meta:
		model = ExhibitedProduct
		fields = ('cover', 'stick', 'seq', 'product')

class ExhibitSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	publish_time = TimestampField()
	slides = SlideSerializer(many=True)
	hot_bulks = BulkExhibitSerializer(many=True)
	hot_products = ExhibitedProductSerializer(source='exhibitedproduct_set', many=True)

	class Meta:
		model = Exhibit
		fields = ('slides', 'hot_bulks', 'hot_products', 'create_time', 'publish_time')

class UserGuestSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	class Meta:
		model = User
		fields = ('id', 'name', 'create_time', 
			'wx_nickname', 'wx_headimgurl')

class StepSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	width = serializers.SerializerMethodField(read_only=True)
	height = serializers.SerializerMethodField(read_only=True)
	image = serializers.ImageField(source='image.image')

	class Meta:
		model = Step
		fields = ('image', 'plain', 'seq', 'create_time', 'width', 'height')

	def get_width(self, obj):
		if hasattr(obj, 'image') and hasattr(obj.image, 'image'):
			return obj.image.image.width
		return 0

	def get_height(self, obj):
		if hasattr(obj, 'image') and hasattr(obj.image, 'image'):
			return obj.image.image.height
		return 0

class IngredientSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	class Meta:
		model = Ingredient
		fields = ('name', 'seq', 'quantity')

#class TipSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
#
#	class Meta:
#		model = Tip
#		fields = ('plain',)

class StepCreateSerializer(serializers.Serializer):
	image = serializers.CharField()
	plain = serializers.CharField()
	seq = serializers.IntegerField()

class IngredientCreateSerializer(serializers.Serializer):
	name = serializers.CharField()
	seq = serializers.IntegerField()
	quantity = serializers.CharField()

class RecipeUpdateSerializer(serializers.Serializer):
	name = serializers.CharField()
	desc = serializers.CharField()
	cover = serializers.CharField()
	tag = serializers.CharField()
	tips = serializers.ListField(
		child=serializers.CharField()
		)
	steps = StepCreateSerializer(many=True)
	ingredients = IngredientCreateSerializer(many=True)
	time = serializers.CharField()

	def update(self, instance, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException('Bad Request')
		instance.name = validated_data.get('name', instance.name)
		instance.desc = validated_data.get('desc', instance.desc)
		cover_md5 = validated_data.get('cover', None)
		if cover_md5:
			cover = Image.objects.get(pk=cover_md5)
			if cover:
				instance.cover = cover
		instance.tag = validated_data.get('tag', instance.tag)
		instance.time = validated_data.get('time', instance.time)
		try:
			steps = validated_data.get('steps', None)
			if request.method == 'PUT':
				instance.step_set.all().delete()
				if steps:
					for step in steps:
						image_md5 = step.get('image')
						plain = step.get('plain')
						seq = step.get('seq')
						image = Image.objects.get(pk=image_md5)
						instance.step_set.create(
							recipe=instance,
							image=image,
							plain=plain,
							seq=seq
							)
			elif request.method == 'PATCH':
				if steps:
					instance.step_set.all().delete()
					for step in steps:
						image_md5 = step.get('image')
						plain = step.get('plain')
						seq = step.get('seq')
						image = Image.objects.get(pk=image_md5)
						instance.step_set.create(
							recipe=instance,
							image=image,
							plain=plain,
							seq=seq
							)
			ingredients = validated_data.get('ingredients', None)
			if request.method == 'PUT':
				instance.ingredient_set.all().delete()
				if ingredients:
					for ingredient in ingredients:
						name = ingredient.get('name')
						seq = ingredient.get('seq')
						quantity = ingredient.get('quantity')
						Ingredient.objects.create(
							recipe=recipe,
							name=name,
							seq=seq,
							quantity=quantity
							)
			elif request.method == 'PATCH':
				if ingredients:
					instance.ingredient_set.all().delete()
					for ingredient in ingredients:
						name = ingredient.get('name')
						seq = ingredient.get('seq')
						quantity = ingredient.get('quantity')
						Ingredient.objects.create(
							recipe=recipe,
							name=name,
							seq=seq,
							quantity=quantity
							)
			tips = validated_data.get('tips', None)
			if request.method == 'PUT':
				instance.tips.all().delete()
				if tips:
					for tip in tips:
						instance.tips.create(plain=tip)
			elif request.method == 'PATCH':
				if tips:
					instance.tips.all().delete()
					for tip in tips:
						instance.tips.create(plain=tip)
		except IntegrityError:
			raise BadRequestException('Update failed')
		return instance

class RecipeCreateSerializer(serializers.Serializer):
	name = serializers.CharField()
	desc = serializers.CharField()
	cover = serializers.CharField()
	tag = serializers.CharField(required=False)
	tips = serializers.ListField(
		child=serializers.CharField()
		)
	steps = StepCreateSerializer(many=True)
	ingredients = IngredientCreateSerializer(many=True)
	time = serializers.CharField()

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException('Bad Request')
		mob_user = request.user
		user = mob_user.user
		if user is None:
			raise BadRequestException('User not found')
		name = validated_data.get('name')
		desc = validated_data.get('desc')
		cover_md5 = validated_data.get('cover')
		tag = validated_data.get('tag', None)
		time = validated_data.get('time')
		tips = validated_data.get('tips')
		steps = validated_data.get('steps')
		ingredients = validated_data.get('ingredients')
		try:
			cover = Image.objects.get(pk=cover_md5)
			recipe = Recipe.objects.create(
				name=name,
				desc=desc,
				user=user,
				status=0,
				tag=tag,
				time=time,
				cover=cover
				)
			for step in steps:
				image_md5 = step.get('image')
				plain = step.get('plain')
				seq = step.get('seq')
				image = Image.objects.get(pk=image_md5)
				Step.objects.create(
					recipe=recipe,
					image=image,
					plain=plain,
					seq=seq
					)
			for ingredient in ingredients:
				name = ingredient.get('name')
				seq = ingredient.get('seq')
				quantity = ingredient.get('quantity')
				Ingredient.objects.create(
					recipe=recipe,
					name=name,
					seq=seq,
					quantity=quantity
					)
			for tip in tips:
				recipe.tips.create(plain=tip)
			return recipe
		except Image.DoesNotExist:
			raise BadRequestException('Image does not exist')
		except IntegrityError:
			raise BadRequestException('Create failed')

class RecipeSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	create_time = TimestampField()	
	user = UserGuestSerializer()
	tips = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='plain'
	)
	steps = StepSerializer(source='step_set', many=True)
	dish_num = serializers.SerializerMethodField()
	ingredients = IngredientSerializer(source='ingredient_set', many=True)
	step_num = serializers.SerializerMethodField()
	cover = serializers.ImageField(source='cover.image')

	class Meta:
		model = Recipe
		fields = ('url', 'id', 'name', 'user', 'desc', 'cover', 
			'status', 'tag', 'tips', 'time', 'steps',
			'dish_num', 'ingredients', 'step_num',
			'create_time')

	def get_dish_num(self, obj):
		return Dish.objects.filter(recipe=obj).count()

	def get_step_num(self, obj):
		return obj.step_set.count()

class DishDetailsSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	width = serializers.SerializerMethodField()
	height = serializers.SerializerMethodField()
	image = serializers.ImageField(source='image.image')

	class Meta:
		model = Step
		fields = ('image', 'plain', 'seq', 'create_time', 'width', 'height')

	def get_width(self, obj):
		if hasattr(obj, 'image') and hasattr(obj.image, 'image'):
			return obj.image.image.width
		return 0

	def get_height(self, obj):
		if hasattr(obj, 'image') and hasattr(obj.image, 'image'):
			return obj.image.image.height
		return 0

class DishDetailsCreateSerializer(serializers.Serializer):
	image = serializers.CharField()
	plain = serializers.CharField()
	seq = serializers.IntegerField()

class DishUpdateSerializer(serializers.Serializer):
	name = serializers.CharField()
	desc = serializers.CharField()
	cover = serializers.CharField()
	tag = serializers.CharField()
	tips = serializers.ListField(
		child=serializers.CharField()
		)
	steps = StepCreateSerializer(many=True)

	def update(self, instance, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException('Bad Request')
		instance.name = validated_data.get('name', instance.name)
		instance.desc = validated_data.get('desc', instance.desc)
		cover_md5 = validated_data.get('cover', None)
		if cover_md5:
			cover = Image.objects.get(pk=cover_md5)
			if cover:
				instance.cover = cover
		instance.tag = validated_data.get('tag', instance.tag)
		try:
			steps = validated_data.get('steps', None)
			if request.method == 'PUT':
				instance.dishdetails_set.all().delete()
				if steps:
					for step in steps:
						image_md5 = step.get('image')
						plain = step.get('plain')
						seq = step.get('seq')
						image = Image.objects.get(pk=image_md5)
						instance.dishdetails_set.create(
							dish=instance,
							image=image,
							plain=plain,
							seq=seq
							)
			elif request.method == 'PATCH':
				if steps:
					instance.dishdetails_set.all().delete()
					for step in steps:
						image_md5 = step.get('image')
						plain = step.get('plain')
						seq = step.get('seq')
						image = Image.objects.get(pk=image_md5)
						instance.dishdetails_set.create(
							dish=instance,
							image=image,
							plain=plain,
							seq=seq
							)
			tips = validated_data.get('tips', None)
			if request.method == 'PUT':
				instance.tips.all().delete()
				if tips:
					for tip in tips:
						instance.tips.create(plain=tip)
			elif request.method == 'PATCH':
				if tips:
					instance.tips.all().delete()
					for tip in tips:
						instance.tips.create(plain=tip)
		except IntegrityError:
			raise BadRequestException('Update failed')
		return instance

class DishCreateSerializer(serializers.Serializer):
	name = serializers.CharField()
	desc = serializers.CharField()
	cover = serializers.CharField()
	tag = serializers.CharField(required=False)
	tips = serializers.ListField(
		child=serializers.CharField()
		)
	recipe = serializers.IntegerField()
	steps = DishDetailsCreateSerializer(many=True)

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException('Bad Request')
		mob_user = request.user
		user = mob_user.user
		if user is None:
			raise BadRequestException('User not found')
		recipe_id = validated_data.get('recipe')
		name = validated_data.get('name')
		desc = validated_data.get('desc')
		cover_md5 = validated_data.get('cover')
		tag = validated_data.get('tag', None)
		tips = validated_data.get('tips')
		steps = validated_data.get('steps')
		try:
			recipe = Recipe.objects.get(pk=recipe_id)
			cover = Image.objects.get(pk=cover_md5)
			dish = Dish.objects.create(
				name=name,
				desc=desc,
				recipe=recipe,
				user=user,
				status=0,
				tag=tag,
				cover=cover
				)
			for step in steps:
				image_md5 = step.get('image')
				plain = step.get('plain')
				seq = step.get('seq')
				image = Image.objects.get(pk=image_md5)
				DishDetails.objects.create(
					dish=dish,
					image=image,
					plain=plain,
					seq=seq
					)
			for tip in tips:
				dish.tips.create(plain=tip)
			return dish
		except Recipe.DoesNotExist:
			raise BadRequestException('Recipe does not exist')
		except Image.DoesNotExist:
			raise BadRequestException('Image does not exist')
		except IntegrityError:
			raise BadRequestException('Create failed')

class DishSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	create_time = TimestampField()
	user = UserGuestSerializer(read_only=True)
	tips = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='plain'
	)
	recipe = serializers.HyperlinkedRelatedField(read_only=True, view_name='recipe-detail')
	steps = DishDetailsSerializer(source='dishdetails_set', many=True)
	step_num = serializers.SerializerMethodField()
	cover = serializers.ImageField(source='cover.image')

	class Meta:
		model = Dish
		fields = ('url', 'id', 'name', 'user', 'desc', 'cover',
			'status', 'tag', 'tips', 'create_time', 'recipe',
			'steps', 'step_num')

	def get_step_num(self, obj):
		return obj.dishdetails_set.count()

class ImageSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):

	class Meta:
		model = Image
		fields = ('image', 'md5')
