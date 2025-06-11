"""
Custom migration to convert raw_data from JSONField (jsonb) to BinaryField (bytea) in PostgreSQL.
"""
from django.db import migrations, connection

def jsonb_to_bytea(apps, schema_editor):
    with connection.cursor() as cursor:
        # 1. Add a new temporary column
        cursor.execute('ALTER TABLE gps_gpsevent ADD COLUMN raw_data_bin bytea;')
        # 2. Copy and convert data from jsonb to bytea
        cursor.execute("UPDATE gps_gpsevent SET raw_data_bin = convert_to(raw_data::text, 'UTF8') WHERE raw_data IS NOT NULL;")
        # 3. Drop the old column
        cursor.execute('ALTER TABLE gps_gpsevent DROP COLUMN raw_data;')
        # 4. Rename the new column
        cursor.execute('ALTER TABLE gps_gpsevent RENAME COLUMN raw_data_bin TO raw_data;')

def reverse_bytea_to_jsonb(apps, schema_editor):
    with connection.cursor() as cursor:
        # 1. Add a new temporary column
        cursor.execute('ALTER TABLE gps_gpsevent ADD COLUMN raw_data_jsonb jsonb;')
        # 2. Copy and convert data from bytea to jsonb
        cursor.execute("UPDATE gps_gpsevent SET raw_data_jsonb = raw_data::text::jsonb WHERE raw_data IS NOT NULL;")
        # 3. Drop the old column
        cursor.execute('ALTER TABLE gps_gpsevent DROP COLUMN raw_data;')
        # 4. Rename the new column
        cursor.execute('ALTER TABLE gps_gpsevent RENAME COLUMN raw_data_jsonb TO raw_data;')

class Migration(migrations.Migration):
    dependencies = [
        ('gps', '0003_merge_20250606_2029'),
    ]

    operations = [
        migrations.RunPython(jsonb_to_bytea, reverse_bytea_to_jsonb),
    ] 