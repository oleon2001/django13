"""
Hardware GPS Service for SkyGuard
Procesa señales GPS directamente de hardware usando protocolos NMEA y binarios.
Basado en la implementación del proyecto django14.
"""

import socket
import struct
import threading
import time
import logging
import serial
import pynmea2
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone
import pytz

from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
from skyguard.apps.gps.protocols import GPSProtocolHandler

logger = logging.getLogger(__name__)

# Constantes para protocolos GPS
CRC_FUN = None
try:
    import crcmod
    CRC_FUN = crcmod.predefined.mkPredefinedCrcFun("x-25")
except ImportError:
    logger.warning("crcmod no disponible, CRC validation deshabilitado")

# Protocolos soportados
PROTOCOL_CONCOX = 0x01
PROTOCOL_MEILIGAO = 0x02
PROTOCOL_WIALON = 0x03
PROTOCOL_NMEA = 0x04

class HardwareGPSService:
    """Servicio para procesar señales GPS de hardware."""
    
    def __init__(self):
        self.active_connections = {}
        self.running = False
        self.threads = []
        
    def start_server(self, host='0.0.0.0', port=8001):
        """Inicia el servidor GPS para recibir datos de dispositivos."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"Servidor GPS iniciado en {host}:{port}")
            
            # Iniciar thread principal
            main_thread = threading.Thread(target=self._accept_connections)
            main_thread.daemon = True
            main_thread.start()
            self.threads.append(main_thread)
            
            return True
        except Exception as e:
            logger.error(f"Error iniciando servidor GPS: {e}")
            return False
    
    def stop_server(self):
        """Detiene el servidor GPS."""
        self.running = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        
        # Esperar que terminen los threads
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        logger.info("Servidor GPS detenido")
    
    def _accept_connections(self):
        """Acepta conexiones entrantes de dispositivos GPS."""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"Nueva conexión GPS desde {address}")
                
                # Crear thread para manejar la conexión
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                self.threads.append(client_thread)
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error aceptando conexión: {e}")
    
    def _handle_client(self, client_socket, address):
        """Maneja una conexión de cliente GPS."""
        try:
            client_socket.settimeout(30)  # 30 segundos timeout
            
            while self.running:
                # Recibir datos del dispositivo
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Procesar datos GPS
                self._process_gps_data(data, address)
                
        except socket.timeout:
            logger.warning(f"Timeout en conexión GPS desde {address}")
        except Exception as e:
            logger.error(f"Error manejando cliente GPS {address}: {e}")
        finally:
            client_socket.close()
            logger.info(f"Conexión GPS cerrada desde {address}")
    
    def _process_gps_data(self, data: bytes, address: tuple):
        """Procesa datos GPS recibidos."""
        try:
            # Detectar protocolo basado en los primeros bytes
            if data.startswith(b'\x78\x78'):
                self._process_concox_data(data, address)
            elif data.startswith(b'\x79\x79'):
                self._process_meiligao_data(data, address)
            elif data.startswith(b'$'):
                self._process_nmea_data(data, address)
            else:
                logger.warning(f"Datos GPS desconocidos desde {address}: {data[:20].hex()}")
                
        except Exception as e:
            logger.error(f"Error procesando datos GPS: {e}")
    
    def _process_concox_data(self, data: bytes, address: tuple):
        """Procesa datos del protocolo Concox."""
        try:
            if len(data) < 10:
                return
            
            # Extraer IMEI (primeros 8 bytes después del header)
            imei_bytes = data[2:10]
            imei = self._decode_imei(imei_bytes)
            
            # Extraer datos GPS
            if len(data) >= 25:
                gps_data = self._extract_concox_gps(data)
                if gps_data:
                    self._save_gps_location(imei, gps_data, 'concox')
                    
        except Exception as e:
            logger.error(f"Error procesando datos Concox: {e}")
    
    def _process_meiligao_data(self, data: bytes, address: tuple):
        """Procesa datos del protocolo Meiligao."""
        try:
            if len(data) < 10:
                return
            
            # Similar a Concox pero con header diferente
            imei_bytes = data[2:10]
            imei = self._decode_imei(imei_bytes)
            
            if len(data) >= 25:
                gps_data = self._extract_meiligao_gps(data)
                if gps_data:
                    self._save_gps_location(imei, gps_data, 'meiligao')
                    
        except Exception as e:
            logger.error(f"Error procesando datos Meiligao: {e}")
    
    def _process_nmea_data(self, data: bytes, address: tuple):
        """Procesa datos NMEA."""
        try:
            nmea_string = data.decode('utf-8', errors='ignore')
            
            # Procesar diferentes tipos de sentencias NMEA
            if '$GPRMC' in nmea_string:
                self._process_gprmc(nmea_string, address)
            elif '$GPGGA' in nmea_string:
                self._process_gpgga(nmea_string, address)
            elif '$GPGLL' in nmea_string:
                self._process_gpgll(nmea_string, address)
                
        except Exception as e:
            logger.error(f"Error procesando datos NMEA: {e}")
    
    def _decode_imei(self, imei_bytes: bytes) -> int:
        """Decodifica IMEI desde bytes BCD."""
        try:
            if not imei_bytes or len(imei_bytes) < 8:
                logger.warning(f"Datos IMEI insuficientes: {len(imei_bytes) if imei_bytes else 0} bytes")
                return 0
            
            imei = 0
            for byte in imei_bytes:
                # Convertir BCD a decimal
                high = (byte >> 4) & 0x0F
                low = byte & 0x0F
                
                # Validar que los valores BCD sean válidos (0-9)
                if high > 9 or low > 9:
                    logger.warning(f"Valor BCD inválido: high={high}, low={low}")
                    continue
                
                imei = imei * 100 + high * 10 + low
            
            # Validar que el IMEI tenga una longitud razonable
            if imei < 100000000000000:  # Mínimo 15 dígitos
                logger.warning(f"IMEI demasiado corto: {imei}")
                return 0
                
            return imei
            
        except Exception as e:
            logger.error(f"Error decodificando IMEI: {e}")
            return 0
    
    def _extract_concox_gps(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Extrae datos GPS del protocolo Concox."""
        try:
            if len(data) < 25:
                logger.warning(f"Datos Concox insuficientes: {len(data)} bytes")
                return None
            
            # Extraer datos GPS (bytes 10-25)
            gps_data = data[10:25]
            
            # Validar que tenemos suficientes datos
            if len(gps_data) < 15:
                logger.warning(f"Datos GPS Concox insuficientes: {len(gps_data)} bytes")
                return None
            
            # Extraer coordenadas (formato: DDMM.MMMM)
            # Usar '>i' (signed int) en lugar de '>I' (unsigned int) para evitar overflow
            lat_raw = struct.unpack('>i', gps_data[0:4])[0] / 1000000.0
            lon_raw = struct.unpack('>i', gps_data[4:8])[0] / 1000000.0
            
            # Convertir a formato decimal
            lat_deg = int(lat_raw / 100)
            lat_min = lat_raw % 100
            latitude = lat_deg + lat_min / 60.0
            
            lon_deg = int(lon_raw / 100)
            lon_min = lon_raw % 100
            longitude = lon_deg + lon_min / 60.0
            
            # Validar coordenadas
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                logger.warning(f"Coordenadas Concox inválidas: lat={latitude}, lon={longitude}")
                return None
            
            # Extraer velocidad y curso
            speed = struct.unpack('>H', gps_data[8:10])[0] / 10.0  # km/h
            course = struct.unpack('>H', gps_data[10:12])[0] / 10.0  # grados
            
            # Extraer timestamp
            timestamp = self._decode_utc(gps_data[12:15])
            
            return {
                'timestamp': timestamp,
                'latitude': latitude,
                'longitude': longitude,
                'speed': speed,
                'course': course,
                'satellites': 0,
                'fix_quality': 1
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo datos Concox: {e}")
            return None
    
    def _decode_utc(self, utc_data: bytes) -> datetime:
        """Decodifica tiempo UTC desde bytes."""
        try:
            if not utc_data or len(utc_data) < 6:
                logger.warning(f"Datos UTC insuficientes: {len(utc_data) if utc_data else 0} bytes")
                return timezone.now()
            
            # Extraer hora, minuto, segundo, día, mes, año
            hour, minute, second, day, month, year = struct.unpack('>BBBBBB', utc_data[:6])
            
            # Validar valores de tiempo
            if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                logger.warning(f"Valores de tiempo inválidos: {hour}:{minute}:{second}")
                return timezone.now()
            
            if not (1 <= day <= 31 and 1 <= month <= 12):
                logger.warning(f"Valores de fecha inválidos: {day}/{month}")
                return timezone.now()
            
            # Año 2000+ si es menor a 50, 1900+ si es mayor
            if year < 50:
                year += 2000
            else:
                year += 1900
            
            # Crear datetime
            dt = datetime(year, month, day, hour, minute, second)
            return timezone.make_aware(dt, pytz.UTC)
            
        except Exception as e:
            logger.error(f"Error decodificando UTC: {e}")
            return timezone.now()
    
    def _process_gprmc(self, nmea_string: str, address: tuple):
        """Procesa sentencia GPRMC."""
        try:
            msg = pynmea2.parse(nmea_string)
            if msg.status == 'A':  # Datos válidos
                # Validar que las coordenadas no sean None
                if msg.latitude is None or msg.longitude is None:
                    logger.warning(f"Coordenadas inválidas en GPRMC: lat={msg.latitude}, lon={msg.longitude}")
                    return
                
                gps_data = {
                    'timestamp': msg.datetime.replace(tzinfo=pytz.UTC) if msg.datetime else timezone.now(),
                    'latitude': float(msg.latitude),
                    'longitude': float(msg.longitude),
                    'speed': float(msg.spd_over_grnd * 1.852) if msg.spd_over_grnd else 0,  # Nudos a km/h
                    'course': float(msg.true_course) if msg.true_course else 0,
                    'satellites': 0,
                    'fix_quality': 1
                }
                
                # Usar IP como identificador temporal
                device_id = f"nmea_{address[0]}"
                self._save_gps_location(device_id, gps_data, 'nmea')
                
        except Exception as e:
            logger.error(f"Error procesando GPRMC: {e}")
    
    def _process_gpgga(self, nmea_string: str, address: tuple):
        """Procesa sentencia GPGGA."""
        try:
            msg = pynmea2.parse(nmea_string)
            if msg.gps_qual > 0:  # Fix válido
                # Validar que las coordenadas no sean None
                if msg.latitude is None or msg.longitude is None:
                    logger.warning(f"Coordenadas inválidas en GPGGA: lat={msg.latitude}, lon={msg.longitude}")
                    return
                
                gps_data = {
                    'timestamp': timezone.now(),
                    'latitude': float(msg.latitude),
                    'longitude': float(msg.longitude),
                    'speed': 0,
                    'course': 0,
                    'satellites': int(msg.num_sats) if msg.num_sats else 0,
                    'fix_quality': int(msg.gps_qual) if msg.gps_qual else 0,
                    'altitude': float(msg.altitude) if msg.altitude else 0
                }
                
                device_id = f"nmea_{address[0]}"
                self._save_gps_location(device_id, gps_data, 'nmea')
                
        except Exception as e:
            logger.error(f"Error procesando GPGGA: {e}")
    
    def _process_gpgll(self, nmea_string: str, address: tuple):
        """Procesa sentencia GPGLL."""
        try:
            msg = pynmea2.parse(nmea_string)
            if msg.status == 'A':  # Datos válidos
                # Validar que las coordenadas no sean None
                if msg.latitude is None or msg.longitude is None:
                    logger.warning(f"Coordenadas inválidas en GPGLL: lat={msg.latitude}, lon={msg.longitude}")
                    return
                
                gps_data = {
                    'timestamp': timezone.now(),
                    'latitude': float(msg.latitude),
                    'longitude': float(msg.longitude),
                    'speed': 0,
                    'course': 0,
                    'satellites': 0,
                    'fix_quality': 1
                }
                
                device_id = f"nmea_{address[0]}"
                self._save_gps_location(device_id, gps_data, 'nmea')
                
        except Exception as e:
            logger.error(f"Error procesando GPGLL: {e}")
    
    def _save_gps_location(self, device_id, gps_data: dict, protocol: str):
        """Guarda ubicación GPS en la base de datos."""
        try:
            # Validar datos GPS requeridos
            if not gps_data or 'latitude' not in gps_data or 'longitude' not in gps_data:
                logger.warning(f"Datos GPS incompletos para dispositivo {device_id}")
                return
            
            # Validar coordenadas
            lat = gps_data.get('latitude')
            lon = gps_data.get('longitude')
            
            if lat is None or lon is None:
                logger.warning(f"Coordenadas inválidas para dispositivo {device_id}: lat={lat}, lon={lon}")
                return
            
            # Convertir device_id a string para evitar errores de isdigit()
            device_id_str = str(device_id)
            
            # Buscar o crear dispositivo
            device = self._get_or_create_device(device_id_str, protocol)
            if not device:
                logger.error(f"No se pudo obtener/crear dispositivo para {device_id_str}")
                return
            
            # Crear punto geoespacial
            try:
                position = Point(float(lon), float(lat))
            except (ValueError, TypeError) as e:
                logger.error(f"Error creando punto geoespacial: {e}, lat={lat}, lon={lon}")
                return
            
            # Validar timestamp
            timestamp = gps_data.get('timestamp')
            if not timestamp:
                timestamp = timezone.now()
            elif timestamp.tzinfo is None:
                timestamp = timezone.make_aware(timestamp)
            
            # Calcular accuracy basado en HDOP y satélites
            hdop = gps_data.get('hdop', 0)
            satellites = gps_data.get('satellites', 0)
            
            # Fórmula simple para accuracy: HDOP * factor + offset basado en satélites
            if satellites >= 8:
                accuracy = max(5.0, hdop * 2.5)  # Alta precisión
            elif satellites >= 6:
                accuracy = max(10.0, hdop * 3.0)  # Buena precisión
            elif satellites >= 4:
                accuracy = max(15.0, hdop * 4.0)  # Precisión media
            else:
                accuracy = max(25.0, hdop * 5.0)  # Baja precisión
            
            # Crear registro de ubicación
            location = GPSLocation.objects.create(
                device=device,
                position=position,
                timestamp=timestamp,
                speed=gps_data.get('speed', 0),
                course=gps_data.get('course', 0),
                altitude=gps_data.get('altitude', 0),
                satellites=satellites,
                accuracy=accuracy,
                hdop=hdop,
                pdop=gps_data.get('pdop', 0),
                fix_quality=gps_data.get('fix_quality', 0)
            )
            
            # Actualizar posición del dispositivo
            device.position = position
            device.speed = gps_data.get('speed', 0)
            device.course = gps_data.get('course', 0)
            device.altitude = gps_data.get('altitude', 0)
            device.last_connection = timezone.now()
            device.connection_status = 'ONLINE'
            device.update_heartbeat()
            device.save()
            
            # Crear evento de tracking
            event = GPSEvent.objects.create(
                device=device,
                type='TRACK',
                timestamp=timestamp,
                position=position,
                speed=gps_data.get('speed', 0),
                course=gps_data.get('course', 0),
                altitude=gps_data.get('altitude', 0),
                source=protocol
            )
            
            logger.info(f"GPS data saved: {device.name} at {position.y:.6f}, {position.x:.6f}")
            
        except Exception as e:
            logger.error(f"Error guardando ubicación GPS: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _get_or_create_device(self, device_id, protocol: str) -> Optional[GPSDevice]:
        """Obtiene o crea un dispositivo GPS."""
        try:
            # Normalizar device_id a string primero
            device_id_str = str(device_id)
            
            # Si es un IMEI numérico (string que contiene solo dígitos)
            if device_id_str.isdigit():
                imei = int(device_id_str)
                
                # Evitar IMEI = 0, usar un valor por defecto
                if imei == 0:
                    imei = 999999999999999  # IMEI temporal para dispositivos sin IMEI real
                
                try:
                    device, created = GPSDevice.objects.get_or_create(
                        imei=imei,
                        defaults={
                            'name': f"Device {imei}",
                            'protocol': protocol,
                            'connection_status': 'ONLINE',
                            'owner_id': 1  # Usuario por defecto
                        }
                    )
                    if created:
                        logger.info(f"Dispositivo GPS creado: {device.name}")
                    return device
                except Exception as e:
                    # Si hay conflicto de IMEI, intentar buscar por nombre
                    logger.warning(f"Conflicto de IMEI {imei}, buscando por nombre: {e}")
                    try:
                        device = GPSDevice.objects.get(name=f"Device {imei}")
                        return device
                    except GPSDevice.DoesNotExist:
                        # Crear con nombre único
                        import time
                        unique_name = f"Device_{imei}_{int(time.time())}"
                        device = GPSDevice.objects.create(
                            imei=imei,
                            name=unique_name,
                            protocol=protocol,
                            connection_status='ONLINE',
                            owner_id=1
                        )
                        logger.info(f"Dispositivo GPS creado con nombre único: {device.name}")
                        return device
            else:
                # Para dispositivos NMEA o identificadores no numéricos, usar nombre
                try:
                    device, created = GPSDevice.objects.get_or_create(
                        name=device_id_str,
                        defaults={
                            'imei': 999999999999999,  # IMEI temporal
                            'protocol': protocol,
                            'connection_status': 'ONLINE',
                            'owner_id': 1  # Usuario por defecto
                        }
                    )
                    if created:
                        logger.info(f"Dispositivo GPS creado: {device.name}")
                    return device
                except Exception as e:
                    logger.error(f"Error creando dispositivo con nombre {device_id_str}: {e}")
                    return None
                
        except Exception as e:
            logger.error(f"Error obteniendo/creando dispositivo: {e}")
            return None
    
    def read_serial_gps(self, port="/dev/ttyS0", baudrate=9600):
        """Lee datos GPS desde puerto serial (para Raspberry Pi)."""
        try:
            ser = serial.Serial(port, baudrate=baudrate, timeout=1)
            logger.info(f"Conectado a GPS en {port}")
            
            while self.running:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore')
                    if line.strip():
                        # Procesar línea NMEA
                        self._process_nmea_data(line.encode(), ('serial', port))
                except serial.SerialException as e:
                    logger.error(f"Error serial: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error leyendo GPS serial: {e}")
            
            ser.close()
            
        except Exception as e:
            logger.error(f"Error conectando a GPS serial {port}: {e}")
    
    def start_serial_monitoring(self, port="/dev/ttyS0", baudrate=9600):
        """Inicia monitoreo de GPS serial en thread separado."""
        serial_thread = threading.Thread(
            target=self.read_serial_gps,
            args=(port, baudrate)
        )
        serial_thread.daemon = True
        serial_thread.start()
        self.threads.append(serial_thread)
        logger.info(f"Monitoreo serial GPS iniciado en {port}")

    def _extract_meiligao_gps(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Extrae datos GPS del protocolo Meiligao."""
        try:
            if len(data) < 25:
                logger.warning(f"Datos Meiligao insuficientes: {len(data)} bytes")
                return None
            
            # Similar a Concox pero con validaciones adicionales
            gps_data = data[10:25]
            
            if len(gps_data) < 15:
                logger.warning(f"Datos GPS Meiligao insuficientes: {len(gps_data)} bytes")
                return None
            
            # Extraer coordenadas
            # Usar '>i' (signed int) en lugar de '>I' (unsigned int) para evitar overflow
            lat_raw = struct.unpack('>i', gps_data[0:4])[0] / 1000000.0
            lon_raw = struct.unpack('>i', gps_data[4:8])[0] / 1000000.0
            
            # Convertir a formato decimal
            lat_deg = int(lat_raw / 100)
            lat_min = lat_raw % 100
            latitude = lat_deg + lat_min / 60.0
            
            lon_deg = int(lon_raw / 100)
            lon_min = lon_raw % 100
            longitude = lon_deg + lon_min / 60.0
            
            # Validar coordenadas
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                logger.warning(f"Coordenadas Meiligao inválidas: lat={latitude}, lon={longitude}")
                return None
            
            # Extraer velocidad y curso
            speed = struct.unpack('>H', gps_data[8:10])[0] / 10.0
            course = struct.unpack('>H', gps_data[10:12])[0] / 10.0
            
            # Extraer timestamp
            timestamp = self._decode_utc(gps_data[12:15])
            
            return {
                'timestamp': timestamp,
                'latitude': latitude,
                'longitude': longitude,
                'speed': speed,
                'course': course,
                'satellites': 0,
                'fix_quality': 1
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo datos Meiligao: {e}")
            return None


# Instancia global del servicio
hardware_gps_service = HardwareGPSService() 