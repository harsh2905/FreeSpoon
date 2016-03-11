from django.contrib import admin

# Register your models here.

from .models import Batch
from .models import Commodity
from .models import CommodityImage
from .models import CommodityInBatch
from .models import Customer
from .models import Distributer
from .models import Leader
from .models import Order
from .models import Membership_Order_To_Commodities

class CommodityImageInline(admin.TabularInline):
	model = CommodityImage
	extra = 1
	readonly_fields = ('render',)

class CommodityAdmin(admin.ModelAdmin):
	inlines = [CommodityImageInline]

class CommodityInBatchInline(admin.TabularInline):
	model = CommodityInBatch
	extra = 1

class BatchAdmin(admin.ModelAdmin):
	#fields = ['title', 'desc', 'leader', \
	#		'end_time', 'status']
	inlines = [CommodityInBatchInline]
	list_display = ('title', 'desc', 'leader', \
			'start_time', 'end_time', 'status')
	list_filter = ['start_time']
	search_fields = ['title']

class Membership_Order_To_CommoditiesInline(admin.TabularInline):
	model = Membership_Order_To_Commodities
	extra = 1

class OrderAdmin(admin.ModelAdmin):
	#model = Order
	#filter_horizontal = ('commodities',)
	inlines = (Membership_Order_To_CommoditiesInline,)

admin.site.register(Commodity, CommodityAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Customer)
admin.site.register(Distributer)
admin.site.register(Leader)
admin.site.register(Order, OrderAdmin)

