# Generated by Django 3.1.6 on 2021-04-07 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_userprofile_ms_farmer_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('crop_cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.cropcv')),
            ],
        ),
        migrations.CreateModel(
            name='NurseryType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='WoodUse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='industryofficial',
            name='is_contact_person',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='nurseryincharge',
            name='is_contact_person',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='scientist',
            name='is_contact_person',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='NurseryOfficeCropMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.clone')),
                ('nursery_office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.nurseryoffice')),
            ],
        ),
        migrations.CreateModel(
            name='IndustryOfficeCropMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crop_cv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.cropcv')),
                ('industry_office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.industryoffice')),
                ('procurement_purpose', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.wooduse')),
            ],
        ),
    ]
