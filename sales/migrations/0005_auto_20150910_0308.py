# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_auto_20150910_0139'),
    ]

    operations = [
        migrations.AddField(
            model_name='statpublisherbase',
            name='advertiser_genre',
            field=models.ForeignKey(related_name='advertiser_genre', db_constraint=False, default=None, to='sales.Genre'),
        ),
        migrations.AddField(
            model_name='statpublisherbase',
            name='os',
            field=models.CharField(default=b'', max_length=15),
        ),
        migrations.AddField(
            model_name='statpublisherbase',
            name='publisher_genre',
            field=models.ForeignKey(related_name='publisher_genre', db_constraint=False, default=None, to='sales.Genre'),
        ),
    ]
