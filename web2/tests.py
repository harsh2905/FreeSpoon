from django.test import TestCase
import auth

import requests, urllib2
import urlparse
import pdb

# Create your tests here.

class AuthTestCase(TestCase):
	def setUp(self):
		pass

	def test_fetch_wechat_access_token(self):
		access_token = auth.fetch_access_token()
		self.assertNotEqual(access_token, None)
		self.assertTrue(len(access_token) > 0)

	#def test_fetch_wechat_page_code(self):
	#	pdb.set_trace()
	#	redirect_url = 'http://www.baidu.com'
	#	redirect_url = redirect_url.encode('utf-8')
	#	redirect_url = urllib2.quote(redirect_url)
	#	state = '0'
	#	url = auth.gen_authorize_redirect_url(redirect_url, state)
	#	r = requests.get(url)
	#	redirect_url_ = r.url
	#	parseResult = urlparse.urlparse(redirect_url_)
	#	params = urlparse.parse_qs(parseResult.query, True)
	#	page_code = params.get('code', None)
	#	self.assertNotEqual(page_code, None)
	#	self.assertTrue(len(page_code) > 0)
