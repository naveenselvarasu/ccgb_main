# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-04-10 08:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0022_auto_20200409_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='emergency_number',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
    ]