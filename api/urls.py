#!/usr/bin/python

from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^r/(.+)$', views.redirector, name='redirector'),
	url(r'^q/(.+)$', views.createQR, name='createQR'),
	url(r'^batch$', views.batch, name='batch'),
	url(r'^checkout$', views.checkout, name='checkout'),
	url(r'^payNotify$', views.payNotify, name='payNotify'),
]
