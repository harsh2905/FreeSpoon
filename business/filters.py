from rest_framework import filters
from .models import *
from .exceptions import *

class IsOwnedByUserFilterBackend(filters.BaseFilterBackend):

	def filter_queryset(self, request, queryset, view):
		mob_user = request.user
		if mob_user is None:
			raise BadRequestException('Mob user not found')
		owners = User.objects.filter(mob_user__in=mob_user.associated)
		return queryset.filter(user__in=owners)

class FieldFilterBackend(filters.BaseFilterBackend):

	def filter_queryset(self, request, queryset, view):
		conditions = {}
		for filter_field in view.filter_fields:
			condition = request.query_params.get(filter_field, None)
			if view.filter_field_raise_exception and condition is None:
				raise BadRequestException('%s is required' % filter_field)
			if condition is not None:
				conditions[filter_field] = condition
		queryset = queryset.filter(**conditions)
		return queryset

class FieldOrderBackend(filters.BaseFilterBackend):

	def filter_queryset(self, request, queryset, view):
		queryset = queryset.order_by(*view.order_fields)
		return queryset
