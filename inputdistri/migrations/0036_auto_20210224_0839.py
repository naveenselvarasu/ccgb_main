# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-24 08:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inputdistri', '0035_auto_20210224_0713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='areacv',
            name='quantity_in_acre',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]