from rest_framework.viewsets import ViewSetMixin
from .generics import *
from .mixins import *

class GenericViewSet(ViewSetMixin, GenericAPIView):
	pass

class ReadOnlyModelViewSet(RetrieveModelMixin,
		ListModelMixin,
		GenericViewSet):
	pass

class ModelViewSet(CreateModelMixin,
		RetrieveModelMixin,
		UpdateModelMixin,
		DestroyModelMixin,
		ListModelMixin,
		GenericViewSet):
	pass
