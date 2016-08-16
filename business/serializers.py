import urlparse

from django.db.models import Sum
from rest_framework import exceptions

from django.utils.timezone import UTC
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
from rest_framework.response import Response
from rest_framework import status

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
	recent_storage = serializers.IntegerField(source='recent_storage.id')
	create_time = TimestampField()
	class Meta:
		model = User
		fields = ('id', 'name', 'create_time', 'mob', 
			'recent_obtain_name', 'recent_obtain_mob', 
			'recent_storage', 'wx_nickname', 'wx_headimgurl', 'balance')

class LoginUserSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	recent_storage = serializers.IntegerField(source='recent_storage.id')
	class Meta:
		model = User
		fields = ('id', 'create_time', 'balance', 'name',
			'recent_storage', 'recent_obtain_name', 'recent_obtain_mob')

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
		fields = ('id', 'tail', 'create_time')

#class ResellerJWTSerializer(serializers.Serializer):
#	token = serializers.CharField()
#	user = ResellerSerializer()

class DispatcherSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.mob')
	create_time = TimestampField()
	class Meta:
		model = Dispatcher
		fields = ('id', 'name', 'tail', 'create_time', 
			'mob', 'wx_nickname', 'wx_headimgurl')

class LoginDispatcherSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	class Meta:
		model = Dispatcher
		fields = ('id', 'tail', 'create_time',)

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

class StorageSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField(read_only=True)
	class Meta:
		model = Storage
		fields = ('id', 'address', 'create_time', 
			'mob', 'opening_time', 'closing_time',
			'is_custom')
	
	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException(detail='Bad Request')
		mob_user = request.user
		reseller = None
		if hasattr(mob_user, 'reseller'):
			reseller = mob_user.reseller
		if reseller is None:
			raise BadRequestException(detail='Reseller not found')

		mob = validated_data.get('mob')
		address = validated_data.get('address')
		opening_time = validated_data.get('opening_time')
		closing_time = validated_data.get('closing_time')

		storage = Storage.objects.create(
			mob=mob,
			address=address,
			opening_time=opening_time,
			closing_time=closing_time,
			is_custom=True,
			reseller=reseller)
		return storage


class BulkCreateSerializer(serializers.Serializer):
	title = serializers.CharField()
	category = serializers.IntegerField()
	storages = serializers.ListField(
		child=serializers.IntegerField()
		)
	dead_time = TimestampField()
	arrived_time = TimestampField()
	location = serializers.CharField()
	receive_mode = serializers.IntegerField()
	products = serializers.ListField(
		child=serializers.IntegerField()
		)

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException(detail='Bad Request')
		mob_user = request.user
		reseller = None
		if hasattr(mob_user, 'reseller'):
			reseller = mob_user.reseller
		if reseller is None:
			raise BadRequestException(detail='Reseller not found')

		title = validated_data.get('title')
		category_id = validated_data.get('category')
		category = None
		try:
			category = Category.objects.get(pk=category_id)
		except:
			raise BadRequestException(detail='Category does not exist')
		storages_ = validated_data.get('storages')
		if len(storages_) == 0:
			raise BadRequestException(detail='Storages can not be empty')
		storages = []
		try:
			for storage_id in storages_:
				storage = Storage.objects.get(pk=storage_id)
				storages.append(storage)
		except ObjectDoesNotExist:
			raise BadRequestException(detail='Storage does not exist')

		dead_time = validated_data.get('dead_time')
		arrived_time = validated_data.get('arrived_time')
		location = validated_data.get('location')
		receive_mode = validated_data.get('receive_mode')
		if receive_mode not in [1, 2, 3]:
			raise BadRequestException(detail='Receive mode is incorrect')
		products_ = validated_data.get('products')
		if len(products_) == 0:
			raise BadRequestException(detail='Products can not be empty')
		products = []
		try:
			for product_id in products_:
				product = Product.objects.get(pk=product_id)
				products.append(product)
		except ObjectDoesNotExist:
			raise BadRequestException(detail='Product does not exist')

		bulk = Bulk(
			title=title,
			category=category,
			reseller=reseller,
			dead_time=dead_time,
			arrived_time=arrived_time,
			status=0,
			location=location,
			receive_mode=receive_mode,
			card_title=title,
			card_desc=title,
			card_icon=products[0].cover
			)
		bulk.save()
		for storage in storages:
			bulk.storages.add(storage)
		for product in products:
			productdetails_set = product.productdetails_set.all() # Cache
			product.pk = None
			product.is_snapshot = True
			product.save()
			for product_details in productdetails_set:
				product_details.pk = None
				product_details.is_snapshot = True
				product_details.product = product
				product_details.save()
			bulk.product_set.add(product)
		return bulk

class BulkUpdateSerializer(serializers.Serializer):
	title = serializers.CharField()
	category = serializers.IntegerField()
	storages = serializers.ListField(
		child=serializers.IntegerField()
		)
	dead_time = TimestampField()
	arrived_time = TimestampField()
	location = serializers.CharField()
	receive_mode = serializers.IntegerField()
	products = serializers.ListField(
		child=serializers.IntegerField()
		)

	def update(self, instance, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException(detail='Bad Request')
		mob_user = request.user
		reseller = None
		if hasattr(mob_user, 'reseller'):
			reseller = mob_user.reseller
		if reseller is None:
			raise BadRequestException(detail='Reseller not found')

		title = validated_data.get('title')
		category_id = validated_data.get('category')
		category = None
		try:
			category = Category.objects.get(pk=category_id)
		except ObjectDoesNotExist:
			raise BadRequestException(detail='Category does not exist')
		except IntegrityError:
			raise BadRequestException(detail='Category does not exist')
		storages_ = validated_data.get('storages')
		if len(storages_) == 0:
			raise BadRequestException(detail='Storages can not be empty')
		storages = []
		try:
			for storage_id in storages_:
				storage = Storage.objects.get(pk=storage_id)
				storages.append(storage)
		except ObjectDoesNotExist:
			raise BadRequestException(detail='Storage does not exist')
		except IntegrityError:
			raise BadRequestException(detail='Storage does not exist')

		dead_time = validated_data.get('dead_time')
		arrived_time = validated_data.get('arrived_time')
		location = validated_data.get('location')
		receive_mode = validated_data.get('receive_mode')
		if receive_mode not in [1, 2, 3]:
			raise BadRequestException(detail='Receive mode is incorrect')
		products_ = validated_data.get('products')
		if len(products_) == 0:
			raise BadRequestException(detail='Products can not be empty')
		products = []
		try:
			for product_id in products_:
				product = Product.objects.get(pk=product_id)
				products.append(product)
		except ObjectDoesNotExist:
			raise BadRequestException(detail='Product does not exist')
		except IntegrityError:
			raise BadRequestException(detail='Product does not exist')

		instance.title=title
		instance.category=category
		instance.reseller=reseller
		instance.dead_time=dead_time
		instance.arrived_time=arrived_time
		instance.status=0
		instance.location=location
		instance.receive_mode=receive_mode
		instance.card_title=title
		instance.card_desc=title
		instance.card_icon=products[0].cover
		instance.save()

		if request.method == 'PUT':
			instance.storages.remove()
			instance.product_set.all().delete()
			for storage in storages:
				instance.storages.add(storage)
			for product in products:
				productdetails_set = product.productdetails_set.all() # Cache
				product.pk = None
				product.is_snapshot = True
				product.save()
				for product_details in productdetails_set:
					product_details.pk = None
					product_details.is_snapshot = True
					product_details.product = product
					product_details.save()
				instance.product_set.add(product)
		elif request.method == 'PATCH':
			if len(storages) > 0:
				instance.storages.remove()
				for storage in storages:
					instance.storages.add(storage)
			if len(products) > 0:
				instance.product_set.all().delete()
				for product in products:
					productdetails_set = product.productdetails_set.all() # Cache
					product.pk = None
					product.is_snapshot = True
					product.save()
					for product_details in productdetails_set:
						product_details.pk = None
						product_details.is_snapshot = True
						product_details.product = product
						product_details.save()
					instance.product_set.add(product)
			
		return instance

class BulkListSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	#url = serializers.HyperlinkedIdentityField(
	#	view_name='bulk-detail',
	#	lookup_field='id'
	#)
	category = serializers.CharField(source='category.name')
	reseller = ResellerSerializer()
	covers = serializers.SerializerMethodField(method_name='get_product_covers')
	create_time = TimestampField()
	dead_time = TimestampField()
	arrived_time = TimestampField()
	participant_count = serializers.SerializerMethodField()

	class Meta:
		model = Bulk
		fields = ('url', 'id', 'title', 'category', 'reseller', 'covers',
			'dead_time', 'arrived_time', 'status', 'receive_mode',
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
	width = serializers.SerializerMethodField(read_only=True)
	height = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = ProductDetails
		fields = ('image', 'plain', 'seq', 'width', 'height')

	def get_width(self, obj):
		if hasattr(obj, 'image'):
			return obj.image.width
		return 0

	def get_height(self, obj):
		if hasattr(obj, 'image'):
			return obj.image.height
		return 0

class ProductListSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	create_time = TimestampField()
	category = serializers.CharField(source='category.name')
	participant_count = serializers.SerializerMethodField()
	purchased_count = serializers.SerializerMethodField()
	participant_avatars = serializers.SerializerMethodField()
	history = serializers.SerializerMethodField()
	details = ProductDetailsSerializer(source='productdetails_set', many=True)

	class Meta:
		model = Product
		fields = ('url', 'id', 'title', 'desc', 'category', 'unit_price', 'market_price',
			'spec', 'spec_desc', 'cover', 'create_time', 'details',
			'participant_count', 'purchased_count', 'tag', 'tag_color',
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
			if hasattr(user, 'mob_user') and user.mob_user:
				url = user.mob_user.real_wx_headimgurl
				if url is not None and len(url) > 0:
					if request:
						url = request.build_absolute_uri(url)
					avatars[user.pk] = url
				else:
					avatars[user.pk] = ''
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
	create_time = TimestampField()
	category = serializers.CharField(source='category.name')
	details = ProductDetailsSerializer(source='productdetails_set', many=True)
	bulk_url = serializers.HyperlinkedRelatedField(
		source='bulk', read_only=True, view_name='bulk-detail')

	class Meta:
		model = Product
		fields = ('url', 'id', 'title', 'desc', 'category', 'unit_price', 'market_price',
			'spec', 'spec_desc', 'cover', 'create_time', 'details', 'bulk_url')

class BulkSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	category = serializers.CharField(source='category.name')
	reseller = ResellerSerializer()
	storages = StorageSerializer(many=True)
	create_time = TimestampField()
	dead_time = TimestampField()
	standard_time = StandardTimeField(source='*')
	arrived_time = TimestampField()
	products = ProductListSerializer(source='product_set', many=True)
	participant_count = serializers.SerializerMethodField()
	recent_obtain_name = serializers.SerializerMethodField()
	recent_obtain_mob = serializers.SerializerMethodField()
	recent_storage = serializers.SerializerMethodField()
	card_url = serializers.SerializerMethodField()

	class Meta:
		model = Bulk
		fields = ('url', 'id', 'title', 'category', 'reseller', 'storages', 
			'products', 'location', 'standard_time', 'dead_time', 
			'arrived_time', 'status', 'card_title', 'card_desc',
			'card_icon', 'card_url', 'create_time', 'participant_count',
			'recent_obtain_name', 'recent_obtain_mob', 'recent_storage',
			'receive_mode',)

	def get_participant_count(self, obj):
		return Order.objects.filter(bulk_id=obj.pk).count()

	def get_recent_obtain_name(self, obj):
		request = self.context.get('request', None)
		if request is None:
			return None
		mob_user = request.user
		if isinstance(mob_user, MobUser):
			if hasattr(mob_user, 'user'):
				return mob_user.user.recent_obtain_name
		return None

	def get_recent_obtain_mob(self, obj):
		request = self.context.get('request', None)
		if request is None:
			return None
		mob_user = request.user
		if isinstance(mob_user, MobUser):
			if hasattr(mob_user, 'user'):
				return mob_user.user.recent_obtain_mob
		return None

	def get_recent_storage(self, obj):
		request = self.context.get('request', None)
		if request is None:
			return None
		mob_user = request.user
		if isinstance(mob_user, MobUser):
			if hasattr(mob_user, 'user'):
				if hasattr(mob_user.user, 'recent_storage') and \
					mob_user.user.recent_storage is not None:
					return mob_user.user.recent_storage.id
		return None

	def get_card_url(self, obj):
		return config.CARD_BULK_URL % obj.id

class CategorySerializer(serializers.ModelSerializer):
	name = serializers.CharField()
	class Meta:
		model = Category
		fields = ('id', 'name',)

class ShippingAddressSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = ShippingAddress
		fields = ('url', 'id', 'name', 'mob', 'address')

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException(detail='Bad Request')
		mob_user = request.user
		user = None
		if hasattr(mob_user, 'user'):
			user = mob_user.user
		if user is None:
			raise BadRequestException(detail='User not found')

		name = validated_data.get('name')
		mob = validated_data.get('mob')
		address = validated_data.get('address')

		shippingaddress = ShippingAddress.objects.create(
			name=name,
			mob=mob,
			address=address,
			user=user)
		return shippingaddress

class BulkSummarySerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	bulk_id = serializers.ReadOnlyField()
	cover = serializers.ImageField(source='product.cover', read_only=True)
	title = serializers.ReadOnlyField(source='product.title')
	quantity = serializers.ReadOnlyField()
	total_price = serializers.ReadOnlyField()
	spec = serializers.ReadOnlyField()

	class Meta:
		model = BulkSummary
		fields = ('bulk_id', 'cover', 'title', 'quantity', 'total_price', 'spec',)


class PurchasedProductHistorySerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	order_id = serializers.ReadOnlyField()
	bulk_id = serializers.ReadOnlyField()
	product_id = serializers.ReadOnlyField()
	name = serializers.ReadOnlyField()
	wx_nickname = serializers.ReadOnlyField(source='user.mob_user.real_wx_nickname')
	wx_headimgurl = serializers.ReadOnlyField(source='user.mob_user.real_wx_headimgurl')
	quantity = serializers.ReadOnlyField()
	spec = serializers.ReadOnlyField()
	create_time = TimestampField(read_only=True)

	class Meta:
		model = PurchasedProductHistory
		fields = ('order_id', 'bulk_id', 'product_id', 'name',
			'wx_nickname', 'wx_headimgurl', 'quantity', 'spec', 'create_time',)

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
	storage_id = serializers.IntegerField()

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException(detail='Bad Request')
		mob_user = request.user
		user = mob_user.user
		if user is None:
			raise BadRequestException(detail='User not found')
		bulk_id = validated_data.get('bulk_id')
		bulk = None
		try:
			bulk = Bulk.objects.get(pk=bulk_id)
		except ObjectDoesNotExist:
			raise BadRequestException(detail='Bulk not found')
		if bulk.status < 0 or bulk.dead_time < datetime.datetime.now(tz=UTC()):
			raise BadRequestException(detail='Bulk has been expired')
		if bulk is None:
			raise BadRequestException(detail='Bulk not found')
		storage_id = validated_data.get('storage_id')
		storage = None
		try:
			storage = Storage.objects.get(pk=storage_id)
		except ObjectDoesNotExist:
			raise BadRequestException(detail='Storage not found')
		if storage is None:
			raise BadRequestException(detail='Storage not found')
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
				raise BadRequestException(detail='Product not found')
		order_id = utils.createDisplayOrderId()
		bulk.seq += 1
		order = Order.objects.create(
			id=order_id,
			status=0,
			freight=0,
			total_fee=total_fee,
			bulk_id=bulk_id,
			storage_id=storage_id,
			user_id=user.id,
			obtain_name=obtain_name,
			obtain_mob=obtain_mob,
			seq=bulk.seq
		)
		bulk.save()
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
		user.recent_storage = storage
		user.save()
		return order
		
class OrderListSerializer(serializers.HyperlinkedModelSerializer):
	reseller = ResellerSerializer(source='bulk.reseller')
	create_time = TimestampField()
	covers = serializers.SerializerMethodField(method_name='get_goods_covers')
	count = serializers.SerializerMethodField(method_name='get_goods_count')
	card_title = serializers.CharField(source='bulk.card_title')
	card_desc = serializers.CharField(source='bulk.card_desc')
	card_icon = serializers.ImageField(source='bulk.card_icon')
	card_url = serializers.SerializerMethodField()
	bulk_status = serializers.IntegerField(source='bulk.status')

	class Meta:
		model = Order
		fields = ('url', 'id', 'create_time', 'reseller', 
			'status', 'total_fee', 'covers', 'count', 'seq',
			'card_title', 'card_desc', 'card_icon', 'card_url',
			'bulk_status')

	def get_card_url(self, obj):
		return config.CARD_BULK_URL % obj.bulk.id

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

class PayRequestModelSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):

	class Meta:
		model = PayRequest
		fields = ('third_party_order_id', 'third_party_fee', 
				'balance_fee', 'use_balance', 'status')

class OrderSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	storage = StorageSerializer()
	create_time = TimestampField()
	goods = GoodsSerializer(source='goods_set', many=True)
	wx_pay_request = serializers.SerializerMethodField()
	payrequest = PayRequestModelSerializer()
	card_title = serializers.CharField(source='bulk.card_title')
	card_desc = serializers.CharField(source='bulk.card_desc')
	card_icon = serializers.ImageField(source='bulk.card_icon')
	card_url = serializers.SerializerMethodField()
	bulk_status = serializers.IntegerField(source='bulk.status')

	class Meta:
		model = Order
		fields = ('url', 'id', 'create_time', 'storage', 
			'status', 'freight', 'total_fee', 'obtain_name', 
			'obtain_mob', 'goods', 'wx_pay_request', 'payrequest',
			'card_title', 'card_desc', 'card_icon', 'card_url',
			'seq', 'bulk_status')

	def get_card_url(self, obj):
		return config.CARD_BULK_URL % obj.bulk.id

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
		fields = ('source', 'key', 'image', 'category', 'seq', 'create_time')

class SlideDetailsSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	source = serializers.SerializerMethodField()

	class Meta:
		model = Slide
		fields = ('source', 'key', 'image', 'category', 'seq', 'create_time')

	def get_source(self, obj):
		request = self.context.get('request', None)
		#if obj.category == 'bulk':
		#	try:
		#		instance = Bulk.objects.get(pk=obj.key)
		#		serializer = BulkSerializer(instance=instance, context={'request': request})
		#		return serializer.data
		#	except Bulk.DoesNotExist:
		#		pass
		if obj.category == 'recipe':
			try:
				instance = Recipe.objects.get(pk=obj.key)
				serializer = RecipeSerializer(instance=instance, context={'request': request})
				return serializer.data
			except Recipe.DoesNotExist:
				pass
		elif obj.category == 'dish':
			try:
				instance = Dish.objects.get(pk=obj.key)
				serializer = DishSerializer(instance=instance, context={'request': request})
				return serializer.data
			except Dish.DoesNotExist:
				pass
		return obj.source

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
	category = serializers.CharField(source='category.name')
	participant_count = serializers.SerializerMethodField()
	purchased_count = serializers.SerializerMethodField()
	details = ProductDetailsSerializer(source='productdetails_set', many=True)
	bulk_url = serializers.HyperlinkedRelatedField(
		source='bulk', read_only=True, view_name='bulk-detail')

	class Meta:
		model = Product
		fields = ('url', 'id', 'title', 'desc', 'category', 'unit_price', 'market_price',
			'spec', 'spec_desc', 'cover', 'create_time', 'details',
			'participant_count', 'purchased_count', 'tag', 'tag_color', 'bulk_url')

	def get_participant_count(self, obj):
		return Goods.objects.filter(product_id=obj.pk).count()

	def get_purchased_count(self, obj):
		result = Goods.objects.filter(product_id=obj.pk).aggregate(Sum('quantity'))
		return result.get('quantity__sum', 0)

class ExhibitedProductSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	product = ProductExhibitSerializer()

	class Meta:
		model = ExhibitedProduct
		fields = ('cover_2x', 'cover_3x', 'stick', 'seq', 'product')

class ExhibitSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	publish_time = TimestampField()
	slides = SlideDetailsSerializer(many=True)
	hot_bulks = BulkExhibitSerializer(many=True)
	hot_products = ExhibitedProductSerializer(source='exhibitedproduct_set', many=True)

	class Meta:
		model = Exhibit
		fields = ('slides', 'hot_bulks', 'hot_products', 'create_time', 'publish_time')

class RecipeExhibitSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	publish_time = TimestampField()
	slides = SlideDetailsSerializer(many=True)

	class Meta:
		model = RecipeExhibit
		fields = ('slides', 'create_time', 'publish_time')

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
	md5 = serializers.CharField(source='image.md5')
	plain = serializers.CharField(allow_blank=True)

	class Meta:
		model = Step
		fields = ('image', 'plain', 'seq', 'create_time', 'width', 'height', 'md5')

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
	plain = serializers.CharField(allow_blank=True)
	seq = serializers.IntegerField()

class IngredientCreateSerializer(serializers.Serializer):
	name = serializers.CharField(allow_blank=True)
	seq = serializers.IntegerField()
	quantity = serializers.CharField(allow_blank=True)

class RecipeUpdateSerializer(serializers.Serializer):
	name = serializers.CharField(allow_blank=True)
	desc = serializers.CharField(allow_blank=True)
	cover = serializers.CharField()
	tag = serializers.CharField(allow_blank=True)
	tips = serializers.ListField(
		child=serializers.CharField(allow_blank=True)
		)
	steps = StepCreateSerializer(many=True)
	ingredients = IngredientCreateSerializer(many=True)
	time = serializers.CharField(required=False, allow_blank=True)

	def update(self, instance, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException(detail='Bad Request')
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
							recipe=instance,
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
							recipe=instance,
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
			raise BadRequestException(detail='Update failed')
		instance.save()
		return instance

class RecipeCreateSerializer(serializers.Serializer):
	name = serializers.CharField(allow_blank=True)
	desc = serializers.CharField(allow_blank=True)
	cover = serializers.CharField()
	tag = serializers.CharField(required=False, allow_blank=True)
	tips = serializers.ListField(
		child=serializers.CharField(allow_blank=True)
		)
	steps = StepCreateSerializer(many=True)
	ingredients = IngredientCreateSerializer(many=True)
	time = serializers.CharField(required=False, allow_blank=True)

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException(detail='Bad Request')
		mob_user = request.user
		user = mob_user.user
		if user is None:
			raise BadRequestException(detail='User not found')
		name = validated_data.get('name')
		desc = validated_data.get('desc')
		cover_md5 = validated_data.get('cover')
		tag = validated_data.get('tag', None)
		time = validated_data.get('time', None)
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
			raise BadRequestException(detail='Image does not exist')
		except IntegrityError:
			raise BadRequestException(detail='Create failed')

class RecipeSimpleSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	create_time = TimestampField()
	cover = serializers.ImageField(source='cover.image')
	cover_md5 = serializers.CharField(source='cover.md5')

	class Meta:
		model = Recipe
		fields = ('url', 'id', 'name', 'cover', 'cover_md5', 'create_time')

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
	cover_md5 = serializers.CharField(source='cover.md5')
	more = serializers.SerializerMethodField()
	card_url =serializers.SerializerMethodField()

	class Meta:
		model = Recipe
		fields = ('url', 'id', 'name', 'user', 'desc', 'cover', 
			'cover_md5', 'status', 'tag', 'tips', 'time', 'steps',
			'dish_num', 'ingredients', 'step_num',
			'create_time', 'more', 'card_url')

	def get_dish_num(self, obj):
		return Dish.objects.filter(recipe=obj).count()

	def get_step_num(self, obj):
		return obj.step_set.count()

	def get_more(self, obj):
		request = self.context.get('request', None)
		recipes = None
		if hasattr(obj, 'user') and obj.user:
			recipes = obj.user.recipe_set.exclude(id=obj.id)[:3]
			serializer = RecipeSimpleSerializer(data=recipes, many=True, context={'request': request})
			serializer.is_valid()
			return serializer.data
		return []

	def get_card_url(self, obj):
		return config.CARD_RECIPE_URL % obj.id



class DishDetailsSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):
	create_time = TimestampField()
	width = serializers.SerializerMethodField()
	height = serializers.SerializerMethodField()
	image = serializers.ImageField(source='image.image')
	md5 = serializers.CharField(source='image.md5')

	class Meta:
		model = Step
		fields = ('image', 'plain', 'seq', 'create_time', 'width', 'height', 'md5')

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
	plain = serializers.CharField(allow_blank=True)
	seq = serializers.IntegerField()

class DishUpdateSerializer(serializers.Serializer):
	name = serializers.CharField(allow_blank=True)
	desc = serializers.CharField(allow_blank=True)
	cover = serializers.CharField()
	tag = serializers.CharField(required=False, allow_blank=True)
	tips = serializers.ListField(
		child=serializers.CharField(allow_blank=True)
		)
	steps = StepCreateSerializer(many=True)

	def update(self, instance, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException(detail='Bad Request')
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
			raise BadRequestException(detail='Update failed')
		return instance

class DishCreateSerializer(serializers.Serializer):
	name = serializers.CharField(allow_blank=True)
	desc = serializers.CharField(allow_blank=True)
	cover = serializers.CharField()
	tag = serializers.CharField(required=False, allow_blank=True)
	tips = serializers.ListField(
		child=serializers.CharField(allow_blank=True)
		)
	recipe = serializers.IntegerField(required=False)
	steps = DishDetailsCreateSerializer(many=True)

	def create(self, validated_data):
		request = self.context.get('request', None)
		if request is None:
			raise BadRequestException(detail='Bad Request')
		mob_user = request.user
		user = mob_user.user
		if user is None:
			raise BadRequestException(detail='User not found')
		recipe_id = validated_data.get('recipe')
		name = validated_data.get('name')
		desc = validated_data.get('desc')
		cover_md5 = validated_data.get('cover')
		tag = validated_data.get('tag', None)
		tips = validated_data.get('tips')
		steps = validated_data.get('steps')
		try:
			recipe = None
			if Recipe.objects.filter(pk=recipe_id).exists():
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
			raise BadRequestException(detail='Recipe does not exist')
		except Image.DoesNotExist:
			raise BadRequestException(detail='Image does not exist')
		except IntegrityError:
			raise BadRequestException(detail='Create failed')

class DishSimpleSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	create_time = TimestampField()
	cover = serializers.ImageField(source='cover.image')
	cover_md5 = serializers.CharField(source='cover.md5')

	class Meta:
		model = Dish
		fields = ('url', 'id', 'name', 'cover', 'cover_md5', 'create_time')

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
	cover_md5 = serializers.CharField(source='cover.md5')
	more = serializers.SerializerMethodField()
	card_url =serializers.SerializerMethodField()

	class Meta:
		model = Dish
		fields = ('url', 'id', 'name', 'user', 'desc', 'cover',
			'cover_md5', 'status', 'tag', 'tips', 'create_time', 'recipe',
			'steps', 'step_num', 'more', 'card_url')

	def get_step_num(self, obj):
		return obj.dishdetails_set.count()

	def get_more(self, obj):
		request = self.context.get('request', None)
		dishs = None
		if hasattr(obj, 'user') and obj.user:
			dishs = obj.user.dish_set.exclude(id=obj.id)[:3]
			if dishs and dishs.count() == 0:
				dishs = Dish.objects.order_by('-create_time').exclude(id=obj.id)[:3]
		else:
			dishs = Dish.objects.order_by('-create_time').exclude(id=obj.id)[:3]
		serializer = DishSimpleSerializer(data=dishs, many=True, context={'request': request})
		serializer.is_valid()
		return serializer.data

	def get_card_url(self, obj):
		return config.CARD_DISH_URL % obj.id


class ImageSerializer(RemoveNullSerializerMixIn, serializers.ModelSerializer):

	class Meta:
		model = Image
		fields = ('image', 'md5')
