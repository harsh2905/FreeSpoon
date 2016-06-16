#!/usr/bin/python
# -*- coding:utf-8 -*-

from django.http import HttpResponse
import json
import logging
from . import utils


logger = logging.getLogger('django')

class ResObject(object):
	def __init__(self, errcode, **kwargs):
		self.errcode = errcode
		self.res = {}
		for (key, value) in kwargs:
			self.res[key] = value
	
	def put(self, key, value):
		self.res[key] = value

	def puts(self, d):
		if type(d) <> 'dict':
			return
		for (key, value) in d.items():
			self.res[key] = value

class JSONResponse(HttpResponse):
	def __init__(self, data, **kwargs):
		data = utils.object2dict(data)
		content = json.dumps(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)
		super(JSONResponse, self).__setitem__('Access-Control-Allow-Origin', '*')
		super(JSONResponse, self).__setitem__('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
		super(JSONResponse, self).__setitem__('Access-Control-Allow-Headers', 'Content-Type')
		super(JSONResponse, self).__setitem__('Access-Control-Max-Age', '180')

class CrossDomainResponse(HttpResponse):
	def __init__(self, **kwargs):
		super(CrossDomainResponse, self).__init__(**kwargs)
		super(CrossDomainResponse, self).__setitem__('Access-Control-Allow-Origin', '*')
		super(CrossDomainResponse, self).__setitem__(
			'Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
		super(CrossDomainResponse, self).__setitem__('Access-Control-Allow-Headers', 'Content-Type')
		super(CrossDomainResponse, self).__setitem__('Access-Control-Max-Age', '180')

