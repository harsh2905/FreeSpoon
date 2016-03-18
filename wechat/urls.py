#!/usr/bin/python

from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^([0-9]*)$', views.index, name='index'),
	url(r'^pay/cb/[0-9]*$', views.pay_callback, name='pay_callback'),
	url(r'^confirm$', views.confirm, name='confirm'),
	url(r'^complete$', views.complete, name='complete'),
	url(r'^qr/confirm/([0-9]*)$', views.qr_confirm, name='qr_confirm'),
	url(r'^order/report/([0-9]*)/([0-9]*)$', views.order_report, name='order_report'),
]
