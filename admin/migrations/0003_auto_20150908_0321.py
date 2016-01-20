# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0002_auto_20150908_0252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authuser',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='authuser',
            name='date_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
