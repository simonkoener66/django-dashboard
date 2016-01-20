# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_auto_20150910_0345'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='statpublisherbase',
            unique_together=set([('app_id', 'app_name', 'publisher_id', 'type', 'os', 'advertiser_genre', 'publisher_genre', 'country')]),
        ),
    ]
