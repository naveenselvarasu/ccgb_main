# Generated by Django 3.1.6 on 2021-08-25 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0010_circularlog_circular_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circularlog',
            name='circular_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='diagnosis.circularcategory'),
        ),
    ]
