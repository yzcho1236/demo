# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-19 02:24
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0006_auto_20181218_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='ancestor',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='祖先'),
        ),
        migrations.AlterField(
            model_name='item',
            name='effective_start',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 12, 19, 0, 0), null=True, verbose_name='生效开始'),
        ),
    ]