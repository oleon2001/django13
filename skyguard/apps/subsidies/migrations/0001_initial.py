# Generated migration for subsidies system
# Migrated from legacy django14 system to modern architecture

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('gps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Nombre')),
                ('middle', models.CharField(max_length=40, verbose_name='A. Paterno')),
                ('last', models.CharField(max_length=40, verbose_name='A. Materno')),
                ('birth', models.DateField(verbose_name='F. de nacimiento')),
                ('cstatus', models.CharField(choices=[('SOL', 'Soltero'), ('CAS', 'Casado'), ('VIU', 'Viudo'), ('DIV', 'Divorciado')], max_length=40, verbose_name='Estado Civil')),
                ('payroll', models.CharField(max_length=40, verbose_name='Nómina')),
                ('socials', models.CharField(max_length=40, verbose_name='Seguro social')),
                ('taxid', models.CharField(max_length=40, verbose_name='RFC')),
                ('license', models.CharField(blank=True, max_length=40, null=True, verbose_name='Licencia')),
                ('lic_exp', models.DateField(blank=True, null=True, verbose_name='Vencimiento')),
                ('address', models.TextField(verbose_name='Dirección')),
                ('phone', models.CharField(max_length=40, verbose_name='Teléfono')),
                ('phone1', models.CharField(blank=True, max_length=40, null=True, verbose_name='Teléfono 1')),
                ('phone2', models.CharField(blank=True, max_length=40, null=True, verbose_name='Teléfono 2')),
                ('active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'Chofer',
                'verbose_name_plural': 'Choferes',
                'ordering': ('middle', 'last', 'name'),
            },
        ),
        migrations.CreateModel(
            name='DailyLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route', models.IntegerField(blank=True, null=True, verbose_name='Ruta')),
                ('start', models.DateTimeField(verbose_name='Inicio')),
                ('stop', models.DateTimeField(verbose_name='Fin')),
                ('regular', models.IntegerField(default=0, verbose_name='Ordinarias')),
                ('preferent', models.IntegerField(default=0, verbose_name='Preferentes')),
                ('total', models.IntegerField(default=0, verbose_name='Total de pasajeros')),
                ('due', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='A pagar')),
                ('payed', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Pagado')),
                ('difference', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Diferencia')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_logs', to='subsidies.driver')),
            ],
            options={
                'verbose_name': 'Registro',
                'verbose_name_plural': 'Registros',
                'ordering': ['-start'],
            },
        ),
        migrations.CreateModel(
            name='CashReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket1', models.IntegerField(verbose_name='Folio de Caseta')),
                ('ticket2', models.IntegerField(blank=True, null=True, verbose_name='Folio de Liquidación')),
                ('payed1', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='$ Vuelta 1')),
                ('payed2', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='$ Vuelta 2')),
                ('payed3', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='$ Vuelta 3')),
                ('payed4', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='$ Vuelta 4')),
                ('payed5', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='$ Vuelta 5')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_receipts', to='subsidies.driver')),
            ],
            options={
                'verbose_name': 'Recibo de efectivo',
                'verbose_name_plural': 'Recibos de efectivo',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TimeSheetCapture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='date')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('times', models.JSONField(default=list, verbose_name='times')),
                ('driver', models.CharField(blank=True, max_length=100, verbose_name='driver')),
                ('route', models.CharField(blank=True, max_length=50, verbose_name='route')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'Time Sheet Capture',
                'verbose_name_plural': 'Time Sheet Captures',
                'ordering': ['-date', 'name'],
                'unique_together': {('date', 'name')},
            },
        ),
        migrations.CreateModel(
            name='SubsidyRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('route_code', models.CharField(choices=[('A6', 'Ruta A6'), ('155', 'Ruta 155'), ('202', 'Ruta 202'), ('31', 'Ruta 31'), ('207E', 'Ruta 207E'), ('207P', 'Ruta 207P'), ('400S1', 'Ruta 400 Sector 1'), ('400S2', 'Ruta 400 Sector 2'), ('400S4H', 'Ruta 400 Sector 4 H'), ('400S4J', 'Ruta 400 Sector 4 J')], max_length=20, verbose_name='route code')),
                ('company', models.CharField(max_length=200, verbose_name='company')),
                ('branch', models.CharField(blank=True, max_length=200, verbose_name='branch')),
                ('flag', models.CharField(max_length=100, verbose_name='flag')),
                ('units', models.JSONField(default=list, verbose_name='units')),
                ('km', models.DecimalField(decimal_places=3, default=0, max_digits=8, verbose_name='kilometers')),
                ('frequency', models.IntegerField(default=0, verbose_name='frequency')),
                ('time_minutes', models.IntegerField(default=0, verbose_name='time in minutes')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'Subsidy Route',
                'verbose_name_plural': 'Subsidy Routes',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SubsidyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('daily', 'Daily Report'), ('weekly', 'Weekly Report'), ('monthly', 'Monthly Report'), ('timesheet', 'Time Sheet Report'), ('cash', 'Cash Report')], max_length=20, verbose_name='report type')),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(verbose_name='end date')),
                ('file_path', models.CharField(blank=True, max_length=500, verbose_name='file path')),
                ('report_data', models.JSONField(default=dict, verbose_name='report data')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('generated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subsidy_reports', to='auth.user')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='subsidies.subsidyroute')),
            ],
            options={
                'verbose_name': 'Subsidy Report',
                'verbose_name_plural': 'Subsidy Reports',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EconomicMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_name', models.CharField(max_length=100, unique=True, verbose_name='unit name')),
                ('economic_number', models.CharField(max_length=20, verbose_name='economic number')),
                ('route', models.CharField(blank=True, max_length=50, verbose_name='route')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'Economic Mapping',
                'verbose_name_plural': 'Economic Mappings',
                'ordering': ['unit_name'],
            },
        ),
    ] 