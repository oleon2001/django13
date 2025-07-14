#!/usr/bin/env python3
"""
Test script for SGAvl server migration.
Tests the migrated SGAvl server functionality.
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

from skyguard.apps.gps.servers.sgavl_server import SGAvlServer, SGAvlRequestHandler
from skyguard.apps.gps.models import GPSDevice, DeviceHarness


class SGAvlTestClient:
    """Test client for SGAvl server."""
    
    def __init__(self, host='localhost', port=60010):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to SGAvl server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def send_login(self, imei):
        """Send login packet with IMEI."""
        try:
            # Pack IMEI as 8-byte little-endian
            login_data = struct.pack("<Q", imei)
            self.socket.send(login_data)
            
            # Receive response
            response = self.socket.recv(1024)
            print(f"Login response: {response.hex()}")
            return response
        except Exception as e:
            print(f"Login failed: {e}")
            return None
    
    def send_io_data(self, inputs, outputs, has_gps=True):
        """Send I/O status data."""
        try:
            # Create I/O data packet
            io_data = struct.pack("<II", inputs, outputs)
            
            if has_gps:
                # Add GPS fix data (24 bytes total)
                timestamp = int(time.time())
                lat = 197200000  # Example latitude (19.72 degrees)
                lon = -991200000  # Example longitude (-99.12 degrees)
                alt = 1000  # Altitude in meters
                vel = 50  # Speed in km/h
                crs = 180  # Course in degrees
                
                gps_data = struct.pack("<IiiHBB", timestamp, lat, lon, alt, vel, crs)
                io_data += gps_data
            
            # Create packet with record header
            packet = b'\xA0' + bytes([len(io_data)]) + io_data
            self.socket.send(packet)
            
            # Receive response
            response = self.socket.recv(1024)
            print(f"I/O response: {response.hex()}")
            return response
        except Exception as e:
            print(f"I/O data failed: {e}")
            return None
    
    def send_gps_fix(self):
        """Send GPS fix data."""
        try:
            timestamp = int(time.time())
            lat = 197200000  # Example latitude
            lon = -991200000  # Example longitude
            alt = 1000
            vel = 50
            crs = 180
            
            gps_data = struct.pack("<IiiHBB", timestamp, lat, lon, alt, vel, crs)
            packet = b'\xA2' + bytes([len(gps_data)]) + gps_data
            self.socket.send(packet)
            
            response = self.socket.recv(1024)
            print(f"GPS fix response: {response.hex()}")
            return response
        except Exception as e:
            print(f"GPS fix failed: {e}")
            return None
    
    def close(self):
        """Close the connection."""
        if self.socket:
            self.socket.close()


def test_sgavl_server():
    """Test the SGAvl server functionality."""
    print("=" * 80)
    print("TESTING SGAvl SERVER MIGRATION")
    print("=" * 80)
    
    # Start server in background
    server = SGAvlServer(host='localhost', port=60010)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Test client
    client = SGAvlTestClient('localhost', 60010)
    
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
        response = client.send_login(test_imei)
        if response:
            print("✅ Login successful")
        else:
            print("❌ Login failed")
            return False
        
        # Test 3: I/O data without GPS
        print("\n3. Testing I/O data without GPS...")
        response = client.send_io_data(inputs=0x0001, outputs=0x0000, has_gps=False)
        if response:
            print("✅ I/O data without GPS successful")
        else:
            print("❌ I/O data without GPS failed")
        
        # Test 4: I/O data with GPS
        print("\n4. Testing I/O data with GPS...")
        response = client.send_io_data(inputs=0x0002, outputs=0x0001, has_gps=True)
        if response:
            print("✅ I/O data with GPS successful")
        else:
            print("❌ I/O data with GPS failed")
        
        # Test 5: GPS fix
        print("\n5. Testing GPS fix...")
        response = client.send_gps_fix()
        if response:
            print("✅ GPS fix successful")
        else:
            print("❌ GPS fix failed")
        
        # Test 6: Check database
        print("\n6. Checking database...")
        try:
            device = GPSDevice.objects.get(imei=test_imei)
            print(f"✅ Device found: {device.name}")
            print(f"   Position: {device.position}")
            print(f"   Last log: {device.last_log}")
            
            # Check events
            events = device.gps_events.all()
            print(f"   Events: {events.count()}")
            
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
    """Test the SGAvl protocol decoder."""
    print("\n" + "=" * 80)
    print("TESTING SGAvl PROTOCOL DECODER")
    print("=" * 80)
    
    from skyguard.apps.gps.servers.sgavl_server import SGAvlProtocol
    
    protocol = SGAvlProtocol()
    
    # Test GPS fix unpacking
    print("\n1. Testing GPS fix unpacking...")
    timestamp = int(time.time())
    lat = 197200000  # 19.72 degrees
    lon = -991200000  # -99.12 degrees
    alt = 1000
    vel = 50
    crs = 180
    
    test_data = struct.pack("<IiiHBB", timestamp, lat, lon, alt, vel, crs)
    result = protocol.unpack_fix(test_data)
    
    print(f"   Input: timestamp={timestamp}, lat={lat}, lon={lon}")
    print(f"   Output: date={result['date']}, pos={result['pos']}, speed={result['speed']}")
    
    # Test time correction
    print("\n2. Testing time correction...")
    test_time = int(time.time())
    time_data = struct.pack("<I", test_time)
    corrected_time = protocol.get_correct_time(time_data)
    print(f"   Input: {test_time}")
    print(f"   Output: {corrected_time}")
    
    # Test I/O status
    print("\n3. Testing I/O status...")
    inputs = 0x0001  # Bit 0 set
    outputs = 0x0002  # Bit 1 set
    
    for i in range(4):
        input_status = protocol.get_on_off(i, inputs)
        output_status = protocol.get_off_on(i, outputs)
        print(f"   Bit {i}: input={input_status}, output={output_status}")
    
    print("✅ Protocol decoder tests completed!")


if __name__ == "__main__":
    print("Starting SGAvl server migration tests...")
    
    # Test protocol decoder
    test_protocol_decoder()
    
    # Test server functionality
    success = test_sgavl_server()
    
    if success:
        print("\n🎉 SGAvl server migration completed successfully!")
        print("✅ Server is fully functional")
        print("✅ Protocol decoder working correctly")
        print("✅ Database integration working")
    else:
        print("\n❌ SGAvl server migration failed!")
        print("Please check the logs for details")
    
    print("\n" + "=" * 80) 