# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-24 07:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inputdistri', '0034_auto_20210224_0706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='areacv',
            name='quantity_in_acre',
            field=models.IntegerField(),
        ),
    ]
