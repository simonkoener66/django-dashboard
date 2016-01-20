# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_auto_20150910_0308'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='statpublisherbase',
            unique_together=set([('app_id', 'app_name', 'publisher_id', 'type', 'os', 'advertiser_genre', 'publisher_genre')]),
        ),
    ]
