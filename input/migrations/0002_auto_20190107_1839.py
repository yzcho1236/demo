# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-07 10:39
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tree_model',
            name='effective_start',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 1, 7, 0, 0), null=True, verbose_name='生效开始'),
        ),
    ]