"""
Migration to transfer data from the old system to the new one.
"""
from django.db import migrations
import json
from datetime import datetime
from django.contrib.gis.geos import Point

def transfer_data_forward(apps, schema_editor):
    """Transfer data from old system to new system."""
    # Get the models
    OldGPSEvent = apps.get_model('gps', 'GPSEvent')
    NewGPSEvent = apps.get_model('gps', 'GPSEvent')
    
    # Transfer data
    for old_event in OldGPSEvent.objects.all():
        try:
            # Create new event
            new_event = NewGPSEvent(
                device=old_event.device,
                timestamp=old_event.timestamp,
                latitude=old_event.latitude,
                longitude=old_event.longitude,
                altitude=old_event.altitude,
                speed=old_event.speed,
                heading=old_event.heading,
                satellites=old_event.satellites,
                hdop=old_event.hdop,
                battery_level=old_event.battery_level,
                signal_strength=old_event.signal_strength,
                raw_data=old_event.raw_data,
                created_at=old_event.created_at,
                updated_at=old_event.updated_at
            )
            new_event.save()
                    
        except Exception as e:
            print(f"Error transferring event {old_event.id}: {str(e)}")
            continue

def transfer_data_backward(apps, schema_editor):
    """Reverse the data transfer."""
    # Get the models
    NewGPSEvent = apps.get_model('gps', 'GPSEvent')
    
    # Delete transferred data
    NewGPSEvent.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('gps', '0007_convert_raw_data'),
    ]

    operations = [
        migrations.RunPython(
            transfer_data_forward,
            transfer_data_backward,
        ),
    ] 