#!/usr/bin/env python3
"""
Script de inicio rápido para PC GPS Simulator
Generado automáticamente por setup_pc_gps.py
"""

import subprocess
import sys
import os

def main():
    print("🖥️  Iniciando PC GPS Simulator...")
    print("📱 Dispositivo: PC-DESKTOP-5V9VDBR")
    print("🆔 IMEI: PC985982AA71FD")
    print("🌐 Servidor: localhost:20332")
    print()
    
    try:
        # Ejecutar simulador GPS
        subprocess.run([sys.executable, "pc_gps_simulator.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Simulador detenido por el usuario")
    except FileNotFoundError:
        print("❌ No se encontró pc_gps_simulator.py")
        print("💡 Ejecuta primero: python setup_pc_gps.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
