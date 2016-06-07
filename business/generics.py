from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django.db.models.query import QuerySet
from rest_framework.generics import GenericAPIView as BaseGenericAPIView

def get_object_or_404(queryset, *filter_args, **filter_kwargs):
	try:
		return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
	except (TypeError, ValueError):
		raise Http404

class GenericAPIView(BaseGenericAPIView):

	def get_queryset(self, suffix=None):
		queryset = self.queryset
		_ = 'queryset_%s' % suffix
		if suffix and hasattr(self, _):
			queryset = getattr(self, _)
		assert queryset is not None, (
			"'%s' should either include a `queryset` attribute, "
			"or override the `get_queryset()` method."
			% self.__class__.__name__
		)
		
		if isinstance(queryset, QuerySet):
			# Ensure queryset is re-evaluated on each request.
			queryset = queryset.all()
		return queryset

	def get_object(self, suffix=None):
		queryset = self.filter_queryset(self.get_queryset(suffix))
		
		# Perform the lookup filtering.
		lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
		
		assert lookup_url_kwarg in self.kwargs, (
			'Expected view %s to be called with a URL keyword argument '
			'named "%s". Fix your URL conf, or set the `.lookup_field` '
			'attribute on the view correctly.' %
			(self.__class__.__name__, lookup_url_kwarg)
		)
		
		filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
		obj = get_object_or_404(queryset, **filter_kwargs)
		
		# May raise a permission denied
		self.check_object_permissions(self.request, obj)
		
		return obj

	def get_serializer(self, *args, **kwargs):
		suffix = kwargs.pop('suffix', None)
		serializer_class = self.get_serializer_class(suffix)
		kwargs['context'] = self.get_serializer_context()
		return serializer_class(*args, **kwargs)

	def get_serializer_class(self, suffix=None):
		serializer_class = self.serializer_class
		_ = 'serializer_class_%s' % suffix
		if suffix and hasattr(self, _):
			serializer_class = getattr(self, _)
		assert serializer_class is not None, (
			"'%s' should either include a `serializer_class` attribute, "
			"or override the `get_serializer_class()` method."
			% self.__class__.__name__
		)
		
		return serializer_class
