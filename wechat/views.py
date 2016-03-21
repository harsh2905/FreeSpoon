from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.utils.safestring import SafeString

import json

from django.core.exceptions import ObjectDoesNotExist
import qrcode

from console.models import Batch, Customer, Order, Distributer
from wechat import auth

import pdb

# Create your views here.

def index(request, batch_id):
	#return HttpResponse(batch_id)
	batch = Batch.objects.get(pk=batch_id)
	template = loader.get_template('wechat/index.html')
	commodities = {}
	for commodityinbatch in batch.commodityinbatch_set.all():
		commodity = {}
		commodity['id'] = commodityinbatch.id
		commodity['title'] = commodityinbatch.commodity.title
		commodity['unit_price'] = long(commodityinbatch.unit_price)
		commodity['quota'] = commodityinbatch.quota
		commodities[str(commodityinbatch.id)] = commodity
	commoditiesJson = json.dumps(commodities)
	context = RequestContext(request, {
		'batch': batch,
		'commoditiesJson': SafeString(commoditiesJson)
	})
	return HttpResponse(template.render(context))

def pay_callback(request):
	template = loader.get_template('wechat/paycb.html')
	context = RequestContext(request)
	return HttpResponse(template.render(context))

def confirm(request):
	code = request.GET.get('code', None)
	batch_id = request.GET.get('state', None)
	if code is None or batch_id is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	result = auth.fetch_web_access_token(code)
	access_token = result.get('access_token', None)
	open_id = result.get('openid', None)
	result = auth.fetch_user_info(access_token, open_id)
	nickname = result.get('nickname', None)
	sex = result.get('sex', 0)
	headimgurl = result.get('headimgurl', None)
	try:
		customer = Customer.objects.get(id_wechat=open_id)
		order = Order.objects.filter(batch_id=batch_id, customer_id=customer.id).first()
		template = loader.get_template('wechat/confirm.html')
		context = RequestContext(request, {
			'nickname': nickname,
			'sex': sex,
			'headimgurl': headimgurl,
			'order': order,
			'datetime': datetime.now()
		})
		return HttpResponse(template.render(context))
	except ObjectDoesNotExist:
		print('Customer Not Found')

def complete(request):
	if request.method == 'GET':
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	order_id = request.POST.get('order_id', None)
	if order_id is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	try:
		order = Order.objects.get(pk=order_id)
		order.status = 1
		order.save()
		template = loader.get_template('wechat/complete.html')
		context = RequestContext(request, {
			'order': order,
			'datetime': datetime.now()
		})
		return HttpResponse(template.render(context))
	except ObjectDoesNotExist:
		print('Customer Not Found')

def qr_confirm(request, batch_id):
	url = auth.gen_order_confirm_url(batch_id)
	qr = qrcode.QRCode(
		version=None
	)
	qr.add_data(url)
	qr.make(fit=True)
	img = qr.make_image()
	response = HttpResponse(content_type='image/png')
	img.save(response, 'PNG')
	return response

def order_report(request, batch_id, dist_id):
	try:
		batch = Batch.objects.get(pk=batch_id)
		dist = Distributer.objects.get(pk=dist_id)
		orders = Order.objects.filter(batch_id=batch.id, distributer_id=dist.id).all()
		template = loader.get_template('wechat/order_report.html')
		context = RequestContext(request, {
			'batch': batch,
			'distributer': dist,
			'orders': orders,
			'datetime': datetime.now()
		})
		return HttpResponse(template.render(context))
	except ObjectDoesNotExist:
		print('Customer Not Found')
		




