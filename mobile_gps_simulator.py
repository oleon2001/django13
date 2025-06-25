#!/usr/bin/env python3
"""
Simulador de GPS móvil para SkyGuard
Permite usar un celular como dispositivo GPS conectándose al servidor Bluetooth
"""

import socket
import struct
import time
import threading
import json
import requests
from datetime import datetime
from typing import Optional, Tuple
import math
import random

class MobileGPSSimulator:
    """Simulador de GPS móvil que se conecta al servidor SkyGuard."""
    
    def __init__(self, server_host: str = 'localhost', server_port: int = 50100):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.session_id = None
        self.imei = 123456789012345  # IMEI simulado
        self.running = False
        self.position = (19.4326, -99.1332)  # Ciudad de México por defecto
        self.speed = 0.0
        self.course = 0.0
        self.altitude = 2240.0
        self.satellites = 8
        self.battery_level = 85
        self.signal_strength = -65
        
        # Constantes del protocolo
        self.PKTID_LOGIN = 0x01
        self.PKTID_PING = 0x02
        self.PKTID_DEVINFO = 0x03
        self.PKTID_DATA = 0x04
        
        self.RSPID_SESSION = 0x10
        self.RSPID_LOGIN = 0x11
        
        self.CMDID_DEVINFO = 0x20
        self.CMDID_DATA = 0x21
        self.CMDID_ACK = 0x22
        
        self.RECID_TRACKS = 0x30
        self.RECID_PEOPLE = 0x31
        
    def connect(self) -> bool:
        """Conectar al servidor SkyGuard."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            
            # Enviar login
            login_packet = self.create_login_packet()
            self.socket.sendto(login_packet, (self.server_host, self.server_port))
            
            # Recibir respuesta
            response, addr = self.socket.recvfrom(1024)
            if len(response) >= 5:
                self.session_id = struct.unpack("<I", response[1:5])[0]
                print(f"Conectado al servidor. Session ID: {self.session_id}")
                self.running = True
                return True
            else:
                print("Respuesta de login inválida")
                return False
                
        except Exception as e:
            print(f"Error al conectar: {e}")
            return False
    
    def create_login_packet(self) -> bytes:
        """Crear paquete de login."""
        # Formato: PKTID_LOGIN + IMEI (8 bytes) + MAC (6 bytes)
        imei_bytes = struct.pack("<Q", self.imei)
        mac_bytes = b'\x00\x11\x22\x33\x44\x55'  # MAC simulado
        return struct.pack("B", self.PKTID_LOGIN) + imei_bytes + mac_bytes
    
    def create_ping_packet(self) -> bytes:
        """Crear paquete de ping con posición."""
        if not self.session_id:
            raise ValueError("No hay sesión activa")
        
        # Crear datos de posición
        timestamp = int(time.time())
        lat = int(self.position[0] * 10000000)  # Convertir a formato del protocolo
        lon = int(self.position[1] * 10000000)
        speed_int = int(self.speed * 10)  # km/h * 10
        course_int = int(self.course * 10)  # grados * 10
        
        # Paquete de ping: PKTID_PING + timestamp + lat + lon + speed + course + inputs
        inputs = 0x01  # Ignición encendida
        ping_data = struct.pack("<IiiBB", timestamp, lat, lon, speed_int, inputs)
        
        return struct.pack("B", self.PKTID_PING) + ping_data
    
    def update_position(self, lat: float, lon: float, speed: float = 0.0, course: float = 0.0):
        """Actualizar posición del dispositivo."""
        self.position = (lat, lon)
        self.speed = speed
        self.course = course
        print(f"Posición actualizada: {lat:.6f}, {lon:.6f}, Velocidad: {speed} km/h")
    
    def simulate_movement(self, route_points: list, speed_kmh: float = 30.0):
        """Simular movimiento a lo largo de una ruta."""
        if not route_points or len(route_points) < 2:
            print("Se necesitan al menos 2 puntos para la ruta")
            return
        
        current_point_idx = 0
        
        while self.running and current_point_idx < len(route_points) - 1:
            start_point = route_points[current_point_idx]
            end_point = route_points[current_point_idx + 1]
            
            # Calcular distancia y dirección
            distance = self.calculate_distance(start_point, end_point)
            bearing = self.calculate_bearing(start_point, end_point)
            
            # Simular movimiento
            steps = max(1, int(distance * 1000 / (speed_kmh / 3.6)))  # Pasos basados en velocidad
            step_distance = distance / steps
            
            for step in range(steps + 1):
                if not self.running:
                    break
                
                # Interpolar posición
                ratio = step / steps
                lat = start_point[0] + (end_point[0] - start_point[0]) * ratio
                lon = start_point[1] + (end_point[1] - start_point[1]) * ratio
                
                self.update_position(lat, lon, speed_kmh, bearing)
                
                # Enviar ping
                self.send_ping()
                
                # Esperar
                time.sleep(1.0)  # 1 segundo entre actualizaciones
            
            current_point_idx += 1
    
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calcular distancia entre dos puntos en km."""
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 6371 * c  # Radio de la Tierra en km
    
    def calculate_bearing(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calcular dirección entre dos puntos en grados."""
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlon = lon2 - lon1
        
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360
    
    def send_ping(self):
        """Enviar ping al servidor."""
        try:
            if self.socket and self.session_id:
                ping_packet = self.create_ping_packet()
                self.socket.sendto(ping_packet, (self.server_host, self.server_port))
                
                # Recibir respuesta
                try:
                    response, addr = self.socket.recvfrom(1024)
                    print(f"Ping enviado - Respuesta recibida: {len(response)} bytes")
                except socket.timeout:
                    print("Timeout en respuesta del ping")
                    
        except Exception as e:
            print(f"Error enviando ping: {e}")
    
    def start_ping_thread(self, interval: float = 30.0):
        """Iniciar thread para enviar pings periódicos."""
        def ping_loop():
            while self.running:
                self.send_ping()
                time.sleep(interval)
        
        ping_thread = threading.Thread(target=ping_loop, daemon=True)
        ping_thread.start()
        return ping_thread
    
    def get_location_from_ip(self) -> Optional[Tuple[float, float]]:
        """Obtener ubicación aproximada basada en IP."""
        try:
            response = requests.get('http://ip-api.com/json/', timeout=5)
            data = response.json()
            if data['status'] == 'success':
                return (data['lat'], data['lon'])
        except Exception as e:
            print(f"Error obteniendo ubicación por IP: {e}")
        return None
    
    def disconnect(self):
        """Desconectar del servidor."""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        print("Desconectado del servidor")

def main():
    """Función principal para probar el simulador."""
    print("=== Simulador de GPS Móvil para SkyGuard ===")
    
    # Crear simulador
    simulator = MobileGPSSimulator()
    
    # Intentar obtener ubicación real por IP
    real_location = simulator.get_location_from_ip()
    if real_location:
        print(f"Ubicación detectada por IP: {real_location[0]:.6f}, {real_location[1]:.6f}")
        simulator.update_position(*real_location)
    
    # Conectar al servidor
    if simulator.connect():
        print("Conectado exitosamente al servidor SkyGuard")
        
        # Iniciar ping automático
        simulator.start_ping_thread(interval=30.0)
        
        # Ejemplo de ruta en Ciudad de México
        route = [
            (19.4326, -99.1332),  # Zócalo
            (19.4200, -99.1200),  # Punto intermedio
            (19.4100, -99.1100),  # Destino
        ]
        
        print("Iniciando simulación de movimiento...")
        print("Presiona Ctrl+C para detener")
        
        try:
            # Simular movimiento
            simulator.simulate_movement(route, speed_kmh=25.0)
        except KeyboardInterrupt:
            print("\nDeteniendo simulación...")
        finally:
            simulator.disconnect()
    else:
        print("No se pudo conectar al servidor")

if __name__ == "__main__":
    main() 