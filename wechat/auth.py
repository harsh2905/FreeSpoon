#!/usr/bin/python

import os
from datetime import datetime
import requests

import pdb

APPID = os.getenv('APPID')
APPSECRET = os.getenv('APPSECRET')

access_token_fetch_url = \
	'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
authorize_url = \
	'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base&state=%s#wechat_redirect'
access_token_expires_time = datetime.min
access_token = None

def fetch_access_token():
	global access_token_expires_time
	global access_token
	#pdb.set_trace()
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
