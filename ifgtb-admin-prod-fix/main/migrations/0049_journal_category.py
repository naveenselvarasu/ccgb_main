# Generated by Django 3.1.6 on 2021-12-29 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_journal_journalscategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.journalscategory'),
            preserve_default=False,
        ),
    ]
