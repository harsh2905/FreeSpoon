from django.conf.urls import url, include

from rest_auth.views import (
	LoginView,
	UserDetailsView,
)

from rest_framework_jwt.views import refresh_jwt_token

from .views import *

urlpatterns = [
	url(r'^login$', LoginView.as_view(), name='login'),
	url(r'^refresh$', refresh_jwt_token, name='refresh'),
	url(r'^user$', UserDetailsView.as_view(), name='details'),
	url(r'^weixin$', WeixinLogin.as_view(), name='sociallogin'),
	url(r'^bind$', BindView.as_view(), name='bind'),
]
