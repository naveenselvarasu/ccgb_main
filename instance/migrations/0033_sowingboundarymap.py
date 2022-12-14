# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-14 07:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('instance', '0032_auto_20200829_1201'),
    ]

    operations = [
        migrations.CreateModel(
            name='SowingBoundaryMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_latitude', models.DecimalField(blank=True, decimal_places=7, max_digits=9, null=True)),
                ('device_longitude', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('data_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instance.FarmerDataSource')),
                ('sowing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instance.Sowing')),
                ('sowing_boundry', models.ManyToManyField(to='instance.SowingBoundary')),
            ],
        ),
    ]
