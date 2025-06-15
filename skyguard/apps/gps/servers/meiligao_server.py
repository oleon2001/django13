"""
Modern Meiligao UDP server implementation.
Migrated from old backend to use new structure.
"""
import socket
import struct
import threading
import sys
import time
import binascii
import crcmod
from datetime import datetime
from pytz import utc
from django.contrib.gis.geos import Point
from django.db import transaction

from skyguard.apps.gps.servers.base import BaseGPSRequestHandler, BaseGPSServer
from skyguard.apps.gps.models import GPSDevice, GPSEvent
from skyguard.apps.gps.protocols.meiligao import MeiligaoProtocol


def nmea2deg(nmea_str):
    """Convert NMEA coordinate to decimal degrees."""
    try:
        degrees = float(nmea_str[:-7])
        minutes = float(nmea_str[-7:])
        return degrees + minutes / 60.0
    except (ValueError, IndexError):
        return 0.0


def nmea2date(time_str, date_str):
    """Convert NMEA time and date to datetime object."""
    try:
        # Time format: HHMMSS.SSS
        hours = int(time_str[:2])
        minutes = int(time_str[2:4])
        seconds = int(float(time_str[4:]))
        
        # Date format: DDMMYY
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year = 2000 + int(date_str[4:6])
        
        return datetime(year, month, day, hours, minutes, seconds, tzinfo=utc)
    except (ValueError, IndexError):
        return datetime.now(utc)


class MeiligaoRequestHandler(BaseGPSRequestHandler):
    """Modern Meiligao protocol handler (UDP)."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = MeiligaoProtocol()
        self.crc = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, rev=False)
        
    def setup(self):
        """Initialize the handler."""
        super().setup()
        print(f"Meiligao device connected from {self.client_address}")
        
    def find_or_create_device(self, imei):
        """Find or create device by IMEI."""
        try:
            self.device = GPSDevice.objects.get(imei=imei)
            print(f"Found existing device: {self.device.name} (IMEI: {imei})")
        except GPSDevice.DoesNotExist:
            if 10000000000000 <= imei <= 899999999999999:
                self.device = GPSDevice.objects.create(
                    imei=imei,
                    name=f"{imei:015d}"
                )
                print(f"Created new device: {self.device.name} (IMEI: {imei})")
            else:
                print(f"Invalid IMEI: {imei}. Not creating device.")
                self.device = None
                
    def get_id(self, data):
        """Extract IMEI from hex data."""
        hexs = []
        for byte in data:
            if isinstance(byte, str):
                byte = ord(byte)
            hexs.append(byte >> 4)
            hexs.append(byte & 15)
            
        imei = 0
        for digit in hexs:
            if digit != 15:
                imei = imei * 10 + digit
        return imei
        
    def handle_position_data(self, payload):
        """Handle position data from GPRMC."""
        try:
            fields = payload.split(b'|')
            if not fields:
                return
                
            gprmc = fields[0].decode('ascii', errors='ignore').split(',')
            if len(gprmc) < 9:
                return
                
            # Extract coordinates
            if gprmc[4] and gprmc[2]:
                lon = nmea2deg(gprmc[4])
                if gprmc[5] == "W":
                    lon = -lon
                    
                lat = nmea2deg(gprmc[2])
                if gprmc[3] == 'S':
                    lat = -lat
                    
                # Extract time
                timestamp = nmea2date(gprmc[1], gprmc[9])
                
                print(f"Position: {lat:.7f}, {lon:.7f} at {timestamp.isoformat()}")
                
                if self.device:
                    position = Point(lon, lat)
                    
                    # Save location event
                    GPSEvent.objects.create(
                        device=self.device,
                        event_type="LOCATION",
                        position=position,
                        timestamp=timestamp,
                        speed=0,
                        course=0,
                        altitude=0
                    )
                    
                    # Update device position
                    self.device.position = position
                    self.device.last_seen = timestamp
                    self.device.save()
                    
        except Exception as e:
            print(f"Error processing position data: {e}")
            
    def validate_packet(self, data):
        """Validate Meiligao packet."""
        if len(data) < 8:
            print("Packet too short")
            return False
            
        # Check start and end markers
        if data[:2] != b'$$' or data[-2:] != b'\r\n':
            print("Invalid packet markers")
            return False
            
        # Check CRC
        pcrc = struct.unpack(">H", data[-4:-2])[0]
        dlen = struct.unpack(">H", data[2:4])[0]
        ecrc = self.crc(data[:-4])
        
        if pcrc != ecrc:
            print(f"Invalid CRC: expected {ecrc:04x}, got {pcrc:04x}")
            return False
            
        if dlen != len(data):
            print(f"Invalid data length: expected {dlen}, got {len(data)}")
            return False
            
        return True
        
    def handle(self):
        """Handle the UDP packet."""
        try:
            data = self.request[0]
            socket = self.request[1]
            
            print(f"Received {len(data)} bytes from {self.client_address}")
            print(f"Data: {binascii.hexlify(data).decode()}")
            
            # Validate packet
            if not self.validate_packet(data):
                return
                
            # Extract device ID
            id_hex = data[4:11]
            self.imei = self.get_id(id_hex)
            
            # Extract command
            command = struct.unpack(">H", data[11:13])[0]
            payload = data[13:-4]
            
            print(f"Command: {command:04x}, IMEI: {self.imei}, Payload: {len(payload)} bytes")
            
            # Find or create device
            self.find_or_create_device(self.imei)
            
            # Process command
            if command == 0x9955:  # Position data
                print("Processing position data")
                self.handle_position_data(payload)
                
            elif command == 0x5000:  # Heartbeat
                print("Heartbeat received")
                if self.device:
                    self.device.last_seen = datetime.now(utc)
                    self.device.save()
                    
            else:
                print(f"Unknown command: {command:04x}")
                
        except Exception as e:
            print(f"Error handling packet: {e}")
            import traceback
            traceback.print_exc()
            
    def finish(self):
        """Clean up."""
        super().finish()
        print(f"Meiligao packet processed from {self.client_address}")


class MeiligaoServer(BaseGPSServer):
    """Meiligao UDP server."""
    
    def __init__(self, host='', port=62000):
        """Initialize the Meiligao server."""
        # For UDP servers, we need to use UDPServer instead of TCPServer
        import socketserver
        self.server = socketserver.ThreadingUDPServer((host, port), MeiligaoRequestHandler)
        self.port = port
        print(f"Meiligao UDP server initialized on port {port}")
        
    def start(self):
        """Start the server."""
        print("_" * 80)
        print(f"Meiligao UDP server started on port {self.port}")
        print("-" * 80)
        sys.stdout.flush()
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("_" * 80)
            print("Meiligao server received signal, exiting.")
            print("-" * 80)
            sys.stdout.flush()
            
    def stop(self):
        """Stop the server."""
        self.server.shutdown()
        self.server.server_close()


def start_meiligao_server(host='', port=62000):
    """Start the Meiligao server."""
    server = MeiligaoServer(host=host, port=port)
    server.start()


if __name__ == "__main__":
    import os
    import django
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
    django.setup()
    
    # Start server
    try:
        print("Starting Meiligao GPS Server...")
        start_meiligao_server()
    except KeyboardInterrupt:
        print("\nShutting down Meiligao server...") 