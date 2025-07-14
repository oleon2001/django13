"""
SAT GPS server implementation.
Migrated from legacy django14 system to modern architecture.
"""
import socket
import struct
import threading
import sys
import time
import os
from datetime import datetime, timedelta
from pytz import utc, timezone
from django.db import transaction
from django.contrib.gis.geos import Point
from django.conf import settings

from skyguard.apps.gps.servers.base import BaseGPSRequestHandler, BaseGPSServer
from skyguard.apps.gps.models import (
    GPSDevice, GPSLocation, GPSEvent, DeviceHarness
)


class SATProtocol:
    """SAT protocol decoder."""
    
    @staticmethod
    def decode_datetime(ym, tm):
        """Decode date and time from SAT protocol."""
        year = (ym >> 4) + 2007
        month = ym & 0x0F
        day = (tm >> 11) & 0x1F
        hour = (tm >> 6) & 0x1F
        minute = tm & 0x3F
        
        # Validate date components
        if not (1 <= month <= 12 and 1 <= day <= 31 and 
                0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"Invalid date/time: {year}-{month}-{day} {hour}:{minute}")
        
        return datetime(year, month, day, hour, minute, tzinfo=utc)
    
    @staticmethod
    def decode_position(data):
        """Decode position from SAT protocol."""
        lat, lon = struct.unpack("<ff", data)
        
        # Validate coordinates
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"Invalid coordinates: lat={lat}, lon={lon}")
        
        return Point(lon, lat)
    
    @staticmethod
    def validate_packet(data):
        """Validate SAT packet structure."""
        if len(data) < 38:
            raise ValueError(f"Packet too short: {len(data)} bytes")
        
        # Check minimum packet structure
        if len(data) < 50:  # At least header + one position record
            raise ValueError(f"Packet incomplete: {len(data)} bytes")
        
        return True


class SATRequestHandler(BaseGPSRequestHandler):
    """Modern SAT protocol handler."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = SATProtocol()
        self.device = None
        self.imei = None
        self.packet_number = None
        self.log_file = None
        
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
            print(f"Device not found. Creating SAT device with IMEI: {imei}")
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
                name=f"SAT-{imei}",
                harness=harness,
                comments="SAT Device"
            )
            print(f"Created SAT device: {self.device.name}")
        
        return self.device
    
    def log_packet(self, data, packet_number):
        """Log packet data for debugging."""
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_filename = f"{log_dir}/satlog_{packet_number}_{self.imei}.bin"
            with open(log_filename, "wb") as log_file:
                log_file.write(data)
            print(f"Packet logged to: {log_filename}")
        except Exception as e:
            print(f"Failed to log packet: {e}")
    
    def process_position_record(self, data):
        """Process a single position record."""
        if len(data) < 12:
            print(f"Position record too short: {len(data)} bytes")
            return None, data
        
        try:
            # Extract date and time
            ym, tm = struct.unpack("<BH", data[0:3])
            dt = self.protocol.decode_datetime(ym, tm)
            
            # Extract position
            position = self.protocol.decode_position(data[3:11])
            
            print(f"SAT Position - Date: {dt}, Lat: {position.y}, Lon: {position.x}")
            
            return {
                'timestamp': dt,
                'position': position,
                'speed': 0,  # SAT protocol doesn't include speed
                'course': 0,  # SAT protocol doesn't include course
                'altitude': 0,  # SAT protocol doesn't include altitude
                'satellites': 0  # SAT protocol doesn't include satellite count
            }, data[12:]
            
        except Exception as e:
            print(f"Error processing position record: {e}")
            return None, data[12:]
    
    def handle(self):
        """Handle the SAT connection."""
        try:
            print("*" * 80)
            print(f"{self.local_time.ctime()} {self.client_address} connected!")
            
            # Receive data
            data = self.request.recv(2048)
            if not data:
                print("No data received")
                return
            
            n_bytes = len(data)
            print(f"Received {n_bytes} bytes from {self.client_address}")
            
            # Validate packet
            try:
                self.protocol.validate_packet(data)
            except ValueError as e:
                print(f"Invalid packet: {e}")
                return
            
            # Extract IMEI and packet number
            try:
                self.imei = int(data[10:25])
                self.packet_number, = struct.unpack("<H", data[26:28])
            except (ValueError, struct.error) as e:
                print(f"Error extracting IMEI/packet number: {e}")
                return
            
            print(f"IMEI: {self.imei}")
            print(f"Packet Sequence: {self.packet_number}")
            
            # Log packet for debugging
            self.log_packet(data, self.packet_number)
            
            # Find or create device
            self.device = self.find_or_create_device(self.imei)
            
            # Process position records
            payload_data = data[38:]
            position_count = 0
            
            while len(payload_data) >= 12:
                position_record, payload_data = self.process_position_record(payload_data)
                
                if position_record:
                    # Update device position
                    self.device.position = position_record['position']
                    self.device.last_log = self.device.date = position_record['timestamp']
                    
                    # Create GPS event
                    event = GPSEvent(
                        device=self.device,
                        event_type="TRACK",
                        position=position_record['position'],
                        speed=position_record['speed'],
                        course=position_record['course'],
                        altitude=position_record['altitude'],
                        satellites=position_record['satellites'],
                        timestamp=position_record['timestamp']
                    )
                    
                    # Save to database
                    with transaction.atomic():
                        self.device.save()
                        event.save()
                    
                    position_count += 1
                else:
                    # Skip invalid record
                    break
            
            print(f"Processed {position_count} position records for device {self.device.imei}")
            
            # Send acknowledgment (optional)
            try:
                ack_response = struct.pack("<BHI", 0x01, self.packet_number, position_count)
                self.request.send(ack_response)
                print(f"Sent acknowledgment for packet {self.packet_number}")
            except Exception as e:
                print(f"Failed to send acknowledgment: {e}")
                
        except Exception as e:
            print(f"Error handling SAT connection: {e}")
            import traceback
            traceback.print_exc()
    
    def finish(self):
        """Clean up after handling the request."""
        try:
            dt = datetime.now(utc) - self.time_check
            print(f"Finished processing SAT packet in {dt.seconds}.{dt.microseconds:06d} seconds")
        except Exception as e:
            print(f"Error in finish: {e}")
        finally:
            super().finish()


class SATServer(BaseGPSServer):
    """SAT GPS server."""
    
    def __init__(self, host='', port=15557):
        """Initialize the SAT server."""
        super().__init__(host=host, port=port, handler_class=SATRequestHandler)
        
    def start(self):
        """Start the server."""
        print("_" * 80)
        print(f"SAT TCP Server started on port {self.port}")
        print("-" * 80)
        sys.stdout.flush()
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("_" * 80)
            print("Server received signal, exiting.")
            print("-" * 80)
            sys.stdout.flush()
        except Exception as e:
            print(f"Server error: {e}")
            raise


def start_sat_server(host='', port=15557):
    """Start the SAT server."""
    server = SATServer(host, port)
    server.start()


if __name__ == "__main__":
    try:
        start_sat_server()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}") 