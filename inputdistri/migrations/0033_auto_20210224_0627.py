# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-24 06:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inputdistri', '0032_inputpacketinventorycodebank'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComboIssueRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_code', models.CharField(max_length=50)),
                ('quantity_in_numbers', models.PositiveIntegerField()),
                ('expected_date', models.DateTimeField()),
                ('issue_rised_date', models.DateTimeField()),
                ('max_status_date', models.DateTimeField()),
                ('senior_supervisor_status_date', models.DateTimeField(blank=True, null=True)),
                ('assitant_manager_status_date', models.DateTimeField(blank=True, null=True)),
                ('agri_officer_status_date', models.DateTimeField(blank=True, null=True)),
                ('gm_status_date', models.DateTimeField(blank=True, null=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('agri_officer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agri_offcier_user_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ComboIssueRequestAgentMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_rised_date', models.DateTimeField()),
                ('quantity_in_numbers', models.PositiveIntegerField()),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_user_id', to=settings.AUTH_USER_MODEL)),
                ('combo_issue_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inputdistri.ComboIssueRequest')),
            ],
        ),
        migrations.CreateModel(
            name='IssueRequestStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
            ],
        ),
        migrations.CreateModel(
            name='MaxStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
            ],
        ),
        migrations.AddField(
            model_name='inputpacketinventorylabel',
            name='label_range_start_default',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='agri_officer_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agri_officer_status', to='inputdistri.IssueRequestStatus'),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='assitant_manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asst_manager_user_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='assitant_manager_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assitant_manager_status', to='inputdistri.IssueRequestStatus'),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='gm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gm_user_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='gm_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gm_status', to='inputdistri.IssueRequestStatus'),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='input_combo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inputdistri.InputCombo'),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='max_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inputdistri.MaxStatus'),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='quantity_for_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inputdistri.AreaCv'),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='senior_supervisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='senior_supervisor_user_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='senior_supervisor_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='senior_supervisor_status', to='inputdistri.IssueRequestStatus'),
        ),
        migrations.AddField(
            model_name='comboissuerequest',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervisor_user_id', to=settings.AUTH_USER_MODEL),
        ),
    ]
