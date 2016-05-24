from __future__ import unicode_literals

from django.db import models

# Create your models here.

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

class User(models.Model):
	tel = models.CharField(max_length=20, unique=True)
	passwd = models.CharField(max_length=100)
	name = models.CharField(max_length=200)
	id_wechat = models.CharField(max_length=200, unique=True)
	avatar = models.CharField(max_length=200)
	def render(self):
		return u'<img style="max-height:150px;" src="%s" />' % self.avatar.url
	render.allow_tags = True
	def __unicode__(self):
		return self.name

class Customer(models.Model):
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

