# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-10 08:55
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0010_auto_20190110_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='upload_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 1, 10, 8, 55, 57, 970767, tzinfo=utc), null=True, verbose_name='上传时间'),
        ),
        migrations.AlterField(
            model_name='uploadfilemodel',
            name='upload_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 1, 10, 8, 55, 57, 971768, tzinfo=utc), null=True, verbose_name='上传时间'),
        ),
    ]
