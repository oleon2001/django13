"""
Wialon protocol handler.
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from django.contrib.gis.geos import Point
import struct
import binascii
import logging

from skyguard.core.interfaces import IProtocolHandler
from skyguard.apps.gps.models.device import GPSDevice

logger = logging.getLogger(__name__)

class WialonProtocolHandler(IProtocolHandler):
    """Handler for Wialon protocol."""
    
    def __init__(self):
        """Initialize the protocol handler."""
        self.supported_protocols = {
            'wialon': WialonProtocolHandler
        }
    
    def get_handler(self, protocol: str) -> 'WialonProtocolHandler':
        """Get the appropriate protocol handler."""
        handler_class = self.supported_protocols.get(protocol.lower())
        if not handler_class:
            raise ValueError(f"Unsupported protocol: {protocol}")
        return handler_class()
    
    def decode_packet(self, data: bytes) -> Dict[str, Any]:
        """Decode a Wialon protocol packet."""
        try:
            # Remove any whitespace and decode
            data = data.strip()
            if not data:
                return None
                
            # Check packet type
            if data.startswith(b'#L#'):
                return self._decode_login(data)
            elif data.startswith(b'#D#'):
                return self._decode_data(data)
            else:
                logger.warning(f"Unknown packet type: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error decoding packet: {e}")
            return None
    
    def _decode_login(self, data: bytes) -> Dict[str, Any]:
        """Decode a login packet."""
        try:
            # Format: #L#<IMEI>;<password>\r\n
            parts = data[3:-2].split(b';')
            if len(parts) != 2:
                raise ValueError("Invalid login packet format")
                
            imei = int(parts[0])
            password = parts[1].decode('ascii')
            
            return {
                'type': 'login',
                'imei': imei,
                'password': password
            }
            
        except Exception as e:
            logger.error(f"Error decoding login packet: {e}")
            return None
    
    def _decode_data(self, data: bytes) -> Dict[str, Any]:
        """Decode a data packet."""
        try:
            # Format: #D#<date>;<time>;<lat1>;<lat2>;<lon1>;<lon2>;<speed>;<course>;<height>;<sats>;<hdop>;<inputs>;<outputs>;<adc>;<ibutton>;<params>\r\n
            parts = data[3:-2].split(b';')
            if len(parts) < 15:
                raise ValueError("Invalid data packet format")
                
            # Parse date and time
            date_str = parts[0].decode('ascii')
            time_str = parts[1].decode('ascii')
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%d%m%y %H%M%S")
            
            # Parse coordinates
            lat1 = float(parts[2])
            lat2 = float(parts[3])
            lon1 = float(parts[4])
            lon2 = float(parts[5])
            
            # Convert to decimal degrees
            lat = lat1 + lat2/60.0
            lon = lon1 + lon2/60.0
            
            # Parse other fields
            speed = float(parts[6])
            course = float(parts[7])
            height = float(parts[8])
            sats = int(parts[9])
            hdop = float(parts[10])
            inputs = int(parts[11])
            outputs = int(parts[12])
            
            return {
                'type': 'data',
                'timestamp': timestamp,
                'position': Point(lon, lat),
                'speed': speed,
                'course': course,
                'altitude': height,
                'satellites': sats,
                'hdop': hdop,
                'inputs': inputs,
                'outputs': outputs
            }
            
        except Exception as e:
            logger.error(f"Error decoding data packet: {e}")
            return None
    
    def encode_command(self, command: str, params: Dict[str, Any]) -> bytes:
        """Encode a command for the device."""
        try:
            if command == 'ping':
                return b'#P#\r\n'
            elif command == 'reboot':
                return b'#R#\r\n'
            else:
                raise ValueError(f"Unsupported command: {command}")
                
        except Exception as e:
            logger.error(f"Error encoding command: {e}")
            return None
    
    def validate_packet(self, data: bytes) -> bool:
        """Validate a Wialon protocol packet."""
        try:
            if not data:
                return False
            # Validar primero el final del paquete
            if not data.endswith(b'\r\n'):
                return False
            # Ahora quitar espacios para validar el tipo
            data_stripped = data.strip()
            if not data_stripped:
                return False
            # Check packet type
            if not (data_stripped.startswith(b'#L#') or data_stripped.startswith(b'#D#') or data_stripped.startswith(b'#P#')):
                return False
            return True
        except Exception as e:
            logger.error(f"Error validating packet: {e}")
            return False
    
    def send_ping(self, device: GPSDevice) -> Dict[str, Any]:
        """Send a ping command to the device."""
        try:
            command = self.encode_command('ping', {})
            if not command:
                return None
                
            return {
                'command': command,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error sending ping: {e}")
            return None 