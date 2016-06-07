#!/usr/bin/python

from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
	url(r'^wxConfig$', views.wxConfig, name='wxConfig2'),
	url(r'^login$', views.UserLoginView.as_view(), name='userLogin'),
	url(r'^weixin$', views.WeixinLogin.as_view(), name='userWeixinLogin'),
	url(r'^resellerLogin$', views.ResellerLoginView.as_view(), name='resellerLogin'),
	url(r'^resellerWeixinLogin$', views.ResellerWeixinLogin.as_view(), name='resellerWeixinLogin'),
	url(r'^dispatcherLogin$', views.DispatcherLoginView.as_view(), name='dispatcherLogin'),
	url(r'^dispatcherWeixinLogin$', views.DispatcherWeixinLogin.as_view(), name='dispatcherWeixinLogin'),
]

router = DefaultRouter()
router.register(r'bulks', views.BulkViewSet, base_name='bulk')
router.register(r'products', views.ProductViewSet, base_name='product')
router.register(r'shippingaddresses', views.ShippingAddressViewSet, base_name='shippingaddress')
router.register(r'purchasedproducthistorys', views.PurchasedProductHistoryViewSet, 
		base_name='purchasedproducthistory')
router.register(r'orders', views.OrderViewSet, base_name='order')
urlpatterns.extend(router.urls)
