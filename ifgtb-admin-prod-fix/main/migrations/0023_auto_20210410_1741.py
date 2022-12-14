# Generated by Django 3.1.6 on 2021-04-10 17:41

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_nursery_nursery_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='industryoffice',
            name='image',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=main.models.get_industry_office_image),
        ),
        migrations.AddField(
            model_name='instituteoffice',
            name='image',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=main.models.get_scientist_office_image),
        ),
        migrations.AddField(
            model_name='nurseryoffice',
            name='image',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=main.models.get_nursery_office_image),
        ),
    ]
