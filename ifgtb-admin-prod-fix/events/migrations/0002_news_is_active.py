# Generated by Django 3.1.6 on 2021-05-18 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
