# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0010_statpublisherbase_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='statpublisher',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
