from rest_framework.parsers import BaseParser

class StreamParser(BaseParser):

	media_type = 'application/octet-stream'

	def parse(self, stream, media_type=None, parser_context=None):
		return stream.read()