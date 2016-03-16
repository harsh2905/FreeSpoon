from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from django.core.exceptions import ObjectDoesNotExist

from console.models import Batch, Customer, Order
from wechat import auth

import pdb

# Create your views here.

def index(request, batch_id):
	#return HttpResponse(batch_id)
	batch = Batch.objects.get(pk=batch_id)
	template = loader.get_template('wechat/index.html')
	context = RequestContext(request, {
		'batch': batch,
	})
	return HttpResponse(template.render(context))

def pay_callback(request):
	template = loader.get_template('wechat/paycb.html')
	context = RequestContext(request)
	return HttpResponse(template.render(context))

def confirm(request):
	pdb.set_trace()
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
		order = Order.objects.filter(batch_id=batch_id, customer_id=customer.id)
		template = loader.get_template('wechat/confirm.html')
		context = RequestContext(request, {
			'nickname': nickname,
			'sex': sex,
			'headimgurl': headimgurl,
			'order': order
		})
	except ObjectDoesNotExist:
		print('Customer Not Found')

def confirm1(request):
	template = loader.get_template('wechat/confirm.html')
	context = RequestContext(request, {
	})
	return HttpResponse(template.render(context))
	
