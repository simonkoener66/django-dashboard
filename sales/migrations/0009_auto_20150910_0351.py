# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0008_auto_20150910_0348'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='statpublisher',
            table='stats_publisher',
        ),
    ]
