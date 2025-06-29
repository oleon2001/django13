#!/usr/bin/env python3
"""
Script de configuración automática para PC como dispositivo GPS
Registra el PC en la base de datos y configura todos los servicios necesarios
"""

import os
import sys
import json
import platform
import socket
import subprocess
import django
from datetime import datetime

# Configurar el entorno de Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
django.setup()

# Importar después de configurar Django
from skyguard.apps.gps.models.device import GPSDevice
from django.contrib.auth.models import User

class PCGPSSetup:
    """Configurador automático para PC como dispositivo GPS."""
    
    def __init__(self):
        """Inicializar configurador."""
        self.pc_info = self.get_pc_info()
        self.config = self.generate_config()
        
    def get_pc_info(self) -> dict:
        """Obtener información del PC."""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except:
            hostname = platform.node()
            local_ip = "127.0.0.1"
        
        return {
            'hostname': hostname,
            'platform': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'local_ip': local_ip,
            'python_version': platform.python_version(),
            'user': os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        }
    
    def generate_config(self) -> dict:
        """Generar configuración para el PC."""
        # Generar IMEI único basado en información del PC
        import hashlib
        pc_signature = f"{self.pc_info['hostname']}-{self.pc_info['machine']}-{self.pc_info['user']}"
        hash_obj = hashlib.md5(pc_signature.encode())
        imei_suffix = hash_obj.hexdigest()[:12]
        imei = f"PC{imei_suffix.upper()}"
        
        return {
            "host": "localhost",
            "port": 20332,
            "imei": imei,
            "password": "123456",
            "interval": 15,
            "protocol": "wialon",
            "device_name": f"PC-{self.pc_info['hostname']}",
            "auto_register": True,
            "use_real_location": True,
            "fallback_to_mock": True,
            "debug": True,
            "pc_info": self.pc_info
        }
    
    def check_dependencies(self) -> bool:
        """Verificar dependencias necesarias."""
        print("🔍 Verificando dependencias...")
        
        required_packages = ['requests', 'django']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")
        
        if missing_packages:
            print(f"\n📦 Instalando paquetes faltantes: {', '.join(missing_packages)}")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install'
                ] + missing_packages)
                print("✅ Paquetes instalados correctamente")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Error instalando paquetes: {e}")
                return False
        
        return True
    
    def register_device_in_database(self) -> bool:
        """Registrar el PC como dispositivo GPS en la base de datos."""
        print("📝 Registrando PC como dispositivo GPS...")
        
        try:
            # Buscar o crear usuario administrador
            user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@skyguard.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                user.set_password('admin123')
                user.save()
                print("   ✅ Usuario administrador creado")
            
            # Registrar dispositivo PC
            device, created = GPSDevice.objects.get_or_create(
                imei=self.config['imei'],
                defaults={
                    'name': self.config['device_name'],
                    'owner': user,
                    'protocol': self.config['protocol'],
                    'connection_status': 'OFFLINE',
                    'is_active': True,
                    'route': 99,  # Ruta especial para PCs
                    'economico': 9999,
                    'model': 99,  # Modelo especial para PC
                    'software_version': '1.0-PC',
                    'current_ip': self.pc_info['local_ip'],
                    'current_port': self.config['port']
                }
            )
            
            if created:
                print(f"   ✅ Dispositivo PC registrado:")
                print(f"      • IMEI: {device.imei}")
                print(f"      • Nombre: {device.name}")
                print(f"      • Propietario: {device.owner.username}")
            else:
                print(f"   ℹ️ Dispositivo PC ya existía:")
                print(f"      • IMEI: {device.imei}")
                print(f"      • Nombre: {device.name}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error registrando dispositivo: {e}")
            return False
    
    def create_config_file(self) -> bool:
        """Crear archivo de configuración."""
        print("📄 Creando archivo de configuración...")
        
        try:
            config_file = "pc_gps_config.json"
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            print(f"   ✅ Archivo creado: {config_file}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error creando archivo: {e}")
            return False
    
    def test_server_connection(self) -> bool:
        """Probar conexión al servidor GPS."""
        print("🔌 Probando conexión al servidor GPS...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.config['host'], self.config['port']))
            sock.close()
            
            if result == 0:
                print("   ✅ Servidor GPS disponible")
                return True
            else:
                print("   ⚠️ Servidor GPS no disponible")
                print("   💡 Asegúrate de ejecutar: python start_gps_server.py")
                return False
                
        except Exception as e:
            print(f"   ❌ Error probando conexión: {e}")
            return False
    
    def create_start_script(self) -> bool:
        """Crear script de inicio rápido."""
        print("🚀 Creando script de inicio...")
        
        try:
            script_content = f'''#!/usr/bin/env python3
"""
Script de inicio rápido para PC GPS Simulator
Generado automáticamente por setup_pc_gps.py
"""

import subprocess
import sys
import os

def main():
    print("🖥️  Iniciando PC GPS Simulator...")
    print("📱 Dispositivo: {self.config['device_name']}")
    print("🆔 IMEI: {self.config['imei']}")
    print("🌐 Servidor: {self.config['host']}:{self.config['port']}")
    print()
    
    try:
        # Ejecutar simulador GPS
        subprocess.run([sys.executable, "pc_gps_simulator.py"], check=True)
    except KeyboardInterrupt:
        print("\\n🛑 Simulador detenido por el usuario")
    except FileNotFoundError:
        print("❌ No se encontró pc_gps_simulator.py")
        print("💡 Ejecuta primero: python setup_pc_gps.py")
    except Exception as e:
        print(f"❌ Error: {{e}}")

if __name__ == "__main__":
    main()
'''
            
            with open("start_pc_gps.py", 'w') as f:
                f.write(script_content)
            
            # Hacer ejecutable en sistemas Unix
            if os.name != 'nt':
                os.chmod("start_pc_gps.py", 0o755)
            
            print("   ✅ Script de inicio creado: start_pc_gps.py")
            return True
            
        except Exception as e:
            print(f"   ❌ Error creando script: {e}")
            return False
    
    def show_setup_summary(self):
        """Mostrar resumen de la configuración."""
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE CONFIGURACIÓN")
        print("=" * 60)
        
        print(f"🖥️  PC: {self.pc_info['hostname']} ({self.pc_info['platform']})")
        print(f"📱 Dispositivo: {self.config['device_name']}")
        print(f"🆔 IMEI: {self.config['imei']}")
        print(f"🌐 Servidor: {self.config['host']}:{self.config['port']}")
        print(f"📡 Protocolo: {self.config['protocol']}")
        print(f"⏱️  Intervalo: {self.config['interval']}s")
        print(f"🔍 IP Local: {self.pc_info['local_ip']}")
        
        print("\n🚀 COMANDOS PARA USAR:")
        print("   1. Iniciar servidor GPS:")
        print("      python start_gps_server.py")
        print()
        print("   2. Iniciar simulador PC (en otra terminal):")
        print("      python start_pc_gps.py")
        print("      # o directamente:")
        print("      python pc_gps_simulator.py")
        print()
        print("   3. Ver en el frontend:")
        print("      http://localhost:3000")
        print()
        print("   4. Verificar dispositivo:")
        print("      python test_mi_celular.py")
        
        print("\n📊 ARCHIVOS CREADOS:")
        print("   • pc_gps_config.json - Configuración")
        print("   • start_pc_gps.py - Script de inicio")
        print("   • pc_gps_simulator.py - Simulador principal")
        
        print("\n✅ ¡Configuración completada!")
        print("=" * 60)
    
    def run_setup(self):
        """Ejecutar configuración completa."""
        print("🖥️  PC GPS SETUP - SkyGuard")
        print("🌍 Configurando PC como dispositivo GPS")
        print("=" * 60)
        
        steps = [
            ("Verificar dependencias", self.check_dependencies),
            ("Registrar en base de datos", self.register_device_in_database),
            ("Crear archivo de configuración", self.create_config_file),
            ("Probar conexión al servidor", self.test_server_connection),
            ("Crear script de inicio", self.create_start_script),
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            if step_func():
                success_count += 1
            else:
                print(f"⚠️ {step_name} falló, pero continuando...")
        
        print(f"\n📊 Completado: {success_count}/{len(steps)} pasos exitosos")
        
        if success_count >= 3:  # Mínimo necesario
            self.show_setup_summary()
        else:
            print("❌ Configuración incompleta. Revisa los errores anteriores.")


def main():
    """Función principal."""
    try:
        setup = PCGPSSetup()
        setup.run_setup()
    except Exception as e:
        print(f"❌ Error fatal en configuración: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 