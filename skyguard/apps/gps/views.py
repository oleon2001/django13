"""
Views for the GPS application.
"""
from typing import Dict, Any
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.conf import settings
import logging

from skyguard.apps.gps.services import GPSService
from skyguard.apps.gps.services.connection import DeviceConnectionService
from skyguard.apps.gps.repositories import GPSDeviceRepository
from skyguard.apps.gps.protocols import GPSProtocolHandler
from skyguard.apps.gps.models import GPSDevice, GPSEvent, NetworkEvent, DeviceSession
from skyguard.core.exceptions import (
    DeviceNotFoundError,
    InvalidLocationDataError,
    InvalidEventDataError,
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def process_location(request):
    """
    Process location data from GPS device.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON response with status
    """
    try:
        # Get device IMEI from request
        
        imei = request.POST.get('imei')
        if not imei:
            return JsonResponse({'error': 'IMEI is required'}, status=400)
        
        # Get device
        device = GPSDevice.objects.filter(imei=imei).first()
        if not device:
            return JsonResponse({'error': 'Device not found'}, status=404)
        
        # Process location data
        location_data = {
            'latitude': float(request.POST.get('latitude', 0)),
            'longitude': float(request.POST.get('longitude', 0)),
            'timestamp': timezone.now(),
            'speed': float(request.POST.get('speed', 0)),
            'course': float(request.POST.get('course', 0)),
            'altitude': float(request.POST.get('altitude', 0)),
            'satellites': int(request.POST.get('satellites', 0)),
            'accuracy': float(request.POST.get('accuracy', 0)),
            'hdop': float(request.POST.get('hdop', 0)),
            'pdop': float(request.POST.get('pdop', 0)),
            'fix_quality': int(request.POST.get('fix_quality', 0)),
            'fix_type': int(request.POST.get('fix_type', 0))
        }
        
        # Create service and repository
        repository = GPSDeviceRepository()
        service = GPSService(repository)
        
        # Process location
        service.process_location(device, location_data)
        
        return JsonResponse({'status': 'success'})
    except (InvalidLocationDataError, InvalidEventDataError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def process_event(request):
    """
    Process event data from GPS device.
    
    Args:
        request: HTTP request object containing:
            - imei: Device IMEI number
            - token: Authentication token
            - type: Event type (LOCATION, ALARM, etc.)
            - latitude: Device latitude
            - longitude: Device longitude
            - speed: Device speed in km/h
            - course: Device course in degrees
            - altitude: Device altitude in meters
            - odometer: Device odometer reading
            - battery: Battery level (optional)
            - signal: Signal strength (optional)
            - satellites: Number of satellites (optional)
        
    Returns:
        JSON response with status and optional data
    """
    try:
        # Validate authentication
        token = request.headers.get('X-Device-Token')
        if not token or token != settings.GPS_DEVICE_TOKEN:
            return JsonResponse({'error': 'Invalid authentication token'}, status=401)
        
        # Get and validate IMEI
        imei = request.POST.get('imei')
        if not imei:
            return JsonResponse({'error': 'IMEI is required'}, status=400)
            
        try:
            imei = int(imei)
        except ValueError:
            return JsonResponse({'error': 'Invalid IMEI format'}, status=400)
        
        # Get device
        try:
            device = GPSDevice.objects.get(imei=imei)
        except GPSDevice.DoesNotExist:
            return JsonResponse({'error': 'Device not found'}, status=404)
            
        # Validate device is active
        if not device.is_active:
            return JsonResponse({'error': 'Device is inactive'}, status=403)
        
        # Process event data
        event_data = {
            'type': request.POST.get('type', 'LOCATION'),
            'timestamp': timezone.now(),
            'position': {
                'latitude': float(request.POST.get('latitude', 0)),
                'longitude': float(request.POST.get('longitude', 0))
            },
            'speed': float(request.POST.get('speed', 0)),
            'course': float(request.POST.get('course', 0)),
            'altitude': float(request.POST.get('altitude', 0)),
            'odometer': float(request.POST.get('odometer', 0)),
            'battery': float(request.POST.get('battery', 0)),
            'signal': int(request.POST.get('signal', 0)),
            'satellites': int(request.POST.get('satellites', 0))
        }
        
        # Validate position data
        if not (-90 <= event_data['position']['latitude'] <= 90):
            return JsonResponse({'error': 'Invalid latitude'}, status=400)
        if not (-180 <= event_data['position']['longitude'] <= 180):
            return JsonResponse({'error': 'Invalid longitude'}, status=400)
        
        # Create service and repository
        repository = GPSDeviceRepository()
        service = GPSService(repository)
        
        # Process event
        result = service.process_event(device, event_data)
        
        # Update device connection status
        device.update_connection_status('ONLINE')
        device.update_heartbeat()
        
        return JsonResponse({
            'status': 'success',
            'device_id': device.id,
            'timestamp': result.timestamp.isoformat(),
            'position': {
                'latitude': result.position.y,
                'longitude': result.position.x
            }
        })
        
    except (InvalidLocationDataError, InvalidEventDataError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        # Log the error
        if device:
            device.last_error = str(e)
            device.error_count += 1
            device.save()
        return JsonResponse({'error': 'Internal server error'}, status=500)


@require_http_methods(["GET"])
def get_device_history(request, imei):
    """
    Get location history for a GPS device.
    
    Args:
        request: HTTP request object
        imei: Device IMEI
        
    Returns:
        JSON response with location history
    """
    try:
        # Get time range from request
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        
        # Create service and repository
        repository = GPSDeviceRepository()
        service = GPSService(repository)
        
        # Get device history
        history = service.get_device_history(imei, start_time, end_time)
        
        return JsonResponse({'history': history})
    except DeviceNotFoundError as e:
        return JsonResponse({'error': str(e)}, status=404)
    except InvalidLocationDataError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DeviceCommandView(View):
    """View for sending commands to devices."""
    
    def post(self, request, imei: int):
        """Send a command to a device."""
        try:
            # Get device
            repository = GPSDeviceRepository()
            device = repository.get_device(imei)
            if not device:
                return JsonResponse({'error': 'Device not found'}, status=404)
            
            # Get command data
            command_data = request.json()
            command = command_data.get('command')
            params = command_data.get('params', {})
            
            if not command:
                return JsonResponse({'error': 'Command is required'}, status=400)
            
            # Get protocol handler
            handler = GPSProtocolHandler().get_handler(device.protocol)
            
            # Encode command
            command_bytes = handler.encode_command(command, params)
            
            # TODO: Send command to device
            
            return JsonResponse({'status': 'Command sent'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DeviceHistoryView(View):
    """View for retrieving device history."""
    
    def get(self, request, imei: int):
        """Get device history."""
        try:
            # Get device
            repository = GPSDeviceRepository()
            device = repository.get_device(imei)
            if not device:
                return JsonResponse({'error': 'Device not found'}, status=404)
            
            # Get time range
            start_time = request.GET.get('start_time')
            end_time = request.GET.get('end_time')
            
            # Get history
            service = GPSService(repository)
            history = service.get_device_history(imei, start_time, end_time)
            
            return JsonResponse({'history': history})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DeviceEventsView(View):
    """View for retrieving device events."""
    
    def get(self, request, imei: int):
        """Get device events."""
        try:
            # Get device
            repository = GPSDeviceRepository()
            device = repository.get_device(imei)
            if not device:
                return JsonResponse({'error': 'Device not found'}, status=404)
            
            # Get event type
            event_type = request.GET.get('type')
            
            # Get events
            service = GPSService(repository)
            events = service.get_device_events(imei, event_type)
            
            return JsonResponse({'events': events})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current user information."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_connections(request, imei: int):
    """Get device connection history."""
    try:
        # Get device
        repository = GPSDeviceRepository()
        device = repository.get_device(imei)
        if not device:
            return Response({'error': 'Device not found'}, status=404)

        # Get time range
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        # Convert string dates to datetime objects
        if start_time:
            start_time = datetime.fromisoformat(start_time)
        if end_time:
            end_time = datetime.fromisoformat(end_time)

        # Get connection history
        service = DeviceConnectionService(repository)
        history = service.get_connection_history(device, start_time, end_time)

        return Response({'history': history})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_connection_stats(request, imei: int):
    """Get device connection statistics."""
    try:
        # Get device
        repository = GPSDeviceRepository()
        device = repository.get_device(imei)
        if not device:
            return Response({'error': 'Device not found'}, status=404)

        # Get connection stats
        service = DeviceConnectionService(repository)
        stats = service.get_connection_stats(device)

        return Response(stats)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_current_status(request, imei: int):
    """Get current device connection status."""
    try:
        # Get device
        repository = GPSDeviceRepository()
        device = repository.get_device(imei)
        if not device:
            return Response({'error': 'Device not found'}, status=404)

        # Get current status
        status = {
            'imei': device.imei,
            'name': device.name,
            'connection_status': device.connection_status,
            'current_ip': device.current_ip,
            'current_port': device.current_port,
            'last_connection': device.last_connection,
            'last_heartbeat': device.last_heartbeat,
            'is_online': device.is_online,
            'connection_duration': device.connection_duration,
            'error_count': device.error_count,
            'last_error': device.last_error
        }

        return Response(status)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_sessions(request):
    """Get all active device sessions."""
    try:
        repository = GPSDeviceRepository()
        service = DeviceConnectionService(repository)
        sessions = service.get_active_sessions()

        return Response({
            'sessions': [{
                'device_imei': session.device.imei,
                'device_name': session.device.name,
                'session_id': session.session_id,
                'start_time': session.start_time,
                'duration': session.duration,
                'ip_address': session.ip_address,
                'port': session.port,
                'protocol': session.protocol,
                'total_packets': session.total_packets,
                'total_bytes': session.total_bytes
            } for session in sessions]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_sessions(request):
    """Clean up old device sessions."""
    try:
        days = int(request.data.get('days', 30))
        repository = GPSDeviceRepository()
        service = DeviceConnectionService(repository)
        count = service.cleanup_old_sessions(days)

        return Response({
            'message': f'Cleaned up {count} old sessions',
            'days': days
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_all_devices_status(request):
    """Check status of all devices and update offline ones."""
    try:
        timeout_seconds = int(request.data.get('timeout', 60))  # Default 1 minute
        
        # Calcular el tiempo límite
        timeout_time = timezone.now() - timedelta(seconds=timeout_seconds)
        
        # Obtener dispositivos que están marcados como ONLINE
        online_devices = GPSDevice.objects.filter(connection_status='ONLINE')
        
        devices_updated = []
        devices_still_online = []
        
        for device in online_devices:
            # Verificar si el dispositivo tiene heartbeat reciente
            should_be_offline = False
            reason = ""
            
            if device.last_heartbeat is None:
                should_be_offline = True
                reason = "No heartbeat recorded"
            elif device.last_heartbeat < timeout_time:
                time_since_heartbeat = timezone.now() - device.last_heartbeat
                should_be_offline = True
                reason = f"Last heartbeat {time_since_heartbeat.total_seconds():.0f}s ago"
            
            if should_be_offline:
                try:
                    device.update_connection_status('OFFLINE')
                    devices_updated.append({
                        'imei': device.imei,
                        'name': device.name,
                        'reason': reason
                    })
                    logger.info(f'Marked device {device.imei} as OFFLINE: {reason}')
                except Exception as e:
                    logger.error(f'Error updating device {device.imei}: {e}')
            else:
                time_since_heartbeat = timezone.now() - device.last_heartbeat
                devices_still_online.append({
                    'imei': device.imei,
                    'name': device.name,
                    'heartbeat_age_seconds': time_since_heartbeat.total_seconds()
                })
        
        # Obtener estadísticas actualizadas
        all_devices = GPSDevice.objects.all()
        stats = {
            'total': all_devices.count(),
            'online': all_devices.filter(connection_status='ONLINE').count(),
            'offline': all_devices.filter(connection_status='OFFLINE').count(),
        }
        
        return Response({
            'message': f'Device status check completed',
            'timeout_seconds': timeout_seconds,
            'devices_checked': online_devices.count(),
            'devices_updated_to_offline': len(devices_updated),
            'devices_still_online': len(devices_still_online),
            'updated_devices': devices_updated,
            'online_devices': devices_still_online,
            'current_stats': stats
        })
        
    except Exception as e:
        logger.error(f'Error checking device status: {str(e)}', exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_devices_activity_status(request):
    """Get real-time activity status of all devices."""
    try:
        # Obtener parámetro de timeout
        timeout_minutes = int(request.GET.get('timeout', 1))  # Default 1 minuto
        timeout_time = timezone.now() - timedelta(minutes=timeout_minutes)
        
        # Obtener todos los dispositivos activos
        devices = GPSDevice.objects.filter(is_active=True).order_by('imei')
        
        devices_status = []
        stats = {'online': 0, 'offline': 0, 'total': 0}
        
        for device in devices:
            # Determinar el estado real basado en heartbeat
            is_really_online = False
            heartbeat_age = None
            
            if device.last_heartbeat:
                heartbeat_age = (timezone.now() - device.last_heartbeat).total_seconds()
                is_really_online = device.last_heartbeat >= timeout_time
            
            # Actualizar estadísticas
            stats['total'] += 1
            if is_really_online:
                stats['online'] += 1
            else:
                stats['offline'] += 1
            
            # Si el estado en BD no coincide con el estado real, marcarlo para actualización
            needs_update = (device.connection_status == 'ONLINE') != is_really_online
            
            device_info = {
                'imei': device.imei,
                'name': device.name,
                'connection_status_db': device.connection_status,
                'connection_status_real': 'ONLINE' if is_really_online else 'OFFLINE',
                'needs_update': needs_update,
                'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                'heartbeat_age_seconds': heartbeat_age,
                'current_ip': device.current_ip,
                'current_port': device.current_port,
                'total_connections': device.total_connections,
                'position': {
                    'latitude': device.position.y,
                    'longitude': device.position.x
                } if device.position else None,
                'speed': device.speed,
                'last_update': device.updated_at.isoformat() if device.updated_at else None
            }
            
            devices_status.append(device_info)
        
        return Response({
            'timestamp': timezone.now().isoformat(),
            'timeout_minutes': timeout_minutes,
            'stats': stats,
            'devices': devices_status
        })
        
    except Exception as e:
        logger.error(f'Error getting devices activity status: {str(e)}', exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_real_time_positions(request):
    """Get real-time positions of all devices."""
    try:
        repository = GPSDeviceRepository()
        devices = repository.get_all_devices()
        
        positions = []
        for device in devices:
            if device.position and device.is_online:
                positions.append({
                    'imei': device.imei,
                    'name': device.name,
                    'position': {
                        'latitude': device.position.y,
                        'longitude': device.position.x
                    },
                    'speed': device.speed,
                    'course': device.course,
                    'altitude': device.altitude,
                    'last_update': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                    'connection_status': device.connection_status,
                    'route': device.route,
                    'economico': device.economico
                })
        
        return Response({'positions': positions})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_device_trail(request, imei):
    """Get device position trail for the last period."""
    try:
        hours = int(request.GET.get('hours', 24))
        
        # Get device
        repository = GPSDeviceRepository()
        device = repository.get_device(imei)
        if not device:
            return Response({'error': 'Device not found'}, status=404)
        
        # Get trail from events/history
        from skyguard.apps.gps.models import GPSEvent
        from django.utils import timezone
        from datetime import timedelta
        
        start_time = timezone.now() - timedelta(hours=hours)
        events = GPSEvent.objects.filter(
            device=device,
            timestamp__gte=start_time,
            event_type='LOCATION'
        ).order_by('timestamp')
        
        trail = []
        for event in events:
            if event.position:
                trail.append({
                    'latitude': event.position.y,
                    'longitude': event.position.x,
                    'speed': event.speed,
                    'timestamp': event.timestamp.isoformat(),
                    'course': event.course
                })
        
        return Response({
            'device_imei': imei,
            'device_name': device.name,
            'trail': trail,
            'hours': hours
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_devices(request):
    """Get all GPS devices or create a new one."""
    if request.method == 'POST':
        try:
            imei = request.data.get('imei')
            name = request.data.get('name')
            protocol = request.data.get('protocol', 'concox')  # Default to concox if not specified
            
            if not imei or len(str(imei)) != 15:
                return Response({'error': 'IMEI must be 15 digits'}, status=400)
                
            if GPSDevice.objects.filter(imei=int(imei)).exists():
                return Response({'error': 'Device already exists'}, status=409)
                
            device = GPSDevice.objects.create(
                imei=int(imei),
                name=name or f'Device_{imei}',
                owner=request.user,
                is_active=True,
                connection_status='OFFLINE',
                protocol=protocol
            )
            
            return Response({
                'imei': device.imei,
                'name': device.name,
                'connection_status': device.connection_status,
                'protocol': device.protocol,
                'created_at': device.created_at.isoformat(),
                'updated_at': device.updated_at.isoformat()
            }, status=201)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    # GET method
    try:
        repository = GPSDeviceRepository()
        devices = repository.get_all_devices()
        
        devices_data = []
        for device in devices:
            try:
                device_data = {
                    'imei': device.imei,
                    'name': device.name,
                    'serial': device.serial,
                    'model': device.model,
                    'software_version': device.software_version,
                    'route': device.route,
                    'economico': device.economico,
                    'position': {
                        'latitude': device.position.y,
                        'longitude': device.position.x
                    } if device.position else None,
                    'speed': device.speed,
                    'course': device.course,
                    'altitude': device.altitude,
                    'odometer': device.odometer,
                    'connection_status': device.connection_status,
                    'current_ip': device.current_ip,
                    'current_port': device.current_port,
                    'last_connection': device.last_connection.isoformat() if device.last_connection else None,
                    'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                    'total_connections': device.total_connections,
                    'created_at': device.created_at.isoformat() if device.created_at else None,
                    'updated_at': device.updated_at.isoformat() if device.updated_at else None
                }
                devices_data.append(device_data)
            except Exception as device_error:
                print(f"Error serializing device {device.imei}: {device_error}")
                continue
        
        return Response({'devices': devices_data})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_device(request, imei):
    """Actualizar o eliminar dispositivo GPS existente."""
    try:
        device = GPSDevice.objects.get(imei=imei)
        
        # Permitir que cualquier usuario autenticado modifique o elimine el dispositivo
        
        if request.method == 'DELETE':
            device_name = device.name
            device.delete()
            return Response({
                'message': f'Device {device_name} deleted successfully'
            })
        
        # PATCH method
        if 'name' in request.data:
            device.name = request.data['name']
        if 'route' in request.data:
            device.route = request.data['route']
        if 'economico' in request.data:
            device.economico = request.data['economico']
        if 'is_active' in request.data:
            device.is_active = request.data['is_active']
            
        device.save()
        
        return Response({
            'imei': device.imei,
            'name': device.name,
            'route': device.route,
            'economico': device.economico,
            'is_active': device.is_active,
            'updated_at': device.updated_at.isoformat()
        })
        
    except GPSDevice.DoesNotExist:
        return Response({'error': 'Device not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_device_connection(request, imei):
    """
    Probar conectividad con un dispositivo GPS.
    """
    try:
        logger.info(f"Testing connection for device IMEI: {imei}")
        
        # Buscar el dispositivo
        try:
            device = GPSDevice.objects.get(imei=imei)
            logger.info(f"Found device: {device.name} (Protocol: {device.protocol})")
        except GPSDevice.DoesNotExist:
            logger.error(f"Device not found: {imei}")
            return Response({'error': 'Device not found'}, status=404)
            
        # Verificar permisos
        if not request.user.is_staff and device.owner != request.user:
            logger.warning(f"Permission denied for user {request.user} on device {imei}")
            return Response({'error': 'Permission denied'}, status=403)
            
        # Verificar protocolo
        if not device.protocol:
            logger.error(f"Device {imei} has no protocol configured")
            return Response({
                'success': False,
                'message': 'Device protocol not configured',
                'status': 'ERROR',
                'error': 'Protocol must be configured before testing connection'
            }, status=400)
            
        # Obtener servicios
        repository = GPSDeviceRepository()
        connection_service = DeviceConnectionService(repository)
        
        # Verificar heartbeat reciente (último minuto)
        heartbeat_timeout = 60  # 1 minuto en segundos
        is_recent_heartbeat = False
        
        if device.last_heartbeat:
            time_since_heartbeat = timezone.now() - device.last_heartbeat
            is_recent_heartbeat = time_since_heartbeat.total_seconds() < heartbeat_timeout
            
            if is_recent_heartbeat:
                logger.info(f"Device {imei} has recent heartbeat (last: {device.last_heartbeat})")
                device.update_connection_status('ONLINE')
                device.update_heartbeat()  # Actualizar el heartbeat
                return Response({
                    'success': True,
                    'message': f'Device is online (last heartbeat: {time_since_heartbeat.total_seconds():.0f}s ago)',
                    'last_seen': device.last_heartbeat.isoformat(),
                    'status': 'ONLINE',
                    'heartbeat_age_seconds': time_since_heartbeat.total_seconds(),
                    'connection_details': {
                        'ip_address': device.current_ip,
                        'port': device.current_port,
                        'connection_duration': device.connection_duration.total_seconds() if device.connection_duration else None,
                        'total_connections': device.total_connections,
                        'error_count': device.error_count,
                        'protocol': device.protocol
                    }
                })
        
        # Si no hay heartbeat reciente, intentar ping directo
        logger.info(f"No recent heartbeat for device {imei}, attempting direct ping")
        
        try:
            logger.info(f"Attempting to get protocol handler for {device.protocol}")
            handler = GPSProtocolHandler().get_handler(device.protocol)
            
            logger.info(f"Sending ping to device {imei}")
            ping_result = handler.send_ping(device)
            logger.info(f"Ping result: {ping_result}")
            
            if ping_result and ping_result.get('success'):
                logger.info(f"Device {imei} responded to ping")
                device.update_connection_status('ONLINE')
                device.update_heartbeat()  # Actualizar heartbeat después del ping exitoso
                return Response({
                    'success': True,
                    'message': 'Device responded to ping test',
                    'status': 'ONLINE',
                    'response_time': ping_result.get('response_time', 0),
                    'connection_details': {
                        'ip_address': device.current_ip,
                        'port': device.current_port,
                        'protocol': device.protocol,
                        'total_connections': device.total_connections,
                        'test_method': 'direct_ping'
                    }
                })
            else:
                error_msg = ping_result.get('error_message', 'No response from device') if ping_result else 'Ping failed'
                logger.warning(f"Device {imei} did not respond to ping: {error_msg}")
                device.update_connection_status('OFFLINE')
                return Response({
                    'success': False,
                    'message': f'Device did not respond to ping: {error_msg}',
                    'status': 'OFFLINE',
                    'last_seen': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                    'heartbeat_age_seconds': time_since_heartbeat.total_seconds() if device.last_heartbeat else None,
                    'error': error_msg
                })
                
        except ValueError as ve:
            logger.error(f"Protocol error for device {imei}: {str(ve)}")
            return Response({
                'success': False,
                'message': 'Protocol error',
                'status': 'ERROR',
                'error': str(ve)
            }, status=400)
        except Exception as e:
            logger.error(f"Connection test failed for device {imei}: {str(e)}", exc_info=True)
            connection_service.register_error(device, str(e))
            return Response({
                'success': False,
                'message': 'Connection test failed',
                'status': 'ERROR',
                'error': str(e)
            }, status=500)
            
    except Exception as e:
        logger.error(f"Unexpected error testing device {imei}: {str(e)}", exc_info=True)
        return Response({'error': f'Internal server error: {str(e)}'}, status=500)


# Mock endpoints removed - now using real database endpoints


# Temporary test endpoints removed - production code only

# Mock detail endpoints removed - now using real database endpoints
