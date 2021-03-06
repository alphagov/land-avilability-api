# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-16 09:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0048_location_estimated_floor_space'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='nearest_school_distance',
            new_name='nearest_primary_school_distance',
        ),
        migrations.RemoveField(
            model_name='location',
            name='nearest_school',
        ),
        migrations.AddField(
            model_name='location',
            name='nearest_primary_school',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_school_locations', to='api.School'),
        ),
        migrations.AddField(
            model_name='location',
            name='nearest_secondary_school',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='secondary_school_locations', to='api.School'),
        ),
        migrations.AddField(
            model_name='location',
            name='nearest_secondary_school_distance',
            field=models.FloatField(null=True),
        ),
    ]
