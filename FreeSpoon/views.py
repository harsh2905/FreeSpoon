from rest_framework.decorators import (
	api_view,
	permission_classes,
)
from rest_framework.permissions import (
	AllowAny,
)
from rest_framework.reverse import reverse
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
	return Response({
		'refresh': reverse('refresh', request=request, format=format),
		'user': reverse('details', request=request, format=format),
		'bind': reverse('bind', request=request, format=format),
		'wxConfig': reverse('wxConfig', request=request, format=format),
		'login': reverse('login', request=request, format=format),
		'index': reverse('index', request=request, format=format),
		'recipeIndex': reverse('recipeIndex', request=request, format=format),
		'images': reverse('imageRetrieve', request=request, format=format, kwargs={'pk': 'yourkey'}),
		'payNotify': reverse('payNotify', request=request, format=format, kwargs={'appid': 'yourappid'}),
		'payRequest': reverse('payRequest', request=request, format=format, kwargs={'pk': 123456}),
		'sms': reverse('sms', request=request, format=format, kwargs={'mob': 18600000000}),
		'bulks': reverse('bulk-list', request=request, format=format),
		'products': reverse('product-list', request=request, format=format),
		'shippingaddresses': reverse('shippingaddress-list', request=request, format=format),
		'purchasedproducthistorys': reverse('purchasedproducthistory-list', request=request, format=format),
		'orders': reverse('order-list', request=request, format=format),
		'recipes': reverse('recipe-list', request=request, format=format),
		'dishs': reverse('dish-list', request=request, format=format),
	})

@api_view(['GET'])
@permission_classes([AllowAny])
def meta(request, format=None):
	return Response({
		'name': 'FreeSpoon API',
		'version': '0.0.1'
	})
