#!/usr/bin/python

from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^wxConfig$', views.wxConfig, name='wxConfig2'),
	url(r'^login$', views.UserLoginView.as_view(), name='userLogin'),
	url(r'^weixin$', views.WeixinLogin.as_view(), name='userSociallogin'),
]
