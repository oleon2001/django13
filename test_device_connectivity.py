#!/usr/bin/env python3
"""
Script de prueba para verificar conectividad de dispositivos GPS
Uso: python test_device_connectivity.py <imei> [server_url] [token]
"""

import sys
import requests
import json
from datetime import datetime
import time

class GPSDeviceTester:
    def __init__(self, server_url="http://localhost:8000", token="default_token"):
        self.server_url = server_url.rstrip('/')
        self.token = token
        self.test_data = {
            'latitude': -34.6037,  # Buenos Aires, Argentina
            'longitude': -58.3816,
            'speed': 45.5,
            'course': 90.0,
            'altitude': 25.0,
            'satellites': 8,
            'accuracy': 5.0,
            'battery': 85.5,
            'signal': 75,
            'type': 'LOCATION'
        }
    
    def test_endpoints(self, imei):
        """Prueba todos los endpoints disponibles"""
        print(f"🧪 Testing GPS Device Connectivity for IMEI: {imei}")
        print(f"🌐 Server: {self.server_url}")
        print(f"🔑 Token: {self.token[:10]}...")
        print("=" * 60)
        
        # Test 1: Endpoint simple sin autenticación
        print("\n1️⃣ Testing simple location endpoint...")
        self.test_location_endpoint(imei)
        
        # Test 2: Endpoint completo con autenticación
        print("\n2️⃣ Testing authenticated event endpoint...")
        self.test_event_endpoint(imei)
        
        # Test 3: Verificar estado del dispositivo
        print("\n3️⃣ Checking device status...")
        self.check_device_status(imei)
        
        print("\n" + "=" * 60)
        print("🏁 Testing completed!")
    
    def test_location_endpoint(self, imei):
        """Prueba el endpoint simple de ubicación"""
        try:
            url = f"{self.server_url}/api/gps/location/"
            data = {
                'imei': imei,
                'latitude': self.test_data['latitude'],
                'longitude': self.test_data['longitude'],
                'speed': self.test_data['speed'],
                'course': self.test_data['course'],
                'altitude': self.test_data['altitude']
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print("   ✅ Location endpoint: SUCCESS")
                result = response.json()
                print(f"   📍 Response: {result}")
            elif response.status_code == 404:
                print("   ❌ Location endpoint: DEVICE NOT FOUND")
                print("   💡 Tip: Register the device in Django admin first")
            elif response.status_code == 400:
                print("   ❌ Location endpoint: BAD REQUEST")
                print(f"   📄 Error: {response.text}")
            else:
                print(f"   ⚠️ Location endpoint: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Location endpoint: CONNECTION ERROR")
            print("   💡 Tip: Make sure Django server is running")
        except Exception as e:
            print(f"   ❌ Location endpoint: ERROR - {e}")
    
    def test_event_endpoint(self, imei):
        """Prueba el endpoint completo de eventos"""
        try:
            url = f"{self.server_url}/api/gps/event/"
            headers = {
                'X-Device-Token': self.token,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'imei': imei,
                **self.test_data
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("   ✅ Event endpoint: SUCCESS")
                result = response.json()
                print(f"   📊 Device ID: {result.get('device_id')}")
                print(f"   📍 Position: {result.get('position')}")
                print(f"   ⏰ Timestamp: {result.get('timestamp')}")
            elif response.status_code == 401:
                print("   ❌ Event endpoint: AUTHENTICATION FAILED")
                print("   💡 Tip: Check GPS_DEVICE_TOKEN in settings.py")
            elif response.status_code == 404:
                print("   ❌ Event endpoint: DEVICE NOT FOUND")
                print("   💡 Tip: Register the device first")
            elif response.status_code == 403:
                print("   ❌ Event endpoint: DEVICE INACTIVE")
                print("   💡 Tip: Activate the device in Django admin")
            else:
                print(f"   ⚠️ Event endpoint: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Event endpoint: CONNECTION ERROR")
            print("   💡 Tip: Make sure Django server is running")
        except Exception as e:
            print(f"   ❌ Event endpoint: ERROR - {e}")
    
    def check_device_status(self, imei):
        """Verifica el estado del dispositivo"""
        try:
            url = f"{self.server_url}/api/gps/devices/{imei}/status/"
            headers = {'X-Device-Token': self.token}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("   ✅ Device status: ACCESSIBLE")
                status = response.json()
                print(f"   📊 Connection Status: {status.get('connection_status')}")
                print(f"   📡 Last Heartbeat: {status.get('last_heartbeat')}")
                print(f"   🌐 Current IP: {status.get('current_ip')}")
            elif response.status_code == 404:
                print("   ❌ Device status: NOT FOUND")
            else:
                print(f"   ⚠️ Device status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Device status: CONNECTION ERROR")
        except Exception as e:
            print(f"   ❌ Device status: ERROR - {e}")
    
    def simulate_continuous_sending(self, imei, interval=30, duration=300):
        """Simula envío continuo de datos como haría un dispositivo real"""
        print(f"\n🔄 Simulating continuous GPS data sending...")
        print(f"📱 IMEI: {imei}")
        print(f"⏱️ Interval: {interval} seconds")
        print(f"⏳ Duration: {duration} seconds")
        print("Press Ctrl+C to stop...\n")
        
        start_time = time.time()
        count = 0
        
        try:
            while time.time() - start_time < duration:
                count += 1
                
                # Simular pequeñas variaciones en coordenadas
                lat_variation = (count % 10) * 0.0001
                lon_variation = (count % 10) * 0.0001
                
                test_data = {
                    'imei': imei,
                    'latitude': self.test_data['latitude'] + lat_variation,
                    'longitude': self.test_data['longitude'] + lon_variation,
                    'speed': self.test_data['speed'] + (count % 5),
                    'course': (self.test_data['course'] + count) % 360,
                    'type': 'LOCATION'
                }
                
                # Enviar datos
                url = f"{self.server_url}/api/gps/event/"
                headers = {'X-Device-Token': self.token}
                
                try:
                    response = requests.post(url, data=test_data, headers=headers, timeout=5)
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"{status} Send #{count:03d} - Status: {response.status_code} - "
                          f"Lat: {test_data['latitude']:.6f}, Lon: {test_data['longitude']:.6f}")
                except Exception as e:
                    print(f"❌ Send #{count:03d} - Error: {e}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n⏹️ Stopped after {count} transmissions")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_device_connectivity.py <imei> [server_url] [token]")
        print("Example: python test_device_connectivity.py 123456789012345")
        print("Example: python test_device_connectivity.py 123456789012345 http://localhost:8000 my_secret_token")
        sys.exit(1)
    
    imei = sys.argv[1]
    server_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    token = sys.argv[3] if len(sys.argv) > 3 else "default_token"
    
    tester = GPSDeviceTester(server_url, token)
    
    # Validar IMEI
    if not imei.isdigit() or len(imei) != 15:
        print("❌ Error: IMEI must be 15 digits")
        sys.exit(1)
    
    # Ejecutar pruebas
    tester.test_endpoints(imei)
    
    # Preguntar si quiere simular envío continuo
    response = input("\n🤔 Do you want to simulate continuous GPS sending? (y/N): ")
    if response.lower() in ['y', 'yes']:
        try:
            interval = int(input("⏱️ Enter interval in seconds (default 30): ") or "30")
            duration = int(input("⏳ Enter duration in seconds (default 300): ") or "300")
            tester.simulate_continuous_sending(imei, interval, duration)
        except ValueError:
            print("❌ Invalid number format")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 