# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-06-24 04:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inputdistri', '0019_auto_20200624_0347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harvest',
            name='nth_harvest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inputdistri.HarvestLevel'),
        ),
    ]