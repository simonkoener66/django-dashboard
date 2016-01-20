# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0008_auto_20150908_1658'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='base_id',
            new_name='internal_id',
        ),
        migrations.AlterUniqueTogether(
            name='account',
            unique_together=set([('internal_id', 'type')]),
        ),
    ]
