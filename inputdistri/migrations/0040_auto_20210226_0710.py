# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-26 07:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inputdistri', '0039_auto_20210225_0448'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputcombo',
            name='display_ordinal',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='inputtype',
            name='display_ordinal',
            field=models.PositiveIntegerField(default=0),
        ),
    ]