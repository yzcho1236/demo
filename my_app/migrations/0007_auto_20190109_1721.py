# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-09 09:21
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0006_auto_20190109_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='upload_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 1, 9, 9, 21, 15, 684426, tzinfo=utc), null=True, verbose_name='上传时间'),
        ),
    ]
