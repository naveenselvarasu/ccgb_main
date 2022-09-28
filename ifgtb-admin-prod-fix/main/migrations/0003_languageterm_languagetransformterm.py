# Generated by Django 3.1.6 on 2021-03-08 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20210205_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='LanguageTerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='LanguageTransformTerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.language')),
                ('language_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.languageterm')),
            ],
            options={
                'unique_together': {('language', 'language_term')},
            },
        ),
    ]
