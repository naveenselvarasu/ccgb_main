# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-31 10:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inputdistri', '0007_auto_20200525_0823'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='procurementtransportinchargekyc',
            name='mobile_number',
        ),
        migrations.AddField(
            model_name='procurement',
            name='procurement_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inputdistri.ProcurementGroup'),
            preserve_default=False,
        ),
    ]
