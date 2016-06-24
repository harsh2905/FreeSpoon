#!/usr/bin/python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from datetime import datetime, timedelta
import requests
import hashlib
import json
import logging

from requests.exceptions import RequestException

from . import utils


APPID = os.getenv('APPID')
APPSECRET = os.getenv('APPSECRET')
APPKEY = os.getenv('APPKEY')

AUTHORIZE_BASE_REDIRECT_URL = \
	('https://open.weixin.qq.com/connect/oauth2/authorize'
	'?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base&state=%s#wechat_redirect')
AUTHORIZE_REDIRECT_URL = \
	('https://open.weixin.qq.com/connect/oauth2/authorize'
	'?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=%s#wechat_redirect')
FETCH_WEB_ACCESS_TOKEN_URL = \
	('https://api.weixin.qq.com/sns/oauth2/access_token'
	'?appid=%s&secret=%s&code=%s&grant_type=authorization_code')
REFRESH_WEB_ACCESS_TOKEN_URL = \
	('https://api.weixin.qq.com/sns/oauth2/refresh_token'
	'?appid=%s&grant_type=refresh_token&refresh_token=%s')
FETCH_USER_INFO_URL = \
	'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN'
FETCH_ACCESS_TOKEN_URL = \
	('https://api.weixin.qq.com/cgi-bin/token'
	'?grant_type=client_credential&appid=%s&secret=%s')
FETCH_JSAPI_TICKET_URL = \
	'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi'
UNIFIEDORDER_URL = \
	'https://api.mch.weixin.qq.com/pay/unifiedorder'

logger = logging.getLogger('django')

class AccessToken():
	def __init__(self, access_token, expires_in, refresh_token, openid):
		self.access_token = access_token
		self.expires_in = expires_in
		self.expires_time = datetime.now() + timedelta(seconds=expires_in * 0.8)
		self.refresh_token = refresh_token
		self.openid = openid

	def get(self):
		if datetime.now() < self.expires_time:
			return self.access_token
		if not self.refreshToken():
			return None
		return self.access_token
	
	def getOpenId(self):
		return self.openid
	
	def refreshToken(self):
		try:
			r = requests.get(REFRESH_WEB_ACCESS_TOKEN_URL % (APPID, self.refresh_token))
			result = r.json()
		except RequestException, e:
			logger.error('RequestException: %s' % e)
			return False
		errcode = result.get('errcode', None)
		if errcode is not None:
			errmsg = result.get('errmsg', None)
			logger.error('Refresh Token Error: %s(%s)' % (errmsg, errcode))
			return False
		access_token = result.get('access_token', None)
		if access_token is None:
			logger.error('Refresh Token Error: access_token not found')
			return False
		self.access_token = access_token
		expires_in = result.get('expires_in', None)
		if expires_in is None:
			logger.error('Refresh Token Error: expires_in not found')
			return False
		self.expires_in = expires_in
		self.expires_time = datetime.now() + timedelta(seconds=expires_in * 0.8)
		refresh_token = result.get('refresh_token', None)
		if refresh_token is None:
			logger.error('Refresh Token Error: refresh_token not found')
			return False
		self.refresh_token = refresh_token
		openid = result.get('openid', None)
		if openid is None:
			logger.error('Refresh Token Error: openid not found')
			return False
		self.openid = openid
		return True

class UserInfo():
	def __init__(self, data):
		self.data = data
	def json(self):
		return json.dumps(self.data)
	def getOpenId(self):
		return self.data.get('openid', None)
	def getNickName(self):
		return self.data.get('nickname', None)
	def getSex(self):
		return self.data.get('sex', None)
	def getHeadImgUrl(self):
		return self.data.get('headimgurl', None)

class PrepayInfo():
	def __init__(self, orderId, prepayId):
		self.orderId = orderId
		self.prepayId = prepayId
		expires_in = 2 * 60
		self.expiresTime = datetime.now() + timedelta(minutes=expires_in * 0.8)
	
	def getPrepayId(self):
		if datetime.now() < self.expiresTime:
			return self.prepayId
		return None

class Auth():
	def __init__(self):
		# User Id: AccessToken
		Auth.AccessTokens = {}
		# Order Id: PrepayInfo
		Auth.PrepayIds = {}
		self.accessToken = None
		self.accessTokenExpiresTime = datetime.min
		self.jsApiTicket = None
		self.jsApiTicketExpiresTime = datetime.min
	
	def createAuthorizeRedirectUrl(self, redirectUrl, state):
		return AUTHORIZE_REDIRECT_URL % (APPID, redirectUrl, state)

	def createAuthorizeBaseRedirectUrl(self, redirectUrl, state):
		return AUTHORIZE_BASE_REDIRECT_URL % (APPID, redirectUrl, state)
	
	def fetchAccessToken(self):
		if datetime.now() < self.accessTokenExpiresTime:
			return self.accessToken
		result = None
		try:
			r = requests.get(FETCH_ACCESS_TOKEN_URL % (APPID, APPSECRET))
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
		self.accessToken = access_token
		self.accessTokenExpiresTime = datetime.now() + timedelta(seconds=expires_in * 0.8)
		return access_token
	
	def fetchJsApiTicket(self):
		if datetime.now() < self.jsApiTicketExpiresTime:
			return self.jsApiTicket
		access_token = self.fetchAccessToken()
		if access_token is None:
			return None
		try:
			r = requests.get(FETCH_JSAPI_TICKET_URL % access_token)
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
		self.jsApiTicket = ticket
		self.jsApiTicketExpiresTime = datetime.now() + timedelta(seconds=expires_in * 0.8)
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
			'appId': APPID,
			'timestamp': timestamp,
			'nonceStr': nonceStr,
			'signature': signature,
			'jsApiList': jsApiList
		}
		return dd
	
	def fetchWebAccessToken(self, code):
		try:
			r = requests.get(FETCH_WEB_ACCESS_TOKEN_URL % (APPID, APPSECRET, code))
			result = r.json()
		except RequestException, e:
			logger.error('RequestException: %s' % e)
			return None
		errcode = result.get('errcode', None)
		if errcode is not None:
			errmsg = result.get('errmsg', None)
			logger.error('Fetch Web Token Error: %s(%s)' % (errmsg, errcode))
			return None
		access_token = result.get('access_token', None)
		if access_token is None:
			logger.error('Fetch Web Token Error: access_token not found')
			return None
		expires_in = result.get('expires_in', None)
		if expires_in is None:
			logger.error('Fetch Web Token Error: expires_in not found')
			return None
		refresh_token = result.get('refresh_token', None)
		if refresh_token is None:
			logger.error('Fetch Web Token Error: refresh_token not found')
			return None
		openid = result.get('openid', None)
		if openid is None:
			logger.error('Fetch Web Token Error: openid not found')
			return None
		return AccessToken(access_token, expires_in, refresh_token, openid)
	
	def fetchUserInfo(self, code):
		accessToken = self.fetchWebAccessToken(code)
		if accessToken is None:
			return None
		access_token = accessToken.get()
		if access_token is None:
			return None
		openid = accessToken.getOpenId()
		if openid is None:
			return None
		try:
			r = requests.get(FETCH_USER_INFO_URL % (access_token, openid))
			result = json.loads(r.content)
		except RequestException, e:
			logger.error('RequestException: %s' % e)
			return None
		errcode = result.get('errcode', None)
		if errcode is not None:
			errmsg = result.get('errmsg', None)
			logger.error('Fetch User Info Error: %s(%s)' % (errmsg, errcode))
			return None
		return UserInfo(result)

	def fetchOpenId(self, code):
		accessToken = self.fetchWebAccessToken(code)
		if accessToken is None:
			return None
		return accessToken.getOpenId()
	
	def createPrepayId(
		self,
		orderId,
		total_fee,
		ipaddress,
		time_start,
		time_expire,
		openid,
		title,
		detail,
		notify_url,
		attach=None):
		d = {
			'appid': APPID,
			'mch_id': MCHID,
			'device_info': 'WEB',
			'nonce_str': utils.nonceStr(),
			'body': title,
			'detail': detail,
			'attach': attach,
			'out_trade_no': orderId,
			'fee_type': 'CNY',
			'total_fee': str(total_fee),
			'spbill_create_ip': ipaddress,
			'time_start': time_start.strftime('%Y%m%d%H%M%S'),
			'time_expire': time_expire.strftime('%Y%m%d%H%M%S'),
			'notify_url': notify_url,
			'trade_type': 'JSAPI',
			'openid': openid
		}
		d['sign'] = utils.generateSign(d, APPKEY)
		xml = utils.mapToXml(d)
		try:
			r = requests.post(UNIFIEDORDER_URL, xml)
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
		prepayId = result.get('prepay_id', None)
		if prepayId is not None:
			Auth.PrepayIds[orderId] = PrepayInfo(orderId, prepayId)
		return prepayId
	
	def payNotify(self, xmlData):
		requestData = utils.xmlToMap(xmlData)
		rawData = {}
		rawSign = None
		for (name, value) in requestData.items():
			if name <> 'sign':
				rawData[name] = value
			else:
				rawSign = value
		sign = utils.generateSign(rawData, APPKEY)
		if rawSign is None or rawSign <> sign:
			return None
		return_code = requestData.get('return_code', None)
		if return_code <> 'SUCCESS':
			return_msg = requestData.get('return_msg', None)
			logger.error('Pay Notify Error: %s' % return_msg)
			return None
		return requestData.get('out_trade_no', None)
	
	def fetchPrepayId(self, orderId):
		prepayInfo = Auth.PrepayIds.get(orderId, None)
		if prepayInfo is None:
			return None
		return prepayInfo.getPrepayId()
	
	def createPayRequestJson(self, prepayId):
		d = {
			'appId': APPID,
			'timeStamp': str(utils.now()),
			'nonceStr': utils.nonceStr(),
			'package': 'prepay_id=%s' % prepayId,
			'signType': 'MD5'
		}
		d['paySign'] = utils.generateSign(d, APPKEY)
		return d


