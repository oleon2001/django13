#!/usr/bin/env python3
import requests
import json
import sys

def test_endpoint(url, description):
    """Test an endpoint and show results."""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print('='*50)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            if 'devices' in data:
                print(f"📊 Found {len(data['devices'])} devices")
                if data['devices']:
                    print("📋 First device sample:")
                    first_device = data['devices'][0]
                    for key, value in list(first_device.items())[:5]:  # Show first 5 fields
                        print(f"   {key}: {value}")
            elif 'device_count' in data:
                print(f"📊 Device count: {data['device_count']}")
            else:
                print(f"📋 Response: {json.dumps(data, indent=2)[:200]}...")
                
        elif response.status_code == 401:
            print("🔒 AUTHENTICATION REQUIRED (Expected for authenticated endpoints)")
            
        elif response.status_code == 500:
            print("❌ SERVER ERROR!")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
                if 'traceback' in error_data:
                    print("Stack trace:")
                    print(error_data['traceback'][:500] + "...")
            except:
                print(f"Error response: {response.text[:200]}...")
                
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Make sure Django server is running on localhost:8000")
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT ERROR")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    base_url = "http://localhost:8000"
    
    print("🧪 Django Endpoint Testing Script")
    print(f"🌐 Base URL: {base_url}")
    
    # Test endpoints
    endpoints = [
        (f"{base_url}/api/gps/test-devices/", "Simple test endpoint (no auth)"),
        (f"{base_url}/api/gps/devices-debug/", "Full devices list (no auth)"),
        (f"{base_url}/api/gps/devices/", "Original devices endpoint (requires auth)"),
    ]
    
    for url, description in endpoints:
        test_endpoint(url, description)
    
    print(f"\n{'='*50}")
    print("🏁 Testing completed!")
    print("💡 If the debug endpoints work but the original fails with 401,")
    print("   then the serialization issue is fixed and you just need JWT authentication.")
    print("='*50")

if __name__ == "__main__":
    main() 