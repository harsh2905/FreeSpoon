#!/usr/bin/python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from datetime import datetime
import requests
import hashlib
import json

from wechat import utils

import pdb

APPID = os.getenv('APPID')
APPSECRET = os.getenv('APPSECRET')
MCHID = os.getenv('MCHID')

access_token_fetch_url = \
	('https://api.weixin.qq.com/cgi-bin/token'
	'?grant_type=client_credential&appid=%s&secret=%s')
authorize_url = \
	('https://open.weixin.qq.com/connect/oauth2/authorize'
	'?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=%s#wechat_redirect')
web_access_token_fetch_url = \
	('https://api.weixin.qq.com/sns/oauth2/access_token'
	'?appid=%s&secret=%s&code=%s&grant_type=authorization_code')
user_info_fetch_url = \
	'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN'
jsapi_ticket_fetch_url = \
	'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi'
unifiedorder_url = \
	'https://api.mch.weixin.qq.com/pay/unifiedorder'

index_url = \
	'http://carlinkall.com/wechat'
order_confirm_url = \
	'http://carlinkall.com/wechat/confirm'
wx_unifiedorder_notify_url = \
	'http://carlinkall.com/wechat/unifiedorder/pay'
app_key = 'b70fa237cfd3478bb520af328afb40c8'

access_token_expires_time = datetime.min
access_token = None

def fetch_prepay_id(
		order_id, 
		total_fee, 
		ipaddress, 
		time_start, 
		time_expire, 
		openid,
		title, 
		detail, 
		attach=None):
	d = {
		'appid': APPID,
		'mch_id': MCHID,
		'device_info': 'WEB',
		'nonce_str': utils.nonceStr(),
		'body': title,
		'detail': detail,
		'attach': attach,
		'out_trade_no': '%09d' % order_id,
		'fee_type': 'CNY',
		'total_fee': str(int(total_fee * 100)),
		'spbill_create_ip': ipaddress,
		'time_start': time_start.strftime('%Y%m%d%H%M%S'),
		'time_expire': time_expire.strftime('%Y%m%d%H%M%S'),
		'notify_url': wx_unifiedorder_notify_url,
		'trade_type': 'JSAPI',
		'openid': openid
	}
	d['sign'] = utils.generateSign(d, app_key)
	xml = utils.mapToXml(d)
	r = requests.post(unifiedorder_url, xml)
	responseXml = r.text
	responseDict = utils.xmlToMap(responseXml)
	return responseDict.get('prepay_id', None)

def fetch_jsapi_ticket():
	access_token = fetch_access_token()
	try:
		r = requests.get(jsapi_ticket_fetch_url % access_token)
		result = r.json()
		ticket = result.get('ticket', None)
		return ticket
	except Exception, e:
		pass

def gen_wx_config_data(url):
	index = url.find('#')
	if index <> -1:
		url = url[:index + 1]
	nonceStr = utils.nonceStr()
	jsapi_ticket = fetch_jsapi_ticket()
	timestamp = str(utils.now())
	d = {
		'noncestr': nonceStr,
		'jsapi_ticket': jsapi_ticket,
		'timestamp': timestamp,
		'url': url
	}
	signature = utils.generateSHA1Sign(d)
	dd = {
		'debug': True,
		'appId': APPID,
		'timestamp': timestamp,
		'nonceStr': nonceStr,
		'signature': signature,
		'jsApiList': ['chooseWXPay']
	}
	return json.dumps(dd)

def gen_pay_request_data(prepay_id):
	d = {
		'appId': APPID,
		'timeStamp': str(utils.now()),
		'nonceStr': utils.nonceStr(),
		'package': 'prepay_id=%s' % prepay_id,
		'signType': 'MD5'
	}
	d['paySign'] = utils.generateSign(d, app_key)
	return json.dumps(d)
	
	
def fetch_access_token():
	global access_token_expires_time
	global access_token
	if access_token is None or datetime.now() > access_token_expires_time:
		try:
			r = requests.get(access_token_fetch_url % (APPID, APPSECRET))
			result = r.json()
			access_token = result.get('access_token', None)
			expires_in = result.get('expires_in', 0)
			if expires_in is not None:
				expires_in = expires_in - 100
				access_token_expires_time = \
					datetime.now() + timedelta(seconds=expires_in)
		except Exception, e:
			pass
		return access_token

def gen_authorize_redirect_url(redirect_url, state):
	return authorize_url % (APPID, redirect_url, state)

def gen_index_url(batch_id):
	# TODO Wechat confirm redirect
	#return index_url + '/' + str(batch_id)
	return gen_authorize_redirect_url(index_url, batch_id)

def gen_order_confirm_url(batch_id):
	return gen_authorize_redirect_url(order_confirm_url, batch_id)

def fetch_web_access_token(code):
	try:
		r = requests.get(web_access_token_fetch_url % (APPID, APPSECRET, code))
		result = r.json()
		return result
		#access_token = result.get('access_token', None)
		#open_id = result.get('openid', None)
	except Exception, e:
		pass
	return None
		
def fetch_user_info(access_token, open_id):
	try:
		r = requests.get(user_info_fetch_url % (access_token, open_id))
		result = json.loads(r.content)
		return result
	except Exception, e:
		pass
	return None

if __name__ == '__main__':
	print gen_authorize_redirect_url('http://192.168.102.40', '0')
