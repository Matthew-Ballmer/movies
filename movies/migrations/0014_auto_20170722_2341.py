# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 20:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0013_auto_20170716_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='dvd_release_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='movie',
            name='update_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
