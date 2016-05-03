#!/usr/bin/python
# -*- coding:utf-8 -*-

from django.http import HttpResponse
import json
import logging
from . import utils

import pdb

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

