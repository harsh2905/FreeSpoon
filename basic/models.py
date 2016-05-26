from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser)
from django.db import models

# Create your models here.

class UserManager(BaseUserManager):
	def create_user(self, tel, password=None):
		if not tel:
			raise ValueError('Users must have an telephone number')
		user = self.model(
			tel=tel
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, tel, password):
		user = self.create_user(tel, password=password)
		user.is_admin = True
		user.save(using=self._db)
		return user

class User(AbstractBaseUser):
	tel = models.CharField(max_length=20, unique=True)
	USERNAME_FIELD = 'tel'
	name = models.CharField(max_length=200)
	id_wechat = models.CharField(max_length=200)
	avatar = models.CharField(max_length=200)
	create_time = models.DateTimeField(auto_now=True)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	objects = UserManager()
	def get_full_name(self):
		return self.name
	def get_short_name(self):
		return self.name
	def has_perm(self, perm, obj=None):
		return True
	def has_module_perms(self, app_label):
		return True
	def render(self):
		return u'<img style="max-height:150px;" src="%s" />' % self.avatar.url
	render.allow_tags = True
	def __unicode__(self):
		return self.tel

	@property
	def is_staff(self):
		return self.is_admin

class Leader(models.Model):
	name = models.CharField(max_length=200)
	tel = models.CharField(max_length=20, unique=True)
	id_wechat = models.CharField(max_length=200, unique=True)
	avatar = models.ImageField(upload_to='avatars', blank=True)
	def render(self):
		return u'<img style="max-height:150px;" src="%s" />' % self.avatar.url
	render.allow_tags = True
	tail = models.CharField(max_length=255, blank=True)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return self.name

class Batch(models.Model):
	title = models.CharField(max_length=200)
	detail = models.CharField(max_length=200)
	leader = models.ForeignKey(Leader)
	distributers = models.ManyToManyField('Distributer')
	commodities = models.ManyToManyField('Commodity', through='CommodityInBatch')
	start_time = models.DateTimeField(auto_now=True)
	end_time = models.DateTimeField()
	status = models.IntegerField(max_length=10)
	share_title = models.CharField(max_length=200)
	share_desc = models.CharField(max_length=255)
	share_img = models.ImageField(upload_to='shareImg', blank=True)
	def __unicode__(self):
		return self.title

class Commodity(models.Model):
	title = models.CharField(max_length=200)
	details = models.TextField()
	spec = models.CharField(max_length=200)
	image = models.ImageField(upload_to='images/commodity/%Y/%m/%d')
	def render(self):
		return u'<img style="max-height:150px;" src="%s" />' % self.image.url
	render.allow_tags = True
	def __unicode__(self):
		return self.title

class CommodityInBatch(models.Model):
	batch = models.ForeignKey(Batch)
	commodity = models.ForeignKey(Commodity)
	unit_price = models.IntegerField(max_length=10)
	def __unicode__(self):
		return self.commodity.title

class Customer(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	nick_name = models.CharField(max_length=200)
	id_wechat = models.CharField(max_length=200, unique=True)
	avatar = models.CharField(max_length=200)
	def render(self):
		return u'<img style="max-height:150px;" src="%s" />' % self.avatar.url
	render.allow_tags = True
	tel = models.CharField(max_length=20, unique=True)
	def __unicode__(self):
		return self.nick_name

class Distributer(models.Model):
	name = models.CharField(max_length=200)
	tel = models.CharField(max_length=20, unique=True)
	id_wechat = models.CharField(max_length=200, unique=True)
	avatar = models.ImageField(upload_to='avatars', blank=True)
	def render(self):
		return u'<img style="max-height:150px;" src="%s" />' % self.avatar.url
	render.allow_tags = True
	tail = models.CharField(max_length=255, blank=True)
	create_time = models.DateTimeField(auto_now=True)
	location = models.TextField()
	def __unicode__(self):
		return self.name

class Order(models.Model):
	id = models.CharField(max_length=200, primary_key=True)
	customer = models.ForeignKey(Customer)
	batch = models.ForeignKey(Batch)
	distributer = models.ForeignKey(Distributer)
	commodities = models.ManyToManyField(CommodityInBatch, through='CommodityInOrder')
	create_time = models.DateTimeField(auto_now=True)
	status = models.IntegerField(max_length=10)
	prepay_id = models.CharField(max_length=200)
	total_fee = models.DecimalField(max_digits=9, decimal_places=2)
	def __unicode__(self):
		return '%s - %s - %s' % (
			self.batch.title, self.customer.nick_name, self.create_time)

class CommodityInOrder(models.Model):
	order = models.ForeignKey(Order)
	commodity = models.ForeignKey(CommodityInBatch)
	quantity = models.IntegerField(max_length=10)
	def __unicode__(self):
		return self.commodity.commodity.title

