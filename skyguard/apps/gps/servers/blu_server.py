"""
BLU (Bluetooth) GPS server implementation.
Migrated from legacy django14 system to modern architecture.
"""
import socket
import struct
import threading
import sys
import time
import binascii
from datetime import datetime, timedelta
from pytz import utc, timezone
from django.db import transaction
from django.contrib.gis.geos import Point
from django.conf import settings

from skyguard.apps.gps.servers.base import BaseGPSRequestHandler, BaseGPSServer
from skyguard.apps.gps.models import (
    GPSDevice, GPSLocation, GPSEvent, PressureWeightLog, 
    UDPSession, DeviceHarness
)


# BLU Protocol Constants
PKTID_LOGIN = 0x01
PKTID_PING = 0x02
PKTID_DEVINFO = 0x03
PKTID_DATA = 0x04

RSPID_SESSION = 0x10
RSPID_LOGIN = 0x11

CMDID_DEVINFO = 0x20
CMDID_DATA = 0x21
CMDID_ACK = 0x22

RECID_TRACKS = 0x30
RECID_PEOPLE = 0x31

SESSION_EXPIRE = timedelta(hours=10)


class BLUProtocol:
    """BLU protocol decoder."""
    
    @staticmethod
    def calculate_crc(data):
        """Calculate CRC for BLU protocol."""
        crc = 0xFFFF
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
    
    @staticmethod
    def unpack_position(data):
        """Unpack GPS position record."""
        ct, lat, lon, speed = struct.unpack("<IffB", data)
        dt = datetime.fromtimestamp(ct, utc)
        if abs(dt - datetime.now(utc)) > timedelta(days=20):
            dt = datetime.now(utc)
            print("Invalid time in position")
        return {
            'date': dt,
            'pos': Point(lon, lat),
            'speed': speed
        }
    
    @staticmethod
    def unpack_tof(data):
        """Unpack TOF (Time of Flight) counter record."""
        ct, count_in, count_out, mac1, mac2 = struct.unpack("<IIIIH", data)
        dt = datetime.fromtimestamp(ct, utc)
        mac = f"{((mac2 << 32) | mac1):012X}"
        if abs(dt - datetime.now(utc)) > timedelta(days=20):
            dt = datetime.now(utc)
            print("Invalid time in people")
        return {
            'date': dt,
            'in': count_in,
            'out': count_out,
            'id': mac
        }


class BLURequestHandler(BaseGPSRequestHandler):
    """Modern BLU protocol handler."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = BLUProtocol()
        self.session = None
        self.device = None
        self.queries = []
        self.last_pos = None
        self.host = None
        self.port = None
        
    def setup(self):
        """Initialize the handler."""
        super().setup()
        self.time_check = datetime.now(utc)
        self.local_time = datetime.now(timezone(settings.TIME_ZONE))
        
    def find_or_create_device(self, imei):
        """Find or create device by IMEI."""
        try:
            self.device = GPSDevice.objects.get(imei=imei)
        except GPSDevice.DoesNotExist:
            print("Device not found. Creating...")
            try:
                harness = DeviceHarness.objects.get(name="default")
            except DeviceHarness.DoesNotExist:
                harness = DeviceHarness.objects.create(
                    name="default",
                    in00='Pánico', in01='Ignición', in02='i02', in03='i03',
                    in04='i04', in05='i05', in06='BAT_DOK', in07='BAT_CHG',
                    in08='BAT_FLT', in09='i09', in10='i10', in11='i11',
                    in12='i12', in13='i13', in14='i14', in15='i15',
                    out00='Motor', out01='', out02='', out03='',
                    out04='', out05='', out06='', out07='',
                    out08='', out09='', out10='', out11='',
                    out12='', out13='', out14='', out15='',
                    input_cfg='03070000000007000700000000000000'
                )
            
            self.device = GPSDevice.objects.create(
                imei=imei,
                name=f"{imei:015d}",
                harness=harness,
                comments=""
            )
        return self.device
    
    def handle_login(self, data):
        """Handle login packet."""
        if len(data) != 15:
            print(f"Invalid LOGIN size: {len(data)}")
            return
            
        imei, = struct.unpack("<Q", data[1:9])
        mac, = struct.unpack("<Q", data[9:15] + b'\x00\x00')
        
        print(f"Session request from IMEI: {imei:015d} MAC ID: {mac:012X}")
        
        # Find or create device
        self.device = self.find_or_create_device(imei)
        
        # Delete old sessions
        UDPSession.objects.filter(device=self.device).delete()
        
        # Create new session
        expires = self.time_check + SESSION_EXPIRE
        self.session = UDPSession.objects.create(
            device=self.device,
            expires=expires,
            host=self.host,
            port=self.port
        )
        
        # Send response
        if not self.device.comments:
            response = struct.pack("<BLB", RSPID_SESSION, self.session.session, CMDID_DEVINFO)
        else:
            response = struct.pack("<BLB", RSPID_SESSION, self.session.session, CMDID_DATA)
            
        self.request[1].sendto(response, self.client_address)
        print("Sent login response")
    
    def find_session(self, data):
        """Find existing session."""
        session_no, = struct.unpack("<L", data[1:5])
        self.session = None
        
        try:
            self.session = UDPSession.objects.get(session=session_no)
            self.session.expires = self.time_check + SESSION_EXPIRE
            self.session.host = self.host
            self.session.port = self.port
            self.device = GPSDevice.objects.get(imei=self.session.device.imei)
            print(f"AVL: {self.device}")
            self.session.save()
        except UDPSession.DoesNotExist:
            print(f"Unknown session # {session_no}")
        except Exception as e:
            print(f"Error finding session: {e}")
    
    def send_login_request(self):
        """Send login request."""
        self.request[1].sendto(bytes([RSPID_LOGIN]), self.client_address)
        print("Sent login request.")
    
    def handle_ping(self, data):
        """Handle ping packet with position."""
        pos = self.protocol.unpack_position(data[5:18])
        
        # Update device position
        self.device.position = pos["pos"]
        self.device.speed = pos["speed"]
        self.device.last_log = self.device.date = pos["date"]
        self.device.save()
        
        # Send response
        response = struct.pack("<BLBB", RSPID_SESSION, self.session.session, CMDID_ACK, 0)
        self.request[1].sendto(response, self.client_address)
        print(f"Got PING w/position from {self.device.imei}")
    
    def handle_devinfo(self):
        """Handle device info response."""
        print(f"Got DevInfo response from {self.device.imei}")
        self.device.comments = "INFO OK"
        self.device.save()
        
        response = struct.pack("<BLBB", RSPID_SESSION, self.session.session, CMDID_ACK, 0)
        self.request[1].sendto(response, self.client_address)
    
    def unpack_tracks(self, data):
        """Unpack track positions."""
        positions = []
        while len(data) >= 13:
            pos = self.protocol.unpack_position(data[:13])
            data = data[13:]
            positions.append(pos)
            
        print(f"Unpacked {len(positions)} positions.")
        
        # Check for duplicate events
        if positions:
            start_date = positions[0]["date"]
            end_date = positions[-1]["date"]
            existing_events = GPSEvent.objects.filter(
                device=self.device,
                timestamp__range=(start_date, end_date)
            )
            
            if existing_events.exists():
                print("Duplicate track records found")
            else:
                # Create events
                events = []
                for pos in positions:
                    event = GPSEvent(
                        device=self.device,
                        event_type="TRACK",
                        position=pos['pos'],
                        speed=pos['speed'],
                        course=0,
                        altitude=0,
                        timestamp=pos['date']
                    )
                    events.append(event)
                
                GPSEvent.objects.bulk_create(events)
                self.last_pos = positions[-1]
    
    def unpack_people(self, data):
        """Unpack people count records."""
        people = []
        while len(data) >= 18:
            people.append(self.protocol.unpack_tof(data[:18]))
            data = data[18:]
            
        print(f"Unpacked {len(people)} TOF records.")
        
        # Create people count records
        values = []
        for person in people:
            # Check for duplicates
            duplicate = PressureWeightLog.objects.filter(
                device=self.device,
                sensor=person["id"],
                timestamp=person["date"]
            )
            
            if not duplicate.exists():
                values.append(PressureWeightLog(
                    device=self.device,
                    sensor=person["id"],
                    timestamp=person["date"],
                    psi1=str(person["in"]),
                    psi2=str(person["out"])
                ))
        
        if values:
            PressureWeightLog.objects.bulk_create(values)
            
        if len(values) != len(people):
            print(f"Dropped {len(people) - len(values)} TOF duplicates.")
    
    def handle_data(self, data):
        """Handle data packet."""
        # Check CRC
        if self.protocol.calculate_crc(data) != 0:
            print("CRC Failure. Discarding packet")
            return
            
        self.last_pos = None
        packet_data = data[5:-2]
        records = []
        id0 = id1 = 0
        
        # Extract records
        while packet_data:
            if len(packet_data) <= 8:
                print(f"Invalid record header, len={len(packet_data)}")
                break
            else:
                record_id, size = struct.unpack("<II", packet_data[:8])
                if size > 248:
                    print(f"Invalid record size = {size}")
                    break
                else:
                    id1 = record_id
                    if not id0:
                        id0 = record_id
                    record = packet_data[8:8+size]
                    packet_data = packet_data[8+size:]
                    records.append(record)
        
        if id0:
            print(f"Extracted {len(records)} records.")
            
            # Send response
            response = struct.pack("<BIBBII", RSPID_SESSION, self.session.session, 
                                 CMDID_ACK, len(records), id0, id1)
            self.request[1].sendto(response, self.client_address)
            
            # Process records
            for record in records:
                record_id = record[0]
                if record_id == RECID_TRACKS:
                    self.unpack_tracks(record[1:])
                elif record_id == RECID_PEOPLE:
                    self.unpack_people(record[1:])
                else:
                    print(f"Invalid RECID: {record_id:02X}")
            
            # Update device with last position
            if self.last_pos:
                self.device.position = self.last_pos["pos"]
                self.device.speed = self.last_pos["speed"]
                self.device.date = self.last_pos["date"]
                
            self.device.last_log = self.time_check
            self.device.save()
    
    def handle(self):
        """Handle the BLU connection."""
        try:
            data, sock = self.request
            self.host = self.client_address[0]
            self.port = self.client_address[1]
            
            print(f"RX len = {len(data)} from {self.host}:{self.port}")
            
            packet_id = data[0]
            
            if packet_id == PKTID_LOGIN:
                self.handle_login(data)
            else:
                self.find_session(data)
                if not self.session:
                    self.send_login_request()
                else:
                    if packet_id == PKTID_PING:
                        self.handle_ping(data)
                    elif packet_id == PKTID_DEVINFO:
                        self.handle_devinfo()
                    elif packet_id == PKTID_DATA:
                        self.handle_data(data)
                    else:
                        print(f"Invalid token {packet_id}")
                        
        except Exception as e:
            print(f"Error handling BLU packet: {e}")
            raise
    
    def finish(self):
        """Clean up after handling the request."""
        try:
            dt = datetime.now(utc) - self.time_check
            print(f"Finished processing packet in {dt.seconds}.{dt.microseconds:06d} seconds")
        except Exception as e:
            print(f"Error in finish: {e}")
        finally:
            super().finish()


class BLUServer(BaseGPSServer):
    """BLU GPS server."""
    
    def __init__(self, host='', port=50100):
        """Initialize the BLU server."""
        # Override to use UDP server
        if not BLURequestHandler:
            raise ValueError("handler_class must be provided")
            
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.port = self.server.getsockname()[1]
        self.handler_class = BLURequestHandler
        
    def start(self):
        """Start the server."""
        print("_" * 80)
        print(f"BLU UDP Server started on port {self.port}")
        print("-" * 80)
        sys.stdout.flush()
        
        try:
            while True:
                try:
                    data, addr = self.server.recvfrom(1024)
                    handler = self.handler_class((data, self.server), addr, self)
                    handler.handle()
                except Exception as e:
                    print(f"Error handling BLU request: {e}")
        except KeyboardInterrupt:
            print("_" * 80)
            print("Server received signal, exiting.")
            print("-" * 80)
            sys.stdout.flush()
            
    def stop(self):
        """Stop the server."""
        self.server.close()


def start_blu_server(host='', port=50100):
    """Start the BLU server."""
    server = BLUServer(host, port)
    server.start()


if __name__ == "__main__":
    try:
        start_blu_server()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}") 