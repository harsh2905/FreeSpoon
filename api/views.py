from django.shortcuts import render

import qrcode
from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from . import wx, utils, data, config
from .interface import *

wxAuth = wx.Auth()


# Create your views here.

def error():
	return HttpResponse('Bad Request')

def main(request):
	return HttpResponse('FreeSpoon API v0.0.1')

def redirector(request, relativePath):
	if request.method <> 'GET':
		return error()
	state = request.GET.get('state', None)
	if state is None:
		return error()
	targetUrl = '%s%s' % (config.DOMAIN_URL, relativePath)
	redirectUrl = wxAuth.createAuthorizeBaseRedirectUrl(targetUrl, state)
	return HttpResponseRedirect(redirectUrl)

def createQR(request):
	if request.method <> 'GET':
		return error()
	qr = qrcode.QRCode(
		version=None
	)
	targetUrl = request.get_raw_uri()
	targetUrl = targetUrl.replace('/q/', '/')
	qr.add_data(targetUrl)
	qr.make(fit=True)
	img = qr.make_image()
	response = HttpResponse(content_type='image/png')
	img.save(response, 'PNG')
	return response

# Business Views

@csrf_exempt
def wxConfig(request):
	if request.method == 'OPTIONS':
		return CrossDomainResponse() 
	if request.method <> 'POST':
		return JSONResponse(ResObject('InvalidRequest'))
	requestData = json.loads(request.body, parse_float=Decimal)
	jsApiList = requestData.get('jsApiList', None)
	if jsApiList is None:
		return JSONResponse(ResObject('InvalidRequest'))
	url = requestData.get('url', None)
	if url is None:
		return JSONResponse(ResObject('InvalidRequest'))
	wxConfig = wxAuth.createWXConfig(url, jsApiList)
	res = ResObject('Success')
	res.put('wxConfig', wxConfig)
	return JSONResponse(res)

@csrf_exempt
def batch(request):
	if request.method == 'OPTIONS':
		return CrossDomainResponse() 
	if request.method <> 'POST':
		return JSONResponse(ResObject('InvalidRequest'))
	requestData = json.loads(request.body, parse_float=Decimal)
	batchId = requestData.get('batchId', None)
	if batchId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res = ResObject('Success')
	code = requestData.get('code', None)
	if code is not None:
		openId = wxAuth.fetchOpenId(code)
		if openId is not None:
			res.put('openId', openId)
	do = data.createBatchInfo(batchId)
	if do is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res.put('data', do)
	return JSONResponse(res)

@csrf_exempt
def checkout(request):
	if request.method == 'OPTIONS':
		return CrossDomainResponse() 
	if request.method <> 'POST':
		return JSONResponse(ResObject('InvalidRequest'))
	requestData = json.loads(request.body, parse_float=Decimal)
	batchId = requestData.get('batchId', None)
	if batchId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	openId = requestData.get('openId', None)
	res = ResObject('Success')
	do = data.createCheckoutInfo(batchId, openId)
	if do is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res.put('data', do)
	return JSONResponse(res)
	
@csrf_exempt
def unifiedOrder(request):
	if request.method <> 'POST':
		return JSONResponse(ResObject('InvalidRequest'))
	requestData = json.loads(request.body, parse_float=Decimal)
	puchared = requestData.get('puchared', None)
	if puchared is None:
		return JSONResponse(ResObject('InvalidRequest'))
	ipaddress = requestData.get('ipaddress', None)
	if ipaddress is None:
		return JSONResponse(ResObject('InvalidRequest'))
	openid = requestData.get('openid', None)
	if openid is None:
		return JSONResponse(ResObject('InvalidRequest'))
	nickname = requestData.get('nickname', None)
	if nickname is None:
		return JSONResponse(ResObject('InvalidRequest'))
	tel = requestData.get('tel', None)
	if tel is None:
		return JSONResponse(ResObject('InvalidRequest'))
	(customer, iscreated) = data.updateOrCreateCustomer(
		nickname, tel, openid)
	batchId = requestData.get('batch_id', None)
	if batchId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	batch = data.fetchBatch(batchId)
	if batch is None:
		return JSONResponse(ResObject('InvalidRequest'))
	distId = requestData.get('dist_id', None)
	if distId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	totalFee = data.calcTotalFee(puchared)
	time_start = datetime.now()
	time_expire = time_start + timedelta(minutes=30)
	orderId = utils.createOrderId()
	prepayId = wxAuth.createPrepayId(
		orderId=orderId,
		total_fee=totalFee,
		ipaddress=ipaddress,
		time_start=time_start,
		time_expire=time_expire,
		openid=openid,
		title=batch.title,
		detail=batch.detail,
		notify_url='%s/api/payNotify' % config.DOMAIN_URL
	)
	if prepayId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	order = data.createOrder(
		orderId, batchId, customer.id, distId, 0, prepayId, totalFee)
	if order is None:
		return JSONResponse(ResObject('InvalidRequest'))
	data.createCommoditiesToOrder(puchared, order.id)
	res = ResObject('Success')
	res.put('orderId', orderId)
	return JSONResponse(res)

@csrf_exempt
def order(request):
	if request.method <> 'POST':
		return JSONResponse(ResObject('InvalidRequest'))
	requestData = json.loads(request.body, parse_float=Decimal)
	orderId = requestData.get('orderId', None)
	if orderId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	order = data.fetchOrderById(orderId)
	if order is None:
		return JSONResponse(ResObject('InvalidRequest'))
	payRequest = wxAuth.createPayRequestJson(order.prepay_id)
	if payRequest is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res = ResObject('Success')
	do = data.createOrderInfo(orderId)
	if do is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res.put('data', do)
	res.put('payRequest', payRequest)
	return JSONResponse(res)

@csrf_exempt
def orders(request):
	if request.method <> 'POST':
		return JSONResponse(ResObject('InvalidRequest'))
	requestData = json.loads(request.body, parse_float=Decimal)
	openId = requestData.get('openId', None)
	if openId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res = ResObject('Success')
	do = data.createOrdersInfo(openId)
	if do is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res.put('data', do)
	return JSONResponse(res)

@csrf_exempt
def undo(request):
	if request.method <> 'POST':
		return JSONResponse(ResObject('InvalidRequest'))
	requestData = json.loads(request.body, parse_float=Decimal)
	orderId = requestData.get('orderId', None)
	if orderId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	data.deleteOrderById(orderId)
	res = ResObject('Success')
	return JSONResponse(res)

@csrf_exempt
def orderAmount(request):
	if request.method <> 'POST':
		return JSONResponse(ResObject('InvalidRequest'))
	requestData = json.loads(request.body, parse_float=Decimal)
	orderId = requestData.get('orderId', None)
	if orderId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	order = data.fetchOrderById(orderId)
	if order is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res = ResObject('Success')
	orderAmount = data.fetchOrderAmounts(order.batch_id)
	res.put('orderAmount', orderAmount)
	return JSONResponse(res)

@csrf_exempt
def shareInfo(request):
	if request.method <> 'POST':
		return JSONResponse(ResObject('InvalidRequest'))
	requestData = json.loads(request.body, parse_float=Decimal)
	batchId = requestData.get('batchId', None)
	if batchId is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res = ResObject('Success')
	do = data.createShareInfo(batchId)
	if do is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res.put('data', do)
	return JSONResponse(res)

@csrf_exempt
def payNotify(request):
	error = {
		"return_code": "FAIL"
	}
	orderId = wxAuth.payNotify(request.body)
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

