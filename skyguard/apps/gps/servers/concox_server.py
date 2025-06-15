"""
Modern Concox TCP server implementation.
Migrated from old backend to use new structure.
"""
import socket
import struct
import threading
import sys
import time
import binascii
from datetime import datetime
from pytz import utc
from django.contrib.gis.geos import Point
from django.db import transaction

from skyguard.apps.gps.servers.base import BaseGPSRequestHandler, BaseGPSServer
from skyguard.apps.gps.models import GPSDevice, GPSEvent, GPRSSession
from skyguard.apps.gps.protocols.concox import ConcoxProtocol


def decode_imei(data):
    """Decode IMEI from binary data."""
    return struct.unpack(">Q", data)[0]


def crc_fun(data):
    """Calculate CRC for Concox protocol."""
    crc = 0
    for byte in data:
        if isinstance(byte, str):
            byte = ord(byte)
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return crc & 0xFFFF


class ConcoxRequestHandler(BaseGPSRequestHandler):
    """Modern Concox protocol handler."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = ConcoxProtocol()
        self.data_buffer = b""
        self.session = None
        
    def setup(self):
        """Initialize the handler."""
        super().setup()
        self.request.settimeout(30.0)  # 30 second timeout
        self.request.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        print(f"Concox device connected from {self.client_address}")
        
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
                
    def get_utc_time(self, data):
        """Extract UTC time from Concox data."""
        year, month, day, hour, minute, second = struct.unpack("BBBBBB", data)
        return datetime(2000 + year, month, day, hour, minute, second, tzinfo=utc)
        
    def get_mcc_mnc(self, data):
        """Extract MCC/MNC from data."""
        mcc, mnc = struct.unpack(">HH", data[:4])
        if mcc & 0x8000:
            return mcc & 0x7FFF, mnc, data[4:]
        else:
            return mcc, mnc >> 8, data[3:]
            
    def get_lac_ci(self, data, is_4g=False):
        """Extract LAC and Cell ID."""
        if is_4g:
            lac, ci = struct.unpack(">IQ", data[:12])
            return lac, ci, data[12:]
        else:
            lac, ci1, ci2 = struct.unpack(">HBH", data[:5])
            ci = (ci1 << 16) | ci2
            return lac, ci, data[5:]
            
    def handle_gps_data(self, payload):
        """Handle GPS location data."""
        if len(payload) < 24:
            return
            
        # Extract timestamp
        utc_time = self.get_utc_time(payload[:6])
        
        # Extract GPS data
        ns, lat, lon, speed, cs = struct.unpack(">BIIBH", payload[6:18])
        lat = lat / 1800000.0
        lon = lon / 1800000.0
        
        # Extract cellular data
        mcc, mnc, rest = self.get_mcc_mnc(payload[18:])
        
        # Extract course and direction
        course = cs & 0x03FF
        if cs & 0x0400 == 0:
            lat = -lat
        if cs & 0x0800:
            lon = -lon
            
        # Extract LAC and Cell ID
        lac, ci, rest = self.get_lac_ci(rest, self.proto == 0xA0)
        
        # Extract additional data
        if len(rest) >= 3:
            acc, dum, drl = struct.unpack(">BBB", rest[:3])
        else:
            acc = dum = drl = 0
            
        # Check GPS fix
        if cs & 0x1000:
            print(f"GPS FIX: Position {lat:.7f}, {lon:.7f} @ {ns&0x0f} sats")
            print(f"Speed: {speed} km/h, Course: {course}°, ACC: {acc}")
            print(f"Cell: {mcc}.{mnc}:{lac}-{ci}")
            
            if self.device:
                # Save location event
                position = Point(lon, lat)
                event = GPSEvent.objects.create(
                    device=self.device,
                    event_type="LOCATION",
                    position=position,
                    timestamp=utc_time,
                    speed=speed,
                    course=course,
                    altitude=0,
                    satellites=ns & 0x0f
                )
                
                # Update device position
                self.device.position = position
                self.device.last_seen = utc_time
                self.device.speed = speed
                self.device.course = course
                self.device.save()
        else:
            print(f"GPS NOT FIXED: Position {lat:.7f}, {lon:.7f} - DISCARDED")
            
    def handle_wifi_data(self, payload):
        """Handle WiFi scan data."""
        if len(payload) < 22:
            return
            
        utc_time = self.get_utc_time(payload[:6])
        mcc, mnc, rest = self.get_mcc_mnc(payload[6:])
        
        print(f"WiFi scan at {utc_time.isoformat()}")
        print(f"MCC/MNC: {mcc}-{mnc}")
        
        # Extract WiFi data
        if len(rest) >= 16:
            mac1 = rest[2:8]
            wifi1 = rest[8] if len(rest) > 8 else 0
            mac2 = rest[9:15] if len(rest) > 14 else b'\x00' * 6
            wifi2 = rest[15] if len(rest) > 15 else 0
            
            print(f"WiFi 1: {binascii.hexlify(mac1).decode()} RSSI: {wifi1}")
            print(f"WiFi 2: {binascii.hexlify(mac2).decode()} RSSI: {wifi2}")
            
    def handle_alarm(self, payload):
        """Handle alarm data."""
        if len(payload) < 9:
            return
            
        mcc, mnc, rest = self.get_mcc_mnc(payload)
        lac, ci, rest = self.get_lac_ci(rest, self.proto == 0xA5)
        
        if len(rest) >= 5:
            ti, vl, ss, alert, lang = struct.unpack(">BBBBB", rest[:5])
            print(f"ALARM from cell {mcc}.{mnc} {lac}-{ci}")
            print(f"TI={ti} VL={vl} SS={ss} Alert={alert:02X} Lang={lang}")
            
            if self.device:
                GPSEvent.objects.create(
                    device=self.device,
                    event_type="ALARM",
                    timestamp=datetime.now(utc),
                    data=f"Alert:{alert:02X} TI:{ti} VL:{vl} SS:{ss}"
                )
                
    def send_packet(self, proto, payload):
        """Send response packet to device."""
        plen = len(payload) + 5
        packet = struct.pack(">HBB", 0x7878, plen, proto) + payload + struct.pack(">H", self.isn)
        crc = crc_fun(packet[2:])
        packet += struct.pack(">HH", crc, 0x0D0A)
        
        try:
            self.request.send(packet)
            print(f"SENT: {binascii.hexlify(packet).decode()}")
        except socket.error as e:
            print(f"Error sending packet: {e}")
            
    def get_packet(self, data):
        """Extract and validate packet from data."""
        if len(data) < 10:
            raise ValueError("Packet too short")
            
        head = struct.unpack(">H", data[:2])[0]
        
        if head == 0x7878:
            self.plen = data[2]
            if len(data) < self.plen + 5:
                raise ValueError(f"Incomplete packet: {len(data)} < {self.plen + 5}")
                
            self.proto = data[3]
            self.payload = data[4:self.plen - 1]
            tail = struct.unpack(">H", data[3 + self.plen:5 + self.plen])[0]
            
            if tail != 0x0D0A:
                raise ValueError(f"Invalid tail: {tail:04X}")
                
            # Extract ISN and CRC
            self.isn, pcrc = struct.unpack(">HH", data[self.plen - 3:self.plen + 1])
            
            # Validate CRC
            crc = crc_fun(data[2:self.plen + 1])
            if pcrc != crc:
                raise ValueError(f"Invalid CRC: {pcrc:04X} != {crc:04X}")
                
            packet = data[:5 + self.plen]
            remaining = data[5 + self.plen:]
            
            print(f"RECV: {binascii.hexlify(packet).decode()}")
            return remaining
            
        else:
            raise ValueError(f"Invalid header: {head:04X}")
            
    def handle_packets(self, data):
        """Process incoming packets."""
        while data:
            try:
                data = self.get_packet(data)
                
                if self.proto == 0x01:  # Login packet
                    if len(self.payload) >= 8:
                        self.imei = decode_imei(self.payload[:8])
                        self.find_or_create_device(self.imei)
                        
                        if len(self.payload) >= 12:
                            ti, tz = struct.unpack(">HH", self.payload[8:12])
                            print(f"Login from IMEI {self.imei} TI={ti:04X} TZ={tz:04X}")
                        
                        self.send_packet(0x01, b"")  # Login response
                        
                elif self.proto in [0x19, 0xA5]:  # Alarm packet
                    self.handle_alarm(self.payload)
                    if self.proto == 0xA5:
                        self.send_packet(0x26, b"")
                        
                elif self.proto in [0x22, 0x2D, 0xA0]:  # GPS location
                    self.handle_gps_data(self.payload)
                    if self.proto == 0x2D:
                        self.send_packet(0x2D, b"")
                        
                elif self.proto == 0x23:  # Heartbeat
                    if len(self.payload) >= 5:
                        tic, volts, gsmss, pad = struct.unpack(">BHBH", self.payload)
                        print(f"Heartbeat TIC={tic:02X} Volts={volts/100.0:.2f}V GSM={gsmss} Pad={pad:04X}")
                        
                    self.send_packet(0x23, b"")  # Heartbeat response
                    
                elif self.proto in [0x2C, 0xA2]:  # WiFi info
                    self.handle_wifi_data(self.payload)
                    
                elif self.proto == 0x8A:  # Time calibration
                    dt = datetime.now(utc)
                    payload = struct.pack(">BBBBBB", 
                                        dt.year % 100, dt.month, dt.day,
                                        dt.hour, dt.minute, dt.second)
                    self.send_packet(0x8A, payload)
                    print(f"Time calibrated to: {dt.isoformat()}")
                    
                elif self.proto == 0x94:  # General info
                    if len(self.payload) >= 1:
                        info_type = self.payload[0]
                        if info_type == 0 and len(self.payload) >= 3:
                            voltage = struct.unpack(">H", self.payload[1:3])[0] / 100.0
                            print(f"External voltage: {voltage:.2f}V")
                        elif info_type == 4:
                            print(f"Device info: {self.payload[1:].decode('ascii', errors='ignore')}")
                        elif info_type == 10 and len(self.payload) >= 27:
                            imei = decode_imei(self.payload[1:9])
                            imsi = decode_imei(self.payload[9:17])
                            iccid = decode_imei(self.payload[17:27])
                            print(f"IMEI: {imei}")
                            print(f"IMSI: {imsi}")
                            print(f"ICCID: {iccid}")
                            
                else:
                    print(f"Unknown protocol: {self.proto:02X}")
                    
            except ValueError as e:
                print(f"Packet error: {e}")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break
                
    def handle(self):
        """Handle the connection."""
        timeouts = 0
        
        while True:
            try:
                data = self.request.recv(2048)
                if not data:
                    break
                    
                self.data_buffer += data
                
                # Process complete packets
                if self.data_buffer:
                    self.handle_packets(self.data_buffer)
                    self.data_buffer = b""
                    timeouts = 0
                    
            except socket.timeout:
                timeouts += 1
                if timeouts >= 3:  # 90 seconds total
                    print(f"Connection timeout from {self.client_address}")
                    break
                    
            except Exception as e:
                print(f"Connection error: {e}")
                break
                
    def finish(self):
        """Clean up connection."""
        super().finish()
        print(f"Concox device disconnected from {self.client_address}")


class ConcoxServer(BaseGPSServer):
    """Concox TCP server."""
    
    def __init__(self, host='', port=55300):
        """Initialize the Concox server."""
        super().__init__(host=host, port=port, handler_class=ConcoxRequestHandler)
        print(f"Concox server initialized on port {port}")


def start_concox_server(host='', port=55300):
    """Start the Concox server."""
    server = ConcoxServer(host=host, port=port)
    server.start()


if __name__ == "__main__":
    import os
    import django
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
    django.setup()
    
    # Start server
    try:
        print("Starting Concox GPS Server...")
        start_concox_server()
    except KeyboardInterrupt:
        print("\nShutting down Concox server...") 