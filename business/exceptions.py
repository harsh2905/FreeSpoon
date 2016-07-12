from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.encoding import force_text

class BadRequestException(APIException):

	status_code = status.HTTP_400_BAD_REQUEST
	
	def __init__(self, detail=None, errcode=0):
		if detail is not None:
			self.detail = {
				'errcode': errcode,
				'detail': force_text(detail)
			}
			self.detail_ = force_text(detail)
		else:
			self.detail = {
				'errcode': errcode,
				'detail': force_text(self.default_detail)
			}
			self.detail_ = force_text(self.default_detail)

	def __str__(self):
		return self.detail_
