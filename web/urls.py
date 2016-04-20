#!/usr/bin/python

from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^r$', views.redirectToIndex, name='redirectToIndex'),
	url(r'^d$', views.redirectToConfirm, name='redirectToConfirm'),
	url(r'^createQRFromIndexWithRedirect$', 
		views.createQRFromIndexWithRedirect, name='createQRFromIndexWithRedirect'),
	url(r'^createQRFromConfirmWithRedirect$', 
		views.createQRFromConfirmWithRedirect, name='createQRFromConfirmWithRedirect'),
	url(r'^createQRFromIndex$', views.createQRFromIndex, name='createQRFromIndex'),
	url(r'^createQRFromIndex_$', views.createUrlFromIndex, name='createUrlFromIndex'),
	url(r'^createQRFromConfirm$', views.createQRFromConfirm, name='createQRFromConfirm'),
	url(r'^$', views.index, name='index'),
	url(r'^order$', views.order, name='order'),
	url(r'^unifiedOrder$', views.unifiedOrder, name='unifiedOrder'),
	url(r'^payNotify$', views.payNotify, name='payNotify'),
	url(r'^confirm$', views.confirm, name='confirm'),
	url(r'^complete$', views.complete, name='complete'),
	url(r'^distReport$', views.distReport, name='distReport'),
]
