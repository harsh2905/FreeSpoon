#!/usr/bin/python
# -*- coding:utf-8 -*-

import xml.etree.ElementTree as ET
import uuid, hashlib
from datetime import datetime
import random
import time

import pdb

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


