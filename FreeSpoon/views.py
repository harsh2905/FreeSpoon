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
		'login': reverse('login', request=request, format=format),
		'refresh': reverse('refresh', request=request, format=format),
		'user': reverse('details', request=request, format=format),
		'weixin': reverse('sociallogin', request=request, format=format),
		'bind': reverse('bind', request=request, format=format),

		'wxConfig': reverse('wxConfig2', request=request, format=format),
	})
