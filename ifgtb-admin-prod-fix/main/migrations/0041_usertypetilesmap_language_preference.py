# Generated by Django 3.1.6 on 2021-12-04 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_usertypetilesmap_display_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertypetilesmap',
            name='language_preference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.language'),
        ),
    ]
