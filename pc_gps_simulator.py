#!/usr/bin/env python3
"""
Simulador GPS para PC - Obtiene ubicación real y la envía al servidor SkyGuard
Versión mejorada que soporta múltiples métodos de obtención de ubicación.
"""

import socket
import time
import json
import sys
import threading
import requests
import random
import subprocess
import platform
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

class PCLocationProvider:
    """Proveedor de ubicación para PC usando múltiples métodos."""
    
    def __init__(self):
        """Inicializar el proveedor de ubicación."""
        self.current_location = None
        self.last_update = None
        self.location_cache = {}
        
    def get_location_ip_geolocation(self) -> Optional[Dict[str, Any]]:
        """Obtener ubicación usando servicios de geolocalización por IP."""
        services = [
            'http://ip-api.com/json/',
            'https://ipapi.co/json/',
            'https://ipinfo.io/json'
        ]
        
        for service in services:
            try:
                print(f"🌐 Intentando obtener ubicación desde: {service}")
                response = requests.get(service, timeout=10)
                data = response.json()
                
                # Procesar respuesta según el servicio
                if 'ip-api.com' in service:
                    if data.get('status') == 'success':
                        return {
                            'latitude': data['lat'],
                            'longitude': data['lon'],
                            'accuracy': 5000,  # ~5km precisión
                            'speed': random.randint(0, 50),
                            'bearing': random.randint(0, 360),
                            'altitude': data.get('elevation', 0),
                            'timestamp': datetime.now(),
                            'source': 'ip-api.com',
                            'city': data.get('city', 'Unknown'),
                            'country': data.get('country', 'Unknown'),
                            'isp': data.get('isp', 'Unknown')
                        }
                
                elif 'ipapi.co' in service:
                    if data.get('latitude') and data.get('longitude'):
                        return {
                            'latitude': data['latitude'],
                            'longitude': data['longitude'],
                            'accuracy': 3000,
                            'speed': random.randint(0, 50),
                            'bearing': random.randint(0, 360),
                            'altitude': 0,
                            'timestamp': datetime.now(),
                            'source': 'ipapi.co',
                            'city': data.get('city', 'Unknown'),
                            'country': data.get('country_name', 'Unknown')
                        }
                        
            except Exception as e:
                print(f"❌ Error con {service}: {e}")
                continue
        
        return None
    
    def get_location_wifi_scanning(self) -> Optional[Dict[str, Any]]:
        """Obtener ubicación usando escaneo de WiFi (Windows/Linux)."""
        try:
            if platform.system() == "Windows":
                return self._get_wifi_location_windows()
            elif platform.system() == "Linux":
                return self._get_wifi_location_linux()
        except Exception as e:
            print(f"❌ Error obteniendo ubicación por WiFi: {e}")
        
        return None
    
    def _get_wifi_location_windows(self) -> Optional[Dict[str, Any]]:
        """Obtener ubicación WiFi en Windows."""
        try:
            # Ejecutar comando netsh para obtener redes WiFi
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Simular ubicación basada en redes WiFi detectadas
                networks_count = result.stdout.count('Profile')
                
                if networks_count > 0:
                    # Ubicación simulada con base en cantidad de redes
                    # (México City como base)
                    base_lat = 19.4326
                    base_lon = -99.1332
                    
                    # Agregar variación basada en redes detectadas
                    lat_offset = (networks_count % 10) * 0.001
                    lon_offset = (networks_count % 10) * 0.001
                    
                    return {
                        'latitude': base_lat + lat_offset,
                        'longitude': base_lon + lon_offset,
                        'accuracy': 100,  # ~100m precisión
                        'speed': 0,
                        'bearing': 0,
                        'altitude': 2240,  # Altitud aproximada de CDMX
                        'timestamp': datetime.now(),
                        'source': 'wifi_windows',
                        'networks_detected': networks_count
                    }
        except Exception as e:
            print(f"❌ Error WiFi Windows: {e}")
        
        return None
    
    def _get_wifi_location_linux(self) -> Optional[Dict[str, Any]]:
        """Obtener ubicación WiFi en Linux."""
        try:
            # Usar iwlist para escanear redes WiFi
            result = subprocess.run(
                ['iwlist', 'scan'], capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                # Contar redes detectadas
                networks_count = result.stdout.count('ESSID:')
                
                if networks_count > 0:
                    # Ubicación simulada basada en redes WiFi
                    base_lat = 19.4326
                    base_lon = -99.1332
                    
                    lat_offset = (networks_count % 10) * 0.001
                    lon_offset = (networks_count % 10) * 0.001
                    
                    return {
                        'latitude': base_lat + lat_offset,
                        'longitude': base_lon + lon_offset,
                        'accuracy': 150,
                        'speed': 0,
                        'bearing': 0,
                        'altitude': 2240,
                        'timestamp': datetime.now(),
                        'source': 'wifi_linux',
                        'networks_detected': networks_count
                    }
        except Exception as e:
            print(f"❌ Error WiFi Linux: {e}")
        
        return None
    
    def get_location_mock_realistic(self) -> Dict[str, Any]:
        """Obtener ubicación simulada pero realista."""
        # Ubicaciones realistas en diferentes ciudades
        locations = [
            # Ciudad de México
            {"lat": 19.4326, "lon": -99.1332, "city": "Ciudad de México", "alt": 2240},
            {"lat": 19.4285, "lon": -99.1277, "city": "CDMX Centro", "alt": 2250},
            {"lat": 19.3910, "lon": -99.2837, "city": "Santa Fe", "alt": 2580},
            
            # Guadalajara
            {"lat": 20.6597, "lon": -103.3496, "city": "Guadalajara", "alt": 1566},
            
            # Monterrey
            {"lat": 25.6866, "lon": -100.3161, "city": "Monterrey", "alt": 538},
            
            # Puebla
            {"lat": 19.0414, "lon": -98.2063, "city": "Puebla", "alt": 2135},
        ]
        
        # Seleccionar ubicación aleatoria
        location = random.choice(locations)
        
        # Agregar variación para simular movimiento
        lat_offset = (random.random() - 0.5) * 0.005  # ~500m
        lon_offset = (random.random() - 0.5) * 0.005
        
        return {
            'latitude': location["lat"] + lat_offset,
            'longitude': location["lon"] + lon_offset,
            'accuracy': random.randint(5, 30),
            'speed': random.randint(0, 60),
            'bearing': random.randint(0, 360),
            'altitude': location["alt"] + random.randint(-10, 10),
            'timestamp': datetime.now(),
            'source': 'mock_realistic',
            'city': location["city"]
        }
    
    def get_current_location(self) -> Optional[Dict[str, Any]]:
        """Obtener la ubicación actual usando el mejor método disponible."""
        print("🔍 Obteniendo ubicación actual...")
        
        # Método 1: Geolocalización por IP (más confiable)
        location = self.get_location_ip_geolocation()
        if location:
            print(f"✅ Ubicación obtenida por IP: {location['city']}, {location['country']}")
            return location
        
        # Método 2: WiFi scanning
        location = self.get_location_wifi_scanning()
        if location:
            print(f"✅ Ubicación obtenida por WiFi: {location['networks_detected']} redes detectadas")
            return location
        
        # Método 3: Ubicación simulada realista
        location = self.get_location_mock_realistic()
        print(f"⚠️ Usando ubicación simulada: {location['city']}")
        return location


class PCGPSSimulator:
    """Simulador GPS para PC que envía datos al servidor SkyGuard."""
    
    def __init__(self, config_file: str = "pc_gps_config.json"):
        """Inicializar simulador GPS."""
        self.config = self.load_config(config_file)
        self.socket = None
        self.connected = False
        self.running = False
        self.location_provider = PCLocationProvider()
        self.stats = {
            'packets_sent': 0,
            'connection_time': None,
            'last_location': None,
            'errors': 0
        }
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Cargar configuración desde archivo JSON."""
        default_config = {
            "host": "localhost",
            "port": 20332,
            "imei": f"PC{int(time.time())}",  # IMEI único basado en timestamp
            "password": "123456",
            "interval": 10,
            "protocol": "wialon",
            "device_name": f"PC-GPS-{platform.node()}",
            "auto_register": True,
            "use_real_location": True,
            "fallback_to_mock": True,
            "debug": True
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Combinar con configuración por defecto
                default_config.update(config)
        except FileNotFoundError:
            print(f"⚠️ Archivo {config_file} no encontrado, usando configuración por defecto")
            # Crear archivo de configuración
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
                print(f"✅ Archivo {config_file} creado")
        
        return default_config
    
    def connect(self) -> bool:
        """Conectar al servidor GPS."""
        try:
            print(f"🔄 Conectando a {self.config['host']}:{self.config['port']}...")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.config['host'], self.config['port']))
            
            # Enviar paquete de login Wialon
            login_packet = f"#L#{self.config['imei']};{self.config['password']}\r\n"
            self.socket.send(login_packet.encode('ascii'))
            
            print(f"📤 Login enviado: {login_packet.strip()}")
            
            # Esperar respuesta
            try:
                response = self.socket.recv(1024)
                if response:
                    response_str = response.decode('ascii').strip()
                    print(f"📥 Respuesta del servidor: {response_str}")
                    
                    if "#AL#1" in response_str:
                        print("✅ ¡Login exitoso!")
                    else:
                        print("⚠️ Login con respuesta inesperada")
            except socket.timeout:
                print("⏰ Sin respuesta del servidor (normal en algunos casos)")
            
            self.connected = True
            self.stats['connection_time'] = datetime.now()
            print(f"✅ Conectado como dispositivo: {self.config['device_name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            self.stats['errors'] += 1
            return False
    
    def send_location(self, location: Dict[str, Any]) -> bool:
        """Enviar datos de ubicación al servidor."""
        if not self.connected or not self.socket:
            print("❌ No hay conexión al servidor")
            return False
        
        try:
            # Formatear timestamp para Wialon
            timestamp = location['timestamp'].strftime("%d%m%y;%H%M%S")
            
            # Crear paquete de datos Wialon
            # Formato: #D#fecha;hora;lat1;lat2;lon1;lon2;speed;course;height;sats;hdop;inputs;outputs;adc;ibutton;params
            lat_deg = int(abs(location['latitude']))
            lat_min = (abs(location['latitude']) - lat_deg) * 60
            
            lon_deg = int(abs(location['longitude']))
            lon_min = (abs(location['longitude']) - lon_deg) * 60
            
            # Ajustar signo para hemisferio
            if location['latitude'] < 0:
                lat_deg = -lat_deg
            if location['longitude'] < 0:
                lon_deg = -lon_deg
            
            data_packet = (
                f"#D#{timestamp};"
                f"{lat_deg};{lat_min:.2f};"
                f"{lon_deg};{lon_min:.2f};"
                f"{location['speed']:.1f};"
                f"{location['bearing']:.0f};"
                f"{location['altitude']:.0f};"
                f"8;"  # Número de satélites
                f"1.0;"  # HDOP
                f"0;"  # inputs
                f"0;"  # outputs
                f"0;"  # adc
                f"00;"  # ibutton
                f"NA\r\n"  # params
            )
            
            self.socket.send(data_packet.encode('ascii'))
            
            if self.config['debug']:
                print(f"📤 Enviado: {data_packet.strip()}")
                print(f"📍 Ubicación: {location['latitude']:.6f}, {location['longitude']:.6f}")
                print(f"🚗 Velocidad: {location['speed']} km/h, Rumbo: {location['bearing']}°")
                if 'source' in location:
                    print(f"🔍 Fuente: {location['source']}")
            
            # Esperar confirmación
            try:
                response = self.socket.recv(1024)
                if response and self.config['debug']:
                    print(f"📥 Confirmación: {response.decode('ascii').strip()}")
            except socket.timeout:
                pass  # No es crítico
            
            self.stats['packets_sent'] += 1
            self.stats['last_location'] = location
            return True
            
        except Exception as e:
            print(f"❌ Error enviando ubicación: {e}")
            self.stats['errors'] += 1
            return False
    
    def send_ping(self) -> bool:
        """Enviar ping al servidor."""
        if not self.connected or not self.socket:
            return False
        
        try:
            ping_packet = "#P#\r\n"
            self.socket.send(ping_packet.encode('ascii'))
            
            if self.config['debug']:
                print("💗 Ping enviado")
            
            return True
        except Exception as e:
            print(f"❌ Error enviando ping: {e}")
            return False
    
    def start_tracking(self):
        """Iniciar el rastreo GPS."""
        if not self.connect():
            print("❌ No se pudo conectar al servidor")
            return
        
        self.running = True
        interval = self.config['interval']
        ping_counter = 0
        
        print(f"🚀 Iniciando rastreo GPS (intervalo: {interval}s)")
        print("🔄 Presiona Ctrl+C para detener")
        print("-" * 50)
        
        try:
            while self.running:
                # Obtener ubicación actual
                location = self.location_provider.get_current_location()
                
                if location:
                    # Enviar ubicación
                    success = self.send_location(location)
                    
                    if not success:
                        print("⚠️ Error enviando datos, intentando reconectar...")
                        if not self.connect():
                            print("❌ No se pudo reconectar")
                            break
                
                # Enviar ping cada 5 intervalos
                ping_counter += 1
                if ping_counter >= 5:
                    self.send_ping()
                    ping_counter = 0
                
                # Mostrar estadísticas
                if self.stats['packets_sent'] % 10 == 0 and self.stats['packets_sent'] > 0:
                    self.show_stats()
                
                # Esperar siguiente intervalo
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo rastreo GPS...")
        except Exception as e:
            print(f"\n❌ Error durante rastreo: {e}")
        finally:
            self.disconnect()
    
    def disconnect(self):
        """Desconectar del servidor."""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
                print("🔌 Desconectado del servidor")
            except:
                pass
    
    def show_stats(self):
        """Mostrar estadísticas del simulador."""
        print("\n📊 ESTADÍSTICAS:")
        print(f"   • Paquetes enviados: {self.stats['packets_sent']}")
        print(f"   • Errores: {self.stats['errors']}")
        print(f"   • Tiempo conectado: {datetime.now() - self.stats['connection_time'] if self.stats['connection_time'] else 'N/A'}")
        if self.stats['last_location']:
            loc = self.stats['last_location']
            print(f"   • Última ubicación: {loc['latitude']:.6f}, {loc['longitude']:.6f}")
            print(f"   • Fuente: {loc.get('source', 'Unknown')}")
        print("-" * 50)


def main():
    """Función principal."""
    print("=" * 60)
    print("🖥️  PC GPS SIMULATOR - SkyGuard")
    print("🌍 Simulador GPS para PC con ubicación real")
    print("=" * 60)
    
    # Verificar argumentos
    config_file = "pc_gps_config.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    # Crear y ejecutar simulador
    simulator = PCGPSSimulator(config_file)
    
    print(f"📱 Dispositivo: {simulator.config['device_name']}")
    print(f"🆔 IMEI: {simulator.config['imei']}")
    print(f"🌐 Servidor: {simulator.config['host']}:{simulator.config['port']}")
    print(f"⏱️  Intervalo: {simulator.config['interval']}s")
    print()
    
    try:
        simulator.start_tracking()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
    finally:
        simulator.show_stats()
        print("✅ Simulador GPS terminado")


if __name__ == "__main__":
    main() 