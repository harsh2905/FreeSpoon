# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-08 15:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0016_product_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulk',
            name='category',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
