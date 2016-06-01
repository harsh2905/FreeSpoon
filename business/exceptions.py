from rest_framework.exceptions import APIException

class BadRequestException(APIException):

	status_code = 400
	detail = 'Bad Request'
	
	def __init__(self, detail=None):
		if detail:
			self.detail = detail

