# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-06-17 07:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0027_auto_20200614_0641'),
        ('inputdistri', '0012_auto_20200616_0035'),
    ]

    operations = [
        migrations.CreateModel(
            name='Harvest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_harvest', models.DateField()),
                ('value', models.IntegerField()),
                ('latitude', models.DecimalField(blank=True, decimal_places=7, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ('device_datacapture_datetime', models.DateTimeField(blank=True, null=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instance.Business')),
            ],
        ),
        migrations.CreateModel(
            name='HarvestProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('harvest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inputdistri.Harvest')),
            ],
        ),
        migrations.CreateModel(
            name='harvestPropertyName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='harvestlevel',
            name='ordinal',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='harvestproperty',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inputdistri.harvestPropertyName'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='nth_harvest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inputdistri.HarvestLevel'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='sowing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instance.Sowing'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inputdistri.Unit'),
        ),
    ]
