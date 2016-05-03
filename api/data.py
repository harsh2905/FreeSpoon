#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import json
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from basic.models import *
from . import utils

import pdb

logger = logging.getLogger('django')

class DataObject(object):
	def __init__(self, **kwargs):
		for (key, value) in kwargs.items():
			setattr(self, key, value)

# Method

def fetchBatch(batchId):
	try:
		batch = Batch.objects.get(pk=batchId)
	except ObjectDoesNotExist:
		logger.error('Batch id \'%s\' not found' % batchId)
		return None
	return batch

def fetchCommodityQuantities(commodityId):
	commodities = CommodityInOrder.objects.filter(commodity_id=commodityId).all()
	quantities = 0
	for commodity in commodities:
		quantities += commodity.quantity
	return quantities

def fetchOrderAmounts(batchId):
	return Order.objects.filter(batch_id=batchId, status__gt=0).count()

def fetchCommodityAmounts(commodityId):
	return CommodityInOrder.objects.filter(commodity_id=commodityId).count()

def fetchBatchExpireTime(batchId):
	try:
		batch = Batch.objects.get(pk=batchId)
	except ObjectDoesNotExist:
		logger.error('Batch id \'%s\' not found' % batchId)
		return None
	endTime = batch.end_time.replace(tzinfo=None)
	now = datetime.now()
	if endTime > now:
		delta = endTime - now
		return delta.days + 1
	else:
		return 0

def createBatchInfo(batchId):
	batch = fetchBatch(batchId)
	if batch is None:
		return None
	w = DataObject()
	w.commodities = []
	for commodityInBatch in batch.commodityinbatch_set.all():
		commodity = DataObject()
		commodity.id = commodityInBatch.id
		commodity.title = commodityInBatch.commodity.title
		commodity.describle = commodityInBatch.commodity.desc
		commodity.img = commodityInBatch.commodity.commodityimage_set.first().image.url
		commodity.spec = commodityInBatch.commodity.spec
		commodity.price = commodityInBatch.unit_price
		commodity.peopleCount = fetchCommodityAmounts(commodityInBatch.id)
		commodity.commodityCount = fetchCommodityQuantities(commodityInBatch.id)
		w.commodities.append(commodity)
	w.sponsor = DataObject(
		name=batch.leader.name,
		note=batch.leader.tail,
		img=batch.leader.avatar.url)
	w.offered = DataObject(
		offeredTotal=fetchOrderAmounts(batch.id),
		date=fetchBatchExpireTime(batch.id))
	return w

def createCheckoutInfo(batchId):
	batch = fetchBatch(batchId)
	if batch is None:
		return None
	w = []
	for distributer in batch.distributers.all():
		dist = DataObject(
			id=distributer.id,
			address=distributer.location)
		w.append(dist)
	return w

# Old Method

def updateOrCreateCustomer(nickname, openid, tel):
	return Customer.objects.update_or_create(
		id_wechat=openid,
		defaults={
			'nick_name': nickname,
			'tel': tel
		}
	)

def getOrCreateOrder(orderId, batchId, customerId, distId, status, prepayId, total_fee):
	return Order.objects.get_or_create(
		batch_id=batchId,
		customer_id=customerId,
		defaults={
			'id': orderId,
			'create_time': datetime.now(),
			'status': status,
			'prepay_id': prepayId,
			'distributer_id': distId,
			'total_fee': total_fee
		}
	)

def fetchCustomerTel(openid):
	if openid is None:
		return None
	try:
		customer = Customer.objects.get(id_wechat=openid)
	except ObjectDoesNotExist:
		return None
	return customer.tel

def fetchCustomer(openid):
	if openid is None:
		return None
	try:
		customer = Customer.objects.get(id_wechat=openid)
	except ObjectDoesNotExist:
		return None
	return customer

def fetchDist(distId):
	try:
		dist = Distributer.objects.get(pk=distId)
	except ObjectDoesNotExist:
		logger.error('Distributer id \'%s\' not found' % distId)
		return None
	return dist

def fetchOrderById(orderId):
	try:
		order = Order.objects.get(pk=orderId)
	except ObjectDoesNotExist:
		logger.error('Order id \'%s\' not found' % orderId)
		return None
	return order

def fetchOrders(batchId, distId):
	orders = Order.objects.filter(
		batch_id=batchId, distributer_id=distId).all()
	return orders

def setOrderStatus(order, status):
	order.status = status
	order.save()

def fetchOrder(batchId, openid):
	customer = fetchCustomer(openid)
	if customer is None:
		return None
	try:
		order = Order.objects.get(
			batch_id=batchId, customer_id=customer.id)
	except ObjectDoesNotExist:
		logger.error('Order not found')
		return None
	return order

def createCommoditiesToOrder(commodities, orderId):
	for commodity in commodities:
		id_ = commodity.get('id', None)
		if id_ is None:
			continue
		quantity = commodity.get('quantity', None)
		(commodityInOrder, iscreated) = CommodityInOrder.objects.get_or_create(
			quantity=quantity,
			commodity_id=id_,
			order_id=orderId)

def calcTotalFee(commodities):
	totalFee = 0
	for commodity in commodities:
		id_ = commodity.get('id', None)
		if id_ is None:
			continue
		quantity = commodity.get('quantity', None)
		commodityInBatch = CommodityInBatch.objects.get(pk=id_)
		if commodityInBatch is not None:
			totalFee += quantity * commodityInBatch.unit_price
	return totalFee

def parseToCommoditiesJson(batch):
	if batch is None:
		logger.error('Batch is null')
		return None
	commodities = {}
	for commodityInBatch in batch.commodityinbatch_set.all():
		commodity = {}
		commodity['id'] = commodityInBatch.id
		commodity['title'] = commodityInBatch.commodity.title
		commodity['unit_price'] = commodityInBatch.unit_price
		commodity['quota'] = commodityInBatch.quota
		commodities[str(commodityInBatch.id)] = commodity
	commoditiesJson = json.dumps(commodities)
	return commoditiesJson

def parseToDistJson(batch):
	if batch is None:
		logger.error('Batch is null')
		return None
	dists = {}
	for distributer in batch.distributers.all():
		dist = {}
		dist['id'] = distributer.id
		dist['name'] = distributer.name
		dist['location'] = distributer.location
		dists[str(distributer.id)] = dist
	distsJson = json.dumps(dists)
	return distsJson

def fetchRecentTel(customerId):
	try:
		customer = Customer.objects.get(pk=customerId)
	except ObjectDoesNotExist:
		logger.error('Customer id \'%s\' not found' % customerId)
		return None
	return customer.tel
