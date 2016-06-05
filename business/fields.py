from rest_framework import serializers
import datetime
from .utils import total_microseconds

class TimestampField(serializers.Field):
	def to_representation(self, value):
		# value is local time zone
		epoch = datetime.datetime(1970, 1, 1)
		#return int((value - epoch).total_seconds())
		return int(total_microseconds(value - epoch))

	def to_internal_value(self, value):
		value = value / 10**6
		return datetime.datetime.utcfromtimestamp(value) # No additional time zone

class StandardTimeField(serializers.Field):
	def to_representation(self, value):
		epoch = datetime.datetime(1970, 1, 1)
		now = datetime.datetime.now() # local time zone
		#return int((now - epoch).total_seconds())
		return int(total_microseconds(now - epoch))
