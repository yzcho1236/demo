# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-10 01:35
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0004_auto_20190109_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tree_model',
            name='effective_start',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 1, 10, 0, 0), null=True, verbose_name='生效开始'),
        ),
    ]
