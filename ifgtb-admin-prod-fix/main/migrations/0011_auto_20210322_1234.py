# Generated by Django 3.1.6 on 2021-03-22 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20210320_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farmer',
            name='block',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='farmer',
            name='district',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='farmer',
            name='revenue_village',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='farmer',
            name='state',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
