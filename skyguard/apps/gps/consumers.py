"""
WebSocket consumers for real-time GPS data streaming.
"""
import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder

from .models import GPSDevice, GPSEvent
from .serializers import GPSDeviceSerializer

User = get_user_model()


class GPSRealtimeConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time GPS updates."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room_group_name = None
        self.subscribed_devices = set()
        
    async def connect(self):
        """Handle WebSocket connection."""
        # Authenticate user from query string token
        token = self.scope['query_string'].decode().split('token=')[-1] if b'token=' in self.scope['query_string'] else None
        
        if token:
            try:
                # Validate JWT token
                UntypedToken(token)
                self.user = await self.get_user_from_token(token)
            except (InvalidToken, TokenError):
                await self.close(code=4001)
                return
        else:
            await self.close(code=4001)
            return
            
        if self.user and not isinstance(self.user, AnonymousUser):
            # Join user-specific room
            self.room_group_name = f"gps_user_{self.user.id}"
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send initial device list
            await self.send_device_list()
        else:
            await self.close(code=4003)
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_device':
                await self.handle_device_subscription(data)
            elif message_type == 'unsubscribe_device':
                await self.handle_device_unsubscription(data)
            elif message_type == 'send_command':
                await self.handle_device_command(data)
            elif message_type == 'request_device_list':
                await self.send_device_list()
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
    
    async def handle_device_subscription(self, data):
        """Handle device subscription request."""
        device_imei = data.get('device_imei')
        if device_imei:
            # Verify user has access to this device
            device = await self.get_user_device(device_imei)
            if device:
                self.subscribed_devices.add(device_imei)
                await self.send_success(f"Subscribed to device {device_imei}")
            else:
                await self.send_error(f"Device {device_imei} not found or access denied")
    
    async def handle_device_unsubscription(self, data):
        """Handle device unsubscription request."""
        device_imei = data.get('device_imei')
        if device_imei in self.subscribed_devices:
            self.subscribed_devices.remove(device_imei)
            await self.send_success(f"Unsubscribed from device {device_imei}")
    
    async def handle_device_command(self, data):
        """Handle device command request."""
        device_imei = data.get('device_imei')
        command = data.get('command')
        
        if device_imei and command:
            device = await self.get_user_device(device_imei)
            if device:
                # Process command (implement security validation here)
                success = await self.send_device_command(device, command)
                if success:
                    await self.send_success(f"Command sent to device {device_imei}")
                else:
                    await self.send_error(f"Failed to send command to device {device_imei}")
            else:
                await self.send_error(f"Device {device_imei} not found or access denied")
    
    # WebSocket message types
    async def gps_update(self, event):
        """Send GPS update to WebSocket."""
        device_imei = event['device_imei']
        if str(device_imei) in self.subscribed_devices:
            await self.send(text_data=json.dumps({
                'type': 'gps_update',
                'device_imei': device_imei,
                'position': event['position'],
                'speed': event['speed'],
                'course': event['course'],
                'timestamp': event['timestamp'],
                'status': event['status']
            }, cls=DjangoJSONEncoder))
    
    async def device_status_change(self, event):
        """Send device status change to WebSocket."""
        device_imei = event['device_imei']
        if str(device_imei) in self.subscribed_devices:
            await self.send(text_data=json.dumps({
                'type': 'status_change',
                'device_imei': device_imei,
                'status': event['status'],
                'timestamp': event['timestamp']
            }, cls=DjangoJSONEncoder))
    
    async def alarm_notification(self, event):
        """Send alarm notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'alarm',
            'device_imei': event['device_imei'],
            'alarm_type': event['alarm_type'],
            'message': event['message'],
            'position': event.get('position'),
            'timestamp': event['timestamp'],
            'severity': event.get('severity', 'medium')
        }, cls=DjangoJSONEncoder))
    
    # Helper methods
    @database_sync_to_async
    def get_user_from_token(self, token):
        """Get user from JWT token."""
        try:
            validated_token = UntypedToken(token)
            user_id = validated_token['user_id']
            return User.objects.get(id=user_id)
        except (User.DoesNotExist, KeyError):
            return None
    
    @database_sync_to_async
    def get_user_device(self, device_imei):
        """Get device if user has access."""
        try:
            return GPSDevice.objects.get(imei=device_imei, owner=self.user)
        except GPSDevice.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_user_devices(self):
        """Get all user devices."""
        return list(GPSDevice.objects.filter(owner=self.user).select_related())
    
    async def send_device_list(self):
        """Send user's device list."""
        devices = await self.get_user_devices()
        device_data = []
        
        for device in devices:
            device_data.append({
                'imei': device.imei,
                'name': device.name,
                'status': device.connection_status,
                'last_update': device.last_connection.isoformat() if device.last_connection else None,
                'position': {
                    'latitude': device.position.y if device.position else None,
                    'longitude': device.position.x if device.position else None
                } if device.position else None,
                'speed': device.speed,
                'course': device.course
            })
        
        await self.send(text_data=json.dumps({
            'type': 'device_list',
            'devices': device_data
        }, cls=DjangoJSONEncoder))
    
    async def send_success(self, message):
        """Send success message."""
        await self.send(text_data=json.dumps({
            'type': 'success',
            'message': message
        }))
    
    async def send_error(self, message):
        """Send error message."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def send_device_command(self, device, command):
        """Send command to device (implement actual command sending)."""
        # This would integrate with your existing GPS server infrastructure
        # For now, just log the command
        print(f"Sending command '{command}' to device {device.imei}")
        return True


class GPSAnalyticsConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time analytics."""
    
    async def connect(self):
        """Handle WebSocket connection for analytics."""
        await self.channel_layer.group_add("gps_analytics", self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard("gps_analytics", self.channel_name)
    
    async def analytics_update(self, event):
        """Send analytics update."""
        await self.send(text_data=json.dumps({
            'type': 'analytics_update',
            'data': event['data']
        }, cls=DjangoJSONEncoder)) 