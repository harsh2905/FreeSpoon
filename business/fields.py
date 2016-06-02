from rest_framework import serializers
import datetime

class TimestampField(serializers.Field):
	def to_representation(self, value):
		epoch = datetime.datetime(1970, 1, 1)
		return int((value - epoch).total_seconds())

	def to_internal_value(self, value):
		return datetime.datetime.fromtimestamp(value)
