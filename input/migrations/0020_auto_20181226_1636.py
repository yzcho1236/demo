# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-26 08:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0019_auto_20181226_1003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tree_model',
            name='nr',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='代码'),
        ),
    ]
