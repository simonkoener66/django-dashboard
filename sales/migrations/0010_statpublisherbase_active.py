# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0009_auto_20150910_0351'),
    ]

    operations = [
        migrations.AddField(
            model_name='statpublisherbase',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
