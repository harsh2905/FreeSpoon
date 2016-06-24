from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from authentication.models import MobUser
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class User(models.Model):
	related_field_name = 'user'
	mob_user = models.OneToOneField(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	name = models.CharField(max_length=100, null=True, blank=True)
	avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
	balance = models.IntegerField(max_length=11, default=0)
	recent_obtain_name = models.CharField(max_length=100, null=True, blank=True)
	recent_obtain_mob = models.CharField(max_length=20, null=True, blank=True)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return '%s(%s)' % (self.name, self.id)

class Reseller(models.Model):
	related_field_name = 'reseller'
	mob_user = models.OneToOneField(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	name = models.CharField(max_length=100, null=True, blank=True)
	avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
	tail = models.CharField(max_length=255, blank=True)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return self.name
	
class Dispatcher(models.Model):
	related_field_name = 'dispatcher'
	mob_user = models.OneToOneField(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	name = models.CharField(max_length=100, null=True, blank=True)
	avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
	tail = models.CharField(max_length=255, blank=True)
	address = models.TextField()
	opening_time = models.IntegerField(max_length=11)
	closing_time = models.IntegerField(max_length=11)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return self.name

class Product(models.Model):
	title = models.CharField(max_length=200)
	desc = models.TextField()
	bulk = models.ForeignKey('Bulk', null=True, blank=True)
	unit_price = models.IntegerField(max_length=11)
	market_price = models.IntegerField(max_length=11)
	tag = models.CharField(max_length=20, null=True, blank=True)
	spec = models.CharField(max_length=100)
	spec_desc = models.CharField(max_length=100)
	cover = models.ImageField(upload_to='images/product/%Y/%m/%d')
	is_snapshot = models.BooleanField(default=False)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		if self.is_snapshot:
			return '%s[SnapShot]' % self.title
		return self.title

class ProductDetails(models.Model):
	product = models.ForeignKey('Product')
	image = models.ImageField(upload_to='images/product_details/%Y/%m/%d')
	plain = models.TextField()
	seq = models.IntegerField(max_length=11)
	is_snapshot = models.BooleanField(default=False)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return '%s[%s]' % (self.product.title, self.seq)
	class Meta:
		verbose_name = 'Product details'
		verbose_name_plural = 'Product details'

class Bulk(models.Model):
	title = models.CharField(max_length=200)
	category = models.CharField(max_length=100)
	details = models.TextField()
	reseller = models.ForeignKey('Reseller')
	dispatchers = models.ManyToManyField('Dispatcher')
	dead_time = models.DateTimeField()
	arrived_time = models.DateTimeField()
	status = models.IntegerField(max_length=11)
	location = models.CharField(max_length=100)
	card_title = models.CharField(max_length=100)
	card_desc = models.CharField(max_length=255)
	card_icon = models.ImageField(upload_to='images/card_icon/%Y/%m/%d', blank=True)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return self.title

class Order(models.Model):
	id = models.CharField(max_length=200, primary_key=True)
	user = models.ForeignKey('User')
	bulk = models.ForeignKey('Bulk')
	dispatcher = models.ForeignKey('Dispatcher')
	status = models.IntegerField(max_length=11)
	freight = models.IntegerField(max_length=11)
	total_fee = models.IntegerField(max_length=11)
	create_time = models.DateTimeField(auto_now=True)
	obtain_name = models.CharField(max_length=100, null=True, blank=True)
	obtain_mob = models.CharField(max_length=20, null=True, blank=True)
	is_delete = models.BooleanField(default=False)
	def __unicode__(self):
		return '%s(User: %s, Date: %s)' % (
			self.bulk.title, self.user.name, self.create_time)

class Goods(models.Model):
	order = models.ForeignKey('Order')
	product = models.ForeignKey('Product')
	quantity = models.IntegerField(max_length=11)
	def __unicode__(self):
		return self.product.title
	class Meta:
		verbose_name = 'Goods'
		verbose_name_plural = 'Goods'

class ShippingAddress(models.Model):
	user = models.ForeignKey('User')
	name = models.CharField(max_length=200)
	mob = models.CharField(max_length=20)
	address = models.TextField()
	def __unicode__(self):
		return self.address

# Views

class PurchasedProductHistory(models.Model):
	order = models.ForeignKey('Order', primary_key=True,
		on_delete=models.DO_NOTHING)
	product = models.ForeignKey('Product',
		on_delete=models.DO_NOTHING, null=True)
	bulk = models.ForeignKey('Bulk',
		on_delete=models.DO_NOTHING, null=True)
	mob_user = models.ForeignKey(settings.AUTH_USER_MODEL, 
		on_delete=models.DO_NOTHING, null=True)
	name = models.CharField(max_length=100, null=True, blank=True)
	quantity = models.IntegerField(max_length=11)
	spec = models.CharField(max_length=100)
	create_time = models.DateTimeField()

	class Meta:
		managed = False
		db_table = 'view_history_purchased_products'

class PayRequest(models.Model):
	order = models.OneToOneField('Order', on_delete=models.CASCADE)
	third_party_order_id = models.CharField(max_length=200)
	third_party_fee = models.IntegerField(default=0)
	balance_fee = models.IntegerField(default=0)
	use_balance = models.IntegerField(default=0)
	status = models.IntegerField(default=0)

class Slide(models.Model):
	link = models.CharField(max_length=200)
	image = models.ImageField(upload_to='images/slide/%Y/%m/%d')
	category = models.CharField(max_length=100, null=True, blank=True)
	seq = models.IntegerField(max_length=11)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return self.link

class ExhibitedProduct(models.Model):
	exhibit = models.ForeignKey('Exhibit')
	product = models.ForeignKey('Product')
	cover = models.ImageField(upload_to='images/exhibited_product/%Y/%m/%d', null=True, blank=True)
	seq = models.IntegerField(max_length=11)
	stick = models.BooleanField(default=False)
	def __unicode__(self):
		return self.product.title

class Exhibit(models.Model):
	slides = models.ManyToManyField('Slide')
	hot_bulks = models.ManyToManyField('Bulk')
	hot_products = models.ManyToManyField('Product', through='ExhibitedProduct')
	publish_time = models.DateTimeField()
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.publish_time)

class RecipeExhibit(models.Model):
	slides = models.ManyToManyField('Slide')
	publish_time = models.DateTimeField()
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.publish_time)

class Step(models.Model):
	recipe = models.ForeignKey('Recipe')
	image = models.ForeignKey('Image', on_delete=models.SET_NULL, null=True, blank=True)
	plain = models.TextField(blank=True)
	seq = models.IntegerField(max_length=11)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return '%s[%s]' % (self.recipe.name, self.seq)
	class Meta:
		verbose_name = 'Step details'
		verbose_name_plural = 'Step details'

class Ingredient(models.Model):
	recipe = models.ForeignKey('Recipe')
	name = models.CharField(max_length=200, blank=True)
	seq = models.IntegerField(max_length=11)
	quantity = models.CharField(max_length=200, blank=True)
	def __unicode__(self):
		return self.name

class Recipe(models.Model):
	create_time = models.DateTimeField(auto_now=True)
	name = models.CharField(max_length=200, blank=True)
	user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
	desc = models.TextField(blank=True)
	cover = models.ForeignKey('Image', on_delete=models.SET_NULL, null=True, blank=True)
	status = models.IntegerField(max_length=11)
	tag = models.CharField(max_length=200, null=True, blank=True)
	tips = models.ManyToManyField('Tip')
	time = models.CharField(max_length=200, null=True, blank=True)
	def __unicode__(self):
		return self.name

class DishDetails(models.Model):
	dish = models.ForeignKey('Dish')
	image = models.ForeignKey('Image', on_delete=models.SET_NULL, null=True, blank=True)
	plain = models.TextField(blank=True)
	seq = models.IntegerField(max_length=11)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return '%s[%s]' % (self.dish.name, self.seq)
	class Meta:
		verbose_name = 'Dish details'
		verbose_name_plural = 'Dish details'

class Tip(models.Model):
	plain = models.TextField(blank=True)
	def __unicode__(self):
		return self.plain

class Dish(models.Model):
	create_time = models.DateTimeField(auto_now=True)
	name = models.CharField(max_length=200, blank=True)
	desc = models.TextField(blank=True)
	recipe = models.ForeignKey('Recipe', on_delete=models.SET_NULL, null=True, blank=True)
	cover = models.ForeignKey('Image', on_delete=models.SET_NULL, null=True, blank=True)
	user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
	status = models.IntegerField(max_length=11)
	tag = models.CharField(max_length=200, null=True, blank=True)
	tips = models.ManyToManyField('Tip')
	def __unicode__(self):
		return self.name

class Image(models.Model):
	md5 = models.CharField(max_length=200, primary_key=True)
	create_time = models.DateTimeField(auto_now=True)
	image = models.ImageField(upload_to='images/upload/%Y/%m/%d')
	def __unicode__(self):
		return self.md5
