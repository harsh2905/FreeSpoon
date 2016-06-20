from django.contrib import admin

# Register your models here.

from django import forms
from .models import *

class ProductDetailsInline(admin.TabularInline):
	model = ProductDetails
	extra = 1

class ProductAdmin(admin.ModelAdmin):
	inlines = [
		ProductDetailsInline,
	]

class GoodsInline(admin.TabularInline):
	model = Goods
	extra = 1

class OrderAdmin(admin.ModelAdmin):
	inlines = [
		GoodsInline,
	]

class ExhibitedProductInline(admin.TabularInline):
	model = ExhibitedProduct
	extra = 1

class ExhibitAdmin(admin.ModelAdmin):
	filter_horizontal = ('slides', 'hot_bulks',)
	inlines = [ExhibitedProductInline]

admin.site.register(User)
admin.site.register(Reseller)
admin.site.register(Dispatcher)

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductDetails)
admin.site.register(Bulk)
admin.site.register(Order, OrderAdmin)
admin.site.register(Goods)
admin.site.register(ShippingAddress)

admin.site.register(Slide)
admin.site.register(Exhibit, ExhibitAdmin)