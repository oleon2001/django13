#!/usr/bin/env python3
"""
Script de verificación de salud del sistema Falkon GPS.
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

def check_system_health():
    """Verificar salud general del sistema."""
    print("🏥 VERIFICACIÓN DE SALUD DEL SISTEMA FALKON GPS")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = []
    
    # 1. Verificar modelos
    try:
        from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
        device_count = GPSDevice.objects.count()
        location_count = GPSLocation.objects.count()
        event_count = GPSEvent.objects.count()
        
        print(f"✅ Modelos GPS funcionando:")
        print(f"   - Dispositivos: {device_count}")
        print(f"   - Ubicaciones: {location_count}")
        print(f"   - Eventos: {event_count}")
        checks.append(True)
        
    except Exception as e:
        print(f"❌ Error en modelos GPS: {e}")
        checks.append(False)
    
    # 2. Verificar base de datos
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
            print(f"✅ Base de datos: {db_version}")
        checks.append(True)
        
    except Exception as e:
        print(f"❌ Error base de datos: {e}")
        checks.append(False)
    
    # 3. Verificar Redis (si está configurado)
    try:
        import redis
        from django.conf import settings
        
        if hasattr(settings, 'REDIS_URL'):
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            print("✅ Redis funcionando")
        else:
            print("⚠️  Redis no configurado")
        checks.append(True)
        
    except Exception as e:
        print(f"❌ Error Redis: {e}")
        checks.append(False)
    
    # 4. Verificar servidores GPS
    try:
        from skyguard.apps.gps.servers.server_manager import GPSServerManager
        manager = GPSServerManager()
        stats = manager.get_statistics()
        
        print(f"✅ Estadísticas GPS:")
        print(f"   - Dispositivos totales: {stats.get('total_devices', 0)}")
        print(f"   - Dispositivos activos: {stats.get('active_devices', 0)}")
        checks.append(True)
        
    except Exception as e:
        print(f"❌ Error servidores GPS: {e}")
        checks.append(False)
    
    # 5. Verificar migraciones
    try:
        from django.core.management import execute_from_command_line
        import io
        import contextlib
        
        # Capturar salida del comando showmigrations
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
        
        output = f.getvalue()
        if '[X]' in output and '[ ]' not in output:
            print("✅ Todas las migraciones aplicadas")
            checks.append(True)
        else:
            print("⚠️  Migraciones pendientes encontradas")
            checks.append(False)
            
    except Exception as e:
        print(f"❌ Error verificando migraciones: {e}")
        checks.append(False)
    
    # Resumen
    print()
    print("=" * 60)
    success_rate = sum(checks) / len(checks) * 100
    print(f"📊 RESUMEN: {sum(checks)}/{len(checks)} verificaciones exitosas ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Sistema en buen estado")
    elif success_rate >= 60:
        print("⚠️  Sistema funcional con algunos problemas")
    else:
        print("🚨 Sistema requiere atención urgente")
    
    return success_rate >= 80

if __name__ == "__main__":
    check_system_health()
