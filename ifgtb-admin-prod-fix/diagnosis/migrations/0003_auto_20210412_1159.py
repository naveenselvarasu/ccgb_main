# Generated by Django 3.1.6 on 2021-04-12 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0002_auto_20210211_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='userquery',
            name='age_in_month',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userquery',
            name='age_in_year',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userquery',
            name='area_in_acre',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
    ]
