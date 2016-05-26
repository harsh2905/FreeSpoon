from django.contrib import admin

# Register your models here.

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import *

class CommodityAdmin(admin.ModelAdmin):
	readonly_fields = ('render',)

class LeaderAdmin(admin.ModelAdmin):
	readonly_fields = ('render',)

class DistributerAdmin(admin.ModelAdmin):
	readonly_fields = ('render',)

class CustomerAdmin(admin.ModelAdmin):
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

class UserCreationForm(forms.ModelForm):
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('tel',)
		#fields = ('tel', 'password', 'is_active', 'is_admin')

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError('Passwords don\'t match')
		return password2

	def save(self, commit=True):
		user = super(UserCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data['password1'])
		if commit:
			user.save()
		return user

class UserChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField()
	
	class Meta:
		model = User
		fields = ('tel', 'password', 'is_active', 'is_admin')

	def clean_password(self):
		return self.initial['password']

class UserAdmin(BaseUserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm
	list_display = ('tel', 'is_admin')
	list_filter = ('is_admin',)
	fieldsets = (
		(None, {'fields': ('tel', 'password')}),
		('Permissions', {'fields': ('is_admin',)}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('tel', 'password1', 'password2')}
		),
	)
	readonly_fields = ('render',)
	search_fields = ('tel',)
	ordering = ('tel',)
	filter_horizontal = ()

admin.site.register(Commodity, CommodityAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Distributer, DistributerAdmin)
admin.site.register(Leader, LeaderAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
