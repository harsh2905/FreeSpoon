# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-30 08:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0052_auto_20160630_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='exhibitedproduct',
            name='cover_3x',
            field=models.ImageField(blank=True, null=True, upload_to='images/exhibited_product/%Y/%m/%d'),
        ),
    ]