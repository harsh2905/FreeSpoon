import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from datetime import datetime, timedelta
import requests
import hashlib
import json
import random
import logging
import base64

from requests.exceptions import RequestException

from . import utils
from . import config

logger = logging.getLogger('django')

__all__ = ['SmsApp']

class SmsApp(object):
	rands = {}

	@classmethod
	def check(cls, to, code):
		payload = cls.rands.get(to, None)
		if payload:
			time = payload.get('time', None)
			code_ = payload.get('code', None)
			if time and time + timedelta(minutes=5) > datetime.now()\
				and code_ and code_ == code:
				return True
		return False

	@classmethod
	def send(cls, to):
		now = datetime.now()
		timestamp = now.strftime('%Y%m%d%H%M%f')
		stuff = '%s%s%s' % (
			config.SMS_ACCOUNT_SID,
			config.SMS_AUTH_TOKEN,
			timestamp)
		sigParameter = hashlib.md5(stuff).hexdigest()
		sigParameter = sigParameter.upper()
		stuff = '%s:%s' % (config.SMS_ACCOUNT_SID, timestamp)
		authorization = base64.b64encode(stuff)
		payload = {}
		payload['to'] = to
		payload['appId'] = config.SMS_APP_ID
		payload['templateId'] = config.SMS_TEMPLATE_ID
		rand = '%06d' % random.randint(1, 999999)
		payload['datas'] = [
			rand,
			'5'
		]
		url = config.SMS_REST_URL % sigParameter
		data = json.dumps(payload)
		try:
			headers = {
				'Accept': 'application/json',
				'Content-Type': 'application/json;charset=utf-8',
				'Authorization': authorization,
			}
			r = requests.post(url, data, headers=headers)
			resp = r.json()
			if 'statusCode' not in resp or resp.get('statusCode', '') <> '000000':
				logger.error('RequestException: statusCode not equals 000000')
			else:
				cls.rands[to] = {
					'time': now,
					'code': rand
				}
				return True
		except RequestException, e:
			logger.error('RequestException: %s' % e)
		return False


if __name__ == '__main__':
	SmsApp.send('18600113725')