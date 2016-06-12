#!/usr/bin/python

import os

DOMAIN_NAME = os.getenv('DOMAINNAME')
DOMAIN_URL = 'http://%s' % DOMAIN_NAME

APP_APPID = os.getenv('APPAPPID')
MP_APPID = os.getenv('MPAPPID')
APP_APPSECRET = os.getenv('APPAPPSECRET')
MP_APPSECRET = os.getenv('MPAPPSECRET')

MCHID = os.getenv('MCHID')
APPKEY = os.getenv('APPKEY')

AUTHORIZE_BASE_REDIRECT_URL = \
        ('https://open.weixin.qq.com/connect/oauth2/authorize'
        '?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base&state=%s#wechat_redirect')
AUTHORIZE_REDIRECT_URL = \
        ('https://open.weixin.qq.com/connect/oauth2/authorize'
        '?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=%s#wechat_redirect')
FETCH_ACCESS_TOKEN_URL = \
        ('https://api.weixin.qq.com/cgi-bin/token'
        '?grant_type=client_credential&appid=%s&secret=%s')
FETCH_JSAPI_TICKET_URL = \
        'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi'
