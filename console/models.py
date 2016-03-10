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
	def __str__(self):
		return self.name

class Batch(models.Model):
	title = models.CharField(max_length=200)
	desc = models.CharField(max_length=255)
	leader = models.ForeignKey(Leader)
	start_time = models.DateTimeField(auto_now=True)
	end_time = models.DateTimeField()
	status = models.IntegerField(max_length=10)
	def __str__(self):
		return self.title

class Commodity(models.Model):
	batch = models.ForeignKey(Batch)
	title = models.CharField(max_length=200)
	desc = models.CharField(max_length=255)
	details = models.TextField()
	unit_price = models.DecimalField(max_digits=9, decimal_places=2)
	spec = models.CharField(max_length=200)
	stock = models.IntegerField(max_length=10)
	quota = models.IntegerField(max_length=10)
	def __str__(self):
		return self.title

class Customer(models.Model):
	nick_name = models.CharField(max_length=200)
	id_wechat = models.CharField(max_length=200, unique=True)
	tel = models.CharField(max_length=20, unique=True)
	def __str__(self):
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
	def __str__(self):
		return self.name

class Order(models.Model):
	customer = models.ForeignKey(Customer)
	batch = models.ForeignKey(Batch)
	commodities = models.ManyToManyField(Commodity, through='Membership_Order_To_Commodities')
	create_time = models.DateTimeField(auto_now=True)
	status = models.IntegerField(max_length=10)
	def __str__(self):
		return '%s - %s - %s' % (
			self.batch.title, self.customer.nick_name, self.create_time)

class Membership_Order_To_Commodities(models.Model):
	order = models.ForeignKey(Order)
	commodity = models.ForeignKey(Commodity)
	quantity = models.IntegerField(max_length=10)
	price = models.DecimalField(max_digits=9, decimal_places=2)
	def __str__(self):
		return str(self.id)

