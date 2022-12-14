# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-11 07:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import inputdistri.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inputdistri', '0073_auto_20210603_0618'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcurementFileUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField()),
                ('uploaded_count', models.PositiveIntegerField()),
                ('excel_file', models.FileField(max_length=200, upload_to=inputdistri.models.get_uploaded_excel_from_weigh_bridge_man)),
                ('file_name', models.CharField(blank=True, max_length=100, null=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
