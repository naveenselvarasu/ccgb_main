# Generated by Django 3.1.6 on 2021-05-25 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0003_auto_20210412_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='userquery',
            name='title',
            field=models.TextField(blank=True, null=True),
        ),
    ]