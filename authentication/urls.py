from django.conf.urls import url, include

from rest_auth.views import (
	LoginView,
	UserDetailsView,
)

from rest_framework_jwt.views import refresh_jwt_token

from .views import *

urlpatterns = [
	url(r'^login$', LoginView.as_view(), name='rest_login'),
	url(r'^refresh$', refresh_jwt_token),
	url(r'^user$', UserDetailsView.as_view(), name='rest_user_details'),
	url(r'^weixin_mp$', WeixinLogin.as_view(), name='wx_login'),
]
