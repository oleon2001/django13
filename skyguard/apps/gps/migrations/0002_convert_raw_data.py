"""
Migration to convert raw_data from JSONField to BinaryField.
"""
import json
from django.db import migrations

def convert_raw_data_to_bytes(apps, schema_editor):
    GPSEvent = apps.get_model('gps', 'GPSEvent')
    for event in GPSEvent.objects.all():
        if event.raw_data:
            # Convert JSON to bytes
            event.raw_data = json.dumps(event.raw_data).encode('utf-8')
            event.save()

def convert_bytes_to_json(apps, schema_editor):
    GPSEvent = apps.get_model('gps', 'GPSEvent')
    for event in GPSEvent.objects.all():
        if event.raw_data:
            try:
                # Convert bytes back to JSON
                event.raw_data = json.loads(event.raw_data.decode('utf-8'))
                event.save()
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If conversion fails, set to None
                event.raw_data = None
                event.save()

class Migration(migrations.Migration):
    dependencies = [
        ('gps', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(convert_raw_data_to_bytes, convert_bytes_to_json),
    ] 