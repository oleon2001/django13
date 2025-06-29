#!/usr/bin/env python3
"""
Script de depuración para el servidor Wialon
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from skyguard.apps.gps.protocols.wialon import WialonProtocolHandler

def test_packet_validation():
    """Probar la validación de paquetes Wialon"""
    print("=" * 60)
    print("🔍 DEPURACIÓN DE PAQUETES WIALON")
    print("=" * 60)
    
    protocol = WialonProtocolHandler()
    
    # Paquetes de prueba (como los que envía el simulador)
    test_packets = [
        b'#L#123456789012345;123456\r\n',
        b'#D#280625;114839;10;9.69;-68;0.02;12.0;72;0;8;1.0;0;0;0;00;NA\r\n',
        b'#P#\r\n'
    ]
    
    for packet in test_packets:
        print(f"\n📦 Probando paquete: {packet}")
        
        # Validar paquete
        is_valid = protocol.validate_packet(packet)
        print(f"   • Validación: {'✅ Válido' if is_valid else '❌ Inválido'}")
        
        if is_valid:
            # Decodificar paquete
            decoded = protocol.decode_packet(packet)
            if decoded:
                print(f"   • Tipo: {decoded.get('type', 'Unknown')}")
                if decoded['type'] == 'login':
                    print(f"   • IMEI: {decoded.get('imei')}")
                    print(f"   • Password: {decoded.get('password')}")
                elif decoded['type'] == 'data':
                    print(f"   • Timestamp: {decoded.get('timestamp')}")
                    print(f"   • Position: {decoded.get('position')}")
                    print(f"   • Speed: {decoded.get('speed')} km/h")
            else:
                print("   • ❌ Error al decodificar")
        
        # Probar con diferentes variaciones
        if packet.startswith(b'#D#'):
            print("\n🔧 Probando variaciones del paquete de datos:")
            
            # Variación 1: Formato original del simulador
            var1 = b'#D#280625;114839;1009.69;N;06800.02;W;12.0;72;0;8\r\n'
            print(f"\n   Variación 1 (formato original): {var1}")
            print(f"   • Validación: {'✅ Válido' if protocol.validate_packet(var1) else '❌ Inválido'}")
            
            # Variación 2: Formato esperado por el servidor
            var2 = b'#D#280625;114839;10;9.69;-68;0.02;12.0;72;0;8;1.0;0;0;0;00;NA\r\n'
            print(f"\n   Variación 2 (formato servidor): {var2}")
            print(f"   • Validación: {'✅ Válido' if protocol.validate_packet(var2) else '❌ Inválido'}")

if __name__ == "__main__":
    test_packet_validation() 