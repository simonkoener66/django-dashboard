# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_auto_20150909_1538'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatPublisherBase',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('app_id', models.IntegerField(default=None)),
                ('app_name', models.CharField(max_length=255)),
                ('publisher_id', models.IntegerField(default=None)),
                ('country', models.CharField(default=b'', max_length=15)),
                ('type', models.CharField(default=b'', max_length=15)),
                ('impression_avail', models.IntegerField(default=None)),
            ],
            options={
                'db_table': 'stats_publisher_base',
            },
        ),
        migrations.RenameField(
            model_name='statpublisher',
            old_name='impressions_filled',
            new_name='impression',
        ),
        migrations.RemoveField(
            model_name='statpublisher',
            name='account',
        ),
        migrations.RemoveField(
            model_name='statpublisher',
            name='app_placement_id',
        ),
        migrations.RemoveField(
            model_name='statpublisher',
            name='app_placement_name',
        ),
        migrations.RemoveField(
            model_name='statpublisher',
            name='country',
        ),
        migrations.RemoveField(
            model_name='statpublisher',
            name='genre',
        ),
        migrations.RemoveField(
            model_name='statpublisher',
            name='genre_advertiser',
        ),
        migrations.RemoveField(
            model_name='statpublisher',
            name='impressions_avail',
        ),
        migrations.RemoveField(
            model_name='statpublisher',
            name='status',
        ),
        migrations.RemoveField(
            model_name='statpublisher',
            name='type',
        ),
        migrations.AlterUniqueTogether(
            name='statpublisherbase',
            unique_together=set([('app_id', 'app_name', 'publisher_id', 'type')]),
        ),
        migrations.AddField(
            model_name='statpublisher',
            name='base_id',
            field=models.ForeignKey(default=None, to='sales.StatPublisherBase', db_constraint=False),
        ),
    ]
