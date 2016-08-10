#!/usr/bin/python

from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from . import views

urlpatterns = [
	url(r'^wxConfig$', views.wxConfig, name='wxConfig'),
	url(r'^login$', views.UserLoginView.as_view(), name='login'),
	url(r'^weixin$', views.WeixinLoginView.as_view(), name='weixin'),
	url(r'^bind$', views.BindView.as_view(), name='bind'),
	url(r'^redirect(.*)$', views.redirect, name='redirect'),
	url(r'^index$', views.index, name='index'),	
	url(r'^recipeindex$', views.recipe_index, name='recipeIndex'),	
	url(r'^images/$', views.image_create, name='imageCreate'),	
	url(r'^images/(?P<pk>[^/.]+)/$', views.image_retrieve, name='imageRetrieve'),	
	url(r'^paynotify/(?P<appid>[^/.]+)/$', views.payNotify, name='payNotify'),
	url(r'^payrequest/(?P<pk>[0-9]+)/$', views.payRequest.as_view(), name='payRequest'),
	url(r'^sms/(?P<mob>[0-9]+)/$', views.sms, name='sms'),	
]

router = SimpleRouter()
router.register(r'bulks', views.BulkViewSet, base_name='bulk')
router.register(r'products', views.ProductViewSet, base_name='product')
router.register(r'categorys', views.CategoryViewSet, base_name='category')
router.register(r'shippingaddresses', views.ShippingAddressViewSet, base_name='shippingaddress')
router.register(r'purchasedproducthistorys', views.PurchasedProductHistoryViewSet, 
		base_name='purchasedproducthistory')
router.register(r'orders', views.OrderViewSet, base_name='order')
router.register(r'recipes', views.RecipeViewSet, base_name='recipe')
router.register(r'dishs', views.DishViewSet, base_name='dish')
urlpatterns.extend(router.urls)
