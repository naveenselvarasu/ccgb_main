# Generated by Django 3.1.6 on 2022-01-07 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yield_calculator', '0008_auto_20211211_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantationyield',
            name='actual_yield',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='plantationyield',
            name='estimated_yield',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
    ]
