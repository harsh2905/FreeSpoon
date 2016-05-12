#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import json
import time
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from basic.models import *
from . import utils, config

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

def createOrderInfo(orderId):
	order = fetchOrderById(orderId)
	if order is None:
		return None
	return createOrderInfo_(order)

def createOrdersInfo(openId):
	ws = []
	customer = None
	try:
		customer = Customer.objects.get(id_wechat=openId)
	except ObjectDoesNotExist:
		return ws
	if customer is None:
		return ws
	orders = Order.objects.filter(
		customer_id=customer.id).all()
	for order in orders:
		w = createSimpleOrderInfo_(order)
		ws.append(w)
	return ws

def createSimpleOrderInfo_(order):
	if order is None:
		return None
	w = DataObject()
	w.id = order.id
	w.leader = order.batch.leader.name
	w.status = order.status
	w.totalFee = int(order.total_fee)
	w.avatar = order.batch.leader.avatar.url
	pics = []
	total = 0
	for commodityInOrder in order.commodityinorder_set.all():
		img = commodityInOrder.commodity.commodity.commodityimage_set.first().image.url
		total = total + commodityInOrder.quantity
		pics.append(img)
	w.pics = pics
	w.total = total
	return w

def createOrderInfo_(order):
	if order is None:
		return None
	w = DataObject()
	w.commodities = []
	for commodityInOrder in order.commodityinorder_set.all():
		commodity = DataObject()
		commodity.title = commodityInOrder.commodity.commodity.title
		commodity.price = commodityInOrder.commodity.unit_price
		commodity.quantity = commodityInOrder.quantity
		w.commodities.append(commodity)
	w.id = order.id
	w.createTime = time.mktime(order.create_time.timetuple()) * 1000
	w.nickName = order.distributer.nick_name
	w.address = order.distributer.location
	w.tel = order.distributer.tel
	w.totalFee = int(order.total_fee)
	w.status = order.status
	return w

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
		commodity.describle = commodityInBatch.commodity.details
		img = commodityInBatch.commodity.commodityimage_set.first().image.url
		img = '%s%s' % (config.DOMAIN_URL, img)
		commodity.img = img
		commodity.spec = commodityInBatch.commodity.spec
		commodity.price = commodityInBatch.unit_price
		commodity.peopleCount = fetchCommodityAmounts(commodityInBatch.id)
		commodity.commodityCount = fetchCommodityQuantities(commodityInBatch.id)
		w.commodities.append(commodity)
	w.sponsor = DataObject(
		name=batch.leader.name,
		note=batch.leader.tail,
		img= '%s%s' % (config.DOMAIN_URL, batch.leader.avatar.url))
	w.offered = DataObject(
		offeredTotal=fetchOrderAmounts(batch.id),
		date=fetchBatchExpireTime(batch.id))
	return w

def createCheckoutInfo(batchId, openId):
	batch = fetchBatch(batchId)
	if batch is None:
		return None
	w = DataObject()
	dists = []
	for distributer in batch.distributers.all():
		dist = DataObject(
			id=distributer.id,
			address=distributer.location)
		dists.append(dist)
	w.dists = dists
	customer = fetchCustomer(openId)
	if customer is not None:
		w.nickName = customer.nick_name
		w.tel = customer.tel
	return w

def calcTotalFee(puchared):
	totalFee = 0
	for _ in puchared:
		id_ = _.get('id', None)
		if id_ is None:
			continue
		commodityInBatch = CommodityInBatch.objects.get(pk=id_)
		if commodityInBatch is not None:
			num = _.get('num', 0)
			totalFee += num * commodityInBatch.unit_price
	return totalFee

def createOrder(orderId, batchId, customerId, distId, status, prepayId, total_fee):
	try:
		return Order.objects.create(
			batch_id=batchId,
			customer_id=customerId,
			id=orderId,
			create_time=datetime.now(),
			status=status,
			prepay_id=prepayId,
			distributer_id=distId,
			total_fee=total_fee
		)
	except IntegrityError:
		return None

def updateOrCreateCustomer(nickname, tel, openid):
	return Customer.objects.update_or_create(
		id_wechat=openid,
		defaults={
			'nick_name': nickname,
			'tel': tel
		}
	)

def createCommoditiesToOrder(commodities, orderId):
	for commodity in commodities:
		id_ = commodity.get('id', None)
		if id_ is None:
			continue
		num = commodity.get('num', None)
		(commodityInOrder, iscreated) = CommodityInOrder.objects.get_or_create(
			quantity=num,
			commodity_id=id_,
			order_id=orderId)

def fetchOrderById(orderId):
	try:
		order = Order.objects.get(pk=orderId)
	except ObjectDoesNotExist:
		logger.error('Order id \'%s\' not found' % orderId)
		return None
	return order

def deleteOrderById(orderId):
	try:
		order = Order.objects.get(pk=orderId)
		order.delete()
	except ObjectDoesNotExist:
		logger.error('Order id \'%s\' not found' % orderId)
	CommodityInOrder.objects.filter(order_id=orderId).delete()

def setOrderStatus(order, status):
	order.status = status
	order.save()

def fetchCustomer(openid):
	if openid is None:
		return None
	try:
		customer = Customer.objects.get(id_wechat=openid)
	except ObjectDoesNotExist:
		return None
	return customer

def createShareInfo(batchId):
	batch = fetchBatch(batchId)
	if batch is None:
		return None
	w = DataObject()
	w.title = batch.share_title
	w.desc = batch.share_desc
	w.imgUrl = '%s%s' % (config.DOMAIN_URL, batch.share_img.url)
	w.shareUrl = '%s/api/r?state=%s' % (config.DOMAIN_URL, batchId)
	return w

# Old Method

def fetchCustomerTel(openid):
	if openid is None:
		return None
	try:
		customer = Customer.objects.get(id_wechat=openid)
	except ObjectDoesNotExist:
		return None
	return customer.tel

def fetchDist(distId):
	try:
		dist = Distributer.objects.get(pk=distId)
	except ObjectDoesNotExist:
		logger.error('Distributer id \'%s\' not found' % distId)
		return None
	return dist

def fetchOrders(batchId, distId):
	orders = Order.objects.filter(
		batch_id=batchId, distributer_id=distId).all()
	return orders

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
