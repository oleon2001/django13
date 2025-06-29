#!/usr/bin/env python3
"""
Script de prueba rápida del sistema GPS completo
"""
import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(cmd, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Éxito")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Error")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def main():
    print("🚀 PRUEBA RÁPIDA DEL SISTEMA GPS")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Verificar dispositivo en BD
    run_command("python check_pc_device.py", "Verificando dispositivo en base de datos")
    
    # 2. Verificar servidor Django
    print("\n📝 INSTRUCCIONES:")
    print("1. Detén el servidor simple si está corriendo (Ctrl+C)")
    print("2. Ejecuta en una terminal: python start_django_gps_server.py")
    print("3. Ejecuta en otra terminal: python pc_gps_simulator.py")
    print("4. Verifica el dispositivo en: http://localhost:3000/dashboard")
    
    print("\n💡 COMANDOS RECOMENDADOS:")
    print("   Terminal 1: python manage.py runserver")
    print("   Terminal 2: python start_django_gps_server.py")
    print("   Terminal 3: python pc_gps_simulator.py")
    print("   Terminal 4: cd frontend && npm start")
    
    print("\n🔍 Para verificar el estado del dispositivo:")
    print("   python check_pc_device.py")
    
    print("\n⚠️ IMPORTANTE:")
    print("   - El servidor simple (start_gps_server.py) NO guarda en BD")
    print("   - Usa start_django_gps_server.py para guardar datos")
    print("   - O ejecuta: python manage.py runserver_gps --servers=wialon")

if __name__ == "__main__":
    main() 