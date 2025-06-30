#!/usr/bin/env python3
"""
Script de prueba para simular dispositivos GPS de hardware.
Permite probar el servidor GPS con datos simulados.
"""

import socket
import time
import struct
import random
from datetime import datetime
import pytz

def create_concox_packet(imei, lat, lon, speed=0, course=0, satellites=8):
    """Crea un paquete Concox simulado."""
    # Header Concox
    packet = b'\x78\x78'
    
    # IMEI en BCD (15 dígitos)
    imei_str = f"{imei:015d}"
    imei_bytes = b''
    for i in range(0, 15, 2):
        if i + 1 < len(imei_str):
            high = int(imei_str[i])
            low = int(imei_str[i + 1])
            imei_bytes += bytes([high * 16 + low])
        else:
            imei_bytes += bytes([int(imei_str[i]) * 16])
    
    # Protocolo 0x01 (GPS)
    protocol = b'\x01'
    
    # UTC time (6 bytes: year, month, day, hour, minute, second)
    now = datetime.now(pytz.UTC)
    utc_time = struct.pack('BBBBBB', 
        now.year - 2000, now.month, now.day, 
        now.hour, now.minute, now.second
    )
    
    # GPS data (12 bytes)
    # ns, lat, lon, speed, cs
    lat_int = int(abs(lat) * 1800000)
    lon_int = int(abs(lon) * 1800000)
    
    cs = course & 0x03FF  # Course (10 bits)
    if lat < 0:
        cs |= 0x0400  # South
    if lon < 0:
        cs |= 0x0800  # West
    cs |= 0x1000  # GPS fix
    
    gps_data = struct.pack('>BIIBH', satellites, lat_int, lon_int, speed, cs)
    
    # Serial number (2 bytes)
    serial = struct.pack('>H', random.randint(1, 65535))
    
    # Error check (2 bytes) - CRC
    data_for_crc = protocol + utc_time + gps_data + serial
    crc = 0
    for byte in data_for_crc:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    
    # Length
    length = len(protocol + utc_time + gps_data + serial + struct.pack('>H', crc))
    
    # Construir paquete completo
    packet = packet + bytes([length]) + protocol + utc_time + gps_data + serial + struct.pack('>H', crc) + b'\x0D\x0A'
    
    return packet

def create_nmea_gprmc(lat, lon, speed=0, course=0):
    """Crea una sentencia NMEA GPRMC simulado."""
    now = datetime.now(pytz.UTC)
    
    # Formatear tiempo
    time_str = now.strftime("%H%M%S.%f")[:-3]
    
    # Formatear fecha
    date_str = now.strftime("%d%m%y")
    
    # Formatear coordenadas
    lat_deg = int(abs(lat))
    lat_min = (abs(lat) - lat_deg) * 60
    lat_dir = 'S' if lat < 0 else 'N'
    
    lon_deg = int(abs(lon))
    lon_min = (abs(lon) - lon_deg) * 60
    lon_dir = 'W' if lon < 0 else 'E'
    
    # Velocidad en nudos
    speed_knots = speed / 1.852
    
    # Construir sentencia
    sentence = f"$GPRMC,{time_str},A,{lat_deg:02d}{lat_min:07.4f},{lat_dir},{lon_deg:03d}{lon_min:07.4f},{lon_dir},{speed_knots:.1f},{course:.1f},{date_str},,,A*"
    
    # Calcular checksum
    checksum = 0
    for char in sentence[1:-1]:  # Excluir $ y *
        checksum ^= ord(char)
    
    sentence += f"{checksum:02X}\r\n"
    
    return sentence.encode()

def test_concox_device(host='localhost', port=8001, imei=123456789012345):
    """Prueba un dispositivo Concox simulado."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"✅ Conectado a servidor GPS en {host}:{port}")
        
        # Simular movimiento
        base_lat = 19.4326  # Ciudad de México
        base_lon = -99.1332
        
        for i in range(10):
            # Simular movimiento
            lat = base_lat + (i * 0.001)  # Mover 0.001 grados
            lon = base_lon + (i * 0.001)
            speed = random.randint(0, 60)
            course = random.randint(0, 360)
            
            # Crear paquete
            packet = create_concox_packet(imei, lat, lon, speed, course)
            
            # Enviar paquete
            sock.send(packet)
            print(f"📤 Enviado paquete {i+1}: lat={lat:.6f}, lon={lon:.6f}, speed={speed} km/h")
            
            time.sleep(2)
        
        sock.close()
        print("✅ Prueba Concox completada")
        
    except Exception as e:
        print(f"❌ Error en prueba Concox: {e}")

def test_nmea_device(host='localhost', port=8001):
    """Prueba un dispositivo NMEA simulado."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"✅ Conectado a servidor GPS en {host}:{port}")
        
        # Simular movimiento
        base_lat = 19.4326  # Ciudad de México
        base_lon = -99.1332
        
        for i in range(10):
            # Simular movimiento
            lat = base_lat + (i * 0.001)  # Mover 0.001 grados
            lon = base_lon + (i * 0.001)
            speed = random.randint(0, 60)
            course = random.randint(0, 360)
            
            # Crear sentencia NMEA
            sentence = create_nmea_gprmc(lat, lon, speed, course)
            
            # Enviar sentencia
            sock.send(sentence)
            print(f"📤 Enviada sentencia {i+1}: lat={lat:.6f}, lon={lon:.6f}, speed={speed} km/h")
            
            time.sleep(2)
        
        sock.close()
        print("✅ Prueba NMEA completada")
        
    except Exception as e:
        print(f"❌ Error en prueba NMEA: {e}")

def main():
    """Función principal."""
    print("🧪 Iniciando pruebas de hardware GPS...")
    print("=" * 50)
    
    host = 'localhost'
    port = 8001
    
    print("1. Probando dispositivo Concox...")
    test_concox_device(host, port)
    
    print("\n2. Probando dispositivo NMEA...")
    test_nmea_device(host, port)
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == '__main__':
    main() 