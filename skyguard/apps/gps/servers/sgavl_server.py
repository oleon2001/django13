"""
SGAvl GPS server implementation.
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
    GPSDevice, GPSLocation, GPSEvent, IOEvent, GSMEvent, 
    PressureWeightLog, ServerSMS, DeviceHarness
)


class BadRecord(Exception):
    """Exception for invalid record data."""
    def __init__(self, value, data=None):
        self.value = value
        self.data = data if isinstance(data, str) else None
        
    def __str__(self):
        if self.data:
            return f"INVALID RECORD {repr(self.value)}[{len(self.data)}] ({self.data.encode('hex')})"
        return f"INVALID RECORD {repr(self.value)}"


class SGAvlProtocol:
    """SGAvl protocol decoder."""
    
    @staticmethod
    def unpack_fix(data):
        """Unpack a GpsFullRec."""
        ct, lat, lon, alt, vel, crs = struct.unpack("<IiiHBB", data)
        dt = datetime.fromtimestamp(ct, utc)
        if abs(dt - datetime.now(utc)) > timedelta(days=20):
            dt = datetime.now(utc)
        return {
            'date': dt,
            'pos': Point(lon/10000000.0, lat/10000000.0),
            'speed': vel, 
            'course': crs * 1.40625, 
            'altitude': alt
        }
    
    @staticmethod
    def unpack_delta_fix(data, orig):
        """Unpack a GpsDiffRec with no scaling on the deltas."""
        dct, dlat, dlon, dalt, vel, crs = struct.unpack("<HhhbBB", data)
        return {
            'date': orig['date'] + timedelta(seconds=dct),
            'pos': Point(
                orig['pos'].x + (dlon / 10000000.0),
                orig['pos'].y + (dlat / 10000000.0)
            ),
            'speed': vel, 
            'course': crs * 1.40625, 
            'altitude': orig['altitude'] + dalt
        }
    
    @staticmethod
    def get_correct_time(data, repair=True, out=None):
        """Get correct timestamp from data."""
        ct, = struct.unpack("<I", data)
        if ct < 10000 or ct > (time.time() + 900):
            if repair:
                ct = time.time()
            else:
                if out:
                    print(f"Discarded time {ct}", file=out)
                ct = None
        return ct
    
    @staticmethod
    def get_on_off(bit, data):
        """Get input status (active low)."""
        return "ON" if ((data >> bit) & 1) == 0 else "OFF"
    
    @staticmethod
    def get_off_on(bit, data):
        """Get output status (active high)."""
        return "OFF" if ((data >> bit) & 1) == 0 else "ON"


class SGAvlRequestHandler(BaseGPSRequestHandler):
    """Modern SGAvl protocol handler."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = SGAvlProtocol()
        self.events = []
        self.packets = []
        self.session = None
        self.harness = None
        self.done_outs = None
        self.version = None
        self.check_device_pos = True
        
    def setup(self):
        """Initialize the handler."""
        super().setup()
        self.request.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack("LL", 45, 0))
        self.request.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        
    def find_or_create_device(self):
        """Find or create device by IMEI."""
        try:
            self.device = GPSDevice.objects.get(imei=self.imei)
            self.harness = self.device.harness
        except GPSDevice.DoesNotExist:
            try:
                self.harness = DeviceHarness.objects.get(name="default")
            except DeviceHarness.DoesNotExist:
                print(">>>> Creating default harness")
                self.harness = DeviceHarness.objects.create(
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
            
            if self.imei < 10000000000000 or self.imei > 899999999999999:
                print(f"Invalid device IMEI {self.imei}. Not creating...")
                self.device = None
            else:
                self.device = GPSDevice.objects.create(
                    imei=self.imei,
                    name=f"{self.imei:015d}",
                    harness=self.harness,
                    comments=""
                )
                print(f">>>> Created device {self.device.name}")
    
    def update_device_position(self):
        """Update device position from latest event."""
        if not self.device or not self.events:
            return
            
        latest_event = self.events[-1]
        if hasattr(latest_event, 'position') and latest_event.position:
            self.device.position = latest_event.position
            self.device.last_log = latest_event.timestamp
            self.device.save()
    
    def decode_ios(self, data, event_type, has_fix):
        """Decode I/O status data."""
        if self.done_outs:
            return
            
        if (has_fix and len(data) != 24) or (not has_fix and len(data) != 12):
            raise BadRecord(event_type, data)
            
        old_inputs, old_outputs = self.device.inputs, self.device.outputs
        self.device.inputs, self.device.outputs = struct.unpack("<II", data[:8])
        
        if has_fix:
            gps_fix = self.protocol.unpack_fix(data[8:])
            event = IOEvent.objects.create(
                device=self.device,
                event_type=event_type,
                position=gps_fix['pos'],
                timestamp=gps_fix['date'],
                speed=gps_fix['speed'],
                course=gps_fix['course'],
                altitude=gps_fix['altitude'],
                inputs=self.device.inputs,
                outputs=self.device.outputs,
                changes='',
                odometer=self.device.odometer
            )
        else:
            event = IOEvent.objects.create(
                device=self.device,
                event_type=event_type,
                timestamp=datetime.fromtimestamp(
                    self.protocol.get_correct_time(data[8:]), utc
                ),
                inputs=self.device.inputs,
                outputs=self.device.outputs,
                changes=''
            )
        
        # Process alarm mask
        mask = self.device.alarm_mask & (~self.device.inputs) & 0xFFFF
        self.device.alarms = self.device.alarms | mask
        
        # Calculate changes
        ch_in = self.device.inputs ^ old_inputs
        ch_out = self.device.outputs ^ old_outputs
        event.input_delta = ch_in
        event.output_delta = ch_out
        event.alarm_delta = mask
        
        # Build changes string
        changes = []
        for i in range(16):
            if ch_in & (1 << i) != 0:
                input_name = getattr(self.harness, f'in{i:02d}', f'in{i}')
                status = self.protocol.get_on_off(i, self.device.inputs)
                changes.append(f"{input_name}={status}")
                
        for i in range(16):
            if ch_out & (1 << i) != 0:
                output_name = getattr(self.harness, f'out{i:02d}', f'out{i}')
                status = self.protocol.get_off_on(i, self.device.outputs)
                changes.append(f"{output_name}={status}")
        
        event.changes = " ".join(changes)
        
        # Skip BAT_DOK events
        if 'BAT_DOK' not in event.changes:
            self.events.append(event)
            
        if has_fix and self.check_device_pos:
            self.update_device_position()
    
    def decode_pressure(self, data):
        """Decode pressure sensor data."""
        if len(data) != 25:
            raise BadRecord("PRESSURE INFO", data)
            
        id0, id1, id2, p1, p2, count = struct.unpack("<IIIIIB", data[4:])
        dt = datetime.fromtimestamp(self.protocol.get_correct_time(data[:4]))
        sensor_id = f"{(id0 << 64) | (id1 << 32) | id2:024X}"
        
        psi1 = (p1/count - 1638.4) * 150.0 / 13107.0
        psi2 = (p2/count - 1638.4) * 150.0 / 13107.0
        
        if psi1 != 0 and psi2 != 0:
            print(f"{sensor_id} - Presion = {psi1:.2f} / {psi2:.2f} @ {dt}")
            PressureWeightLog.objects.create(
                device=self.device,
                sensor=sensor_id,
                timestamp=dt,
                psi1=str(psi1),
                psi2=str(psi2)
            )
    
    def decode_people(self, data):
        """Decode people count data."""
        if len(data) != 24:
            raise BadRecord("PEOPLE INFO", data)
            
        id0, id1, id2, p1, p2 = struct.unpack("<IIIII", data[4:])
        dt = self.protocol.get_correct_time(data[:4], False, self.stdout)
        
        if dt:
            dt = datetime.fromtimestamp(dt)
            sensor_id = f"{(id0 << 64) | (id1 << 32) | id2:024X}"
            
            if p1 != 0 and p2 != 0:
                print(f"{sensor_id} - PEOPLE = {p1:.2f} / {p2:.2f} @ {dt}")
                PressureWeightLog.objects.create(
                    device=self.device,
                    sensor=sensor_id,
                    timestamp=dt,
                    psi1=str(p1),
                    psi2=str(p2)
                )
    
    def decode_gps_fix(self, data, event_type):
        """Decode GPS fix data."""
        if len(data) != 24:
            raise BadRecord(event_type, data)
            
        gps_fix = self.protocol.unpack_fix(data)
        
        event = GPSEvent.objects.create(
            device=self.device,
            event_type=event_type,
            position=gps_fix['pos'],
            timestamp=gps_fix['date'],
            speed=gps_fix['speed'],
            course=gps_fix['course'],
            altitude=gps_fix['altitude']
        )
        
        self.events.append(event)
        self.update_device_position()
    
    def decode_ctime(self, data, event_type):
        """Decode time correction data."""
        if len(data) != 4:
            raise BadRecord(event_type, data)
            
        dt = datetime.fromtimestamp(self.protocol.get_correct_time(data), utc)
        
        event = GPSEvent.objects.create(
            device=self.device,
            event_type=event_type,
            timestamp=dt
        )
        
        self.events.append(event)
    
    def parse_record(self, id_byte, data):
        """Parse a single record based on ID byte."""
        try:
            if id_byte == 0xA0:  # I/O status with GPS fix
                self.decode_ios(data, "IO_FIX", True)
            elif id_byte == 0xA1:  # I/O status without GPS fix
                self.decode_ios(data, "IO", False)
            elif id_byte == 0xA2:  # GPS fix
                self.decode_gps_fix(data, "TRACK")
            elif id_byte == 0xA3:  # Time correction
                self.decode_ctime(data, "CTIME")
            elif id_byte == 0xA4:  # Pressure sensor
                self.decode_pressure(data)
            elif id_byte == 0xA5:  # People count
                self.decode_people(data)
            elif id_byte == 0xA6:  # Call received
                dt = datetime.fromtimestamp(self.protocol.get_correct_time(data[:4]), utc)
                GSMEvent.objects.create(
                    device=self.device,
                    event_type="CALL_RECEIVED",
                    timestamp=dt,
                    source=data[4:],
                    text="CALL_RECEIVED"
                )
            elif id_byte == 0xA7:  # SMS received
                dt = datetime.fromtimestamp(self.protocol.get_correct_time(data[:4]), utc)
                GSMEvent.objects.create(
                    device=self.device,
                    event_type="SMS_RECEIVED",
                    timestamp=dt,
                    source=data[4:],
                    text="SMS_RECEIVED"
                )
            else:
                print(f"Unknown record type: 0x{id_byte:02X}")
                
        except BadRecord as e:
            print(f"Bad record: {e}")
        except Exception as e:
            print(f"Error parsing record: {e}")
    
    def get_records(self, packet_data):
        """Extract records from packet data."""
        records = []
        offset = 0
        
        while offset < len(packet_data):
            if offset + 1 >= len(packet_data):
                break
                
            id_byte = packet_data[offset]
            offset += 1
            
            if offset + 1 >= len(packet_data):
                break
                
            length = packet_data[offset]
            offset += 1
            
            if offset + length > len(packet_data):
                break
                
            data = packet_data[offset:offset + length]
            records.append((id_byte, data))
            offset += length
            
        return records
    
    def get_packet(self, login=True):
        """Get and decode packet from connection."""
        try:
            data = self.request.recv(1024)
            if not data:
                return None
                
            if login and len(data) < 8:
                print(f"Invalid login (len={len(data)}) {data.hex()}")
                return None
                
            if login:
                self.imei, = struct.unpack("<Q", data[:8])
                print(f"Login from {self.imei:015d}")
                self.find_or_create_device()
                data = data[8:]
                
            return data
            
        except socket.error as e:
            print(f"Socket error: {e}")
            return None
    
    def handle(self):
        """Handle the SGAvl connection."""
        self.imei = None
        self.done_outs = None
        
        try:
            login = True
            self.packets = []
            self.version = None
            
            while True:
                # Get packet data
                packet_data = self.get_packet(login)
                if not packet_data:
                    return
                    
                # Parse records
                records = self.get_records(packet_data)
                
                # Prepare response
                response = b'\xA0' + bytes([len(records)])
                
                # Handle login commands
                if login and self.device:
                    print(f"IMEI: {self.device.imei}")
                    
                    # Handle new outputs
                    if hasattr(self.device, 'new_outputs') and self.device.new_outputs is not None:
                        print("Setting outputs")
                        outs = b""
                        for i in range(16):
                            outs += b'\x01' if (self.device.new_outputs >> i) & 1 else b'\x00'
                            
                        if len(outs) == 16:
                            response += b'\xC0' + outs
                            print(f"Response + {response}")
                            
                        self.device.outputs = self.device.new_outputs
                        self.device.new_outputs = None
                        self.device.save()
                        self.done_outs = True
                    
                    # Handle new input flags
                    if hasattr(self.device, 'new_inflags') and self.device.new_inflags:
                        try:
                            infs = bytes.fromhex(self.device.new_inflags)
                            if len(infs) == 16:
                                response += b'\xC1' + infs
                        except ValueError:
                            print(f"Invalid inflags for device {self.device.imei}: {self.device.new_inflags}")
                        self.device.new_inflags = ''
                    
                    # Handle firmware update
                    if hasattr(self.device, 'fw_file') and self.device.fw_file:
                        response += b'\xC2'
                    
                    # Handle SMS messages
                    sms_messages = ServerSMS.objects.filter(
                        device=self.device, 
                        sent__isnull=True
                    )
                    if sms_messages.exists():
                        msg = sms_messages.first()
                        response += b'\xC3'
                        response += bytes([len(msg.message)])
                        response += msg.message.encode('ascii', 'replace')
                        msg.sent = datetime.now()
                        msg.save()
                        print(f">> Mensaje '{msg.message}' Enviado <<<")
                
                # Send response
                self.request.send(response)
                login = False
                
                # Process records
                for id_byte, data in records:
                    self.parse_record(id_byte, data)
                    
                self.packets.append((packet_data, response))
                
        except socket.error as e:
            if e.errno == 11:  # EAGAIN
                print("Socket timeout")
        except Exception as e:
            print(f">>>> Unknown exception: {e}")
            raise
    
    def finish(self):
        """Clean up after handling the request."""
        try:
            if not self.imei or not self.device:
                print("Invalid Session")
                return
                
            # Update device
            if self.version and self.version != self.device.firmware_version:
                self.device.firmware_version = self.version
                self.device.save()
                
            # Handle firmware upgrade
            if (self.device.firmware_version in ["1.10", "1.40"] and 
                (self.device.inputs & 2 == 2) and 
                not getattr(self.device, 'fw_file', None)):
                self.device.fw_file = "1.41"
                self.device.save()
                
                # Send SMS for upgrade
                if hasattr(self.device, 'sim') and self.device.sim:
                    import subprocess
                    args = [
                        "ssh", "sms@skyguard.dlinkddns.com",
                        "gammu", "sendsms", "TEXT", self.device.sim.phone,
                        "-text", f'"UPGRADE {self.device.fw_file}"'
                    ]
                    subprocess.call(args)
                    
            print(f"Session completed for device {self.device.imei}")
            print(f"Events processed: {len(self.events)}")
            
        except Exception as e:
            print(f"Error in finish: {e}")
        finally:
            super().finish()


class SGAvlServer(BaseGPSServer):
    """SGAvl GPS server."""
    
    def __init__(self, host='', port=60010):
        """Initialize the SGAvl server."""
        super().__init__(host, port, SGAvlRequestHandler)


def start_sgavl_server(host='', port=60010):
    """Start the SGAvl server."""
    server = SGAvlServer(host, port)
    server.start()


if __name__ == "__main__":
    try:
        start_sgavl_server()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}") 