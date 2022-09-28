# Generated by Django 3.1.6 on 2021-05-26 15:34

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_userprofile_about_me'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='photo',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to=main.models.get_profile_photo_destination),
        ),
    ]
