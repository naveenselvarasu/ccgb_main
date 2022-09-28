# Generated by Django 3.1.6 on 2021-02-05 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='industry',
            name='block',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='district',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='pincode',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='revenue_village',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='state',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='street',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='taluk',
        ),
        migrations.RemoveField(
            model_name='industry',
            name='village',
        ),
        migrations.RemoveField(
            model_name='industryofficial',
            name='industry',
        ),
        migrations.CreateModel(
            name='IndustryOffice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_head_office', models.BooleanField(default=False)),
                ('village', models.CharField(blank=True, max_length=100, null=True)),
                ('street', models.TextField(blank=True, null=True)),
                ('taluk', models.CharField(blank=True, max_length=100, null=True)),
                ('pincode', models.IntegerField(blank=True, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=7, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ('block', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.block')),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.district')),
                ('industry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.industry')),
                ('revenue_village', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.revenuevillage')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.state')),
            ],
        ),
        migrations.AddField(
            model_name='industryofficial',
            name='industry_office',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.industryoffice'),
            preserve_default=False,
        ),
    ]
