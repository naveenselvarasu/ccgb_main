# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-19 07:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0039_clusterseasonmap'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmer',
            name='common_code',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
