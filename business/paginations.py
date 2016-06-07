from rest_framework.pagination import BasePagination
from rest_framework.response import Response

import datetime

class TimestampPagination(BasePagination):

	def paginate_queryset(self, queryset, request, view=None):
                limit = request.query_params.get('time', 0)
                limit = int(limit)
                limit = limit / 10**6
                limit = datetime.datetime.fromtimestamp(limit)
                size = request.query_params.get('page_size', 10)
                size = int(size)
		field_name = view.pagination_field_name
		lookup_type = view.pagination_lookup_type
                queryset = queryset.filter(**{
                        '%s__%s' % (field_name, lookup_type) : limit
                })[:size]
		return queryset

	def get_paginated_response(self, data):
		return Response(data)
