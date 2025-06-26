#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de Termux API.
Ejecuta este script para identificar y solucionar problemas comunes.
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def run_command(cmd, capture_output=True, text=True):
    """Ejecutar comando de shell y capturar salida."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=text, timeout=10)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def check_termux_installation():
    """Verificar instalación básica de Termux."""
    print("🔍 1. Verificando instalación de Termux...")
    
    # Verificar si estamos en Termux
    if not os.path.exists('/data/data/com.termux'):
        print("❌ No se detectó instalación de Termux")
        print("   Instala Termux desde F-Droid o GitHub")
        return False
    
    print("✅ Termux detectado")
    
    # Verificar paquetes básicos
    code, out, err = run_command("which python")
    if code == 0:
        print("✅ Python instalado")
    else:
        print("❌ Python no encontrado")
        print("   Ejecuta: pkg install python")
    
    return True

def check_termux_api_package():
    """Verificar paquete termux-api."""
    print("\n🔍 2. Verificando paquete termux-api...")
    
    code, out, err = run_command("pkg list-installed | grep termux-api")
    if code == 0 and "termux-api" in out:
        print("✅ Paquete termux-api instalado")
    else:
        print("❌ Paquete termux-api no encontrado")
        print("   Ejecuta: pkg install termux-api")
        return False
    
    # Verificar comandos específicos
    commands = ["termux-location", "termux-info", "termux-api-help"]
    for cmd in commands:
        code, out, err = run_command(f"which {cmd}")
        if code == 0:
            print(f"✅ {cmd} disponible")
        else:
            print(f"❌ {cmd} no encontrado")
    
    return True

def check_termux_api_app():
    """Verificar aplicación Termux:API."""
    print("\n🔍 3. Verificando aplicación Termux:API...")
    
    code, out, err = run_command("pm list packages | grep com.termux.api")
    if code == 0 and "com.termux.api" in out:
        print("✅ Aplicación Termux:API instalada")
    else:
        print("❌ Aplicación Termux:API no encontrada")
        print("   Instala Termux:API desde F-Droid o GitHub")
        return False
    
    return True

def check_permissions():
    """Verificar permisos."""
    print("\n🔍 4. Verificando permisos...")
    
    # Intentar acceder a ubicación
    code, out, err = run_command("termux-location -r once", capture_output=True)
    
    if code == 0:
        try:
            location_data = json.loads(out)
            if 'latitude' in location_data and 'longitude' in location_data:
                print("✅ Acceso a ubicación funcionando")
                print(f"   Ubicación: {location_data['latitude']:.4f}, {location_data['longitude']:.4f}")
                return True
        except json.JSONDecodeError:
            pass
    
    print("❌ No se puede acceder a ubicación")
    print("   Revisa permisos en Configuración de Android")
    print("   Configuración → Apps → Termux → Permisos → Ubicación")
    print("   Configuración → Apps → Termux:API → Permisos (todos)")
    
    return False

def check_storage_access():
    """Verificar acceso al almacenamiento."""
    print("\n🔍 5. Verificando acceso al almacenamiento...")
    
    if os.path.exists('/storage/emulated/0'):
        print("✅ Acceso al almacenamiento funcionando")
        return True
    else:
        print("❌ Sin acceso al almacenamiento")
        print("   Ejecuta: termux-setup-storage")
        return False

def check_network():
    """Verificar conectividad de red."""
    print("\n🔍 6. Verificando conectividad de red...")
    
    code, out, err = run_command("ping -c 1 8.8.8.8")
    if code == 0:
        print("✅ Conectividad de red funcionando")
        return True
    else:
        print("❌ Sin conectividad de red")
        return False

def test_location_providers():
    """Probar diferentes proveedores de ubicación."""
    print("\n🔍 7. Probando proveedores de ubicación...")
    
    providers = ["gps", "network", "passive"]
    working_providers = []
    
    for provider in providers:
        print(f"   Probando {provider}...")
        code, out, err = run_command(f"termux-location -p {provider} -r once")
        
        if code == 0:
            try:
                location_data = json.loads(out)
                if 'latitude' in location_data:
                    print(f"   ✅ {provider} funcionando")
                    working_providers.append(provider)
                else:
                    print(f"   ❌ {provider} sin datos")
            except json.JSONDecodeError:
                print(f"   ❌ {provider} respuesta inválida")
        else:
            print(f"   ❌ {provider} error: {err[:50]}")
    
    if working_providers:
        print(f"✅ Proveedores funcionando: {', '.join(working_providers)}")
        return True
    else:
        print("❌ Ningún proveedor de ubicación funciona")
        return False

def check_python_dependencies():
    """Verificar dependencias de Python."""
    print("\n🔍 8. Verificando dependencias de Python...")
    
    dependencies = ["requests", "json", "socket", "datetime"]
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} disponible")
        except ImportError:
            print(f"❌ {dep} no encontrado")
            missing.append(dep)
    
    if missing:
        print(f"   Instala: pip install {' '.join(missing)}")
        return False
    
    return True

def generate_diagnostic_report():
    """Generar reporte de diagnóstico."""
    print("\n📊 Generando reporte de diagnóstico...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {},
        "termux_info": {},
        "errors": [],
        "recommendations": []
    }
    
    # Información del sistema
    code, out, err = run_command("termux-info")
    if code == 0:
        report["termux_info"] = out
    
    # Versión de Android
    code, out, err = run_command("getprop ro.build.version.release")
    if code == 0:
        report["system_info"]["android_version"] = out.strip()
    
    # Espacio disponible
    code, out, err = run_command("df -h /data")
    if code == 0:
        report["system_info"]["storage"] = out
    
    # Guardar reporte
    try:
        with open("termux_diagnostic_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print("✅ Reporte guardado en: termux_diagnostic_report.json")
    except Exception as e:
        print(f"❌ Error guardando reporte: {e}")

def provide_solutions():
    """Proporcionar soluciones comunes."""
    print("\n🔧 SOLUCIONES COMUNES:")
    print("=" * 50)
    
    print("\n1. Si termux-api no funciona:")
    print("   pkg uninstall termux-api")
    print("   pkg update")
    print("   pkg install termux-api")
    
    print("\n2. Si no hay permisos de ubicación:")
    print("   - Ve a Configuración de Android")
    print("   - Apps → Termux → Permisos → Ubicación → Permitir")
    print("   - Apps → Termux:API → Permisos → Permitir todos")
    
    print("\n3. Si no funciona el GPS:")
    print("   - Activa GPS en Configuración → Ubicación")
    print("   - Sal al exterior para mejor señal")
    print("   - Usa: termux-location -p network (Wi-Fi/datos)")
    
    print("\n4. Si falta Termux:API app:")
    print("   - Instala desde F-Droid: https://f-droid.org/packages/com.termux.api/")
    print("   - O GitHub: https://github.com/termux/termux-api/releases")
    
    print("\n5. Reiniciar servicios:")
    print("   - Reinicia Termux")
    print("   - Reinicia el dispositivo")
    print("   - Ejecuta: termux-reload-settings")

def main():
    """Función principal de diagnóstico."""
    print("🔧 DIAGNÓSTICO DE TERMUX API PARA FALKON GPS")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        check_termux_installation,
        check_termux_api_package,
        check_termux_api_app,
        check_permissions,
        check_storage_access,
        check_network,
        test_location_providers,
        check_python_dependencies
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Error en verificación: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN:")
    print(f"Verificaciones exitosas: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 ¡Todo está configurado correctamente!")
        print("   Tu Termux debería funcionar con Falkon GPS")
    else:
        print("⚠️  Algunos problemas encontrados")
        provide_solutions()
    
    generate_diagnostic_report()
    
    print(f"\n📝 Para más ayuda, revisa: TERMUX_SETUP.md")

if __name__ == "__main__":
    main() 