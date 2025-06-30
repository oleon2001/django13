#!/usr/bin/env python3
"""
Script para iniciar el servidor GPS de hardware SkyGuard.
Basado en la implementación del proyecto django14.
"""

import os
import sys
import signal
import time
import logging
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')

import django
django.setup()

from skyguard.apps.gps.services.hardware_gps import hardware_gps_service
from django.conf import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hardware_gps_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """Maneja señales de terminación."""
    logger.info(f"Señal {signum} recibida. Deteniendo servidor GPS...")
    hardware_gps_service.stop_server()
    sys.exit(0)


def main():
    """Función principal."""
    print("🚀 Iniciando servidor GPS de hardware SkyGuard...")
    print("=" * 60)
    
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Obtener configuración
        config = getattr(settings, 'HARDWARE_GPS_CONFIG', {})
        
        if not config.get('enabled', True):
            logger.warning("Hardware GPS está deshabilitado en configuración")
            return
        
        # Iniciar servidor TCP
        tcp_config = config.get('tcp_server', {})
        if tcp_config.get('enabled', True):
            host = tcp_config.get('host', '0.0.0.0')
            port = tcp_config.get('port', 8001)
            
            print(f"📡 Iniciando servidor TCP en {host}:{port}")
            
            if not hardware_gps_service.start_server(host, port):
                logger.error("❌ Error iniciando servidor TCP")
                return
            
            print(f"✅ Servidor TCP iniciado en {host}:{port}")
        
        # Iniciar monitoreo serial
        serial_config = config.get('serial_monitoring', {})
        if serial_config.get('enabled', False):
            port = serial_config.get('port', '/dev/ttyS0')
            baudrate = serial_config.get('baudrate', 9600)
            
            print(f"🔌 Iniciando monitoreo serial en {port} ({baudrate} baud)")
            
            hardware_gps_service.start_serial_monitoring(port, baudrate)
            
            print(f"✅ Monitoreo serial iniciado en {port}")
        
        # Mostrar información de protocolos
        protocols = config.get('protocols', {})
        print("\n📊 Protocolos habilitados:")
        for protocol, config in protocols.items():
            if config.get('enabled', True):
                print(f"   ✅ {protocol.upper()}")
            else:
                print(f"   ❌ {protocol.upper()}")
        
        print("\n🎯 Servidor GPS iniciado correctamente")
        print("📋 Información:")
        print(f"   • Servidor TCP: {tcp_config.get('host', '0.0.0.0')}:{tcp_config.get('port', 8001)}")
        print(f"   • Serial: {'Habilitado' if serial_config.get('enabled') else 'Deshabilitado'}")
        print(f"   • Auto-crear dispositivos: {config.get('auto_create_devices', True)}")
        print(f"   • Timeout conexión: {config.get('connection_timeout', 30)}s")
        print(f"   • Máx conexiones: {config.get('max_connections', 100)}")
        print("\n🔧 Presiona Ctrl+C para detener")
        print("=" * 60)
        
        # Loop principal
        while True:
            time.sleep(1)
            
            # Mostrar estadísticas cada 30 segundos
            if int(time.time()) % 30 == 0:
                active_connections = len(hardware_gps_service.active_connections)
                active_threads = len([t for t in hardware_gps_service.threads if t.is_alive()])
                print(f"📊 Estado: {active_connections} conexiones activas, {active_threads} threads")
    
    except KeyboardInterrupt:
        print("\n⏹️  Deteniendo servidor GPS...")
    except Exception as e:
        logger.error(f"❌ Error en servidor GPS: {e}")
    finally:
        hardware_gps_service.stop_server()
        print("✅ Servidor GPS detenido correctamente")


if __name__ == '__main__':
    main() 