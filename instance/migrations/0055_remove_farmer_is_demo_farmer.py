# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-06-26 16:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0054_farmer_is_demo_farmer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='farmer',
            name='is_demo_farmer',
        ),
    ]
