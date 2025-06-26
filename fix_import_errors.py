#!/usr/bin/env python3
"""
Script para arreglar errores de importación y validar el sistema Falkon GPS.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

def fix_server_manager_indentation():
    """Arreglar problemas de indentación en server_manager.py."""
    print("🔧 Arreglando server_manager.py...")
    
    file_path = "skyguard/apps/gps/servers/server_manager.py"
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Arreglar la línea con indentación incorrecta
        content = content.replace(
            "                             device_count = GPSDevice.objects.filter(protocol=server_name).count()",
            "            device_count = GPSDevice.objects.filter(protocol=server_name).count()"
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ server_manager.py arreglado")
        return True
        
    except Exception as e:
        print(f"❌ Error arreglando server_manager.py: {e}")
        return False

def validate_imports():
    """Validar que todas las importaciones funcionen correctamente."""
    print("\n🔍 Validando importaciones...")
    
    test_imports = [
        ("skyguard.apps.gps.models", "GPSDevice"),
        ("skyguard.apps.gps.models", "GPSLocation"),
        ("skyguard.apps.gps.models", "GPSEvent"),
        ("skyguard.apps.monitoring.models", "DeviceStatus"),
        ("skyguard.apps.tracking.models.base", "Alert"),
        ("skyguard.apps.tracking.models.session", "UDPSession"),
    ]
    
    success_count = 0
    for module_name, class_name in test_imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name}.{class_name}: {e}")
        except AttributeError as e:
            print(f"❌ {module_name}.{class_name}: {e}")
    
    print(f"\n📊 Importaciones exitosas: {success_count}/{len(test_imports)}")
    return success_count == len(test_imports)

def test_database_connection():
    """Probar conexión a la base de datos."""
    print("\n🔍 Probando conexión a la base de datos...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Conexión a la base de datos exitosa")
                return True
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        return False

def check_models():
    """Verificar que los modelos estén correctamente configurados."""
    print("\n🔍 Verificando modelos...")
    
    try:
        from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
        
        # Contar dispositivos
        device_count = GPSDevice.objects.count()
        print(f"✅ Dispositivos GPS: {device_count}")
        
        # Contar ubicaciones
        location_count = GPSLocation.objects.count()
        print(f"✅ Ubicaciones GPS: {location_count}")
        
        # Contar eventos
        event_count = GPSEvent.objects.count()
        print(f"✅ Eventos GPS: {event_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando modelos: {e}")
        return False

def fix_imap_ssl_config():
    """Arreglar configuración SSL de IMAP."""
    print("\n🔧 Arreglando configuración IMAP SSL...")
    
    try:
        # Crear una versión mejorada del script IMAP
        imap_fix_content = '''#!/usr/bin/env python3
"""
Script mejorado para IMAP con soporte SSL moderno.
"""
import ssl
import imaplib
from imapclient import IMAPClient

def create_secure_context():
    """Crear contexto SSL seguro."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

def test_imap_connection():
    """Probar conexión IMAP con SSL moderno."""
    HOST = 'imap.zoho.com'
    USERNAME = 'admin@ensambles.net'
    PASSWORD = 'l6moSa5mgCpg'
    
    try:
        # Método 1: IMAPClient con contexto SSL personalizado
        context = create_secure_context()
        server = IMAPClient(HOST, use_uid=True, ssl=True, ssl_context=context)
        server.login(USERNAME, PASSWORD)
        
        select_info = server.select_folder('INBOX')
        print(f'✅ Conexión IMAP exitosa: {select_info["EXISTS"]} mensajes en INBOX')
        server.logout()
        return True
        
    except Exception as e:
        print(f"❌ Error conexión IMAP: {e}")
        
        try:
            # Método 2: imaplib directo
            context = create_secure_context()
            mail = imaplib.IMAP4_SSL(HOST, 993, ssl_context=context)
            mail.login(USERNAME, PASSWORD)
            mail.select('inbox')
            
            typ, data = mail.search(None, 'ALL')
            print(f'✅ Conexión IMAP alternativa exitosa: {len(data[0].split())} mensajes')
            mail.close()
            mail.logout()
            return True
            
        except Exception as e2:
            print(f"❌ Error conexión IMAP alternativa: {e2}")
            return False

if __name__ == "__main__":
    test_imap_connection()
'''
        
        with open("skyguard/imap_fixed.py", "w") as f:
            f.write(imap_fix_content)
        
        print("✅ Script IMAP mejorado creado: skyguard/imap_fixed.py")
        return True
        
    except Exception as e:
        print(f"❌ Error creando script IMAP: {e}")
        return False

def create_system_health_check():
    """Crear script de verificación de salud del sistema."""
    print("\n🔧 Creando script de verificación de salud...")
    
    health_check_content = '''#!/usr/bin/env python3
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
'''
    
    try:
        with open("system_health_check.py", "w") as f:
            f.write(health_check_content)
        
        print("✅ Script de salud creado: system_health_check.py")
        return True
        
    except Exception as e:
        print(f"❌ Error creando script de salud: {e}")
        return False

def main():
    """Función principal."""
    print("🔧 REPARADOR DE ERRORES FALKON GPS")
    print("=" * 50)
    
    repairs = [
        ("Arreglar server_manager.py", fix_server_manager_indentation),
        ("Validar importaciones", validate_imports),
        ("Probar base de datos", test_database_connection),
        ("Verificar modelos", check_models),
        ("Arreglar IMAP SSL", fix_imap_ssl_config),
        ("Crear verificador de salud", create_system_health_check),
    ]
    
    results = []
    for description, repair_func in repairs:
        print(f"\n🔄 {description}...")
        try:
            result = repair_func()
            results.append(result)
            if result:
                print(f"✅ {description} completado")
            else:
                print(f"⚠️  {description} con problemas")
        except Exception as e:
            print(f"❌ Error en {description}: {e}")
            results.append(False)
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE REPARACIONES:")
    success_count = sum(results)
    print(f"Exitosas: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("🎉 ¡Todos los problemas han sido reparados!")
        print("\n📝 Próximos pasos:")
        print("1. Ejecuta: python system_health_check.py")
        print("2. Ejecuta: python manage.py runserver")
        print("3. Prueba la aplicación web")
    else:
        print("⚠️  Algunos problemas persisten")
        print("\n🔧 Soluciones manuales requeridas:")
        print("1. Revisa los errores mostrados arriba")
        print("2. Ejecuta migraciones: python manage.py migrate")
        print("3. Verifica configuración de base de datos")

if __name__ == "__main__":
    main() 