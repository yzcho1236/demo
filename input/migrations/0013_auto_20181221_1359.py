# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-21 05:59
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0012_auto_20181219_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='effective_start',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 12, 21, 0, 0), null=True, verbose_name='生效开始'),
        ),
        migrations.AlterField(
            model_name='tree_model',
            name='effective_start',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 12, 21, 0, 0), null=True, verbose_name='生效开始'),
        ),
    ]
