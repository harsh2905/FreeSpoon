#!/usr/bin/python

from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^wxConfig$', views.wxConfig, name='wxConfig2'),
]
