from datetime import datetime, timedelta
from decimal import Decimal
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.utils.safestring import SafeString
from django.views.decorators.csrf import csrf_exempt

import json

from django.core.exceptions import ObjectDoesNotExist
import qrcode

from console.models import Batch, Customer, Order, Distributer, CommodityInBatch, CommodityInOrder
from wechat import auth

import pdb

# Create your views here.

def index(request):
	#return HttpResponse(batch_id)
	code = request.GET.get('code', None)
	batch_id = request.GET.get('state', None)
	if code is None or batch_id is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	result = auth.fetch_web_access_token(code)
	access_token = result.get('access_token', None)
	open_id = result.get('openid', None)
	user_info = auth.fetch_user_info(access_token, open_id)
	nickname = user_info.get('nickname', None)
	if nickname is None:
		nickname = ''
	nickname = nickname.encode('utf-8')
	user_info_string = json.dumps(user_info)
	batch = Batch.objects.get(pk=batch_id)
	template = loader.get_template('wechat/index.html')
	commodities = {}
	for commodityinbatch in batch.commodityinbatch_set.all():
		commodity = {}
		commodity['id'] = commodityinbatch.id
		commodity['title'] = commodityinbatch.commodity.title
		commodity['unit_price'] = int(commodityinbatch.unit_price * 100)
		commodity['quota'] = commodityinbatch.quota
		commodities[str(commodityinbatch.id)] = commodity
	commoditiesJson = json.dumps(commodities)
	addresses = {}
	for distributer in batch.distributers.all():
		address = {}
		address['id'] = distributer.id
		address['dist'] = distributer.name
		address['address'] = distributer.location
		addresses[str(distributer.id)] = address
	addressesJson = json.dumps(addresses)
	wx_config_data = auth.gen_wx_config_data(request.get_raw_uri())
	context = RequestContext(request, {
		'batch': batch,
		'commoditiesJson': SafeString(commoditiesJson),
		'addressesJson': SafeString(addressesJson),
		'wx_config_data': SafeString(wx_config_data),
		'user_info': user_info,
		'nickname': nickname,
		'user_info_string': SafeString(user_info_string)
	})
	return HttpResponse(template.render(context))

@csrf_exempt
def unifiedorder(request):
	if not request.is_ajax() or request.method <> 'POST':
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	requestData = json.loads(request.body, parse_float=Decimal)
	wx_nickname = requestData.get('wx_nickname', None)
	if wx_nickname is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	wx_openid = requestData.get('wx_openid', None)
	if wx_openid is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	tel = requestData.get('tel', None)
	if tel is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	(customer, iscreated) = Customer.objects.update_or_create(
		id_wechat=wx_openid,
		defaults={
			'nick_name': wx_nickname,
			'tel': tel
		}
	)
	batch_id = requestData.get('batch_id', None)
	if batch_id is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	batch = Batch.objects.get(pk=batch_id)
	if batch is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	dist_id = requestData.get('dist_id', None)
	if dist_id is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	(order, iscreated) = Order.objects.update_or_create(
		batch_id=batch_id,
		customer_id=customer.id,
		defaults={
			'create_time': datetime.now(),
			'status': 0,
			'distributer_id': dist_id
		}
	)
	if not iscreated:
		return
	commodities = requestData.get('commodities', None)
	if commodities is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	ipaddress = requestData.get('ipaddress', None)
	if ipaddress is None:
		template = loader.get_template('wechat/error.html')
		context = RequestContext(request)
		return HttpResponse(template.render(context))
	total_fee = 0
	for commodity in commodities:
		id_ = commodity.get('id', None)
		quantity = commodity.get('quantity', 0)
		if id_ is None:
			continue
		commodity_in_order = CommodityInOrder.objects.create(
			quantity=quantity,
			commodity_id=id_,
			order_id=order.id)
		commodity_in_batch = CommodityInBatch.objects.get(pk=id_)
		if commodity_in_batch is not None:
			total_fee += quantity * commodity_in_batch.unit_price
	time_start = datetime.now()
	time_expire = time_start + timedelta(minutes=30)
	prepay_id = auth.fetch_prepay_id(
		order_id=order.id,
		total_fee=total_fee,
		ipaddress=ipaddress,
		time_start=time_start,
		time_expire=time_expire,
		openid=customer.id_wechat,
		title=batch.title,
		detail=batch.desc
	)
	# TODO Save Prepay Id
	request_json_data = auth.gen_pay_request_data(prepay_id)
	return HttpResponse(request_json_data, content_type='application/json')

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

def qr_index2(request, batch_id):
	url = auth.gen_index_url(batch_id)
	return HttpResponse(url)

def qr_index(request, batch_id):
	url = auth.gen_index_url(batch_id)
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
		




