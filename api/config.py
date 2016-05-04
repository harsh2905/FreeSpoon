#!/usr/bin/python

import os

DOMAIN_NAME = os.getenv('DOMAINNAME')
DOMAIN_URL = 'http://%s' % DOMAIN_NAME
API_URL = 'http://%s/api' % DOMAIN_NAME

