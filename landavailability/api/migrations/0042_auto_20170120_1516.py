# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-20 15:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20170120_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metrotube',
            name='naptan_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
