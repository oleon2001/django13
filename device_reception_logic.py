#!/usr/bin/env python3
"""
Lógica completa para recepción de dispositivos GPS
Ejemplo de implementación basado en el sistema SkyGuard
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.conf import settings

# Simulación de modelos y servicios
class DeviceReceptionLogic:
    """
    Lógica completa para recibir y procesar datos de dispositivos GPS
    """
    
    def __init__(self):
        self.supported_protocols = ['HTTP', 'UDP_CONCOX', 'UDP_MEILIGAO', 'TCP_SAT']
        self.required_device_token = getattr(settings, 'GPS_DEVICE_TOKEN', 'default_token')
    
    # ==========================================
    # 1. VERIFICACIÓN DE DISPOSITIVO
    # ==========================================
    
    def verify_device_exists(self, imei: str) -> Tuple[bool, Optional[object], str]:
        """
        Verifica si el dispositivo existe en el sistema
        
        Args:
            imei: IMEI del dispositivo
            
        Returns:
            Tuple[existe, dispositivo, mensaje]
        """
        try:
            # Validar formato IMEI
            if not self.validate_imei_format(imei):
                return False, None, "IMEI format invalid"
            
            # Buscar dispositivo en base de datos
            from skyguard.apps.gps.models import GPSDevice
            device = GPSDevice.objects.filter(imei=int(imei)).first()
            
            if not device:
                return False, None, f"Device {imei} not found in system"
            
            # Verificar si está activo
            if not device.is_active:
                return False, device, f"Device {imei} is inactive"
            
            # Verificar si está bloqueado
            if hasattr(device, 'is_blocked') and device.is_blocked:
                return False, device, f"Device {imei} is blocked"
            
            return True, device, "Device verified successfully"
            
        except Exception as e:
            return False, None, f"Error verifying device: {str(e)}"
    
    def validate_imei_format(self, imei: str) -> bool:
        """
        Valida el formato del IMEI
        
        Args:
            imei: IMEI a validar
            
        Returns:
            bool: True si es válido
        """
        try:
            # IMEI debe ser numérico y tener 15 dígitos
            if not imei.isdigit():
                return False
            if len(imei) != 15:
                return False
            return True
        except:
            return False
    
    # ==========================================
    # 2. AUTENTICACIÓN Y AUTORIZACIÓN
    # ==========================================
    
    def authenticate_device(self, request) -> Tuple[bool, str]:
        """
        Autentica el dispositivo usando diferentes métodos
        
        Args:
            request: Objeto request de Django
            
        Returns:
            Tuple[autenticado, mensaje]
        """
        # Método 1: Token en headers (más seguro)
        device_token = request.headers.get('X-Device-Token')
        if device_token:
            if device_token == self.required_device_token:
                return True, "Authentication successful via header token"
            else:
                return False, "Invalid device token"
        
        # Método 2: Token en POST data (compatibilidad)
        token = request.POST.get('token')
        if token:
            if token == self.required_device_token:
                return True, "Authentication successful via POST token"
            else:
                return False, "Invalid POST token"
        
        # Método 3: Autenticación por IP (whitelist)
        client_ip = self.get_client_ip(request)
        if self.is_ip_whitelisted(client_ip):
            return True, f"Authentication successful via IP whitelist: {client_ip}"
        
        return False, "No valid authentication method found"
    
    def get_client_ip(self, request) -> str:
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_ip_whitelisted(self, ip: str) -> bool:
        """Verifica si la IP está en la whitelist"""
        # Implementar lógica de whitelist de IPs
        whitelist = getattr(settings, 'GPS_DEVICE_IP_WHITELIST', [])
        return ip in whitelist
    
    # ==========================================
    # 3. VALIDACIÓN DE DATOS GPS
    # ==========================================
    
    def validate_gps_data(self, data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Valida y normaliza los datos GPS recibidos
        
        Args:
            data: Datos GPS en bruto
            
        Returns:
            Tuple[válido, mensaje, datos_normalizados]
        """
        try:
            # Campos requeridos mínimos
            required_fields = ['latitude', 'longitude', 'imei']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return False, f"Missing required fields: {missing_fields}", {}
            
            # Validar coordenadas
            lat = float(data['latitude'])
            lon = float(data['longitude'])
            
            if not (-90 <= lat <= 90):
                return False, f"Invalid latitude: {lat}", {}
            
            if not (-180 <= lon <= 180):
                return False, f"Invalid longitude: {lon}", {}
            
            # Normalizar datos
            normalized_data = {
                'imei': str(data['imei']),
                'latitude': lat,
                'longitude': lon,
                'speed': float(data.get('speed', 0)),
                'course': float(data.get('course', 0)),
                'altitude': float(data.get('altitude', 0)),
                'timestamp': self.parse_timestamp(data.get('timestamp')),
                'satellites': int(data.get('satellites', 0)),
                'accuracy': float(data.get('accuracy', 0)),
                'battery': float(data.get('battery', 0)),
                'signal': int(data.get('signal', 0)),
                'event_type': data.get('type', 'LOCATION'),
                'odometer': float(data.get('odometer', 0))
            }
            
            return True, "GPS data validated successfully", normalized_data
            
        except (ValueError, TypeError) as e:
            return False, f"Data validation error: {str(e)}", {}
    
    def parse_timestamp(self, timestamp_str: Any) -> datetime:
        """Parsea timestamp en diferentes formatos"""
        if not timestamp_str:
            return timezone.now()
        
        # Si ya es datetime
        if isinstance(timestamp_str, datetime):
            return timestamp_str
        
        # Si es timestamp unix
        try:
            if str(timestamp_str).isdigit():
                return datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc)
        except:
            pass
        
        # Si es string ISO
        try:
            return datetime.fromisoformat(str(timestamp_str))
        except:
            pass
        
        # Default: ahora
        return timezone.now()
    
    # ==========================================
    # 4. PROCESAMIENTO DE DATOS
    # ==========================================
    
    def process_device_data(self, device, validated_data: Dict[str, Any]) -> Tuple[bool, str, Optional[object]]:
        """
        Procesa los datos validados del dispositivo
        
        Args:
            device: Instancia del dispositivo
            validated_data: Datos GPS validados
            
        Returns:
            Tuple[procesado, mensaje, resultado]
        """
        try:
            from skyguard.apps.gps.repositories import GPSDeviceRepository
            from skyguard.apps.gps.services import GPSService
            
            # Crear punto geográfico
            position = Point(validated_data['longitude'], validated_data['latitude'])
            
            # Preparar datos de ubicación
            location_data = {
                'position': position,
                'speed': validated_data['speed'],
                'course': validated_data['course'],
                'altitude': validated_data['altitude'],
                'satellites': validated_data['satellites'],
                'accuracy': validated_data['accuracy'],
                'timestamp': validated_data['timestamp']
            }
            
            # Preparar datos de evento
            event_data = {
                'type': validated_data['event_type'],
                'timestamp': validated_data['timestamp'],
                'position': position,
                'speed': validated_data['speed'],
                'course': validated_data['course'],
                'altitude': validated_data['altitude'],
                'odometer': validated_data['odometer'],
                'raw_data': json.dumps(validated_data)
            }
            
            # Procesar usando servicios
            repository = GPSDeviceRepository()
            service = GPSService(repository)
            
            # Crear ubicación
            location = service.process_location(device, location_data)
            
            # Crear evento
            event = service.process_event(device, event_data)
            
            # Actualizar estado de conexión del dispositivo
            device.update_connection_status('ONLINE')
            device.update_heartbeat()
            
            return True, "Data processed successfully", {
                'location': location,
                'event': event,
                'device_id': device.id
            }
            
        except Exception as e:
            # Registrar error en el dispositivo
            device.record_error(str(e))
            return False, f"Error processing data: {str(e)}", None
    
    # ==========================================
    # 5. ENDPOINT PRINCIPAL
    # ==========================================
    
    @csrf_exempt
    @require_http_methods(["POST"])
    def receive_device_data(self, request):
        """
        Endpoint principal para recibir datos de dispositivos GPS
        
        Args:
            request: Request HTTP de Django
            
        Returns:
            JsonResponse: Respuesta JSON con resultado
        """
        try:
            # Paso 1: Autenticación
            is_authenticated, auth_message = self.authenticate_device(request)
            if not is_authenticated:
                return JsonResponse({
                    'status': 'error',
                    'message': auth_message,
                    'code': 'AUTH_FAILED'
                }, status=401)
            
            # Paso 2: Obtener IMEI
            imei = request.POST.get('imei')
            if not imei:
                return JsonResponse({
                    'status': 'error',
                    'message': 'IMEI is required',
                    'code': 'MISSING_IMEI'
                }, status=400)
            
            # Paso 3: Verificar dispositivo
            device_exists, device, device_message = self.verify_device_exists(imei)
            if not device_exists:
                return JsonResponse({
                    'status': 'error',
                    'message': device_message,
                    'code': 'DEVICE_NOT_FOUND'
                }, status=404)
            
            # Paso 4: Validar datos GPS
            raw_data = dict(request.POST)
            is_valid, validation_message, validated_data = self.validate_gps_data(raw_data)
            if not is_valid:
                return JsonResponse({
                    'status': 'error',
                    'message': validation_message,
                    'code': 'INVALID_DATA'
                }, status=400)
            
            # Paso 5: Procesar datos
            is_processed, process_message, result = self.process_device_data(device, validated_data)
            if not is_processed:
                return JsonResponse({
                    'status': 'error',
                    'message': process_message,
                    'code': 'PROCESSING_ERROR'
                }, status=500)
            
            # Respuesta exitosa
            return JsonResponse({
                'status': 'success',
                'message': 'Data received and processed successfully',
                'data': {
                    'device_id': device.id,
                    'timestamp': result['event'].timestamp.isoformat(),
                    'position': {
                        'latitude': validated_data['latitude'],
                        'longitude': validated_data['longitude']
                    },
                    'processed_at': timezone.now().isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}',
                'code': 'INTERNAL_ERROR'
            }, status=500)

# ==========================================
# 6. CONFIGURACIÓN DE URLs
# ==========================================

# En urls.py:
"""
from django.urls import path
from .views import DeviceReceptionLogic

device_logic = DeviceReceptionLogic()

urlpatterns = [
    path('gps/receive/', device_logic.receive_device_data, name='receive_device_data'),
    path('gps/location/', views.process_location, name='process_location'),  # Endpoint existente
    path('gps/event/', views.process_event, name='process_event'),          # Endpoint existente
]
"""

# ==========================================
# 7. CONFIGURACIÓN DEL HARDWARE
# ==========================================

class HardwareConfiguration:
    """
    Configuraciones para diferentes tipos de hardware GPS
    """
    
    @staticmethod
    def get_configuration_examples():
        return {
            "concox_http": {
                "url": "http://tu-servidor.com/api/gps/receive/",
                "method": "POST",
                "headers": {
                    "X-Device-Token": "",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                "interval": 30  # segundos
            },
            
            "generic_gps_tracker": {
                "server_ip": "tu-servidor.com",
                "server_port": 8080,
                "protocol": "TCP/UDP",
                "format": "GPRMC",
                "auth_method": "IMEI + Token"
            },
            
            "meiligao_protocol": {
                "server_ip": "tu-servidor.com",
                "server_port": 9955,
                "protocol": "UDP",
                "packet_format": "Binary",
                "heartbeat_interval": 60
            }
        }

# ==========================================
# 8. MONITOREO Y DIAGNÓSTICO
# ==========================================

class DeviceMonitoring:
    """
    Herramientas para monitorear la recepción de dispositivos
    """
    
    @staticmethod
    def check_device_connectivity(imei: str) -> Dict[str, Any]:
        """
        Verifica el estado de conectividad de un dispositivo
        """
        try:
            from skyguard.apps.gps.models import GPSDevice
            device = GPSDevice.objects.get(imei=imei)
            
            return {
                "device_found": True,
                "is_active": device.is_active,
                "connection_status": device.connection_status,
                "last_heartbeat": device.last_heartbeat,
                "last_connection": device.last_connection,
                "error_count": device.error_count,
                "last_error": device.last_error,
                "recommendations": [
                    "Check hardware configuration" if device.error_count > 5 else None,
                    "Verify network connectivity" if not device.last_heartbeat else None,
                    "Update firmware" if device.software_version == "----" else None
                ]
            }
        except Exception as e:
            return {
                "device_found": False,
                "error": str(e),
                "recommendations": [
                    "Register device in system first",
                    "Verify IMEI is correct"
                ]
            }

if __name__ == "__main__":
    # Ejemplo de uso
    logic = DeviceReceptionLogic()
    monitoring = DeviceMonitoring()
    
    print("🔧 Configuración de Hardware:")
    configs = HardwareConfiguration.get_configuration_examples()
    for device_type, config in configs.items():
        print(f"  {device_type}: {config}")
    
    print("\n📊 Diagnóstico de dispositivo ejemplo:")
    status = monitoring.check_device_connectivity("123456789012345")
    print(f"  Status: {status}") 