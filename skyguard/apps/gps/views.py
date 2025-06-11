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

from skyguard.apps.gps.services import GPSService
from skyguard.apps.gps.repositories import GPSDeviceRepository
from skyguard.apps.gps.protocols import GPSProtocolHandler


@csrf_exempt
@require_http_methods(["POST"])
def device_data(request, protocol: str):
    """Handle incoming device data."""
    try:
        # Get protocol handler
        handler = GPSProtocolHandler().get_handler(protocol)
        
        # Validate packet
        if not handler.validate_packet(request.body):
            return HttpResponse(status=400)
        
        # Decode packet
        data = handler.decode_packet(request.body)
        
        # Get device
        repository = GPSDeviceRepository()
        device = repository.get_device(data['imei'])
        if not device:
            return HttpResponse(status=404)
        
        # Process data
        service = GPSService(repository)
        service.process_location(device, data)
        
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(str(e), status=500)


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
