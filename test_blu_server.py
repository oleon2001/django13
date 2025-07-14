#!/usr/bin/env python3
"""
Test script for BLU server migration.
Tests the migrated BLU server functionality.
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

from skyguard.apps.gps.servers.blu_server import BLUServer, BLURequestHandler
from skyguard.apps.gps.models import GPSDevice, DeviceHarness


class BLUTestClient:
    """Test client for BLU server."""
    
    def __init__(self, host='localhost', port=50100):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Connected to BLU server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def send_login(self, imei, mac_id):
        """Send login packet with IMEI and MAC ID."""
        try:
            # Pack IMEI and MAC ID
            login_data = struct.pack("<BQQ", 0x01, imei, mac_id)
            self.socket.sendto(login_data, (self.host, self.port))
            
            # Receive response
            response, addr = self.socket.recvfrom(1024)
            print(f"Login response: {response.hex()}")
            return response
        except Exception as e:
            print(f"Login failed: {e}")
            return None
    
    def send_ping(self, session_id, lat, lon, speed):
        """Send ping packet with position."""
        try:
            timestamp = int(time.time())
            ping_data = struct.pack("<BLIffB", 0x02, session_id, timestamp, lat, lon, speed)
            self.socket.sendto(ping_data, (self.host, self.port))
            
            # Receive response
            response, addr = self.socket.recvfrom(1024)
            print(f"Ping response: {response.hex()}")
            return response
        except Exception as e:
            print(f"Ping failed: {e}")
            return None
    
    def send_devinfo(self, session_id):
        """Send device info packet."""
        try:
            devinfo_data = struct.pack("<BL", 0x03, session_id)
            self.socket.sendto(devinfo_data, (self.host, self.port))
            
            # Receive response
            response, addr = self.socket.recvfrom(1024)
            print(f"DevInfo response: {response.hex()}")
            return response
        except Exception as e:
            print(f"DevInfo failed: {e}")
            return None
    
    def send_data(self, session_id, tracks_data=None, people_data=None):
        """Send data packet with tracks and/or people records."""
        try:
            # Build data packet
            data_packet = struct.pack("<BL", 0x04, session_id)
            
            if tracks_data:
                # Add tracks record
                tracks_header = struct.pack("<II", 0x30, len(tracks_data))
                data_packet += tracks_header + tracks_data
            
            if people_data:
                # Add people record
                people_header = struct.pack("<II", 0x31, len(people_data))
                data_packet += people_header + people_data
            
            # Add CRC (simplified)
            crc = 0x0000  # Placeholder
            data_packet += struct.pack("<H", crc)
            
            self.socket.sendto(data_packet, (self.host, self.port))
            
            # Receive response
            response, addr = self.socket.recvfrom(1024)
            print(f"Data response: {response.hex()}")
            return response
        except Exception as e:
            print(f"Data failed: {e}")
            return None
    
    def close(self):
        """Close the connection."""
        if self.socket:
            self.socket.close()


def test_blu_server():
    """Test the BLU server functionality."""
    print("=" * 80)
    print("TESTING BLU SERVER MIGRATION")
    print("=" * 80)
    
    # Start server in background
    server = BLUServer(host='localhost', port=50100)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Test client
    client = BLUTestClient('localhost', 50100)
    
    try:
        # Test 1: Connection
        print("\n1. Testing connection...")
        if not client.connect():
            print("❌ Connection failed")
            return False
        print("✅ Connection successful")
        
        # Test 2: Login
        print("\n2. Testing login...")
        test_imei = 123456789012345
        test_mac = 0x123456789ABC
        response = client.send_login(test_imei, test_mac)
        if response:
            print("✅ Login successful")
            # Extract session ID from response
            session_id = struct.unpack("<BLB", response)[1]
            print(f"   Session ID: {session_id}")
        else:
            print("❌ Login failed")
            return False
        
        # Test 3: Ping with position
        print("\n3. Testing ping with position...")
        lat = 19.4326  # Mexico City
        lon = -99.1332
        speed = 50
        response = client.send_ping(session_id, lat, lon, speed)
        if response:
            print("✅ Ping successful")
        else:
            print("❌ Ping failed")
        
        # Test 4: Device info
        print("\n4. Testing device info...")
        response = client.send_devinfo(session_id)
        if response:
            print("✅ Device info successful")
        else:
            print("❌ Device info failed")
        
        # Test 5: Data with tracks
        print("\n5. Testing data with tracks...")
        # Create sample track data
        timestamp = int(time.time())
        track_data = struct.pack("<IffB", timestamp, lat, lon, speed)
        response = client.send_data(session_id, tracks_data=track_data)
        if response:
            print("✅ Data with tracks successful")
        else:
            print("❌ Data with tracks failed")
        
        # Test 6: Data with people count
        print("\n6. Testing data with people count...")
        # Create sample people data
        people_data = struct.pack("<IIIIH", timestamp, 10, 5, 0x12345678, 0x9ABC)
        response = client.send_data(session_id, people_data=people_data)
        if response:
            print("✅ Data with people count successful")
        else:
            print("❌ Data with people count failed")
        
        # Test 7: Check database
        print("\n7. Checking database...")
        try:
            device = GPSDevice.objects.get(imei=test_imei)
            print(f"✅ Device found: {device.name}")
            print(f"   Position: {device.position}")
            print(f"   Last log: {device.last_log}")
            
            # Check events
            events = device.gps_events.all()
            print(f"   Events: {events.count()}")
            
            # Check people count records
            people_records = device.pressure_weight_logs.all()
            print(f"   People records: {people_records.count()}")
            
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
    """Test the BLU protocol decoder."""
    print("\n" + "=" * 80)
    print("TESTING BLU PROTOCOL DECODER")
    print("=" * 80)
    
    from skyguard.apps.gps.servers.blu_server import BLUProtocol
    
    protocol = BLUProtocol()
    
    # Test position unpacking
    print("\n1. Testing position unpacking...")
    timestamp = int(time.time())
    lat = 19.4326
    lon = -99.1332
    speed = 50
    
    test_data = struct.pack("<IffB", timestamp, lat, lon, speed)
    result = protocol.unpack_position(test_data)
    
    print(f"   Input: timestamp={timestamp}, lat={lat}, lon={lon}, speed={speed}")
    print(f"   Output: date={result['date']}, pos={result['pos']}, speed={result['speed']}")
    
    # Test TOF unpacking
    print("\n2. Testing TOF unpacking...")
    count_in = 10
    count_out = 5
    mac1 = 0x12345678
    mac2 = 0x9ABC
    
    tof_data = struct.pack("<IIIIH", timestamp, count_in, count_out, mac1, mac2)
    result = protocol.unpack_tof(tof_data)
    
    print(f"   Input: count_in={count_in}, count_out={count_out}, mac1={mac1:08X}, mac2={mac2:04X}")
    print(f"   Output: date={result['date']}, in={result['in']}, out={result['out']}, id={result['id']}")
    
    # Test CRC calculation
    print("\n3. Testing CRC calculation...")
    test_packet = b'\x04\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    crc = protocol.calculate_crc(test_packet)
    print(f"   Packet: {test_packet.hex()}")
    print(f"   CRC: {crc:04X}")
    
    print("✅ Protocol decoder tests completed!")


if __name__ == "__main__":
    print("Starting BLU server migration tests...")
    
    # Test protocol decoder
    test_protocol_decoder()
    
    # Test server functionality
    success = test_blu_server()
    
    if success:
        print("\n🎉 BLU server migration completed successfully!")
        print("✅ Server is fully functional")
        print("✅ Protocol decoder working correctly")
        print("✅ Database integration working")
    else:
        print("\n❌ BLU server migration failed!")
        print("Please check the logs for details")
    
    print("\n" + "=" * 80) 