# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0004_auto_20150908_1648'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='account',
            table='accounts',
        ),
    ]
