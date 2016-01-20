# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_auto_20150909_1532'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatAdvertiserBase',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('country', models.CharField(default=b'', max_length=15)),
                ('traffic', models.CharField(default=b'', max_length=15)),
                ('type', models.CharField(default=b'', max_length=15)),
                ('budget', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(to='sales.Campaign', db_constraint=False)),
            ],
            options={
                'db_table': 'stats_advertiser_base',
            },
        ),
        migrations.AlterUniqueTogether(
            name='statbase',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='statbase',
            name='campaign',
        ),
        migrations.AlterField(
            model_name='statadvertiser',
            name='base',
            field=models.ForeignKey(default=None, to='sales.StatAdvertiserBase', db_constraint=False),
        ),
        migrations.DeleteModel(
            name='StatBase',
        ),
        migrations.AlterUniqueTogether(
            name='statadvertiserbase',
            unique_together=set([('country', 'traffic', 'type', 'campaign')]),
        ),
    ]
