#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import struct
import time
import random
import requests
from datetime import datetime
from pytz import utc

# Constantes del protocolo
PKTID_LOGIN = 0x01
PKTID_PING = 0x02
PKTID_DEVINFO = 0x03
PKTID_DATA = 0x04
RSPID_SESSION = 0x10
RSPID_LOGIN = 0x11

# Configuración
IMEI = "123456789012345"
SERVER_HOST = "localhost"
SERVER_PORT = 60001
API_URL = "http://localhost:8000/api/gps"

def calculate_crc(data):
    """Implementación simple de CRC-CCITT"""
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

class GPSSimulator:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.session = None
        self.connected = False
        self.client_ip = "127.0.0.1"  # IP del cliente
        self.client_port = random.randint(10000, 65000)  # Puerto aleatorio para el cliente
        self.socket.bind((self.client_ip, self.client_port))

    def send_packet(self, packet):
        self.socket.sendto(packet, (SERVER_HOST, SERVER_PORT))
        response = self.socket.recvfrom(1024)
        return response[0]

    def update_device_connection(self):
        """Actualiza la IP y puerto del dispositivo en la base de datos"""
        try:
            url = f"{API_URL}/devices/{IMEI}/"
            data = {
                'current_ip': self.client_ip,
                'current_port': self.client_port,
                'connection_status': 'ONLINE'
            }
            response = requests.patch(url, json=data)
            if response.status_code == 200:
                print(f"Dispositivo actualizado con IP {self.client_ip} y puerto {self.client_port}")
            else:
                print(f"Error al actualizar dispositivo: {response.status_code}")
        except Exception as e:
            print(f"Error al actualizar dispositivo: {e}")

    def login(self):
        print("Enviando login...")
        # Crear el paquete con el tamaño exacto
        packet = bytearray(15)  # Inicializar con 15 bytes en cero
        packet[0] = PKTID_LOGIN  # ID del paquete
        # IMEI (8 bytes)
        imei_bytes = struct.pack('<Q', int(IMEI))
        packet[1:9] = imei_bytes
        # MAC ID (6 bytes)
        mac_bytes = struct.pack('<Q', 0x1234567890)[:6]
        packet[9:15] = mac_bytes
        
        response = self.send_packet(packet)
        
        if len(response) >= 5:
            self.session = struct.unpack('<L', response[1:5])[0]  # Cambié a little-endian
            self.connected = True
            print(f"✅ Login exitoso. Sesión: {self.session}")
            print(f"🔗 Cliente conectado desde {self.client_ip}:{self.client_port}")
            print(f"📡 Respuesta del servidor: {response.hex()}")
            return True
        else:
            print(f"❌ Respuesta de login inválida: {response.hex() if response else 'Sin respuesta'}")
            return False

    def send_position(self):
        if not self.connected:
            print("No conectado. Intentando login...")
            if not self.login():
                return False

        # Generar posición aleatoria cerca de un punto de referencia (simulando movimiento)
        # Crear un patrón de movimiento más realista
        current_time = time.time()
        
        # Base: Ciudad de México
        base_lat = 19.4326
        base_lon = -99.1332
        
        # Simular movimiento en círculo para que sea más visible
        angle = (current_time / 10) % (2 * 3.14159)  # Una vuelta cada 10 segundos
        radius = 0.005  # Radio de movimiento
        
        lat = base_lat + radius * random.uniform(0.8, 1.2) * (0.5 + 0.5 * time.time() % 1)
        lon = base_lon + radius * random.uniform(0.8, 1.2) * (0.5 + 0.5 * time.time() % 1)
        
        speed = random.randint(20, 80)  # Velocidad más realista
        inputs = 0x03  # Motor encendido + IGN encendido

        # Crear paquete de posición
        packet = struct.pack('<B', PKTID_PING)
        packet += struct.pack('<L', self.session)
        packet += struct.pack('<I', int(current_time))
        packet += struct.pack('<i', int(lat * 10000000))
        packet += struct.pack('<i', int(lon * 10000000))
        packet += struct.pack('<B', speed)
        packet += struct.pack('<B', inputs)

        try:
            response = self.send_packet(packet)
            print(f"📍 Posición enviada: {lat:.6f}, {lon:.6f}, Velocidad: {speed} km/h")
            print(f"   Sesión: {self.session}, Respuesta: {len(response)} bytes")
            return True
        except Exception as e:
            print(f"❌ Error al enviar posición: {e}")
            self.connected = False
            return False

    def run(self):
        print(f"Iniciando simulador GPS con IMEI: {IMEI}")
        print(f"Conectando a {SERVER_HOST}:{SERVER_PORT}")
        print(f"Cliente escuchando en {self.client_ip}:{self.client_port}")
        
        if not self.login():
            print("Error en el login inicial")
            return

        try:
            while True:
                self.send_position()
                time.sleep(3)  # Enviar posición cada 3 segundos para ver cambios más rápido
        except KeyboardInterrupt:
            print("\nSimulador detenido por el usuario")
        finally:
            self.socket.close()

if __name__ == "__main__":
    simulator = GPSSimulator()
    simulator.run() 