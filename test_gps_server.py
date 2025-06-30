#!/usr/bin/env python3
"""
Script para probar el servidor GPS con datos simulados.
"""

import socket
import time
import struct
import threading

def nmea_checksum(sentence):
    """Calcula el checksum NMEA correctamente."""
    # El checksum se calcula sobre todo el contenido entre $ y *
    # Excluyendo el $ inicial y el * final
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    return f"*{checksum:02X}"

def send_nmea_data():
    """Envía datos NMEA de prueba al servidor GPS con checksum correcto."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8001))
        print("✅ Conectado al servidor GPS")
        # Datos NMEA de prueba (Ciudad de México)
        nmea_bases = [
            "GPRMC,123519,A,1925.95,N,09908.00,W,022.4,084.4,300625,003.1,W",
            "GPGGA,123519,1925.95,N,09908.00,W,1,08,0.9,2240,M,46.9,M,,",
            "GPGLL,1925.95,N,09908.00,W,123519,A"
        ]
        for i, base in enumerate(nmea_bases):
            sentence = f"${base}{nmea_checksum(base)}\r\n"
            sock.send(sentence.encode('utf-8'))
            print(f"📡 Enviado NMEA {i+1}: {sentence.strip()}")
            time.sleep(1)
        sock.close()
        print("✅ Datos NMEA enviados correctamente")
    except Exception as e:
        print(f"❌ Error enviando datos NMEA: {e}")

def send_concox_data():
    """Envía datos Concox de prueba al servidor GPS (lat/lon válidos)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8001))
        print("✅ Conectado al servidor GPS")
        # IMEI en BCD (ejemplo: 123456789012345)
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
        # Ciudad de México: 19.4326, -99.1332
        # DDMM.MMMM - usar valores más pequeños para evitar overflow
        lat_deg = 19
        lat_min = 25.956  # (19.4326 - 19) * 60
        lon_deg = 99
        lon_min = 7.992   # (99.1332 - 99) * 60
        lat_ddmm = lat_deg * 100 + lat_min  # 1925.956
        lon_ddmm = lon_deg * 100 + lon_min  # 9907.992
        # Convertir a formato que quepa en signed int (32 bits)
        lat_raw = int(lat_ddmm * 100000)   # 19259560 (más pequeño)
        lon_raw = int(lon_ddmm * 100000)   # 9907992 (más pequeño)
        speed = 45  # km/h * 10
        course = 180  # grados * 10
        gps_bytes = struct.pack('>iiHH',
            lat_raw,  # Latitud (signed int)
            lon_raw,  # Longitud (signed int)
            speed,    # Velocidad
            course    # Curso
        )
        # Paquete completo
        packet = b'\x78\x78' + bytes([0x0F]) + bytes([0x01]) + imei_bytes + utc_bytes + gps_bytes
        sock.send(packet)
        print(f"📡 Enviado paquete Concox: {len(packet)} bytes (lat_raw={lat_raw}, lon_raw={lon_raw})")
        time.sleep(1)
        sock.close()
        print("✅ Datos Concox enviados correctamente")
    except Exception as e:
        print(f"❌ Error enviando datos Concox: {e}")

def main():
    print("🚀 PRUEBAS DEL SERVIDOR GPS (ajustadas)")
    print("=" * 40)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8001))
        sock.close()
        if result != 0:
            print("❌ El servidor GPS no está ejecutándose en el puerto 8001")
            print("Ejecuta: python3 start_hardware_gps_server.py")
            return False
    except Exception as e:
        print(f"❌ Error verificando servidor: {e}")
        return False
    print("✅ Servidor GPS detectado en puerto 8001")
    print("\n🧪 Probando datos NMEA...")
    send_nmea_data()
    time.sleep(2)
    print("\n🧪 Probando datos Concox...")
    send_concox_data()
    print("\n✅ Pruebas completadas")
    print("Revisa los logs del servidor GPS para verificar el procesamiento")
    return True

if __name__ == '__main__':
    main() 