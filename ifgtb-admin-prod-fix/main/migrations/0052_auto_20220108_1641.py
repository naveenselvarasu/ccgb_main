# Generated by Django 3.1.6 on 2022-01-08 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_industryofficecropprocurementpricelog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industryofficecropmap',
            name='procurement_purpose',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.wooduse'),
        ),
    ]