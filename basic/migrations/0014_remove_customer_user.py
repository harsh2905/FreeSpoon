# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-30 13:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0012_auto_20160530_1322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='user',
        ),
    ]
