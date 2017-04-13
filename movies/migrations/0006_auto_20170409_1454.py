# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-09 11:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_movie_movieinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movieinfo',
            name='dvd_release_date_status',
            field=models.CharField(choices=[('NA', 'N/A'), ('NF', 'not found'), ('R', 'received')], max_length=3),
        ),
    ]
