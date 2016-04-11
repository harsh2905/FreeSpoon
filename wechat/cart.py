#!/usr/bin/python

class Carts():

	def __init__(self):
		self.__Cache__ = {}

	def add(self, data):
		openid = data.get('openid', None)
		batchId = data.get('batch_id', None)
		if openid is None or batchId is None:
			return None 
		token = '%s@%s' % (openid, batchId)
		self.__Cache__[token] = data
		return token

	def fetchByToken(self, token):
		args = token.split('@')
		if len(args) <> 2:
			return None
		openid = args[0]
		batchId = args[1]
		return self.fetch(openid, batchId)

	def fetch(self, openid, batchId):
		if openid is None or batchId is None:
			return None
		token = '%s@%s' % (openid, batchId)
		data = self.__Cache__.get(token, None)
		return data
		
