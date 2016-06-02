from django.contrib import admin

# Register your models here.

from django import forms
from .models import *

admin.site.register(User)
admin.site.register(Reseller)
admin.site.register(Dispatcher)
