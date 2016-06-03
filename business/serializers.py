from django.db.models import Sum
from rest_framework import exceptions

from rest_framework import serializers
from authentication.serializers import LoginSerializer as BaseLoginSerializer
from rest_auth.registration.serializers import SocialLoginSerializer as BaseSocialLoginSerializer

from .models import *
from .fields import *

from collections import OrderedDict
from rest_framework.relations import PKOnlyObject
from rest_framework.fields import SkipField

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
				ret[field.field_name] = None
			else:
				value = field.to_representation(attribute)
				if value:
					ret[field.field_name] = value
		
		return ret

class WeixinSerializerMixIn(RemoveNullSerializerMixIn, serializers.Serializer):
	wx_nickname = serializers.SerializerMethodField(method_name='get_real_wx_nickname')
	wx_headimgurl = serializers.SerializerMethodField(method_name='get_real_wx_headimgurl')

        def get_real_wx_extra_data(self, obj):
		if not hasattr(obj, 'mob_user'):
			return None
		obj = obj.mob_user
		if not obj:
			return None
                extra_data = None
                socialaccounts = obj.socialaccount_set.all()
                for socialaccount in socialaccounts:
                        provider = socialaccount.provider
                        if provider == 'weixin': # Could be configuration
                                extra_data = socialaccount.extra_data
                                if extra_data:
                                        break
                if extra_data:
                        return extra_data
                else:
                        children = obj.mobuser_set.all()
                        for child in children:
                                extra_data = self.get_real_wx_extra_data(child)
                                if extra_data:
                                        break
                return extra_data

        def get_real_wx_nickname(self, obj):
		if not hasattr(obj, 'mob_user'):
			return None
		obj = obj.mob_user
		if not obj:
			return None
		return obj.real_wx_nickname
                #extra_data = self.get_real_wx_extra_data(obj)
                #if extra_data:
                #        return extra_data.get('nickname', None)
                #return None

        def get_real_wx_headimgurl(self, obj):
		if not hasattr(obj, 'mob_user'):
			return None
		obj = obj.mob_user
		if not obj:
			return None
		return obj.real_wx_headimgurl
                #extra_data = self.get_real_wx_extra_data(obj)
                #if extra_data:
                #        return extra_data.get('headimgurl', None)
                #return None

class UserSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.real_mob')
	create_time = TimestampField()
	class Meta:
		model = User
		fields = ('id', 'name', 'create_time', 'mob', 
			'wx_nickname', 'wx_headimgurl')

class UserJWTSerializer(serializers.Serializer):
	token = serializers.CharField()
	user = UserSerializer()

class ResellerSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.real_mob')
	create_time = TimestampField()
	class Meta:
		model = Reseller
		fields = ('id', 'name', 'tail', 'create_time', 
			'mob', 'wx_nickname', 'wx_headimgurl')

class ResellerJWTSerializer(serializers.Serializer):
	token = serializers.CharField()
	user = ResellerSerializer()

class DispatcherSerializer(WeixinSerializerMixIn, serializers.ModelSerializer):
	mob = serializers.CharField(source='mob_user.real_mob')
	create_time = TimestampField()
	class Meta:
		model = Dispatcher
		fields = ('id', 'name', 'tail', 'address', 
			'create_time', 'mob', 'wx_nickname', 'wx_headimgurl')

class DispatcherJWTSerializer(serializers.Serializer):
	token = serializers.CharField()
	user = DispatcherSerializer()

class LoginSerializerMixIn(serializers.Serializer):
	name = serializers.CharField(required=False, allow_blank=True)

	mainModel = None # Must implement it in sub class
	parentClass = None # Must implement it in sub class
	defaultFieldNames = [] # Must implement it in sub class

	def validate(self, attrs):
		attrs = self.parentClass.validate(self, attrs)
		mob_user = attrs['user']
		if mob_user:
			defaults = {}
			for fieldName in self.defaultFieldNames:
				fieldValue = attrs.get(fieldName)
				if fieldValue:
					defaults[fieldName] = fieldValue
			user, created = self.mainModel.objects.get_or_create(
				mob_user=mob_user,
				defaults=defaults
			)
			attrs['wrap_user'] = user
		else:
			msg = _('Unable to log in with provided credentials.')
			raise exceptions.ValidationError(msg)
		return attrs

class UserLoginSerializer(
	LoginSerializerMixIn, 
	BaseLoginSerializer):
	parentClass = BaseLoginSerializer
	defaultFieldNames = ['name']
	mainModel = User

class UserSocialLoginSerializer(
	LoginSerializerMixIn, 
	BaseSocialLoginSerializer):
	parentClass = BaseSocialLoginSerializer
	defaultFieldNames = ['name']
	mainModel = User

class ResellerLoginSerializer(
	LoginSerializerMixIn, 
	BaseLoginSerializer):
	parentClass = BaseLoginSerializer
	defaultFieldNames = ['name', 'tail']
	mainModel = Reseller

class ResellerSocialLoginSerializer(
	LoginSerializerMixIn, 
	BaseSocialLoginSerializer):
	parentClass = BaseSocialLoginSerializer
	defaultFieldNames = ['name', 'tail']
	mainModel = Reseller

class DispatcherLoginSerializer(
	LoginSerializerMixIn, 
	BaseLoginSerializer):
	parentClass = BaseLoginSerializer
	defaultFieldNames = ['name', 'tail', 'address']
	mainModel = Dispatcher

class DispatcherSocialLoginSerializer(
	LoginSerializerMixIn, 
	BaseSocialLoginSerializer):
	parentClass = BaseSocialLoginSerializer
	defaultFieldNames = ['name', 'tail', 'address']
	mainModel = Dispatcher

# Business Serializer model

class BulkListSerializer(RemoveNullSerializerMixIn, serializers.HyperlinkedModelSerializer):
	#url = serializers.HyperlinkedIdentityField(
	#	view_name='bulk-detail',
	#	lookup_field='id'
	#)
	reseller = serializers.SerializerMethodField(method_name='get_reseller_name')
	covers = serializers.SerializerMethodField(method_name='get_product_covers')
	create_time = TimestampField()
	dead_time = TimestampField()
	arrived_time = TimestampField()

	class Meta:
		model = Bulk
		fields = ('url', 'id', 'title', 'reseller', 'covers',
			'dead_time', 'arrived_time', 'status',
			'create_time')
		#extra_kwargs = {
		#	'url': {'view_name': 'bulk', 'lookup_field': 'id'}
		#}

	def get_reseller_name(self, obj):
		obj = obj.reseller
		if not hasattr(obj, 'mob_user'):
			return ''
		obj = obj.mob_user
		if not obj:
			return ''
		return obj.real_wx_nickname

	def get_product_covers(self, obj):
		return map(lambda p: p.cover.url 
			if hasattr(p.cover, 'url') 
			else '', obj.products.all())

class ProductListSerializer(serializers.ModelSerializer):
	create_time = TimestampField()
	participant_count = serializers.SerializerMethodField()
	purchased_count = serializers.SerializerMethodField()
	participant_avatars = serializers.SerializerMethodField()

	class Meta:
		model = Product
		fields = ('id', 'title', 'desc', 'unit_price', 'market_price',
			'spec', 'spec_desc', 'cover', 'create_time',
			'participant_count', 'purchased_count',
			'participant_avatars')

	def get_participant_count(self, obj):
		return Goods.objects.filter(product_id=obj.pk).count()

	def get_purchased_count(self, obj):
		result = Goods.objects.filter(product_id=obj.pk).aggregate(Sum('quantity'))
		return result.get('quantity__sum', 0)

	def get_participant_avatars(self, obj):
		avatars = dict()

		goods = Goods.objects.filter(product_id=obj.pk)
		for _ in goods:
			user = _.order.user
			if user.avatar:
				avatars[user.pk] = user.avatar.url
		return avatars.values()
		

class BulkSerializer(serializers.ModelSerializer):
	reseller = ResellerSerializer()
	dispatchers = DispatcherSerializer(many=True)
	create_time = TimestampField()
	dead_time = TimestampField()
	standard_time = StandardTimeField(source='*')
	arrived_time = TimestampField()
	products = ProductListSerializer(many=True)
	participant_count = serializers.SerializerMethodField()

	class Meta:
		model = Bulk
		fields = ('id', 'title', 'reseller', 'dispatchers', 
			'products', 'standard_time', 'dead_time', 
			'arrived_time', 'status', 'card_title', 'card_desc',
			'card_icon', 'create_time', 'participant_count')

	def get_participant_count(self, obj):
		return Order.objects.filter(bulk_id=obj.pk).count()









