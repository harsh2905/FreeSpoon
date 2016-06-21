#!/usr/bin/python

from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
	url(r'^wxConfig$', views.wxConfig, name='wxConfig2'),
	url(r'^login$', views.UserLoginView.as_view(), name='login'),
	url(r'^weixin$', views.WeixinLoginView.as_view(), name='weixin'),
	url(r'^bind$', views.BindView.as_view(), name='bind'),
	url(r'^redirect(.*)$', views.redirect, name='redirect'),
	url(r'^index$', views.index, name='index'),	
	url(r'^images$', views.image_create, name='imageCreate'),	
	url(r'^images/(?P<pk>[^/.]+)/$', views.image_retrieve, name='imageRetrieve'),	
	url(r'^paynotify$', views.payNotify, name='payNotify'),
	url(r'^payrequest/(?P<pk>[0-9]+)/$', views.payRequest.as_view(), name='payRequest'),
	#url(r'^login$', views.UserLoginView.as_view(), name='userLogin'),
	#url(r'^weixin$', views.WeixinLogin.as_view(), name='userWeixinLogin'),
	#url(r'^resellerLogin$', views.ResellerLoginView.as_view(), name='resellerLogin'),
	#url(r'^resellerWeixinLogin$', views.ResellerWeixinLogin.as_view(), name='resellerWeixinLogin'),
	#url(r'^dispatcherLogin$', views.DispatcherLoginView.as_view(), name='dispatcherLogin'),
	#url(r'^dispatcherWeixinLogin$', views.DispatcherWeixinLogin.as_view(), name='dispatcherWeixinLogin'),
]

router = DefaultRouter()
router.register(r'bulks', views.BulkViewSet, base_name='bulk')
router.register(r'products', views.ProductViewSet, base_name='product')
router.register(r'shippingaddresses', views.ShippingAddressViewSet, base_name='shippingaddress')
router.register(r'purchasedproducthistorys', views.PurchasedProductHistoryViewSet, 
		base_name='purchasedproducthistory')
router.register(r'orders', views.OrderViewSet, base_name='order')
router.register(r'recipes', views.RecipeViewSet, base_name='recipe')
router.register(r'dishs', views.DishViewSet, base_name='dish')
urlpatterns.extend(router.urls)
