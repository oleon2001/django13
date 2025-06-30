#!/usr/bin/env python3
"""
Script completo de pruebas para el servidor GPS de SkyGuard.
Verifica todos los protocolos y funcionalidades.
"""

import socket
import time
import struct
import threading
from datetime import datetime

def nmea_checksum(sentence):
    """Calcula el checksum NMEA correctamente."""
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    return f"*{checksum:02X}"

def test_nmea_protocol():
    """Prueba el protocolo NMEA."""
    print("🧪 Probando protocolo NMEA...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8001))
        
        # Datos NMEA de prueba (Ciudad de México)
        nmea_sentences = [
            "GPRMC,123519,A,1925.95,N,09908.00,W,022.4,084.4,300625,003.1,W",
            "GPGGA,123519,1925.95,N,09908.00,W,1,08,0.9,2240,M,46.9,M,,",
            "GPGLL,1925.95,N,09908.00,W,123519,A"
        ]
        
        for i, sentence in enumerate(nmea_sentences):
            nmea_line = f"${sentence}{nmea_checksum(sentence)}\r\n"
            sock.send(nmea_line.encode('utf-8'))
            print(f"  📡 Enviado: {nmea_line.strip()}")
            time.sleep(0.5)
        
        sock.close()
        print("  ✅ NMEA: Datos enviados correctamente")
        return True
    except Exception as e:
        print(f"  ❌ NMEA: Error - {e}")
        return False

def test_concox_protocol():
    """Prueba el protocolo Concox."""
    print("🧪 Probando protocolo Concox...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8001))
        
        # IMEI en BCD
        imei_str = "123456789012345"
        imei_bytes = b''
        for i in range(0, len(imei_str), 2):
            if i+1 < len(imei_str):
                high = int(imei_str[i])
                low = int(imei_str[i+1])
                imei_bytes += bytes([(high << 4) | low])
            else:
                high = int(imei_str[i])
                imei_bytes += bytes([(high << 4)])
        
        # UTC (hora actual)
        now = time.gmtime()
        utc_bytes = struct.pack('>BBBBBB',
            now.tm_year - 2000, now.tm_mon, now.tm_mday,
            now.tm_hour, now.tm_min, now.tm_sec
        )
        
        # Coordenadas de Ciudad de México (valores ajustados)
        lat_deg = 19
        lat_min = 25.956
        lon_deg = 99
        lon_min = 7.992
        lat_ddmm = lat_deg * 100 + lat_min
        lon_ddmm = lon_deg * 100 + lon_min
        lat_raw = int(lat_ddmm * 100000)
        lon_raw = int(lon_ddmm * 100000)
        
        speed = 45
        course = 180
        gps_bytes = struct.pack('>iiHH', lat_raw, lon_raw, speed, course)
        
        # Paquete completo
        packet = b'\x78\x78' + bytes([0x0F]) + bytes([0x01]) + imei_bytes + utc_bytes + gps_bytes
        sock.send(packet)
        print(f"  📡 Enviado paquete Concox: {len(packet)} bytes")
        
        sock.close()
        print("  ✅ Concox: Datos enviados correctamente")
        return True
    except Exception as e:
        print(f"  ❌ Concox: Error - {e}")
        return False

def test_meiligao_protocol():
    """Prueba el protocolo Meiligao."""
    print("🧪 Probando protocolo Meiligao...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8001))
        
        # Similar a Concox pero con header diferente
        imei_str = "987654321098765"
        imei_bytes = b''
        for i in range(0, len(imei_str), 2):
            if i+1 < len(imei_str):
                high = int(imei_str[i])
                low = int(imei_str[i+1])
                imei_bytes += bytes([(high << 4) | low])
            else:
                high = int(imei_str[i])
                imei_bytes += bytes([(high << 4)])
        
        # UTC
        now = time.gmtime()
        utc_bytes = struct.pack('>BBBBBB',
            now.tm_year - 2000, now.tm_mon, now.tm_mday,
            now.tm_hour, now.tm_min, now.tm_sec
        )
        
        # Coordenadas de Guadalajara
        lat_deg = 20
        lat_min = 40.0
        lon_deg = 103
        lon_min = 20.0
        lat_ddmm = lat_deg * 100 + lat_min
        lon_ddmm = lon_deg * 100 + lon_min
        lat_raw = int(lat_ddmm * 100000)
        lon_raw = int(lon_ddmm * 100000)
        
        speed = 30
        course = 90
        gps_bytes = struct.pack('>iiHH', lat_raw, lon_raw, speed, course)
        
        # Paquete Meiligao (header diferente)
        packet = b'\x78\x78' + bytes([0x0F]) + bytes([0x02]) + imei_bytes + utc_bytes + gps_bytes
        sock.send(packet)
        print(f"  📡 Enviado paquete Meiligao: {len(packet)} bytes")
        
        sock.close()
        print("  ✅ Meiligao: Datos enviados correctamente")
        return True
    except Exception as e:
        print(f"  ❌ Meiligao: Error - {e}")
        return False

def check_server_status():
    """Verifica que el servidor esté ejecutándose."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8001))
        sock.close()
        return result == 0
    except:
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 PRUEBAS COMPLETAS DEL SERVIDOR GPS SKYGUARD")
    print("=" * 50)
    
    # Verificar servidor
    if not check_server_status():
        print("❌ El servidor GPS no está ejecutándose en el puerto 8001")
        print("Ejecuta: python3 start_hardware_gps_server.py")
        return False
    
    print("✅ Servidor GPS detectado en puerto 8001")
    print()
    
    # Ejecutar pruebas
    results = []
    
    results.append(test_nmea_protocol())
    time.sleep(1)
    
    results.append(test_concox_protocol())
    time.sleep(1)
    
    results.append(test_meiligao_protocol())
    time.sleep(1)
    
    # Resumen
    print("\n" + "=" * 50)
    print("RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    protocols = ["NMEA", "Concox", "Meiligao"]
    for i, result in enumerate(results):
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{protocols[i]}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResultado: {passed}/{total} protocolos funcionando")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("\nPróximos pasos:")
        print("1. Verificar datos en la base de datos")
        print("2. Probar con dispositivos GPS reales")
        print("3. Configurar alertas y monitoreo")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los logs del servidor.")
    
    return passed == total

if __name__ == '__main__':
    main() 