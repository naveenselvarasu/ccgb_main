# Generated by Django 3.1.6 on 2022-02-02 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20210825_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='base64_type',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
