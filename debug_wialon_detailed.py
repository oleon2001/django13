#!/usr/bin/env python3
"""
Script de depuración detallada para el servidor Wialon
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from skyguard.apps.gps.protocols.wialon import WialonProtocolHandler

def test_packet_validation_detailed():
    """Probar la validación de paquetes Wialon con detalles"""
    print("=" * 60)
    print("🔍 DEPURACIÓN DETALLADA DE PAQUETES WIALON")
    print("=" * 60)
    
    protocol = WialonProtocolHandler()
    
    # Paquetes de prueba
    test_packets = [
        (b'#L#123456789012345;123456\r\n', "Login"),
        (b'#D#280625;114839;1009.69;N;06800.02;W;12.0;72;0;8\r\n', "Data (formato simulador)"),
        (b'#P#\r\n', "Ping"),
        (b'#L#123456789012345;123456', "Login sin \\r\\n"),
        (b'#D#280625;114839;10;9.69;-68;0.02;12.0;72;0;8;1.0;0;0;0;00;NA\r\n', "Data completo")
    ]
    
    for packet, description in test_packets:
        print(f"\n📦 Probando: {description}")
        print(f"   Paquete: {packet}")
        
        # Verificar cada condición de validación manualmente
        print("   Verificaciones:")
        
        # 1. No vacío
        if not packet:
            print("   ❌ Paquete vacío")
            continue
        print("   ✅ No está vacío")
        
        # 2. Después de strip
        stripped = packet.strip()
        if not stripped:
            print("   ❌ Vacío después de strip()")
            continue
        print(f"   ✅ Después de strip: {stripped}")
        
        # 3. Tipo de paquete
        if stripped.startswith(b'#L#'):
            print("   ✅ Es paquete de login (#L#)")
        elif stripped.startswith(b'#D#'):
            print("   ✅ Es paquete de datos (#D#)")
        elif stripped.startswith(b'#P#'):
            print("   ⚠️ Es paquete de ping (#P#) - NO SOPORTADO EN validate_packet")
        else:
            print(f"   ❌ Tipo de paquete no reconocido: {stripped[:3]}")
        
        # 4. Terminación
        if stripped.endswith(b'\r\n'):
            print("   ✅ Termina con \\r\\n")
        else:
            print("   ❌ NO termina con \\r\\n")
        
        # Resultado final
        is_valid = protocol.validate_packet(packet)
        print(f"   🔍 Resultado validate_packet: {'✅ Válido' if is_valid else '❌ Inválido'}")
        
        # Si es válido, intentar decodificar
        if is_valid:
            decoded = protocol.decode_packet(packet)
            if decoded:
                print(f"   ✅ Decodificado exitosamente: tipo={decoded.get('type')}")
            else:
                print("   ❌ Error al decodificar")

def fix_validation():
    """Mostrar cómo corregir la validación"""
    print("\n" + "=" * 60)
    print("🔧 SOLUCIÓN PROPUESTA")
    print("=" * 60)
    
    print("""
El problema es que la función validate_packet en WialonProtocolHandler
no acepta paquetes #P# (ping). La función debería modificarse así:

def validate_packet(self, data: bytes) -> bool:
    try:
        if not data:
            return False
            
        data = data.strip()
        if not data:
            return False
            
        # Check packet type - AGREGAR #P# AQUÍ
        if not (data.startswith(b'#L#') or 
                data.startswith(b'#D#') or 
                data.startswith(b'#P#')):  # <-- AGREGAR ESTA LÍNEA
            return False
            
        # Check packet end
        if not data.endswith(b'\\r\\n'):
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating packet: {e}")
        return False
""")

if __name__ == "__main__":
    test_packet_validation_detailed()
    fix_validation() 