#!/usr/bin/python

from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.main, name='main'),
	url(r'^r(.*)$', views.redirector, name='redirector'),
	url(r'^q', views.createQR, name='createQR'),
	url(r'^wxConfig$', views.wxConfig, name='wxConfig'),
	url(r'^batch$', views.batch, name='batch'),
	url(r'^checkout$', views.checkout, name='checkout'),
	url(r'^unifiedOrder$', views.unifiedOrder, name='unifiedOrder'),
	url(r'^order$', views.order, name='order'),
	url(r'^orders$', views.orders, name='orders'),
	url(r'^payNotify$', views.payNotify, name='payNotify'),
]
