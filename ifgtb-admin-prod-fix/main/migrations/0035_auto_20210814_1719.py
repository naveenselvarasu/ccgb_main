# Generated by Django 3.1.6 on 2021-08-14 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_menuheader_menuheaderpage_menuheaderpagepermission_menuheaderpermission'),
    ]

    operations = [
        migrations.AddField(
            model_name='forestoffice',
            name='name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='forestoffice',
            name='short_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
