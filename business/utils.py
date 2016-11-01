#!/usr/bin/python
# -*- coding:utf-8 -*-

import xml.etree.ElementTree as ET
import uuid, hashlib
from datetime import datetime
import random
import time
import urlparse
import re
from urllib import urlencode
from functools import partial
from django.db import models

def filter_emoji(desstr,restr=''):
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)

def total_microseconds(td):
	return (td.microseconds + (td.seconds + 
		#td.days * 24 * 3600) * 10**6) / 10**3
		td.days * 24 * 3600) * 10**6)

def object2dict(obj):
	t = type(obj)
	if 'class' in str(t):
		d = {}
		for (key, value) in obj.__dict__.items():
			d[key] = object2dict(value)
		return d
	elif t is dict:
		d = {}
		for (key, value) in obj.items():
			d[key] = object2dict(value)
		return d
	elif t is list:
		l = []
		for _ in obj:
			l.append(object2dict(_))
		return l
	else:
		return obj

def dict2object(d, moduleName, className):
	module = __import__(moduleName)
	if module is None:
		raise Exception('Moudle not found')
	class_ = getattr(module, className)
	inst = class_()
	for (key, value) in d.items():
		setattr(inst, key, value)
	return inst

def CDATA(text):
	return '<![CDATA[%s]]>' % text

def createOrderId():
	prefix = datetime.now().strftime('%Y%m%d%H%M%f')
	randomNum = '%08d' % random.randint(1, 99999999)
	return '%s%s' % (prefix, randomNum)

def createDisplayOrderId():
	timestamp = str(now())
	randomNum = '%04d' % random.randint(1, 9999)
	return '%s%s' % (timestamp, randomNum)

def mapToXml(d):
	xml = ET.Element('xml')
	for (name, value) in d.items():
		ele = ET.SubElement(xml, name)
		ele.text = value
	return ET.tostring(xml, encoding='utf-8')

def generateSign(d, key):
	l = d.items()
	l = filter(lambda t: t[1] is not None and len(t[1].strip()) > 0, l)
	l = map(lambda t: '%s=%s' % t, l)
	l = sorted(l)
	stringSignTemp = reduce(lambda _1, _2: '%s&%s' % (_1, _2), l)
	stringSignTemp = '%s&key=%s' % (stringSignTemp, key)
	stringSignTemp = stringSignTemp.encode('utf8')
	md5Sign = hashlib.md5(stringSignTemp).hexdigest()
	md5Sign = md5Sign.upper()
	return md5Sign

def generateSHA1Sign(d):
	l = d.items()
	l = filter(lambda t: t[1] is not None and len(t[1].strip()) > 0, l)
	l = map(lambda t: '%s=%s' % t, l)
	l = sorted(l)
	stringSignTemp = reduce(lambda _1, _2: '%s&%s' % (_1, _2), l)
	stringSignTemp = stringSignTemp.encode('utf8')
	sha1Sign = hashlib.sha1(stringSignTemp).hexdigest()
	return sha1Sign

def xmlToMap(text):
	text = text.encode('utf8')
	xml = ET.fromstring(text)
	d = dict()
	for child in xml:
		d[child.tag] = child.text
	return d

def now():
	return int(time.mktime(datetime.now().timetuple()))

def nonceStr():
	return str(uuid.uuid1()).replace('-', '')

def addQueryParams(url, params):
	url_parts = list(urlparse.urlparse(url))
	query = urlparse.parse_qs(url_parts[4])
	query.update(params)
	url_parts[4] = urlencode(query)
	return urlparse.urlunparse(url_parts)

def populateRepl(m, obj):
	# 我准备买新鲜美味的{obj.category.name}，快和我一起买吧！
	# 新鲜美味的{obj.category.name}，里面包含了{','.join(set(item.__unicode__() for item in obj.products.all()))}。
	# 我买了{goods_set#{str(obj.product.unit_price*obj.quantity/100.0)}元的{obj.product.__unicode__()}}，就差你一个人了！
	# {obj.goods_set.first().product.desc if obj.goods_set.first() is not None else ''}
	return eval(m.group(2), globals(), {'obj': obj})

def populateRepl2(m, obj):
	attr = None
	if isinstance(obj, dict):
		attr = obj.get(m.group(2), None)
	else:
		attr = getattr(obj, m.group(2))
	if hasattr(attr, 'values'):
		items = set(populateString(m.group(3), item) for item in attr.all())
		return ','.join(items)
	return ''

def populateCascadeString(templateString, obj):
	pattern = re.compile(r'(\{(\w+)#(.+)\})')
	result = pattern.sub(partial(populateRepl2, obj=obj), templateString)
	return populateString(result, obj)

def populateString(templateString, obj):
	pattern = re.compile(r'(\{([^{}]+)\})')
	return pattern.sub(partial(populateRepl, obj=obj), templateString)



