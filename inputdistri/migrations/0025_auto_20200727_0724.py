# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-07-27 07:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inputdistri', '0024_procurement_remarks'),
    ]

    operations = [
        migrations.RenameField(
            model_name='procurement',
            old_name='remarks',
            new_name='remark',
        ),
    ]
