#!/usr/bin/python
# -*- coding:utf-8 -*-

import xml.etree.ElementTree as ET
import uuid, hashlib
from datetime import datetime
import time

import pdb

def CDATA(text):
	return '<![CDATA[%s]]>' % text

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

if __name__ == '__main__':
	d = {
		'appid': 'wxd930ea5d5a258f4f',
		'mch_id': '10000100',
		'device_info': '1000',
		'body': 'test',
		'nonce_str': 'ibuaiVcKdpRxkhJA'
	}
	key = '192006250b4c09247ec02edce69f6a2d'
	sign = generateSign(d, key)
