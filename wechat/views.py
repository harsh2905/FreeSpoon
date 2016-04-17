#!/usr/bin/python
# -*- coding:utf-8 -*-

from datetime import datetime, timedelta
from decimal import Decimal
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.utils.safestring import SafeString
from django.views.decorators.csrf import csrf_exempt

import json
import logging
import qrcode

from wechat import data
from wechat import utils
from wechat.auth import Auth

auth = Auth()

import pdb

# Create your views here.

logger = logging.getLogger('django')

def _error(request, title, desc):
	logger.error('%s: %s' % (title, desc))
	template = loader.get_template('wechat/error.html')
	wxConfigJson = auth.createWXConfigJson(request.get_raw_uri(), [
		'closeWindow'])
	context = RequestContext(request, {
		'title': title,
		'desc': desc,
		'wxConfigJson': SafeString(json.dumps(wxConfigJson))
	})
	return HttpResponse(template.render(context))

def _ajaxError(errcode, errmsg):
	logger.error('%s: %s' % (errcode, errmsg))
	return HttpResponse({
		'errcode': errcode,
		'errmsg': errmsg
	}, content_type='application/json')


def createQRFromIndex(request):
	batch_id = request.GET.get('id', None)
	if batch_id is None:
		return _error(request, u'非法调用', u'参数不正确')
	indexUrl = 'http://carlinkall.com/wechat'
	url = auth.createAuthorizeRedirectUrl(indexUrl, batch_id)
	qr = qrcode.QRCode(
		version=None
	)
	qr.add_data(url)
	qr.make(fit=True)
	img = qr.make_image()
	response = HttpResponse(content_type='image/png')
	img.save(response, 'PNG')
	return response

def createQRFromIndexWithRedirect(request):
	batch_id = request.GET.get('id', None)
	if batch_id is None:
		return _error(request, u'非法调用', u'参数不正确')
	url = 'http://carlinkall.com/wechat/r?id=%s' % batch_id
	qr = qrcode.QRCode(
		version=None
	)
	qr.add_data(url)
	qr.make(fit=True)
	img = qr.make_image()
	response = HttpResponse(content_type='image/png')
	img.save(response, 'PNG')
	return response

def createQRFromConfirmWithRedirect(request):
	batch_id = request.GET.get('b', None)
	dist_id = request.GET.get('d', None)
	if batch_id is None or dist_id is None:
		return _error(request, u'非法调用', u'参数不正确')
	url = 'http://carlinkall.com/wechat/d?b=%s&d=%s' % (batch_id, dist_id)
	qr = qrcode.QRCode(
		version=None
	)
	qr.add_data(url)
	qr.make(fit=True)
	img = qr.make_image()
	response = HttpResponse(content_type='image/png')
	img.save(response, 'PNG')
	return response

def createUrlFromIndex(request):
	batch_id = request.GET.get('id', None)
	if batch_id is None:
		return _error(request, u'非法调用', u'参数异常')
	indexUrl = 'http://carlinkall.com/wechat'
	url = auth.createAuthorizeRedirectUrl(indexUrl, batch_id)
	return HttpResponse(url)

def redirectToIndex(request):
	batch_id = request.GET.get('id', None)
	if batch_id is None:
		return _error(request, u'非法调用', u'参数异常')
	indexUrl = 'http://carlinkall.com/wechat'
	url = auth.createAuthorizeRedirectUrl(indexUrl, batch_id)
	return HttpResponseRedirect(url)

def index(request):
	code = request.GET.get('code', None)
	batch_id = request.GET.get('state', None)
	if code is None or batch_id is None:
		return _error(request, u'非法调用', u'参数异常')
	userInfo = auth.fetchUserInfo(code)
	if userInfo is None:
		return _error(request, u'非法调用', u'参数异常')
	openid = userInfo.getOpenId()
	order = data.fetchOrder(batch_id, openid)
	if order is not None:
		#return _error(request, u'重复提交订单', u'重复提交订单')
		url = 'http://carlinkall.com/wechat/order?orderId=%s' % order.id
		return HttpResponseRedirect(url)
	tel = data.fetchCustomerTel(openid)
	tel = tel if tel is not None else ''
	batch = data.fetchBatch(batch_id)
	if batch is None:
		return _error(request, u'服务异常', u'未知的团购批次')
	expireTime = data.fetchBatchExpireTime(batch.id)
	if expireTime == 0:
		return _error(request, u'对不起', u'该团购已经结束')
	commodities = data.parseToCommodities(batch)
	orderAmounts = data.fetchOrderAmounts(batch.id)
	commoditiesJson = data.parseToCommoditiesJson(batch)
	distsJson = data.parseToDistJson(batch)
	wxConfigJson = auth.createWXConfigJson(request.get_raw_uri(), [
		'onMenuShareAppMessage', 'closeWindow'])
	shareUrl = 'http://carlinkall.com/wechat/r?id=%s' % batch_id
	context = RequestContext(request, {
		'batch': batch,
		'commodities': commodities,
		'orderAmounts': orderAmounts,
		'expireTime': expireTime,
		'commoditiesJson': SafeString(commoditiesJson),
		'distsJson': SafeString(distsJson),
		'wxConfigJson': SafeString(json.dumps(wxConfigJson)),
		'userInfo': userInfo,
		'userInfoJson': SafeString(userInfo.json()),
		'tel': tel,
		'shareUrl': shareUrl
	})
	template = loader.get_template('wechat/index.html')
	return HttpResponse(template.render(context))

@csrf_exempt
def unifiedOrder(request):
	if not request.is_ajax():
		return _error(request, u'非法访问', u'未知错误')
	if request.method <> 'POST':
		return _ajaxError(-1, u'非法访问')
	requestData = json.loads(request.body, parse_float=Decimal)
	nickname = requestData.get('nick_name', None)
	openid = requestData.get('openid', None)
	tel = requestData.get('tel', None)
	if nickname is None or openid is None or tel is None:
		return _ajaxError(-1, u'参数异常')
	batch_id = requestData.get('batch_id', None)
	dist_id = requestData.get('dist_id', None)
	commodities = requestData.get('commodities', None)
	ipaddress = requestData.get('ipaddress', None)
	if batch_id is None or dist_id is None \
		or commodities is None or ipaddress is None:
		return _ajaxError(-1, u'参数异常')
	(customer, iscreated) = data.updateOrCreateCustomer(
		nickname, openid, tel)
	batch = data.fetchBatch(batch_id)
	if batch is None:
		return _ajaxError(request, -1, u'团购批次错误')
		return _error(request, u'非法访问', u'团购批次错误')
	orderId = utils.createOrderId()
	# TODO Verify
	total_fee = data.calcTotalFee(commodities)
	time_start = datetime.now()
	time_expire = time_start + timedelta(minutes=30)
	prepay_id = auth.createPrepayId(
		orderId=orderId,
		total_fee=total_fee,
		ipaddress=ipaddress,
		time_start=time_start,
		time_expire=time_expire,
		openid=customer.id_wechat,
		title=batch.title,
		detail=batch.desc,
		notify_url='http://carlinkall.com/wechat/payNotify'
	)
	if prepay_id is None:
		return _ajaxError(request, -1, u'提交订单错误')
	(order, iscreated) = data.getOrCreateOrder(
		orderId, batch_id, customer.id, dist_id, 0, prepay_id, total_fee)
	if not iscreated:
		return _ajaxError(request, -1, u'重复提交订单')
	data.createCommoditiesToOrder(commodities, order.id)
	result = {
		'errcode': 0,
		'errmsg': '',
		'orderId': orderId
	}
	return HttpResponse(json.dumps(result),
		content_type='application/json')

def order(request):
	orderId = request.GET.get('orderId', None)
	if orderId is None:
		orderId = request.POST.get('orderId', None)
	if orderId is None:
		return _error(request, u'非法调用', u'参数错误')
	pay = request.POST.get('pay', None)
	pay = 'false' if pay is None or pay <> 'yes' else 'true'
	order = data.fetchOrderById(orderId)
	payRequest = auth.createPayRequestJson(order.prepay_id)
	orderAmounts = data.fetchOrderAmounts(order.batch.id) + 1
	wxConfigJson = auth.createWXConfigJson(request.get_raw_uri(), [
		'chooseWXPay', 'onMenuShareAppMessage', 'closeWindow'])
	shareUrl = 'http://carlinkall.com/wechat/r?id=%s' % order.batch.id
	context = RequestContext(request, {
		'order': order,
		'payRequest': SafeString(json.dumps(payRequest)),
		'orderAmounts': orderAmounts,
		'wxConfigJson': SafeString(json.dumps(wxConfigJson)),
		'shareUrl': shareUrl,
		'pay': pay 
	})
	template = loader.get_template('wechat/order.html')
	return HttpResponse(template.render(context))

@csrf_exempt
def payNotify(request):
	error = {
		"return_code": "FAIL"
	}
	orderId = auth.payNotify(request.body)
	if orderId is None:
		error['return_msg'] = 'Error'
    		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	orderId = int(orderId)
	order = data.fetchOrderById(orderId)
	if order is None:
		error['return_msg'] = 'Error'
    		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	if order.status > 1:
		error['return_msg'] = 'Error'
    		xml = utils.mapToXml(error)
		return HttpResponse(xml,
			content_type='text/xml')
	data.setOrderStatus(order, 1)
	success = {
		"return_code": "SUCCESS",
		"return_msg": ""
	}
	xml = utils.mapToXml(success)
	return HttpResponse(xml,
		content_type='text/xml')

def redirectToConfirm(request):
	batch_id = request.GET.get('b', None)
	dist_id = request.GET.get('d', None)
	if batch_id is None or dist_id is None:
		return _error(request, u'非法调用', u'参数异常')
	confirmUrl = 'http://carlinkall.com/wechat/confirm'
	state = '%s,%s' % (batch_id, dist_id)
	url = auth.createAuthorizeRedirectUrl(confirmUrl, state)
	return HttpResponseRedirect(url)

def confirm(request):
	code = request.GET.get('code', None)
	state = request.GET.get('state', None)
	if code is None or state is None:
		return _error(request, u'非法调用', u'参数异常')
	args = state.split(',')
	if len(args) <> 2:
		return _error(request, u'非法调用', u'参数异常')
	batch_id = int(args[0])
	dist_id = int(args[1])
	userInfo = auth.fetchUserInfo(code)
	openid = userInfo.getOpenId()
	order = data.fetchOrder(batch_id, openid)
	if order.status <> 1:
		return _error(request, u'服务器错误', u'订单状态错误')
	if order.distributer.id <> dist_id:
		return _error(request, u'错误', u'配送点错误')
	template = loader.get_template('wechat/confirm.html')
	context = RequestContext(request, {
		'userInfo': userInfo,
		'order': order,
		'datetime': datetime.now()
	})
	return HttpResponse(template.render(context))

def complete(request):
	if request.method <> 'POST':
		return _error(request, u'非法调用', u'非法访问')
	orderId = request.POST.get('order_id', None)
	if orderId is None:
		return _error(request, u'非法调用', u'参数异常')
	order = data.fetchOrderById(orderId)
	if order is None:
		return _error(request, u'服务器错误', u'未知订单')
	if order.status <> 1:
		return _error(request, u'服务器错误', u'订单状态错误')
	data.setOrderStatus(order, 2)
	template = loader.get_template('wechat/complete.html')
	wxConfigJson = auth.createWXConfigJson(request.get_raw_uri(), [
		'closeWindow'])
	context = RequestContext(request, {
		'order': order,
		'datetime': datetime.now(),
		'wxConfigJson': SafeString(json.dumps(wxConfigJson))
	})
	return HttpResponse(template.render(context))

def createQRFromConfirm(request):
	batch_id = request.GET.get('id', None)
	if batch_id is None:
		return _error(request, u'非法调用', u'参数不正确')
	confirmUrl = 'http://carlinkall.com/wechat/confirm'
	url = auth.createAuthorizeRedirectUrl(confirmUrl, batch_id)
	qr = qrcode.QRCode(
		version=None
	)
	qr.add_data(url)
	qr.make(fit=True)
	img = qr.make_image()
	response = HttpResponse(content_type='image/png')
	img.save(response, 'PNG')
	return response

def distReport(request):
	batch_id = request.GET.get('b', None)
	dist_id = request.GET.get('d', None)
	if batch_id is None or dist_id is None:
		return _error(request, u'非法调用', u'参数不正确')
	batch = data.fetchBatch(batch_id)
	if batch is None:
		return _error(request, u'服务器错误', u'团购批次不存在')
	dist = data.fetchDist(dist_id)
	if dist is None:
		return _error(request, u'服务器错误', u'派送员不存在')
	orders = data.fetchOrders(batch_id, dist_id)
	template = loader.get_template('wechat/distReport.html')
	context = RequestContext(request, {
		'batch': batch,
		'distributer': dist,
		'orders': orders,
		'datetime': datetime.now()
	})
	return HttpResponse(template.render(context))
