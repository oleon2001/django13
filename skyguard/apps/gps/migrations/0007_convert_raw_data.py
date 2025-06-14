"""
Migration to convert raw_data from bytea to text and then to jsonb.
"""
from django.db import migrations
import json
from django.db import models

def convert_raw_data_forward(apps, schema_editor):
    """Convert raw_data from bytea to text."""
    GPSEvent = apps.get_model('gps', 'GPSEvent')
    for event in GPSEvent.objects.all():
        if event.raw_data:
            try:
                # Convertir los datos binarios a texto
                if isinstance(event.raw_data, bytes):
                    text_data = event.raw_data.decode('utf-8')
                    # Intentar parsear como JSON para validar
                    json.loads(text_data)
                    event.raw_data = text_data
                else:
                    # Si ya es texto, asegurarse de que es JSON válido
                    json.loads(event.raw_data)
            except (UnicodeDecodeError, json.JSONDecodeError):
                # Si hay error, establecer como None
                event.raw_data = None
        event.save()

def convert_raw_data_backward(apps, schema_editor):
    """Convert raw_data from text to bytea."""
    GPSEvent = apps.get_model('gps', 'GPSEvent')
    for event in GPSEvent.objects.all():
        if event.raw_data:
            try:
                # Convertir el texto a bytes
                event.raw_data = event.raw_data.encode('utf-8')
            except (UnicodeEncodeError, AttributeError):
                event.raw_data = None
        event.save()

class Migration(migrations.Migration):
    dependencies = [
        ('gps', '0006_simcard_alter_gpsdevice_options_and_more'),
    ]

    operations = [
        # Primero convertimos el campo a TextField
        migrations.AlterField(
            model_name='gpsevent',
            name='raw_data',
            field=models.TextField(null=True, blank=True),
        ),
        # Luego ejecutamos la migración de datos
        migrations.RunPython(
            convert_raw_data_forward,
            convert_raw_data_backward,
        ),
        # Finalmente convertimos a JSONField
        migrations.AlterField(
            model_name='gpsevent',
            name='raw_data',
            field=models.JSONField(null=True, blank=True),
        ),
    ] 