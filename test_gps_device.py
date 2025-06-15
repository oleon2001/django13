import requests
import json

def test_gps_device(imei, server_url="http://localhost:8000", token="default_token"):
    """Prueba la conectividad de un dispositivo GPS"""
    print(f"Testing GPS Device: {imei}")
    print(f"Server: {server_url}")
    
    # Datos de prueba
    test_data = {
        'imei': imei,
        'latitude': -34.6037,
        'longitude': -58.3816,
        'speed': 50,
        'course': 90,
        'type': 'LOCATION'
    }
    
    # Test endpoint con autenticación
    url = f"{server_url}/api/gps/event/"
    headers = {'X-Device-Token': token}
    
    try:
        response = requests.post(url, data=test_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Device can send data!")
        elif response.status_code == 404:
            print("❌ Device not found. Register it first.")
        elif response.status_code == 401:
            print("❌ Authentication failed. Check token.")
        else:
            print("⚠️ Unexpected response")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    # Cambiar estos valores por los tuyos
    IMEI = "123456789012345"  # Tu IMEI de 15 dígitos
    SERVER = "http://localhost:8000"  # Tu servidor
    TOKEN = "default_token"  # Tu token
    
    test_gps_device(IMEI, SERVER, TOKEN) 