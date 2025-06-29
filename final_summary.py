#!/usr/bin/env python3
import os, sys, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

def safe_count(model_class):
    try:
        return model_class.objects.count()
    except Exception:
        return "N/A"

print("🎯 RESUMEN FINAL DE MIGRACIÓN - SKYGUARD GPS SYSTEM")
print("="*60)

try:
    from skyguard.gps.tracker.models import SGAvl, SGHarness
    from skyguard.apps.gps.models import GPSDevice, DeviceHarness
    
    legacy_devices = safe_count(SGAvl)
    new_devices = safe_count(GPSDevice)
    legacy_harness = safe_count(SGHarness)
    new_harness = safe_count(DeviceHarness)
    
    print(f"📡 DISPOSITIVOS GPS: Legacy {legacy_devices} → Nuevo {new_devices}")
    print(f"⚙️ CONFIGURACIONES: Legacy {legacy_harness} → Nuevo {new_harness}")
    
    if legacy_devices == new_devices and legacy_harness == new_harness:
        print("✅ MIGRACIÓN EXITOSA - Sistema listo para producción")
    else:
        print("⚠️ MIGRACIÓN INCOMPLETA - Revisar datos")
        
except ImportError as e:
    print(f"❌ Error: {e}")
