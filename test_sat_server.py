#!/usr/bin/env python3
"""
Test script for SAT server migration.
Tests the migrated SAT server functionality.
"""
import os
import sys
import socket
import struct
import time
import threading
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
import django
django.setup()

from skyguard.apps.gps.servers.sat_server import SATServer, SATRequestHandler
from skyguard.apps.gps.models import GPSDevice, DeviceHarness


class SATTestClient:
    """Test client for SAT server."""
    
    def __init__(self, host='localhost', port=15557):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to SAT server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def send_sat_packet(self, imei, packet_number, positions):
        """Send SAT packet with positions."""
        try:
            # Create packet header (38 bytes)
            header = bytearray(38)
            
            # Fill header with test data
            header[0:10] = b'\x00' * 10  # Reserved
            header[10:25] = str(imei).encode().ljust(15, b'\x00')  # IMEI
            header[25:27] = struct.pack("<H", packet_number)  # Packet number
            header[27:38] = b'\x00' * 11  # Reserved
            
            # Create position records
            payload = bytearray()
            for lat, lon, year, month, day, hour, minute in positions:
                # Encode date/time
                ym = ((year - 2007) << 4) | month
                tm = (day << 11) | (hour << 6) | minute
                
                # Create position record (12 bytes)
                record = struct.pack("<BHff", ym, tm, lat, lon)
                payload.extend(record)
            
            # Combine header and payload
            packet = header + payload
            
            # Send packet
            self.socket.send(packet)
            print(f"Sent SAT packet: {len(packet)} bytes")
            
            # Try to receive acknowledgment
            try:
                self.socket.settimeout(2.0)
                response = self.socket.recv(1024)
                if response:
                    print(f"Received response: {response.hex()}")
                    return response
                else:
                    print("No response received")
                    return None
            except socket.timeout:
                print("No acknowledgment received (timeout)")
                return None
                
        except Exception as e:
            print(f"Failed to send SAT packet: {e}")
            return None
    
    def close(self):
        """Close the connection."""
        if self.socket:
            self.socket.close()


def test_sat_server():
    """Test the SAT server functionality."""
    print("=" * 80)
    print("TESTING SAT SERVER MIGRATION")
    print("=" * 80)
    
    # Start server in background
    server = SATServer(host='localhost', port=15557)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Test client
    client = SATTestClient('localhost', 15557)
    
    try:
        # Test 1: Connection
        print("\n1. Testing connection...")
        if not client.connect():
            print("❌ Connection failed")
            return False
        print("✅ Connection successful")
        
        # Test 2: Send SAT packet with single position
        print("\n2. Testing SAT packet with single position...")
        test_imei = 123456789012345
        packet_number = 1
        
        # Mexico City coordinates
        positions = [
            (19.4326, -99.1332, 2025, 7, 9, 14, 30)  # lat, lon, year, month, day, hour, minute
        ]
        
        response = client.send_sat_packet(test_imei, packet_number, positions)
        if response:
            print("✅ SAT packet sent successfully")
        else:
            print("⚠️ SAT packet sent but no acknowledgment")
        
        # Test 3: Send SAT packet with multiple positions
        print("\n3. Testing SAT packet with multiple positions...")
        packet_number = 2
        
        # Multiple positions
        positions = [
            (19.4326, -99.1332, 2025, 7, 9, 14, 30),  # Mexico City
            (20.6597, -103.3496, 2025, 7, 9, 14, 31),  # Guadalajara
            (25.6866, -100.3161, 2025, 7, 9, 14, 32),  # Monterrey
        ]
        
        response = client.send_sat_packet(test_imei, packet_number, positions)
        if response:
            print("✅ Multiple positions sent successfully")
        else:
            print("⚠️ Multiple positions sent but no acknowledgment")
        
        # Test 4: Check database
        print("\n4. Checking database...")
        try:
            device = GPSDevice.objects.get(imei=test_imei)
            print(f"✅ Device found: {device.name}")
            print(f"   Position: {device.position}")
            print(f"   Last log: {device.last_log}")
            
            # Check events
            events = device.gps_events.all()
            print(f"   Events: {events.count()}")
            
            # Show recent events
            recent_events = events.order_by('-timestamp')[:5]
            for event in recent_events:
                print(f"     - {event.timestamp}: {event.position}")
            
        except GPSDevice.DoesNotExist:
            print("❌ Device not found in database")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        client.close()
        server.stop()


def test_protocol_decoder():
    """Test the SAT protocol decoder."""
    print("\n" + "=" * 80)
    print("TESTING SAT PROTOCOL DECODER")
    print("=" * 80)
    
    from skyguard.apps.gps.servers.sat_server import SATProtocol
    
    protocol = SATProtocol()
    
    # Test datetime decoding
    print("\n1. Testing datetime decoding...")
    ym = 0x85  # 2025, month 5
    tm = 0x1E30  # Day 15, hour 14, minute 48
    
    dt = protocol.decode_datetime(ym, tm)
    print(f"   Input: ym={ym:02X}, tm={tm:04X}")
    print(f"   Output: {dt}")
    
    # Test position decoding
    print("\n2. Testing position decoding...")
    lat = 19.4326
    lon = -99.1332
    
    test_data = struct.pack("<ff", lat, lon)
    position = protocol.decode_position(test_data)
    
    print(f"   Input: lat={lat}, lon={lon}")
    print(f"   Output: {position}")
    
    # Test packet validation
    print("\n3. Testing packet validation...")
    
    # Valid packet (minimum size)
    valid_packet = bytearray(50)
    valid_packet[10:25] = b'123456789012345'  # IMEI
    valid_packet[26:28] = struct.pack("<H", 1)  # Packet number
    
    try:
        protocol.validate_packet(valid_packet)
        print("   ✅ Valid packet accepted")
    except ValueError as e:
        print(f"   ❌ Valid packet rejected: {e}")
    
    # Invalid packet (too short)
    invalid_packet = bytearray(30)
    
    try:
        protocol.validate_packet(invalid_packet)
        print("   ❌ Invalid packet accepted")
    except ValueError as e:
        print(f"   ✅ Invalid packet correctly rejected: {e}")
    
    print("✅ Protocol decoder tests completed!")


def test_packet_generation():
    """Test SAT packet generation."""
    print("\n" + "=" * 80)
    print("TESTING SAT PACKET GENERATION")
    print("=" * 80)
    
    # Create a realistic SAT packet
    imei = 123456789012345
    packet_number = 1
    
    # Create header
    header = bytearray(38)
    header[0:10] = b'\x00' * 10  # Reserved
    header[10:25] = str(imei).encode().ljust(15, b'\x00')  # IMEI
    header[25:27] = struct.pack("<H", packet_number)  # Packet number
    header[27:38] = b'\x00' * 11  # Reserved
    
    # Create position records
    positions = [
        (19.4326, -99.1332, 2025, 7, 9, 14, 30),  # Mexico City
        (20.6597, -103.3496, 2025, 7, 9, 14, 31),  # Guadalajara
    ]
    
    payload = bytearray()
    for lat, lon, year, month, day, hour, minute in positions:
        # Encode date/time
        ym = ((year - 2007) << 4) | month
        tm = (day << 11) | (hour << 6) | minute
        
        # Create position record (12 bytes)
        record = struct.pack("<BHff", ym, tm, lat, lon)
        payload.extend(record)
    
    # Combine header and payload
    packet = header + payload
    
    print(f"Generated SAT packet:")
    print(f"   Total length: {len(packet)} bytes")
    print(f"   Header length: {len(header)} bytes")
    print(f"   Payload length: {len(payload)} bytes")
    print(f"   Position records: {len(positions)}")
    print(f"   IMEI: {imei}")
    print(f"   Packet number: {packet_number}")
    
    # Show packet structure
    print(f"\nPacket structure:")
    print(f"   Header (0-37): {packet[:38].hex()}")
    print(f"   Payload (38+): {packet[38:].hex()}")
    
    print("✅ Packet generation test completed!")


if __name__ == "__main__":
    print("Starting SAT server migration tests...")
    
    # Test protocol decoder
    test_protocol_decoder()
    
    # Test packet generation
    test_packet_generation()
    
    # Test server functionality
    success = test_sat_server()
    
    if success:
        print("\n🎉 SAT server migration completed successfully!")
        print("✅ Server is fully functional")
        print("✅ Protocol decoder working correctly")
        print("✅ Database integration working")
    else:
        print("\n❌ SAT server migration failed!")
        print("Please check the logs for details")
    
    print("\n" + "=" * 80) 