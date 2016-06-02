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

admin.site.register(User)
admin.site.register(Reseller)
admin.site.register(Dispatcher)

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductDetails)
admin.site.register(Bulk)
admin.site.register(Order)
admin.site.register(Goods)
