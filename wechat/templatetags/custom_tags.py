#!/usr/bin/python

from django import template

register = template.Library()

@register.filter(name='dict_get')
def dict_get(value, arg):
	return value.get(arg, '')

@register.filter(name='integral_get')
def integral_get(value):
	return str(int(value / 100))

@register.filter(name='decimal_get')
def decimal_get(value):
	return '%02d' % int(value % 100)
