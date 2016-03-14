from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Leader(models.Model):
	name = models.CharField(max_length=200)
	nick_name = models.CharField(max_length=200)
	id_card = models.CharField(max_length=13, unique=True)
	tel = models.CharField(max_length=20, unique=True)
	id_wechat = models.CharField(max_length=200, unique=True)
	avatar = models.ImageField(upload_to='avatars', blank=True)
	tail = models.CharField(max_length=255, blank=True)
	create_time = models.DateTimeField(auto_now=True)
	successful_times = models.IntegerField(max_length=10)
	def __unicode__(self):
		return self.name

class Batch(models.Model):
	title = models.CharField(max_length=200)
	desc = models.CharField(max_length=255)
	leader = models.ForeignKey(Leader)
	commodities = models.ManyToManyField('Commodity', through='CommodityInBatch')
	start_time = models.DateTimeField(auto_now=True)
	end_time = models.DateTimeField()
	status = models.IntegerField(max_length=10)
	def __unicode__(self):
		return self.title

class Commodity(models.Model):
	title = models.CharField(max_length=200)
	desc = models.CharField(max_length=255)
	details = models.TextField()
	spec = models.CharField(max_length=200)
	stock = models.IntegerField(max_length=10)
	def __unicode__(self):
		return self.title

class CommodityImage(models.Model):
	commodity = models.ForeignKey(Commodity)
	image = models.ImageField(upload_to='images/commodity/%Y/%m/%d')
	def render(self):
		return u'<img style="max-height:150px;" src="%s" />' % self.image.url
	render.allow_tags = True

class CommodityInBatch(models.Model):
	batch = models.ForeignKey(Batch)
	commodity = models.ForeignKey(Commodity)
	unit_price = models.DecimalField(max_digits=9, decimal_places=2)
	quota = models.IntegerField(max_length=10)
	def __unicode__(self):
		return str(self.id)

class Customer(models.Model):
	nick_name = models.CharField(max_length=200)
	id_wechat = models.CharField(max_length=200, unique=True)
	tel = models.CharField(max_length=20, unique=True)
	def __unicode__(self):
		return self.nick_name

class Distributer(models.Model):
	name = models.CharField(max_length=200)
	nick_name = models.CharField(max_length=200)
	id_card = models.CharField(max_length=13, unique=True)
	tel = models.CharField(max_length=20, unique=True)
	id_wechat = models.CharField(max_length=200, unique=True)
	avatar = models.ImageField(upload_to='avatars', blank=True)
	tail = models.CharField(max_length=255, blank=True)
	create_time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return self.name

class Order(models.Model):
	customer = models.ForeignKey(Customer)
	batch = models.ForeignKey(Batch)
	commodities = models.ManyToManyField(Commodity, through='CommodityInOrder')
	create_time = models.DateTimeField(auto_now=True)
	status = models.IntegerField(max_length=10)
	def __unicode__(self):
		return '%s - %s - %s' % (
			self.batch.title, self.customer.nick_name, self.create_time)

class CommodityInOrder(models.Model):
	order = models.ForeignKey(Order)
	commodity = models.ForeignKey(Commodity)
	quantity = models.IntegerField(max_length=10)
	price = models.DecimalField(max_digits=9, decimal_places=2)
	def __unicode__(self):
		return str(self.id)

