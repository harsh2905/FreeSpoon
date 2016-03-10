from django.contrib import admin

# Register your models here.

from django.contrib.auth.models import User

from .models import Batch
from .models import Commodity
from .models import Customer
from .models import Distributer
from .models import Leader
from .models import Order
from .models import Membership_Order_To_Commodities

class CommodityInLine(admin.StackedInline):
	model = Commodity
	extra = 1

class BatchAdmin(admin.ModelAdmin):
	fields = ['title', 'desc', 'leader', \
			'end_time', 'status']
	inlines = [CommodityInLine]
	list_display = ('title', 'desc', 'leader', \
			'start_time', 'end_time', 'status')
	list_filter = ['start_time']
	search_fields = ['title']

class Membership_Order_To_CommoditiesInLine(admin.TabularInline):
	model = Membership_Order_To_Commodities
	extra = 1

class OrderAdmin(admin.ModelAdmin):
	#model = Order
	#filter_horizontal = ('commodities',)
	inlines = (Membership_Order_To_CommoditiesInLine,)

class UserInLine(admin.StackedInline):
	model = User

class LeaderAdmin(admin.ModelAdmin):
	inlines = (UserInLine,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Batch, BatchAdmin)
admin.site.register(Customer)
admin.site.register(Distributer)
admin.site.register(Leader)
admin.site.register(Order, OrderAdmin)

