import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from datetime import datetime, timedelta
import requests
import hashlib
import json
import logging

from allauth.socialaccount.models import SocialApp

from requests.exceptions import RequestException

from . import utils
from . import config

logger = logging.getLogger('django')

__all__ = ['WxApp']

class WxApp(object):
	appid = None
	appsecret = None
	access_token = None
	access_token_expires_time = datetime.min
	jsapi_ticket = None
	jsapi_ticket_expires_time = datetime.min
	trade_type = None # JSAPI or APP

	_cache_ = {}

	@classmethod	
	def get_current(cls, request):
		social_app = SocialApp.objects.get_current('weixin', request)
		social_app_id = social_app.id
		app = cls._cache_.get(social_app_id, None)
		if app:
			return app
		app = cls(social_app.client_id, social_app.secret, 
			social_app.mch_id, social_app.mch_appkey, social_app.trade_type)
		cls._cache_[social_app_id] = app
		return app
		

	def __init__(self, appid, appsecret, mch_id, mch_appkey, trade_type):
		self.appid = appid
		self.appsecret = appsecret
		self.mch_id = mch_id
		self.mch_appkey = mch_appkey
		self.trade_type = trade_type

	def createAuthorizeRedirectUrl(self, redirectUrl, state):
		return config.AUTHORIZE_REDIRECT_URL % (self.appid, redirectUrl, state)
	
	def createAuthorizeBaseRedirectUrl(self, redirectUrl, state):
		return config.AUTHORIZE_BASE_REDIRECT_URL % (self.appid, redirectUrl, state)
	
	def fetchAccessToken(self):
		if datetime.now() < self.access_token_expires_time:
			return self.access_token
		result = None
		try:
			r = requests.get(config.FETCH_ACCESS_TOKEN_URL % (self.appid, self.appsecret))
			result = r.json()
		except RequestException, e:
			logger.error('RequestException: %s' % e)
			return None
		errcode = result.get('errcode', None)
		if errcode is not None:
			errmsg = result.get('errmsg', None)
			logger.error('Fetch Access Token Error: %s(%s)' % (errmsg, errcode))
			return None
		access_token = result.get('access_token', None)
		expires_in = result.get('expires_in', None)
		if access_token is None or expires_in is None:
			logger.error('Fetch Access Token Error: invalid arguments')
			return None
		self.access_token = access_token
		self.access_token_expires_time = datetime.now() + timedelta(seconds=expires_in * 0.8)
		return access_token
	
	def fetchJsApiTicket(self):
		if datetime.now() < self.jsapi_ticket_expires_time:
			return self.jsapi_ticket
		access_token = self.fetchAccessToken()
		if access_token is None:
			return None
		try:
			r = requests.get(config.FETCH_JSAPI_TICKET_URL % access_token)
			result = r.json()
		except RequestException, e:
			logger.error('RequestException: %s' % e)
			return None
		errcode = result.get('errcode', None)
		if errcode is None or errcode <> 0:
			errmsg = result.get('errmsg', None)
			logger.error('Fetch JSAPI Ticket Error: %s(%s)' % (errmsg, errcode))
			return None
		ticket = result.get('ticket', None)
		expires_in = result.get('expires_in', None)
		if ticket is None or expires_in is None:
			logger.error('Fetch JSAPI Ticket Error: invalid arguments')
			return None
		self.jsapi_ticket = ticket
		self.jsapi_ticket_expires_time = datetime.now() + timedelta(seconds=expires_in * 0.8)
		return ticket

	def createWXConfig(self, url, jsApiList):
		index = url.find('#')
		if index <> -1:
			url = url[:index + 1]
		nonceStr = utils.nonceStr()
		jsapi_ticket = self.fetchJsApiTicket()
		timestamp = str(utils.now())
		d = {
			'noncestr': nonceStr,
			'jsapi_ticket': jsapi_ticket,
			'timestamp': timestamp,
			'url': url
		}
		signature = utils.generateSHA1Sign(d)
		dd = {
			'debug': False,
			'appId': self.appid,
			'timestamp': timestamp,
			'nonceStr': nonceStr,
			'signature': signature,
			'jsApiList': jsApiList
		}
		return dd
	
	def createPrepayId(
		self,
		order_id,
		total_fee,
		ip_address,
		time_start,
		time_expire,
		openid,
		title,
		detail,
		notify_url,
		device_info='WEB',
		attach=None):
		d = {
			'appid': self.appid,
			'mch_id': self.mch_id,
			'device_info': device_info,
			'nonce_str': utils.nonceStr(),
			'body': title,
			'detail': detail,
			'attach': attach,
			'out_trade_no': order_id,
			'fee_type': 'CNY',
			'total_fee': str(total_fee),
			'spbill_create_ip': ip_address,
			'time_start': time_start.strftime('%Y%m%d%H%M%S'),
			'time_expire': time_expire.strftime('%Y%m%d%H%M%S'),
			'notify_url': notify_url,
			'trade_type': self.trade_type,
			'openid': openid if self.trade_type == 'JSAPI' else None
		}
		d['sign'] = utils.generateSign(d, self.mch_appkey)
		xml = utils.mapToXml(d)
		try:
			r = requests.post(config.UNIFIEDORDER_URL, xml)
			responseXml = r.text
		except RequestException, e:
			logger.error('RequestException: %s' % e)
			return None
		result = utils.xmlToMap(responseXml)
		return_code = result.get('return_code', None)
		if return_code <> 'SUCCESS':
			return_msg = result.get('return_msg', None)
			logger.error('Fetch Prepay Id Error: %s' % return_msg)
			return None
		err_code = result.get('err_code', None)
		if err_code is not None:
			err_code_des = result.get('err_code_des', None)
			logger.error('Fetch Prepay Id Error: %s(%s)' % (err_code_des, err_code))
			return None
		prepay_id = result.get('prepay_id', None)
		return prepay_id

	def payNotify(self, xmlData):
		requestData = utils.xmlToMap(xmlData)
		rawData = {}
		rawSign = None
		for (name, value) in requestData.items():
			if name <> 'sign':
				rawData[name] = value
			else:
				rawSign = value
		sign = utils.generateSign(rawData, self.mch_appkey)
		if rawSign is None or rawSign <> sign:
			return None
		return_code = requestData.get('return_code', None)
		if return_code <> 'SUCCESS':
			return_msg = requestData.get('return_msg', None)
			logger.error('Pay Notify Error: %s' % return_msg)
			return None
		return requestData.get('out_trade_no', None)
	
	def createPayRequestJson(self, prepay_id):
		if self.trade_type == 'JSAPI':
			d = {
				'appId': self.appid,
				'timeStamp': str(utils.now()),
				'nonceStr': utils.nonceStr(),
				'package': 'prepay_id=%s' % prepay_id,
				'signType': 'MD5'
			}
			d['paySign'] = utils.generateSign(d, self.mch_appkey)
			return d
		else:
			d = {
				'appid': self.appid,
				'partnerid': self.mch_id,
				'prepayid': prepay_id,
				'package': 'Sign=WXPay',
				'noncestr': utils.nonceStr(),
				'timestamp': str(utils.now())
			}
			d['sign'] = utils.generateSign(d, self.mch_appkey)
			return d















