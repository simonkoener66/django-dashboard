# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0009_auto_20150909_1518'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('campaign_id', models.AutoField(serialize=False, primary_key=True)),
                ('campaign', models.CharField(max_length=255)),
                ('account_id', models.IntegerField(default=None, null=True)),
                ('os', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'campaigns',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('genre_name', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'db_table': 'genre',
            },
        ),
        migrations.CreateModel(
            name='StatAdvertiser',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('date', models.DateField(default=None)),
                ('campaign_status', models.BooleanField(default=True)),
                ('revenue', models.FloatField(default=None)),
                ('margin', models.FloatField(default=None)),
            ],
            options={
                'db_table': 'stats_advertiser',
            },
        ),
        migrations.CreateModel(
            name='StatBase',
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
                'db_table': 'stats_base',
            },
        ),
        migrations.CreateModel(
            name='StatPublisher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('app_placement_id', models.IntegerField()),
                ('app_placement_name', models.CharField(max_length=255)),
                ('type', models.CharField(default=b'', max_length=15)),
                ('country', models.CharField(default=b'', max_length=15)),
                ('status', models.BooleanField(default=True)),
                ('impressions_avail', models.IntegerField()),
                ('impressions_filled', models.IntegerField()),
                ('revenue', models.FloatField(default=None)),
                ('margin', models.FloatField(default=None)),
                ('account', models.ForeignKey(to='admin.Account', db_constraint=False)),
                ('genre', models.ForeignKey(related_name='genre_publisher', to='sales.Genre', db_constraint=False)),
                ('genre_advertiser', models.ForeignKey(related_name='genre_advertiser', to='sales.Genre', db_constraint=False)),
            ],
            options={
                'db_table': 'stats_supplier',
            },
        ),
        migrations.CreateModel(
            name='UserPlan',
            fields=[
                ('plan_id', models.AutoField(serialize=False, primary_key=True)),
                ('plan', models.CharField(max_length=255)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('target_revenue', models.FloatField()),
                ('target_margin', models.FloatField()),
                ('date_created', models.DateTimeField(null=True, blank=True)),
                ('date_updated', models.DateTimeField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, db_constraint=False)),
            ],
            options={
                'db_table': 'users_plan',
            },
        ),
        migrations.AddField(
            model_name='statadvertiser',
            name='base',
            field=models.ForeignKey(default=None, to='sales.StatBase', db_constraint=False),
        ),
        migrations.AddField(
            model_name='campaign',
            name='genre',
            field=models.ForeignKey(to='sales.Genre', db_constraint=False),
        ),
        migrations.AlterUniqueTogether(
            name='statbase',
            unique_together=set([('country', 'traffic', 'type', 'campaign')]),
        ),
        migrations.AlterUniqueTogether(
            name='statadvertiser',
            unique_together=set([('date', 'base')]),
        ),
    ]
