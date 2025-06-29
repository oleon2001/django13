#!/usr/bin/env python3
"""
Servidor GPS con integración completa a Django
Este servidor SÍ guarda los datos en la base de datos
"""
import os
import sys
import subprocess
import signal
import time
from datetime import datetime

# Configurar el entorno Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')

import django
django.setup()

def start_server():
    """Iniciar el servidor GPS con Django"""
    print("=" * 60)
    print("🚀 SERVIDOR GPS DJANGO - SkyGuard")
    print("💾 Este servidor SÍ guarda datos en la base de datos")
    print("=" * 60)
    
    try:
        # Usar el comando de Django para iniciar el servidor GPS real
        cmd = [sys.executable, 'manage.py', 'runserver_gps', '--servers=wialon']
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🟢 Iniciando servidor GPS Wialon...")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Puerto: 20332")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💾 Base de datos: Habilitada")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📱 Esperando dispositivos GPS...")
        print("-" * 60)
        
        # Ejecutar el servidor
        process = subprocess.Popen(cmd)
        
        # Esperar hasta que se detenga
        process.wait()
        
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Deteniendo servidor GPS...")
        if 'process' in locals():
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Servidor detenido")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    start_server() 