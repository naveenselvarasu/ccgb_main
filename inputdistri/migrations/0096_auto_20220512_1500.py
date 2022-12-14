# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-05-12 15:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inputdistri', '0095_auto_20220512_1450'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='allowance',
        #     name='date',
        #     field=models.DateField(default=django.utils.timezone.now),
        #     preserve_default=False,
        # ),
        migrations.AddField(
            model_name='allowance',
            name='max_status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inputdistri.MaxStatus'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allowance',
            name='max_status_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # migrations.AddField(
        #     model_name='travelallowancedetilas',
        #     name='date',
        #     field=models.DateField(default=django.utils.timezone.now),
        #     preserve_default=False,
        # ),
        migrations.AddField(
            model_name='usertypewiseallowancecost',
            name='max_status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inputdistri.MaxStatus'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertypewiseallowancecost',
            name='max_status_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
