#!/usr/bin/env python3
"""
Cliente GPS para simular un dispositivo GPS real.
Envía datos de ubicación al servidor Falkon usando el protocolo Wialon.
"""

import socket
import time
import json
import sys
import threading
from datetime import datetime
from typing import Optional, Dict, Any

# Intenta importar librerías para obtener ubicación real
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    # Para Android con Termux
    import android
    from android.permissions import request_permission, Permission
    HAS_ANDROID = True
except ImportError:
    HAS_ANDROID = False


class GPSLocationProvider:
    """Proveedor de ubicación GPS."""
    
    def __init__(self):
        """Inicializar el proveedor de ubicación."""
        self.current_location = None
        self.last_update = None
        
        if HAS_ANDROID:
            self._setup_android_gps()
    
    def _setup_android_gps(self):
        """Configurar GPS en Android (Termux)."""
        try:
            # Solicitar permisos
            request_permission(Permission.ACCESS_FINE_LOCATION)
            request_permission(Permission.ACCESS_COARSE_LOCATION)
            print("✅ Permisos de ubicación solicitados")
        except Exception as e:
            print(f"❌ Error solicitando permisos: {e}")
    
    def get_location_android(self) -> Optional[Dict[str, Any]]:
        """Obtener ubicación usando Android API."""
        if not HAS_ANDROID:
            return None
            
        try:
            # Obtener ubicación actual
            location = android.get_location()
            if location:
                return {
                    'latitude': location['latitude'],
                    'longitude': location['longitude'],
                    'accuracy': location.get('accuracy', 0),
                    'speed': location.get('speed', 0),
                    'bearing': location.get('bearing', 0),
                    'altitude': location.get('altitude', 0),
                    'timestamp': datetime.now()
                }
        except Exception as e:
            print(f"❌ Error obteniendo ubicación Android: {e}")
        
        return None
    
    def get_location_ip(self) -> Optional[Dict[str, Any]]:
        """Obtener ubicación aproximada usando IP."""
        if not HAS_REQUESTS:
            return None
            
        try:
            response = requests.get('http://ip-api.com/json/', timeout=5)
            data = response.json()
            
            if data['status'] == 'success':
                return {
                    'latitude': data['lat'],
                    'longitude': data['lon'],
                    'accuracy': 10000,  # Baja precisión
                    'speed': 0,
                    'bearing': 0,
                    'altitude': 0,
                    'timestamp': datetime.now(),
                    'source': 'IP'
                }
        except Exception as e:
            print(f"❌ Error obteniendo ubicación por IP: {e}")
        
        return None
    
    def get_location_mock(self) -> Dict[str, Any]:
        """Obtener ubicación simulada (para pruebas)."""
        # Ubicación simulada en Ciudad de México
        import random
        base_lat = 19.4326
        base_lon = -99.1332
        
        # Agregar variación aleatoria para simular movimiento
        lat_offset = (random.random() - 0.5) * 0.01  # ~1km
        lon_offset = (random.random() - 0.5) * 0.01
        
        return {
            'latitude': base_lat + lat_offset,
            'longitude': base_lon + lon_offset,
            'accuracy': random.randint(5, 50),
            'speed': random.randint(0, 80),
            'bearing': random.randint(0, 360),
            'altitude': random.randint(2200, 2300),
            'timestamp': datetime.now(),
            'source': 'mock'
        }
    
    def get_current_location(self) -> Optional[Dict[str, Any]]:
        """Obtener la ubicación actual usando el mejor método disponible."""
        # Intentar Android primero
        location = self.get_location_android()
        if location:
            location['source'] = 'android_gps'
            return location
        
        # Luego IP
        location = self.get_location_ip()
        if location:
            return location
        
        # Finalmente mock
        return self.get_location_mock()


class WialonGPSClient:
    """Cliente GPS que simula un dispositivo usando protocolo Wialon."""
    
    def __init__(self, host: str, port: int, imei: str, password: str = "123456"):
        """
        Inicializar cliente GPS.
        
        Args:
            host: IP del servidor
            port: Puerto del servidor
            imei: IMEI del dispositivo
            password: Contraseña del dispositivo
        """
        self.host = host
        self.port = port
        self.imei = imei
        self.password = password
        self.socket = None
        self.connected = False
        self.running = False
        
        self.location_provider = GPSLocationProvider()
        
    def connect(self) -> bool:
        """Conectar al servidor GPS."""
        try:
            print(f"🔄 Conectando a {self.host}:{self.port}...")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            # Enviar paquete de login
            login_packet = f"#L#{self.imei};{self.password}\r\n"
            self.socket.send(login_packet.encode('ascii'))
            
            print(f"📤 Enviado login: {login_packet.strip()}")
            
            # Esperar respuesta (opcional)
            try:
                response = self.socket.recv(1024)
                if response:
                    print(f"📥 Respuesta del servidor: {response.decode('ascii').strip()}")
            except socket.timeout:
                print("⏰ No hay respuesta del servidor (normal)")
            
            self.connected = True
            print("✅ ¡Conectado al servidor!")
            return True
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del servidor."""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        print("🔌 Desconectado del servidor")
    
    def send_location(self, location: Dict[str, Any]) -> bool:
        """Enviar ubicación al servidor."""
        if not self.connected or not self.socket:
            return False
        
        try:
            # Formatear fecha y hora para protocolo Wialon
            now = location['timestamp']
            date = now.strftime("%d%m%y")
            time_str = now.strftime("%H%M%S")
            
            # Convertir coordenadas a formato Wialon (grados y minutos)
            lat = abs(location['latitude'])
            lon = abs(location['longitude'])
            lat1 = int(lat)
            lat2 = (lat - lat1) * 60
            lon1 = int(lon)
            lon2 = (lon - lon1) * 60
            
            speed = int(location.get('speed', 0))
            course = int(location.get('bearing', 0))
            altitude = int(location.get('altitude', 0))
            
            # Construir paquete de datos Wialon
            data_packet = (
                f"#D#{date};{time_str};{lat1};{lat2:.4f};{lon1};{lon2:.4f};"
                f"{speed};{course};{altitude};8;1.0;0;0;0;;NA\r\n"
            )
            
            self.socket.send(data_packet.encode('ascii'))
            
            print(f"📡 Ubicación enviada:")
            print(f"   📍 Lat: {location['latitude']:.6f}, Lon: {location['longitude']:.6f}")
            print(f"   🏃 Velocidad: {speed} km/h, Rumbo: {course}°")
            print(f"   📊 Precisión: {location.get('accuracy', 0)}m")
            print(f"   🌐 Fuente: {location.get('source', 'unknown')}")
            print(f"   📤 Paquete: {data_packet.strip()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error enviando ubicación: {e}")
            return False
    
    def start_tracking(self, interval: int = 10):
        """Iniciar rastreo continuo."""
        if not self.connected:
            print("❌ No conectado al servidor")
            return
        
        self.running = True
        print(f"🎯 Iniciando rastreo continuo (cada {interval} segundos)")
        print("📱 Presiona Ctrl+C para detener")
        
        try:
            while self.running and self.connected:
                # Obtener ubicación actual
                location = self.location_provider.get_current_location()
                
                if location:
                    success = self.send_location(location)
                    if not success:
                        print("❌ Error enviando ubicación, reintentando...")
                        break
                else:
                    print("❌ No se pudo obtener ubicación")
                
                # Esperar antes del siguiente envío
                for _ in range(interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Detenido por el usuario")
        except Exception as e:
            print(f"❌ Error en rastreo: {e}")
        finally:
            self.disconnect()


def main():
    """Función principal."""
    print("=" * 60)
    print("📱 FALKON GPS DEVICE SIMULATOR")
    print("=" * 60)
    
    # Configuración por defecto
    config = {
        'host': 'localhost',
        'port': 20332,  # Puerto Wialon por defecto
        'imei': '123456789012345',
        'password': '123456',
        'interval': 10
    }
    
    # Cargar configuración desde archivo si existe
    try:
        with open('gps_config.json', 'r') as f:
            user_config = json.load(f)
            config.update(user_config)
        print("📄 Configuración cargada desde gps_config.json")
    except FileNotFoundError:
        print("📄 Usando configuración por defecto")
    
    # Mostrar configuración
    print(f"🌐 Servidor: {config['host']}:{config['port']}")
    print(f"📱 IMEI: {config['imei']}")
    print(f"⏱️ Intervalo: {config['interval']} segundos")
    print()
    
    # Verificar capacidades
    print("🔍 Verificando capacidades:")
    print(f"   Android API: {'✅' if HAS_ANDROID else '❌'}")
    print(f"   Requests: {'✅' if HAS_REQUESTS else '❌'}")
    print()
    
    # Crear y configurar cliente
    client = WialonGPSClient(
        host=config['host'],
        port=config['port'],
        imei=config['imei'],
        password=config['password']
    )
    
    # Conectar al servidor
    if client.connect():
        # Iniciar rastreo
        client.start_tracking(config['interval'])
    else:
        print("❌ No se pudo conectar al servidor")
        sys.exit(1)


if __name__ == "__main__":
    main() 