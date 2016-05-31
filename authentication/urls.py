from django.conf.urls import url, include

from .views import *

urlpatterns = [
	url(r'^', include('rest_auth.urls')),
	url(r'^weixin_mp/$', WeixinLogin.as_view(), name='wx_login'),
]
