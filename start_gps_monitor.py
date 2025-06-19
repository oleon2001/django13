#!/usr/bin/env python
"""
Script de inicio rápido para el monitor de dispositivos GPS.
Ejecuta verificación cada minuto para detectar dispositivos offline.
"""

import os
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description='Iniciar monitor de dispositivos GPS')
    parser.add_argument('--timeout', type=int, default=1, help='Timeout en minutos (default: 1)')
    parser.add_argument('--quiet', action='store_true', help='Modo silencioso - solo cambios importantes')
    parser.add_argument('--test', action='store_true', help='Ejecutar prueba del sistema completo')
    
    args = parser.parse_args()
    
    print("🚀 Monitor de Dispositivos GPS - Verificación cada minuto")
    print("=" * 60)
    
    if args.test:
        print("🧪 Ejecutando prueba del sistema completo...")
        try:
            subprocess.run([sys.executable, 'test_device_offline_system.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en la prueba: {e}")
            return 1
        except FileNotFoundError:
            print("❌ No se encontró test_device_offline_system.py")
            return 1
        return 0
    
    # Verificar que Django esté disponible
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
        django.setup()
    except ImportError:
        print("❌ Django no está disponible. Asegúrate de estar en el entorno virtual correcto.")
        return 1
    except Exception as e:
        print(f"❌ Error configurando Django: {e}")
        return 1
    
    # Construir comando
    cmd = [sys.executable, 'manage.py', 'quick_device_monitor', '--timeout', str(args.timeout)]
    if args.quiet:
        cmd.append('--quiet')
    
    print(f"⚙️  Configuración:")
    print(f"   - Timeout: {args.timeout} minutos")
    print(f"   - Modo: {'Silencioso' if args.quiet else 'Verbose'}")
    print(f"   - Verificación: Cada minuto")
    print()
    print("💡 Presiona Ctrl+C para detener el monitor")
    print("=" * 60)
    
    try:
        # Ejecutar el monitor
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n✅ Monitor detenido por el usuario")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error ejecutando el monitor: {e}")
        return 1
    except FileNotFoundError:
        print("❌ No se encontró manage.py. Asegúrate de estar en el directorio correcto.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 