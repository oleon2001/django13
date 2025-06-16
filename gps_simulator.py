import requests
import time
import random
from datetime import datetime
import math

# Configuración
BASE_URL = "http://localhost:8000/api/gps"
IMEI = "123456789012345"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwMTA3NDQyLCJpYXQiOjE3NTAxMDM4NDIsImp0aSI6IjU2ZmZiNWQ1N2YyYjRlYWJiM2EyNTQ4YTVlMTg1ODQyIiwidXNlcl9pZCI6Mn0.S0iJVNiGCJFktxgSvXecmGDUhBosFNIih832qMTSJKs"
DEVICE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1MDE5MDI0MiwiaWF0IjoxNzUwMTAzODQyLCJqdGkiOiIxM2JlMTc1NDZlZGI0NDUwOWJmM2Y3MTE5OTVkNWI2YyIsInVzZXJfaWQiOjJ9.aSijRv0w2XF7B1kU_e06ytr-RcL1XUcrtyoJ0J7xF5I"

# Coordenadas iniciales (ejemplo: Ciudad de México)
LATITUDE = 19.4326
LONGITUDE = -99.1332

# Headers para las peticiones
location_headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

event_headers = {
    'X-Device-Token': DEVICE_TOKEN
}

def generate_location():
    """Genera una nueva ubicación simulando movimiento."""
    global LATITUDE, LONGITUDE
    
    # Simular movimiento aleatorio
    lat_change = random.uniform(-0.0001, 0.0001)
    lon_change = random.uniform(-0.0001, 0.0001)
    
    LATITUDE += lat_change
    LONGITUDE += lon_change
    
    # Simular velocidad (0-120 km/h)
    speed = random.uniform(0, 120)
    
    # Simular dirección (0-360 grados)
    course = random.uniform(0, 360)
    
    # Simular altitud (0-2000 metros)
    altitude = random.uniform(0, 2000)
    
    return {
        'latitude': LATITUDE,
        'longitude': LONGITUDE,
        'speed': speed,
        'course': course,
        'altitude': altitude,
        'satellites': random.randint(4, 12),
        'accuracy': random.uniform(1, 10),
        'hdop': random.uniform(0.5, 2.0),
        'pdop': random.uniform(1.0, 3.0),
        'fix_quality': random.randint(1, 5),
        'fix_type': random.randint(1, 3)
    }

def send_location():
    """Envía datos de ubicación al servidor."""
    location_data = generate_location()
    current_time = datetime.now().isoformat()
    
    # Preparar datos para el endpoint de ubicación
    location_payload = {
        'imei': IMEI,
        'timestamp': current_time,
        'latitude': str(location_data['latitude']),
        'longitude': str(location_data['longitude']),
        'speed': str(location_data['speed']),
        'course': str(location_data['course']),
        'altitude': str(location_data['altitude']),
        'satellites': str(location_data['satellites']),
        'accuracy': str(location_data['accuracy']),
        'hdop': str(location_data['hdop']),
        'pdop': str(location_data['pdop']),
        'fix_quality': str(location_data['fix_quality']),
        'fix_type': str(location_data['fix_type'])
    }
    
    # Preparar datos para el endpoint de eventos
    event_payload = {
        'imei': IMEI,
        'type': 'LOCATION',
        'timestamp': current_time,
        'latitude': str(location_data['latitude']),
        'longitude': str(location_data['longitude']),
        'speed': str(location_data['speed']),
        'course': str(location_data['course']),
        'altitude': str(location_data['altitude']),
        'odometer': str(random.uniform(0, 100000)),
        'battery': str(random.uniform(20, 100)),
        'signal': str(random.randint(1, 5)),
        'satellites': str(location_data['satellites'])
    }
    
    try:
        # Enviar ubicación
        location_response = requests.post(
            f"{BASE_URL}/location/",
            data=location_payload,  # Usar data para enviar como form-data
            headers=location_headers
        )
        print(f"Location Response: {location_response.status_code}")
        if location_response.status_code != 200:
            print(f"Location Error: {location_response.text}")
        
        # Enviar evento
        event_response = requests.post(
            f"{BASE_URL}/event/",
            data=event_payload,  # Usar data para enviar como form-data
            headers=event_headers
        )
        print(f"Event Response: {event_response.status_code}")
        if event_response.status_code != 200:
            print(f"Event Error: {event_response.text}")
        
    except Exception as e:
        print(f"Error sending data: {e}")

def main():
    """Función principal que ejecuta el simulador."""
    print(f"Starting GPS simulator for device {IMEI}")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            send_location()
            # Esperar 5 segundos antes de la siguiente actualización
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nSimulator stopped")

if __name__ == "__main__":
    main() 