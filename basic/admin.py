from django.contrib import admin

# Register your models here.

from django import forms
from .models import *

class CommodityAdmin(admin.ModelAdmin):
	readonly_fields = ('render',)

class LeaderAdmin(admin.ModelAdmin):
	readonly_fields = ('render',)

class DistributerAdmin(admin.ModelAdmin):
	readonly_fields = ('render',)

class CustomerAdmin(admin.ModelAdmin):
	readonly_fields = ('render',)

class UserAdmin(admin.ModelAdmin):
	readonly_fields = ('render',)

class CommodityInBatchInline(admin.TabularInline):
	model = CommodityInBatch
	extra = 1

class BatchAdmin(admin.ModelAdmin):
	#fields = ['title', 'desc', 'leader', \
	#		'end_time', 'status']
	inlines = [CommodityInBatchInline]
	list_display = ('id', 'title', 'leader', \
			'start_time', 'end_time', 'status')
	list_filter = ['start_time']
	search_fields = ['title']
	model = Batch
	filter_horizontal = ('distributers',)

class CommodityInOrderInline(admin.TabularInline):
	model = CommodityInOrder
	extra = 1

class OrderAdmin(admin.ModelAdmin):
	#model = Order
	#filter_horizontal = ('commodities',)
	inlines = (CommodityInOrderInline,)

admin.site.register(Commodity, CommodityAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Distributer, DistributerAdmin)
admin.site.register(Leader, LeaderAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(User, UserAdmin)
