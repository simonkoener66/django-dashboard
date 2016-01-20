# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0007_account_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='account',
            unique_together=set([('base_id', 'type')]),
        ),
    ]
