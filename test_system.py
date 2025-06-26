#!/usr/bin/env python3
"""
Script de prueba del sistema Falkon GPS.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

def test_basic_functionality():
    """Probar funcionalidad básica del sistema."""
    print("🧪 PROBANDO SISTEMA FALKON GPS")
    print("=" * 50)
    
    try:
        # 1. Probar importaciones
        print("🔍 1. Probando importaciones...")
        from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
        from skyguard.apps.gps.servers.server_manager import GPSServerManager
        print("✅ Importaciones exitosas")
        
        # 2. Probar base de datos
        print("\n🔍 2. Probando base de datos...")
        device_count = GPSDevice.objects.count()
        location_count = GPSLocation.objects.count()
        event_count = GPSEvent.objects.count()
        print(f"✅ Base de datos funcionando:")
        print(f"   - Dispositivos: {device_count}")
        print(f"   - Ubicaciones: {location_count}")
        print(f"   - Eventos: {event_count}")
        
        # 3. Probar GPS Server Manager
        print("\n🔍 3. Probando GPS Server Manager...")
        manager = GPSServerManager()
        stats = manager.get_statistics()
        print("✅ GPS Server Manager funcionando")
        print(f"   - Servidores configurados: {len(stats['servers'])}")
        for server_name, server_stats in stats['servers'].items():
            print(f"   - {server_name}: Puerto {server_stats['port']} ({server_stats['protocol']})")
        
        # 4. Probar estado de servidores
        print("\n🔍 4. Probando estado de servidores...")
        status = manager.get_server_status()
        print("✅ Estado de servidores obtenido:")
        for server_name, server_status in status.items():
            running = "🟢 Corriendo" if server_status['running'] else "🔴 Detenido"
            print(f"   - {server_name}: {running} (Puerto: {server_status['port']})")
        
        # 5. Probar frontend (verificar archivos)
        print("\n🔍 5. Verificando frontend...")
        frontend_files = [
            "frontend/package.json",
            "frontend/src/App.tsx",
            "frontend/src/components/Navbar.tsx"
        ]
        
        missing_files = []
        for file_path in frontend_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if not missing_files:
            print("✅ Archivos del frontend encontrados")
        else:
            print(f"⚠️  Archivos faltantes: {missing_files}")
        
        # 6. Verificar mobile app
        print("\n🔍 6. Verificando mobile app...")
        mobile_files = [
            "mobile_gps_app/gps_client.py",
            "mobile_gps_app/gps_config.json",
            "mobile_gps_app/index.html"
        ]
        
        missing_mobile = []
        for file_path in mobile_files:
            if not os.path.exists(file_path):
                missing_mobile.append(file_path)
        
        if not missing_mobile:
            print("✅ Archivos de mobile app encontrados")
        else:
            print(f"⚠️  Archivos móviles faltantes: {missing_mobile}")
        
        print("\n" + "=" * 50)
        print("🎉 SISTEMA FALKON GPS FUNCIONANDO CORRECTAMENTE")
        print("\n📝 Próximos pasos:")
        print("1. Iniciar servidores GPS: python3 manage.py runserver_gps")
        print("2. Iniciar aplicación web: python3 manage.py runserver")
        print("3. Abrir frontend: cd frontend && npm start")
        print("4. Probar mobile app: cd mobile_gps_app && python3 gps_client.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_system_info():
    """Mostrar información del sistema."""
    print("\n📊 INFORMACIÓN DEL SISTEMA:")
    print("-" * 30)
    
    try:
        from django.conf import settings
        print(f"Django Settings: {settings.SETTINGS_MODULE}")
        
        # Mostrar base de datos configurada
        db_config = settings.DATABASES['default']
        print(f"Base de datos: {db_config['ENGINE']}")
        print(f"DB Host: {db_config.get('HOST', 'localhost')}")
        print(f"DB Name: {db_config.get('NAME', 'N/A')}")
        
    except Exception as e:
        print(f"Error obteniendo configuración: {e}")

if __name__ == "__main__":
    success = test_basic_functionality()
    show_system_info()
    
    if success:
        print("\n🚀 ¡Sistema listo para usar!")
        sys.exit(0)
    else:
        print("\n🚨 Sistema requiere atención")
        sys.exit(1) 