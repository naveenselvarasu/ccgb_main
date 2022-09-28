# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-05 11:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inputdistri', '0048_auto_20210305_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentinventorystorelabelrangemap',
            name='input_sub_store_inventory',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inputdistri.InputSubStoreInventory'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='substoreissuelabelagentmap',
            name='input_sub_store_inventory',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inputdistri.InputSubStoreInventory'),
            preserve_default=False,
        ),
    ]