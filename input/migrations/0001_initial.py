# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-29 08:24
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nr', models.CharField(max_length=300, unique=True, verbose_name='代码')),
                ('name', models.CharField(max_length=300, verbose_name='名称')),
                ('barcode', models.CharField(max_length=300, verbose_name='条码')),
                ('lft', models.PositiveIntegerField(blank=True, null=True, verbose_name='左节点')),
                ('rght', models.PositiveIntegerField(blank=True, null=True, verbose_name='右节点')),
                ('lvl', models.PositiveIntegerField(blank=True, null=True, verbose_name='层级')),
            ],
        ),
        migrations.CreateModel(
            name='Perm',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('name', models.CharField(max_length=300, unique=True, verbose_name='名称')),
                ('codename', models.CharField(max_length=300, unique=True, verbose_name='名称代码')),
            ],
            options={
                'permissions': (('view_item', 'can view item'), ('view_user', 'can view user'), ('view_user_role', 'can view user role'), ('view_role', 'can view role'), ('view_role_permission', 'can view role permission')),
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('name', models.CharField(max_length=300, unique=True, verbose_name='角色名称')),
            ],
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('permission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='input.Perm', verbose_name='权限')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='input.Role', verbose_name='角色')),
            ],
        ),
        migrations.CreateModel(
            name='Tree_Model',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nr', models.CharField(max_length=300, unique=True, verbose_name='代码')),
                ('name', models.CharField(max_length=300, verbose_name='名称')),
                ('barcode', models.CharField(blank=True, max_length=300, null=True, verbose_name='条码')),
                ('unit', models.CharField(blank=True, max_length=300, null=True, verbose_name='单位')),
                ('qty', models.IntegerField(verbose_name='数量')),
                ('effective_start', models.DateField(blank=True, default=datetime.datetime(2018, 12, 29, 0, 0), null=True, verbose_name='生效开始')),
                ('effective_end', models.DateField(blank=True, default=datetime.datetime(2030, 12, 31, 0, 0), null=True, verbose_name='生效结束')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='input.Tree_Model')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='id')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='input.Role', verbose_name='角色')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
        ),
    ]
