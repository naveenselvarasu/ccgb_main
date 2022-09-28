# Generated by Django 3.1.6 on 2021-04-03 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_farmer_owner_ship'),
    ]

    operations = [
        migrations.CreateModel(
            name='MicroService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='MicroServiceAuthentication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refresh_token', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('expiry_time', models.DateTimeField(blank=True, null=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('micro_service', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.microservice')),
            ],
        ),
    ]