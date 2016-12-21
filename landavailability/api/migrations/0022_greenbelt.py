# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-19 10:16
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_auto_20161216_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Greenbelt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=255)),
                ('la_name', models.CharField(blank=True, max_length=255, null=True)),
                ('gb_name', models.CharField(blank=True, max_length=255, null=True)),
                ('ons_code', models.CharField(blank=True, max_length=255, null=True)),
                ('year', models.CharField(blank=True, max_length=255, null=True)),
                ('area', models.DecimalField(decimal_places=2, max_digits=9, null=True)),
                ('perimeter', models.DecimalField(decimal_places=2, max_digits=9, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(geography=True, srid=4326)),
            ],
        ),
    ]