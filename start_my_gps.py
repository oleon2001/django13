#!/usr/bin/env python3
"""
Script completo para conectar tu celular como dispositivo GPS
IMEI: 352749380148144
"""
import os
import subprocess
import sys
import time
import threading

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - EXITOSO")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
        else:
            print(f"❌ {description} - ERROR")
            if result.stderr.strip():
                print(f"   {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - EXCEPCIÓN: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 INICIANDO CONEXIÓN GPS PARA TU CELULAR")
    print("📱 IMEI: 352749380148144")
    print("=" * 60)
    
    # Paso 1: Cambiar protocolo a Wialon
    print("\n📋 PASO 1: Cambiando protocolo a Wialon...")
    if not run_command("python3 cambiar_protocolo.py", "Cambio de protocolo"):
        print("❌ No se pudo cambiar el protocolo. Continuando de todas formas...")
    
    # Paso 2: Verificar puertos
    print("\n🔍 PASO 2: Verificando puertos GPS...")
    run_command("netstat -tlnp | grep 20332 || echo 'Puerto 20332 libre - Listo para usar'", "Verificación de puerto")
    
    # Paso 3: Iniciar servidor GPS
    print("\n🟢 PASO 3: Iniciando servidor GPS...")
    print("   El servidor se iniciará en el puerto 20332")
    print("   Tu celular debe conectarse a este puerto")
    print()
    print("🔧 CONFIGURACIÓN PARA TU CELULAR:")
    print("   • Host/IP: localhost (o la IP de este servidor)")
    print("   • Puerto: 20332 (Wialon - cambiado desde Concox)")
    print("   • IMEI: 352749380148144")
    print("   • Protocolo: Wialon (recomendado para celulares)")
    print()
    print("📱 OPCIONES PARA CONECTAR:")
    print("   1. Aplicación web: http://localhost/mobile_gps_app/")
    print("   2. Cliente Python: python mobile_gps_app/gps_client.py")
    print("   3. App Termux en Android (ver mobile_gps_app/TERMUX_SETUP.md)")
    print()
    print("🚨 IMPORTANTE: ¡Deja este servidor corriendo y conecta tu celular!")
    print("=" * 60)
    
    # Iniciar servidor GPS
    try:
        os.system("python3 start_gps_server.py")
    except KeyboardInterrupt:
        print("\n🛑 Servidor GPS detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en servidor GPS: {e}")
        print("💡 Intenta ejecutar manualmente: python3 start_gps_server.py")

if __name__ == "__main__":
    main() 