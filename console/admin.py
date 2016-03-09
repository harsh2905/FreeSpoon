from django.contrib import admin

# Register your models here.

from .models import Batch
from .models import Commodity
from .models import Customer
from .models import Distributer
from .models import Leader
from .models import Order

admin.site.register(Batch)
admin.site.register(Commodity)
admin.site.register(Customer)
admin.site.register(Distributer)
admin.site.register(Leader)
admin.site.register(Order)

