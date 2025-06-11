"""
Initial migration for the GPS application.
"""
from django.db import migrations, models
import django.contrib.gis.db.models.fields
import django.utils.timezone


class Migration(migrations.Migration):
    """Initial migration for GPS models."""
    
    initial = True
    
    dependencies = [
    ]
    
    operations = [
        migrations.CreateModel(
            name='GPSDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.BigIntegerField(unique=True, verbose_name='IMEI')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('protocol', models.CharField(choices=[('concox', 'Concox'), ('meiligao', 'Meiligao'), ('wialon', 'Wialon')], max_length=20, verbose_name='Protocol')),
                ('firmware_version', models.CharField(max_length=20, verbose_name='Firmware Version')),
                ('position', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='Position')),
                ('speed', models.FloatField(default=0.0, verbose_name='Speed')),
                ('course', models.FloatField(default=0.0, verbose_name='Course')),
                ('altitude', models.FloatField(default=0.0, verbose_name='Altitude')),
                ('odometer', models.FloatField(default=0.0, verbose_name='Odometer')),
                ('battery_level', models.FloatField(default=100.0, verbose_name='Battery Level')),
                ('signal_strength', models.IntegerField(default=0, verbose_name='Signal Strength')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('last_log', models.DateTimeField(blank=True, null=True, verbose_name='Last Log')),
                ('last_maintenance', models.DateTimeField(blank=True, null=True, verbose_name='Last Maintenance')),
                ('maintenance_interval', models.DurationField(blank=True, null=True, verbose_name='Maintenance Interval')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'GPS Device',
                'verbose_name_plural': 'GPS Devices',
                'ordering': ['-last_log'],
            },
        ),
        migrations.CreateModel(
            name='GPSLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='Position')),
                ('speed', models.FloatField(default=0.0, verbose_name='Speed')),
                ('course', models.FloatField(default=0.0, verbose_name='Course')),
                ('altitude', models.FloatField(default=0.0, verbose_name='Altitude')),
                ('satellites', models.IntegerField(default=0, verbose_name='Satellites')),
                ('accuracy', models.FloatField(default=0.0, verbose_name='Accuracy')),
                ('hdop', models.FloatField(default=0.0, verbose_name='HDOP')),
                ('pdop', models.FloatField(default=0.0, verbose_name='PDOP')),
                ('fix_quality', models.IntegerField(default=0, verbose_name='Fix Quality')),
                ('fix_type', models.IntegerField(default=0, verbose_name='Fix Type')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='gps.gpsdevice', verbose_name='Device')),
            ],
            options={
                'verbose_name': 'GPS Location',
                'verbose_name_plural': 'GPS Locations',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='GPSEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('TRACK', 'Track'), ('ALARM', 'Alarm'), ('STATUS', 'Status'), ('MAINTENANCE', 'Maintenance')], max_length=20, verbose_name='Type')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('position', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='Position')),
                ('speed', models.FloatField(blank=True, null=True, verbose_name='Speed')),
                ('course', models.FloatField(blank=True, null=True, verbose_name='Course')),
                ('altitude', models.FloatField(blank=True, null=True, verbose_name='Altitude')),
                ('odometer', models.FloatField(blank=True, null=True, verbose_name='Odometer')),
                ('raw_data', models.JSONField(blank=True, null=True, verbose_name='Raw Data')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='gps.gpsdevice', verbose_name='Device')),
            ],
            options={
                'verbose_name': 'GPS Event',
                'verbose_name_plural': 'GPS Events',
                'ordering': ['-timestamp'],
            },
        ),
    ] 