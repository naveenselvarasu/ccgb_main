# Generated by Django 3.1.6 on 2021-02-08 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20210206_1241'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FarmerSurveyNumber',
            new_name='LandSurveyNumber',
        ),
    ]