# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-19 06:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0009_auto_20181219_1220'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tree_Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nr', models.CharField(max_length=300, unique=True, verbose_name='代码')),
                ('name', models.CharField(max_length=300, verbose_name='名称')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]