# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-26 02:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0018_auto_20181226_0942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tree_model',
            name='nr',
            field=models.CharField(max_length=300, unique=True, verbose_name='代码'),
        ),
    ]
