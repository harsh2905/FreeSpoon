# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-22 03:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0042_auto_20160622_1148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dish',
            name='cover',
        ),
        migrations.AddField(
            model_name='dish',
            name='cover',
            field=models.ManyToManyField(to='business.Image'),
        ),
        migrations.RemoveField(
            model_name='dishdetails',
            name='image',
        ),
        migrations.AddField(
            model_name='dishdetails',
            name='image',
            field=models.ManyToManyField(to='business.Image'),
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='cover',
        ),
        migrations.AddField(
            model_name='recipe',
            name='cover',
            field=models.ManyToManyField(to='business.Image'),
        ),
        migrations.RemoveField(
            model_name='step',
            name='image',
        ),
        migrations.AddField(
            model_name='step',
            name='image',
            field=models.ManyToManyField(to='business.Image'),
        ),
    ]
