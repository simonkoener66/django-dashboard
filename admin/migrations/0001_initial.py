# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('email', models.CharField(unique=True, max_length=255)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(blank=True)),
                ('date_updated', models.DateTimeField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('type', models.CharField(default=b'regular', max_length=20)),
            ],
            options={
                'db_table': 'sales_authuser',
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('advertiser_id', models.IntegerField(unique=True)),
                ('advertiser', models.CharField(max_length=255, blank=True)),
                ('publisher_id', models.IntegerField(unique=True)),
                ('publisher', models.CharField(max_length=255, blank=True)),
                ('business_unit', models.CharField(max_length=255)),
                ('discount_json', models.TextField()),
                ('region', models.CharField(default=b'', max_length=255)),
                ('date_created', models.DateTimeField(null=True, blank=True)),
                ('date_modified', models.DateTimeField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, db_constraint=False)),
            ],
            options={
                'db_table': 'accounts',
            },
        ),
    ]
