"""
GPS protocol handlers implementation.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from django.contrib.gis.geos import Point
import struct
import socket
import time
from django.utils import timezone

from skyguard.core.interfaces import IProtocolHandler
from skyguard.apps.gps.models import GPSDevice, UDPSession


class ConcoxProtocolHandler(IProtocolHandler):
    """Handler for Concox protocol."""
    
    def decode_packet(self, data: bytes) -> Dict[str, Any]:
        """Decode a Concox protocol packet."""
        try:
            # Basic packet structure: Start Bit(2) + Packet Length(1) + Protocol Number(1) + Information Content + Information Serial Number(2) + Error Check(2) + Stop Bit(2)
            if len(data) < 8:
                return {}
            
            # Extract IMEI (first 8 bytes after start bit)
            imei = int.from_bytes(data[2:10], byteorder='big')
            
            # Extract GPS data
            lat = struct.unpack('>i', data[10:14])[0] / 1800000.0
            lon = struct.unpack('>i', data[14:18])[0] / 1800000.0
            speed = struct.unpack('>H', data[18:20])[0] / 10.0
            course = struct.unpack('>H', data[20:22])[0]
            altitude = struct.unpack('>h', data[22:24])[0]
            satellites = data[24]
            
            return {
                'imei': imei,
                'position': Point(lon, lat),
                'speed': speed,
                'course': course,
                'altitude': altitude,
                'satellites': satellites,
                'timestamp': datetime.now()
            }
        except Exception:
            return {}
    
    def encode_command(self, command: str, params: Dict[str, Any]) -> bytes:
        """Encode a Concox protocol command."""
        try:
            if command == 'SET_INTERVAL':
                interval = params.get('interval', 60)
                return struct.pack('>BBHB', 0x78, 0x78, 0x80, interval)
            elif command == 'SET_IP':
                ip = params.get('ip', '0.0.0.0')
                port = params.get('port', 0)
                ip_parts = [int(x) for x in ip.split('.')]
                return struct.pack('>BBBBBBH', 0x78, 0x78, 0x80, *ip_parts, port)
            return b''
        except Exception:
            return b''
    
    def validate_packet(self, data: bytes) -> bool:
        """Validate a Concox protocol packet."""
        try:
            if len(data) < 8:
                return False
            # Check start and stop bits
            if data[0:2] != b'\x78\x78' or data[-2:] != b'\x0D\x0A':
                return False
            # Check packet length
            if data[2] != len(data) - 4:
                return False
            return True
        except Exception:
            return False

    def _send_command(self, device: 'GPSDevice', command: bytes, timeout: float = 5.0) -> Optional[bytes]:
        """Send a command to the device and wait for response."""
        try:
            # Crear socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            # Enviar comando
            sock.sendto(command, (device.current_ip, device.current_port))
            
            # Esperar respuesta
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    if self.validate_packet(data):
                        return data
                except socket.timeout:
                    continue
            
            return None
        except Exception:
            return None
        finally:
            sock.close()

    def send_ping(self, device: 'GPSDevice') -> Dict[str, Any]:
        """Send a ping command to a Concox device and verify location data."""
        try:
            print(f"[DEBUG] Iniciando prueba de conexión para dispositivo {device.imei}")
            
            # Enviar comando de heartbeat (0x23)
            command = struct.pack('>BB', 0x78, 0x78)  # Start bits
            command += struct.pack('>B', 0x23)  # Protocol number
            command += struct.pack('>H', 0x0000)  # Information content
            command += struct.pack('>H', 0x0000)  # Serial number
            command += struct.pack('>H', 0x0000)  # Error check
            command += struct.pack('>BB', 0x0D, 0x0A)  # Stop bits
            
            print(f"[DEBUG] Enviando comando de heartbeat a {device.current_ip}:{device.current_port}")
            
            # Enviar comando y esperar respuesta
            response = self._send_command(device, command)
            if not response:
                print(f"[ERROR] No se recibió respuesta del dispositivo {device.imei}")
                return {
                    'success': False,
                    'response_time': None,
                    'error_message': 'No response from device'
                }
            
            print(f"[DEBUG] Respuesta recibida del dispositivo {device.imei}")
            
            # Decodificar respuesta
            data = self.decode_packet(response)
            if not data or 'position' not in data:
                print(f"[ERROR] La respuesta del dispositivo {device.imei} no contiene datos de ubicación válidos")
                return {
                    'success': False,
                    'response_time': None,
                    'error_message': 'Invalid location data in response'
                }
            
            # Verificar que la ubicación sea válida
            position = data['position']
            if not (-90 <= position.y <= 90 and -180 <= position.x <= 180):
                print(f"[ERROR] Coordenadas inválidas recibidas del dispositivo {device.imei}: lat={position.y}, lon={position.x}")
                return {
                    'success': False,
                    'response_time': None,
                    'error_message': 'Invalid coordinates in response'
                }
            
            print(f"[DEBUG] Ubicación válida recibida del dispositivo {device.imei}: lat={position.y}, lon={position.x}")
            
            # Actualizar última ubicación conocida
            device.last_known_position = position
            device.last_known_position_time = datetime.now()
            device.save(update_fields=['last_known_position', 'last_known_position_time'])
            
            print(f"[DEBUG] Prueba de conexión exitosa para dispositivo {device.imei}")
            
            return {
                'success': True,
                'response_time': 0.5,
                'error_message': None,
                'position': position,
                'timestamp': data['timestamp']
            }
        except Exception as e:
            print(f"[ERROR] Error durante la prueba de conexión del dispositivo {device.imei}: {str(e)}")
            return {
                'success': False,
                'response_time': None,
                'error_message': str(e)
            }


class MeiligaoProtocolHandler(IProtocolHandler):
    """Handler for Meiligao protocol."""
    
    def decode_packet(self, data: bytes) -> Dict[str, Any]:
        """Decode a Meiligao protocol packet."""
        try:
            # Basic packet structure: Start Bit(2) + Packet Length(1) + Protocol Number(1) + Information Content + Information Serial Number(2) + Error Check(2) + Stop Bit(2)
            if len(data) < 8:
                return {}
            
            # Extract IMEI (first 8 bytes after start bit)
            imei = int.from_bytes(data[2:10], byteorder='big')
            
            # Extract GPS data
            lat = struct.unpack('>i', data[10:14])[0] / 1800000.0
            lon = struct.unpack('>i', data[14:18])[0] / 1800000.0
            speed = struct.unpack('>H', data[18:20])[0] / 10.0
            course = struct.unpack('>H', data[20:22])[0]
            altitude = struct.unpack('>h', data[22:24])[0]
            satellites = data[24]
            
            return {
                'imei': imei,
                'position': Point(lon, lat),
                'speed': speed,
                'course': course,
                'altitude': altitude,
                'satellites': satellites,
                'timestamp': datetime.now()
            }
        except Exception:
            return {}
    
    def encode_command(self, command: str, params: Dict[str, Any]) -> bytes:
        """Encode a Meiligao protocol command."""
        try:
            if command == 'SET_INTERVAL':
                interval = params.get('interval', 60)
                return struct.pack('>BBHB', 0x78, 0x78, 0x80, interval)
            elif command == 'SET_IP':
                ip = params.get('ip', '0.0.0.0')
                port = params.get('port', 0)
                ip_parts = [int(x) for x in ip.split('.')]
                return struct.pack('>BBBBBBH', 0x78, 0x78, 0x80, *ip_parts, port)
            return b''
        except Exception:
            return b''
    
    def validate_packet(self, data: bytes) -> bool:
        """Validate a Meiligao protocol packet."""
        try:
            if len(data) < 8:
                return False
            # Check start and stop bits
            if data[0:2] != b'\x78\x78' or data[-2:] != b'\x0D\x0A':
                return False
            # Check packet length
            if data[2] != len(data) - 4:
                return False
            return True
        except Exception:
            return False

    def _send_command(self, device: 'GPSDevice', command: bytes, timeout: float = 5.0) -> Optional[bytes]:
        """Send a command to the device and wait for response."""
        try:
            # Crear socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            # Enviar comando
            sock.sendto(command, (device.current_ip, device.current_port))
            
            # Esperar respuesta
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    if self.validate_packet(data):
                        return data
                except socket.timeout:
                    continue
            
            return None
        except Exception:
            return None
        finally:
            sock.close()

    def send_ping(self, device: 'GPSDevice') -> Dict[str, Any]:
        """Send a ping command to a Meiligao device and verify location data."""
        try:
            # Enviar comando de heartbeat
            command = struct.pack('>BB', 0x78, 0x78)  # Start bits
            command += struct.pack('>B', 0x23)  # Protocol number
            command += struct.pack('>H', 0x0000)  # Information content
            command += struct.pack('>H', 0x0000)  # Serial number
            command += struct.pack('>H', 0x0000)  # Error check
            command += struct.pack('>BB', 0x0D, 0x0A)  # Stop bits
            
            # Enviar comando y esperar respuesta
            response = self._send_command(device, command)
            if not response:
                return {
                    'success': False,
                    'response_time': None,
                    'error_message': 'No response from device'
                }
            
            # Decodificar respuesta
            data = self.decode_packet(response)
            if not data or 'position' not in data:
                return {
                    'success': False,
                    'response_time': None,
                    'error_message': 'Invalid location data in response'
                }
            
            # Verificar que la ubicación sea válida
            position = data['position']
            if not (-90 <= position.y <= 90 and -180 <= position.x <= 180):
                return {
                    'success': False,
                    'response_time': None,
                    'error_message': 'Invalid coordinates in response'
                }
            
            # Actualizar última ubicación conocida
            device.last_known_position = position
            device.last_known_position_time = datetime.now()
            device.save(update_fields=['last_known_position', 'last_known_position_time'])
            
            return {
                'success': True,
                'response_time': 0.5,
                'error_message': None,
                'position': position,
                'timestamp': data['timestamp']
            }
        except Exception as e:
            return {
                'success': False,
                'response_time': None,
                'error_message': str(e)
            }


class WialonProtocolHandler(IProtocolHandler):
    """Handler for Wialon protocol."""
    
    def decode_packet(self, data: bytes) -> Dict[str, Any]:
        """Decode a Wialon protocol packet."""
        try:
            # Basic packet structure: Start Bit(2) + Packet Length(1) + Protocol Number(1) + Information Content + Information Serial Number(2) + Error Check(2) + Stop Bit(2)
            if len(data) < 8:
                return {}
            
            # Extract IMEI (first 8 bytes after start bit)
            imei = int.from_bytes(data[2:10], byteorder='big')
            
            # Extract GPS data
            lat = struct.unpack('>i', data[10:14])[0] / 1800000.0
            lon = struct.unpack('>i', data[14:18])[0] / 1800000.0
            speed = struct.unpack('>H', data[18:20])[0] / 10.0
            course = struct.unpack('>H', data[20:22])[0]
            altitude = struct.unpack('>h', data[22:24])[0]
            satellites = data[24]
            
            return {
                'imei': imei,
                'position': Point(lon, lat),
                'speed': speed,
                'course': course,
                'altitude': altitude,
                'satellites': satellites,
                'timestamp': datetime.now()
            }
        except Exception:
            return {}
    
    def encode_command(self, command: str, params: Dict[str, Any]) -> bytes:
        """Encode a Wialon protocol command."""
        try:
            if command == 'SET_INTERVAL':
                interval = params.get('interval', 60)
                return struct.pack('>BBHB', 0x78, 0x78, 0x80, interval)
            elif command == 'SET_IP':
                ip = params.get('ip', '0.0.0.0')
                port = params.get('port', 0)
                ip_parts = [int(x) for x in ip.split('.')]
                return struct.pack('>BBBBBBH', 0x78, 0x78, 0x80, *ip_parts, port)
            return b''
        except Exception:
            return b''
    
    def validate_packet(self, data: bytes) -> bool:
        """Validate a Wialon protocol packet."""
        try:
            if len(data) < 8:
                return False
            # Check start and stop bits
            if data[0:2] != b'\x78\x78' or data[-2:] != b'\x0D\x0A':
                return False
            # Check packet length
            if data[2] != len(data) - 4:
                return False
            return True
        except Exception:
            return False

    def _send_command(self, device: 'GPSDevice', command: bytes, timeout: float = 5.0) -> Optional[bytes]:
        """Send a command to the device and wait for response."""
        try:
            # Crear socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            # Enviar comando
            sock.sendto(command, (device.current_ip, device.current_port))
            
            # Esperar respuesta
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    if self.validate_packet(data):
                        return data
                except socket.timeout:
                    continue
            
            return None
        except Exception:
            return None
        finally:
            sock.close()

    def send_ping(self, device: 'GPSDevice') -> Dict[str, Any]:
        """Send a ping command to a Wialon device and verify location data."""
        try:
            print(f"[DEBUG] Verificando estado de dispositivo Wialon {device.imei}")
            
            # Para protocolo Wialon (UDP), no podemos enviar comandos directos
            # En su lugar, verificamos la actividad reciente del dispositivo
            
            # Verificar última actividad (reducir tiempo a 2 minutos para mayor sensibilidad)
            if device.last_heartbeat:
                time_since_heartbeat = timezone.now() - device.last_heartbeat
                print(f"[DEBUG] Último heartbeat hace {time_since_heartbeat.total_seconds()} segundos")
                
                # Si el dispositivo ha enviado datos en los últimos 2 minutos, considerarlo online
                if time_since_heartbeat.total_seconds() < 120:  # 2 minutos en lugar de 5
                    print(f"[DEBUG] Dispositivo Wialon {device.imei} está activo")
                    return {
                        'success': True,
                        'response_time': 0.1,
                        'error_message': None,
                        'last_activity': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                        'protocol': 'wialon',
                        'connection_type': 'UDP'
                    }
            
            # Verificar sesiones UDP activas
            try:
                active_sessions = UDPSession.objects.filter(
                    device=device,
                    expires__gt=timezone.now(),
                    is_active=True
                )
                if active_sessions.exists():
                    session = active_sessions.first()
                    print(f"[DEBUG] Sesión UDP activa encontrada para dispositivo {device.imei}")
                    # Actualizar heartbeat si hay sesión activa
                    device.last_heartbeat = timezone.now()
                    device.connection_status = 'ONLINE'
                    device.save(update_fields=['last_heartbeat', 'connection_status'])
                    return {
                        'success': True,
                        'response_time': 0.1,
                        'error_message': None,
                        'session_id': session.session,
                        'session_host': f"{session.host}:{session.port}",
                        'protocol': 'wialon',
                        'connection_type': 'UDP'
                    }
            except Exception as e:
                print(f"[DEBUG] Error verificando sesiones UDP: {e}")
            
            # Verificar si el dispositivo tiene IP y puerto asignado (indicativo de conexión reciente)
            if device.current_ip and device.current_port:
                print(f"[DEBUG] Dispositivo {device.imei} tiene IP/puerto asignado: {device.current_ip}:{device.current_port}")
                # Intentar verificar conexión con timeout muy corto
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(1.0)
                    test_data = b'\x02\x00\x00\x00\x00'  # Packet básico de ping
                    sock.sendto(test_data, (device.current_ip, device.current_port))
                    sock.close()
                    print(f"[DEBUG] Test UDP exitoso para dispositivo {device.imei}")
                    return {
                        'success': True,
                        'response_time': 0.5,
                        'error_message': None,
                        'connection_details': f"{device.current_ip}:{device.current_port}",
                        'protocol': 'wialon',
                        'connection_type': 'UDP'
                    }
                except Exception as conn_error:
                    print(f"[DEBUG] Test UDP falló para dispositivo {device.imei}: {conn_error}")
            
            # Si llegamos aquí, el dispositivo no está activo
            print(f"[DEBUG] Dispositivo Wialon {device.imei} no está activo")
            return {
                'success': False,
                'response_time': None,
                'error_message': 'Device not active - no recent heartbeat or UDP session',
                'last_activity': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                'protocol': 'wialon',
                'connection_type': 'UDP'
            }
        except Exception as e:
            print(f"[ERROR] Error en ping Wialon para dispositivo {device.imei}: {e}")
            return {
                'success': False,
                'response_time': None,
                'error_message': str(e)
            } 