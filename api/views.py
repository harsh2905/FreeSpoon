from django.shortcuts import render

import qrcode
from decimal import Decimal
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from . import wx, utils, data, config
from .interface import *

wxAuth = wx.Auth()

import pdb

# Create your views here.

def error():
	return HttpResponse('Bad Request')

def redirector(request, relativePath):
	if request.method <> 'GET':
		return error()
	state = request.GET.get('s', None)
	if state is None:
		return error()
	targetUrl = '%s/%s' % (config.API_URL, relativePath)
	redirectUrl = wxAuth.createAuthorizeBaseRedirectUrl(targetUrl, state)
	return HttpReponseRedirect(redirectUrl)

def createQR(request, relativePath):
	if request.method <> 'GET':
		return error()
	state = request.GET.get('s', None)
	if state is None:
		return error()
	qr = qrcode.QRCode(
		version=None
	)
	targetUrl = '%s/%s?s=%s' % (config.API_URL, relativePath, state)
	qr.add_data(targetUrl)
	qr.make(fit=True)
	img = qr.make_image()
	response = HttpResponse(content_type='image/png')
	img.save(response, 'PNG')
	return response

# Business Views

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
	res = ResObject('Success')
	do = data.createCheckoutInfo(batchId)
	if do is None:
		return JSONResponse(ResObject('InvalidRequest'))
	res.put('data', do)
	return JSONResponse(res)
	

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

