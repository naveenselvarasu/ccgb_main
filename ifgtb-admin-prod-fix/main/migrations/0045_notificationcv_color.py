# Generated by Django 3.1.6 on 2021-12-30 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_notificatiionlog_notificationcv'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationcv',
            name='color',
            field=models.CharField(default='#2100cf', max_length=100),
            preserve_default=False,
        ),
    ]
