# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_auto_20150910_0347'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statpublisher',
            old_name='base_id',
            new_name='base',
        ),
    ]
