"""
Middleware para detectar actividad de dispositivos GPS y actualizar heartbeat.
"""

import logging
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from skyguard.apps.gps.models.device import GPSDevice

logger = logging.getLogger(__name__)


class GPSDeviceActivityMiddleware(MiddlewareMixin):
    """
    Middleware para detectar actividad de dispositivos GPS y actualizar su heartbeat.
    """
    
    def process_request(self, request):
        """
        Procesa cada petición para detectar actividad de dispositivos GPS.
        """
        # Solo procesar peticiones a endpoints GPS
        if not request.path.startswith('/api/gps/'):
            return None
            
        # Buscar IMEI en diferentes lugares de la petición
        imei = self._extract_imei(request)
        
        if imei:
            try:
                # Buscar el dispositivo
                device = GPSDevice.objects.get(imei=imei)
                
                # Actualizar heartbeat y estado
                device.last_heartbeat = timezone.now()
                
                # Si el dispositivo estaba offline, marcarlo como online
                if device.connection_status != 'ONLINE':
                    device.connection_status = 'ONLINE'
                    logger.info(f"Device {imei} marked as ONLINE due to activity")
                
                # Actualizar IP y puerto si están disponibles
                client_ip = self._get_client_ip(request)
                if client_ip:
                    device.current_ip = client_ip
                
                device.save()
                
                # Agregar información del dispositivo al request para uso posterior
                request.gps_device = device
                
            except GPSDevice.DoesNotExist:
                logger.warning(f"Received request from unknown device IMEI: {imei}")
            except Exception as e:
                logger.error(f"Error updating device activity for IMEI {imei}: {e}")
        
        return None
    
    def _extract_imei(self, request):
        """
        Extrae el IMEI de la petición desde diferentes fuentes.
        """
        # 1. Desde parámetros POST
        imei = request.POST.get('imei')
        if imei:
            return self._validate_imei(imei)
        
        # 2. Desde parámetros GET
        imei = request.GET.get('imei')
        if imei:
            return self._validate_imei(imei)
        
        # 3. Desde la URL (parámetros de ruta)
        path_parts = request.path.strip('/').split('/')
        for i, part in enumerate(path_parts):
            if part == 'devices' and i + 1 < len(path_parts):
                potential_imei = path_parts[i + 1]
                if self._validate_imei(potential_imei):
                    return potential_imei
        
        # 4. Desde headers personalizados
        imei = request.META.get('HTTP_X_DEVICE_IMEI')
        if imei:
            return self._validate_imei(imei)
        
        # 5. Desde JSON body (si es aplicable)
        if hasattr(request, 'json') and request.json:
            imei = request.json.get('imei')
            if imei:
                return self._validate_imei(imei)
        
        return None
    
    def _validate_imei(self, imei):
        """
        Valida que el IMEI tenga el formato correcto.
        """
        try:
            imei_int = int(imei)
            # IMEI debe tener 15 dígitos
            if 10**14 <= imei_int < 10**15:
                return imei_int
        except (ValueError, TypeError):
            pass
        return None
    
    def _get_client_ip(self, request):
        """
        Obtiene la IP del cliente considerando proxies.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 