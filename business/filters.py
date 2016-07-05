from rest_framework import filters
from .models import *
from .exceptions import *
from django.core.exceptions import ObjectDoesNotExist

class IsOwnedByUserFilterBackend(filters.BaseFilterBackend):

	def filter_queryset(self, request, queryset, view):
		mob_user = request.user
		if mob_user is None:
			raise BadRequestException(detail='Mob user not found')
		return queryset.filter(user=mob_user.user)

class FieldFilterBackend(filters.BaseFilterBackend):

	def filter_queryset(self, request, queryset, view):
		conditions = {}
		for filter_field in view.filter_fields:
			condition = request.query_params.get(filter_field, None)
			if view.filter_field_raise_exception and condition is None:
				raise BadRequestException(detail='%s is required' % filter_field)
			if condition is not None:
				conditions[filter_field] = condition
		queryset = queryset.filter(**conditions)
		return queryset

class FieldOrderBackend(filters.BaseFilterBackend):

	def filter_queryset(self, request, queryset, view):
		queryset = queryset.order_by(*view.order_fields)
		return queryset

class MoreFilterBackend(filters.BaseFilterBackend):

	def filter_queryset(self, request, queryset, view):
		obj_id = request.query_params.get('more', None)
		try:
			obj = queryset.get(pk=obj_id)
			data = None
			if hasattr(obj, 'user') and obj.user:
				data = queryset.filter(user_id=obj.user.id).exclude(id=obj.id)
				if data.count() == 0:
					data = queryset.order_by('-create_time').exclude(id=obj.id)
			else:
				data = queryset.order_by('-create_time').exclude(id=obj.id)
			return data
		except ObjectDoesNotExist:
			return queryset

class MethodFilterBackend(filters.BaseFilterBackend):

	def filter_queryset(self, request, queryset, view):
		queryset = view.filter_method(queryset)
		return queryset