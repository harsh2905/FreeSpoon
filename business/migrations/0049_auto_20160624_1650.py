# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-24 08:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0048_slide_key'),
    ]

    operations = [
        migrations.RenameField(
            model_name='slide',
            old_name='link',
            new_name='source',
        ),
    ]