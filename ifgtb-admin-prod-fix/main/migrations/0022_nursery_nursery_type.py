# Generated by Django 3.1.6 on 2021-04-07 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20210407_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='nursery',
            name='nursery_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.nurserytype'),
            preserve_default=False,
        ),
    ]