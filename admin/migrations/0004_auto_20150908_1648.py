# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_auto_20150908_0321'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='discount_json',
            new_name='json',
        ),
        migrations.RemoveField(
            model_name='account',
            name='advertiser',
        ),
        migrations.RemoveField(
            model_name='account',
            name='advertiser_id',
        ),
        migrations.RemoveField(
            model_name='account',
            name='business_unit',
        ),
        migrations.RemoveField(
            model_name='account',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='account',
            name='publisher',
        ),
        migrations.RemoveField(
            model_name='account',
            name='publisher_id',
        ),
        migrations.RemoveField(
            model_name='account',
            name='region',
        ),
        migrations.AddField(
            model_name='account',
            name='base_id',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='account',
            name='date_updated',
            field=models.DateField(default=datetime.datetime(2015, 9, 8, 16, 48, 2, 600885, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='account',
            name='type',
            field=models.CharField(default=b'', max_length=20),
        ),
        migrations.AlterField(
            model_name='account',
            name='date_created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterModelTable(
            name='account',
            table=None,
        ),
    ]
