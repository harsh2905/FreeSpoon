from django.conf.urls import url, include

from rest_auth.views import (
	LoginView,
	LogoutView,
	UserDetailsView,
)

from .views import *

urlpatterns = [
	url(r'^login$', LoginView.as_view(), name='rest_login'),
	url(r'^logout$', LogoutView.as_view(), name='rest_logout'),
	url(r'^user$', UserDetailsView.as_view(), name='rest_user_details'),
	url(r'^weixin_mp$', WeixinLogin.as_view(), name='wx_login'),
]
