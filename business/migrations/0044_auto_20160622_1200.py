# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-22 04:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0043_auto_20160622_1158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dish',
            name='cover',
        ),
        migrations.AddField(
            model_name='dish',
            name='cover',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='business.Image'),
        ),
        migrations.RemoveField(
            model_name='dishdetails',
            name='image',
        ),
        migrations.AddField(
            model_name='dishdetails',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='business.Image'),
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='cover',
        ),
        migrations.AddField(
            model_name='recipe',
            name='cover',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='business.Image'),
        ),
        migrations.RemoveField(
            model_name='step',
            name='image',
        ),
        migrations.AddField(
            model_name='step',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='business.Image'),
        ),
    ]
