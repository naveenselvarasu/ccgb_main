# Generated by Django 3.1.6 on 2021-03-26 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20210324_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmer',
            name='owner_ship',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.ownership'),
        ),
    ]
