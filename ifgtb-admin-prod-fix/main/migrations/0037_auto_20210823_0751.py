# Generated by Django 3.1.6 on 2021-08-23 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_auto_20210820_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='industryoffice',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='industryoffice',
            name='short_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='instituteoffice',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='instituteoffice',
            name='short_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='nurseryoffice',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='nurseryoffice',
            name='short_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]