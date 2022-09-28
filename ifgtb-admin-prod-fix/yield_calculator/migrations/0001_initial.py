# Generated by Django 3.1.6 on 2021-11-29 13:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0039_auto_20210907_1331'),
    ]

    operations = [
        migrations.CreateModel(
            name='CloneYieldEstimationTypeMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.clone')),
            ],
        ),
        migrations.CreateModel(
            name='UnitCv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='YieldEstimationTypeCv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='YieldFormulaCv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('formula', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='YieldFormula',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('constant', models.CharField(max_length=100)),
                ('constant_value', models.DecimalField(decimal_places=3, max_digits=10)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('clone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yield_calculator.cloneyieldestimationtypemap')),
                ('user_created', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('yield_estimation_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yield_calculator.yieldestimationtypecv')),
                ('yield_formula', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yield_calculator.yieldformulacv')),
            ],
        ),
        migrations.CreateModel(
            name='PlantationYield',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('population', models.PositiveIntegerField()),
                ('number_of_trees_to_sample', models.PositiveIntegerField()),
                ('estimated_yield', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('actual_yield', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('estimated_on', models.DateTimeField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('clone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yield_calculator.cloneyieldestimationtypemap')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('yield_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yield_calculator.unitcv')),
            ],
        ),
        migrations.CreateModel(
            name='PlantationSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nth_sample', models.PositiveIntegerField()),
                ('girth', models.DecimalField(decimal_places=3, max_digits=10)),
                ('calculated_yield', models.DecimalField(decimal_places=3, max_digits=10)),
                ('formula_used', models.CharField(max_length=100)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('girth_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yield_calculator.unitcv')),
                ('plantation_yield', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yield_calculator.plantationyield')),
            ],
        ),
        migrations.CreateModel(
            name='IndividualYield',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('population', models.PositiveIntegerField(default=1)),
                ('girth', models.DecimalField(decimal_places=3, max_digits=10)),
                ('estimated_yield', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('actual_yield', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('estimated_on', models.DateTimeField()),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('clone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yield_calculator.cloneyieldestimationtypemap')),
                ('girth_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='girth_unit', to='yield_calculator.unitcv')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('yield_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yield_unit', to='yield_calculator.unitcv')),
            ],
        ),
        migrations.AddField(
            model_name='cloneyieldestimationtypemap',
            name='yield_estimation_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yield_calculator.yieldestimationtypecv'),
        ),
    ]