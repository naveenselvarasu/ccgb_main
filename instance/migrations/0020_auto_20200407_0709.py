# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-04-07 07:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('instance', '0019_auto_20200407_0707'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentFarmerMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instance.FarmerClusterSeasonMap')),
            ],
        ),
        migrations.CreateModel(
            name='UserFarmerMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instance.FarmerClusterSeasonMap')),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userfarmermap',
            unique_together=set([('officer', 'farmer')]),
        ),
        migrations.AlterUniqueTogether(
            name='agentfarmermap',
            unique_together=set([('agent', 'farmer')]),
        ),
    ]