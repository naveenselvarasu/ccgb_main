# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-05-22 12:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0044_farmerclusterseasonmap_seasonal_farmer_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmerbankdetails',
            name='remarks',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
