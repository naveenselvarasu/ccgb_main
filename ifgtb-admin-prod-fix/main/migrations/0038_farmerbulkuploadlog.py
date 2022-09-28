# Generated by Django 3.1.6 on 2021-08-24 07:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0037_auto_20210823_0751'),
    ]

    operations = [
        migrations.CreateModel(
            name='FarmerBulkUploadLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField()),
                ('uploaded_count', models.PositiveIntegerField()),
                ('already_exists', models.PositiveIntegerField()),
                ('excel_file', models.FileField(upload_to=main.models.get_uploaded_excel_from_bank)),
                ('file_name', models.CharField(blank=True, max_length=100, null=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
