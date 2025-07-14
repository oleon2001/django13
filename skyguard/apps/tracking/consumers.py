"""
WebSocket consumers for real-time tracking data streaming.
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

from .models import DeviceSession, TrackingSession, Alert, Geofence
from .services import TrackingService, AlertService, GeofenceService

User = get_user_model()


class TrackingRealtimeConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time tracking updates."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room_group_name = None
        self.subscribed_sessions = set()
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
            self.room_group_name = f"tracking_user_{self.user.id}"
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send initial session list
            await self.send_session_list()
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
            
            if message_type == 'subscribe_session':
                await self.handle_session_subscription(data)
            elif message_type == 'unsubscribe_session':
                await self.handle_session_unsubscription(data)
            elif message_type == 'subscribe_device':
                await self.handle_device_subscription(data)
            elif message_type == 'unsubscribe_device':
                await self.handle_device_unsubscription(data)
            elif message_type == 'request_session_list':
                await self.send_session_list()
            elif message_type == 'start_tracking':
                await self.handle_start_tracking(data)
            elif message_type == 'stop_tracking':
                await self.handle_stop_tracking(data)
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
    
    async def handle_session_subscription(self, data):
        """Handle tracking session subscription request."""
        session_id = data.get('session_id')
        if session_id:
            session = await self.get_user_session(session_id)
            if session:
                self.subscribed_sessions.add(session_id)
                await self.send_success(f"Subscribed to session {session_id}")
            else:
                await self.send_error(f"Session {session_id} not found or access denied")
    
    async def handle_session_unsubscription(self, data):
        """Handle tracking session unsubscription request."""
        session_id = data.get('session_id')
        if session_id in self.subscribed_sessions:
            self.subscribed_sessions.remove(session_id)
            await self.send_success(f"Unsubscribed from session {session_id}")
    
    async def handle_device_subscription(self, data):
        """Handle device subscription request."""
        device_imei = data.get('device_imei')
        if device_imei:
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
    
    async def handle_start_tracking(self, data):
        """Handle start tracking request."""
        device_imei = data.get('device_imei')
        if device_imei:
            device = await self.get_user_device(device_imei)
            if device:
                session = await self.start_tracking_session(device)
                if session:
                    await self.send_success(f"Started tracking session for device {device_imei}")
                    await self.send_session_update(session)
                else:
                    await self.send_error(f"Failed to start tracking for device {device_imei}")
            else:
                await self.send_error(f"Device {device_imei} not found or access denied")
    
    async def handle_stop_tracking(self, data):
        """Handle stop tracking request."""
        session_id = data.get('session_id')
        if session_id:
            session = await self.get_user_session(session_id)
            if session:
                success = await self.stop_tracking_session(session)
                if success:
                    await self.send_success(f"Stopped tracking session {session_id}")
                    await self.send_session_update(session)
                else:
                    await self.send_error(f"Failed to stop tracking session {session_id}")
            else:
                await self.send_error(f"Session {session_id} not found or access denied")
    
    # WebSocket message types
    async def tracking_update(self, event):
        """Send tracking update to WebSocket."""
        session_id = event['session_id']
        if str(session_id) in self.subscribed_sessions:
            await self.send(text_data=json.dumps({
                'type': 'tracking_update',
                'session_id': session_id,
                'device_imei': event['device_imei'],
                'position': event['position'],
                'speed': event['speed'],
                'course': event['course'],
                'timestamp': event['timestamp'],
                'status': event['status'],
                'distance': event.get('distance'),
                'duration': event.get('duration')
            }, cls=DjangoJSONEncoder))
    
    async def alert_notification(self, event):
        """Send alert notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'alert_id': event['alert_id'],
            'device_imei': event['device_imei'],
            'alert_type': event['alert_type'],
            'message': event['message'],
            'position': event.get('position'),
            'timestamp': event['timestamp'],
            'severity': event.get('severity', 'medium'),
            'acknowledged': event.get('acknowledged', False)
        }, cls=DjangoJSONEncoder))
    
    async def geofence_event(self, event):
        """Send geofence event to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'geofence_event',
            'geofence_id': event['geofence_id'],
            'device_imei': event['device_imei'],
            'event_type': event['event_type'],  # 'enter' or 'exit'
            'geofence_name': event['geofence_name'],
            'position': event.get('position'),
            'timestamp': event['timestamp']
        }, cls=DjangoJSONEncoder))
    
    async def session_status_change(self, event):
        """Send session status change to WebSocket."""
        session_id = event['session_id']
        if str(session_id) in self.subscribed_sessions:
            await self.send(text_data=json.dumps({
                'type': 'session_status_change',
                'session_id': session_id,
                'status': event['status'],
                'timestamp': event['timestamp'],
                'duration': event.get('duration'),
                'distance': event.get('distance')
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
    def get_user_session(self, session_id):
        """Get session if user has access."""
        try:
            return TrackingSession.objects.get(id=session_id, user=self.user)
        except TrackingSession.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_user_device(self, device_imei):
        """Get device if user has access."""
        try:
            from skyguard.apps.gps.models import GPSDevice
            return GPSDevice.objects.get(imei=device_imei, owner=self.user)
        except:
            return None
    
    @database_sync_to_async
    def get_user_sessions(self):
        """Get all user sessions."""
        return list(TrackingSession.objects.filter(user=self.user).select_related('device'))
    
    @database_sync_to_async
    def start_tracking_session(self, device):
        """Start a new tracking session."""
        service = TrackingService()
        return service.start_session(device, self.user)
    
    @database_sync_to_async
    def stop_tracking_session(self, session):
        """Stop a tracking session."""
        service = TrackingService()
        return service.stop_session(session)
    
    async def send_session_list(self):
        """Send current session list to client."""
        sessions = await self.get_user_sessions()
        session_data = []
        for session in sessions:
            session_data.append({
                'id': session.id,
                'device_imei': session.device.imei if session.device else None,
                'status': session.status,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'duration': session.duration,
                'distance': session.distance
            })
        
        await self.send(text_data=json.dumps({
            'type': 'session_list',
            'sessions': session_data
        }, cls=DjangoJSONEncoder))
    
    async def send_session_update(self, session):
        """Send session update to client."""
        await self.send(text_data=json.dumps({
            'type': 'session_update',
            'session': {
                'id': session.id,
                'device_imei': session.device.imei if session.device else None,
                'status': session.status,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'duration': session.duration,
                'distance': session.distance
            }
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


class AlertConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time alert notifications."""
    
    async def connect(self):
        """Handle WebSocket connection for alerts."""
        # Authenticate user
        token = self.scope['query_string'].decode().split('token=')[-1] if b'token=' in self.scope['query_string'] else None
        
        if token:
            try:
                UntypedToken(token)
                self.user = await self.get_user_from_token(token)
            except (InvalidToken, TokenError):
                await self.close(code=4001)
                return
        else:
            await self.close(code=4001)
            return
        
        if self.user and not isinstance(self.user, AnonymousUser):
            self.room_group_name = f"alerts_user_{self.user.id}"
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send unacknowledged alerts
            await self.send_unacknowledged_alerts()
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
            
            if message_type == 'acknowledge_alert':
                await self.handle_alert_acknowledgment(data)
            elif message_type == 'request_alerts':
                await self.send_user_alerts()
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
    
    async def handle_alert_acknowledgment(self, data):
        """Handle alert acknowledgment."""
        alert_id = data.get('alert_id')
        if alert_id:
            success = await self.acknowledge_alert(alert_id)
            if success:
                await self.send_success(f"Alert {alert_id} acknowledged")
            else:
                await self.send_error(f"Failed to acknowledge alert {alert_id}")
    
    async def alert_created(self, event):
        """Send new alert to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'new_alert',
            'alert': event['alert']
        }, cls=DjangoJSONEncoder))
    
    async def alert_updated(self, event):
        """Send alert update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'alert_updated',
            'alert': event['alert']
        }, cls=DjangoJSONEncoder))
    
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
    def get_user_alerts(self):
        """Get user's alerts."""
        return list(Alert.objects.filter(user=self.user).order_by('-created_at')[:50])
    
    @database_sync_to_async
    def get_unacknowledged_alerts(self):
        """Get user's unacknowledged alerts."""
        return list(Alert.objects.filter(user=self.user, acknowledged=False).order_by('-created_at'))
    
    @database_sync_to_async
    def acknowledge_alert(self, alert_id):
        """Acknowledge an alert."""
        try:
            alert = Alert.objects.get(id=alert_id, user=self.user)
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now()
            alert.save()
            return True
        except Alert.DoesNotExist:
            return False
    
    async def send_user_alerts(self):
        """Send user's alerts to client."""
        alerts = await self.get_user_alerts()
        alert_data = []
        for alert in alerts:
            alert_data.append({
                'id': alert.id,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'severity': alert.severity,
                'acknowledged': alert.acknowledged,
                'created_at': alert.created_at.isoformat(),
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
            })
        
        await self.send(text_data=json.dumps({
            'type': 'alerts_list',
            'alerts': alert_data
        }, cls=DjangoJSONEncoder))
    
    async def send_unacknowledged_alerts(self):
        """Send unacknowledged alerts to client."""
        alerts = await self.get_unacknowledged_alerts()
        alert_data = []
        for alert in alerts:
            alert_data.append({
                'id': alert.id,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'severity': alert.severity,
                'created_at': alert.created_at.isoformat()
            })
        
        await self.send(text_data=json.dumps({
            'type': 'unacknowledged_alerts',
            'alerts': alert_data
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


class GeofenceConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time geofence events."""
    
    async def connect(self):
        """Handle WebSocket connection for geofences."""
        # Authenticate user
        token = self.scope['query_string'].decode().split('token=')[-1] if b'token=' in self.scope['query_string'] else None
        
        if token:
            try:
                UntypedToken(token)
                self.user = await self.get_user_from_token(token)
            except (InvalidToken, TokenError):
                await self.close(code=4001)
                return
        else:
            await self.close(code=4001)
            return
        
        if self.user and not isinstance(self.user, AnonymousUser):
            self.room_group_name = f"geofences_user_{self.user.id}"
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send user's geofences
            await self.send_user_geofences()
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
            
            if message_type == 'request_geofences':
                await self.send_user_geofences()
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
    
    async def geofence_event(self, event):
        """Send geofence event to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'geofence_event',
            'geofence_id': event['geofence_id'],
            'device_imei': event['device_imei'],
            'event_type': event['event_type'],
            'geofence_name': event['geofence_name'],
            'position': event.get('position'),
            'timestamp': event['timestamp']
        }, cls=DjangoJSONEncoder))
    
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
    def get_user_geofences(self):
        """Get user's geofences."""
        return list(Geofence.objects.filter(user=self.user))
    
    async def send_user_geofences(self):
        """Send user's geofences to client."""
        geofences = await self.get_user_geofences()
        geofence_data = []
        for geofence in geofences:
            geofence_data.append({
                'id': geofence.id,
                'name': geofence.name,
                'description': geofence.description,
                'geofence_type': geofence.geofence_type,
                'coordinates': geofence.coordinates.coords if geofence.coordinates else None,
                'radius': geofence.radius,
                'active': geofence.active,
                'created_at': geofence.created_at.isoformat()
            })
        
        await self.send(text_data=json.dumps({
            'type': 'geofences_list',
            'geofences': geofence_data
        }, cls=DjangoJSONEncoder))
    
    async def send_error(self, message):
        """Send error message."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        })) 