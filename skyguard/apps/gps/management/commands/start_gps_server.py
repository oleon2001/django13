"""
Comando de Django para iniciar el servidor GPS de hardware.
Basado en la implementación del proyecto django14.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import logging
import time
import signal
import sys

from skyguard.apps.gps.services.hardware_gps import hardware_gps_service

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Inicia el servidor GPS para procesar señales de hardware'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='0.0.0.0',
            help='Host para el servidor GPS (default: 0.0.0.0)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=8001,
            help='Puerto para el servidor GPS (default: 8001)'
        )
        parser.add_argument(
            '--serial-port',
            type=str,
            default='/dev/ttyS0',
            help='Puerto serial para GPS (default: /dev/ttyS0)'
        )
        parser.add_argument(
            '--serial-baudrate',
            type=int,
            default=9600,
            help='Baudrate para puerto serial (default: 9600)'
        )
        parser.add_argument(
            '--enable-serial',
            action='store_true',
            help='Habilitar monitoreo de puerto serial'
        )
        parser.add_argument(
            '--enable-tcp',
            action='store_true',
            default=True,
            help='Habilitar servidor TCP (default: True)'
        )
    
    def handle(self, *args, **options):
        """Ejecuta el comando."""
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando servidor GPS de hardware...')
        )
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Configurar manejo de señales para shutdown graceful
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Iniciar servidor TCP si está habilitado
            if options['enable_tcp']:
                host = options['host']
                port = options['port']
                
                self.stdout.write(
                    f"📡 Iniciando servidor TCP en {host}:{port}"
                )
                
                if not hardware_gps_service.start_server(host, port):
                    self.stdout.write(
                        self.style.ERROR('❌ Error iniciando servidor TCP')
                    )
                    return
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Servidor TCP iniciado en {host}:{port}")
                )
            
            # Iniciar monitoreo serial si está habilitado
            if options['enable_serial']:
                serial_port = options['serial_port']
                baudrate = options['serial_baudrate']
                
                self.stdout.write(
                    f"🔌 Iniciando monitoreo serial en {serial_port} ({baudrate} baud)"
                )
                
                hardware_gps_service.start_serial_monitoring(serial_port, baudrate)
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Monitoreo serial iniciado en {serial_port}")
                )
            
            # Mostrar información de estado
            self.stdout.write(
                self.style.SUCCESS(
                    "🎯 Servidor GPS iniciado correctamente\n"
                    "📊 Protocolos soportados:\n"
                    "   • Concox (0x7878)\n"
                    "   • Meiligao (0x7979)\n"
                    "   • NMEA ($GPRMC, $GPGGA, $GPGLL)\n"
                    "🔧 Presiona Ctrl+C para detener"
                )
            )
            
            # Loop principal
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stdout.write("\n⏹️  Deteniendo servidor GPS...")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error en servidor GPS: {e}")
            )
        finally:
            self._cleanup()
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de terminación."""
        self.stdout.write("\n⏹️  Señal de terminación recibida...")
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Limpia recursos del servidor."""
        try:
            hardware_gps_service.stop_server()
            self.stdout.write(
                self.style.SUCCESS("✅ Servidor GPS detenido correctamente")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error deteniendo servidor: {e}")
            ) 