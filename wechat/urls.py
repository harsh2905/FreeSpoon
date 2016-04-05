#!/usr/bin/python

from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^xhr/unifiedorder$', views.unifiedorder, name='unifiedorder'),
	url(r'^confirm$', views.confirm, name='confirm'),
	url(r'^complete$', views.complete, name='complete'),
	url(r'^qr/index/([0-9]*)$', views.qr_index, name='qr_index'),
	url(r'^qr/index2/([0-9]*)$', views.qr_index2, name='qr_index2'),
	url(r'^qr/confirm/([0-9]*)$', views.qr_confirm, name='qr_confirm'),
	url(r'^order/report/([0-9]*)/([0-9]*)$', views.order_report, name='order_report'),
]
