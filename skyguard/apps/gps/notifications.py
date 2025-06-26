"""
Enterprise Push Notifications System for GPS Events
Provides multi-channel notifications (email, SMS, push, WebSocket) with intelligent routing.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
from celery import shared_task

from .models import GPSDevice, GPSEvent

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class NotificationCategory(Enum):
    """Notification categories."""
    ALARM = "alarm"
    MAINTENANCE = "maintenance"
    SECURITY = "security"
    ANALYTICS = "analytics"
    SYSTEM = "system"


@dataclass
class NotificationRecipient:
    """Notification recipient information."""
    user_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    push_token: Optional[str] = None
    preferred_channels: List[str] = None
    timezone: str = "UTC"


@dataclass
class NotificationMessage:
    """Notification message structure."""
    id: str
    title: str
    message: str
    category: str
    priority: str
    timestamp: datetime
    device_imei: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    expiry: Optional[datetime] = None


class NotificationPreferences:
    """User notification preferences."""
    
    def __init__(self, user: User):
        self.user = user
        self._load_preferences()
    
    def _load_preferences(self):
        """Load user preferences from cache or database."""
        cache_key = f"notification_prefs_{self.user.id}"
        self.preferences = cache.get(cache_key, self._get_default_preferences())
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default notification preferences."""
        return {
            'channels': {
                'email': True,
                'websocket': True,
                'push': False,
                'sms': False
            },
            'categories': {
                'alarm': ['email', 'websocket', 'push'],
                'security': ['email', 'websocket'],
                'maintenance': ['email'],
                'analytics': ['websocket'],
                'system': ['email']
            },
            'priority_rules': {
                'emergency': ['email', 'sms', 'push', 'websocket'],
                'critical': ['email', 'push', 'websocket'],
                'high': ['email', 'websocket'],
                'medium': ['websocket'],
                'low': ['websocket']
            },
            'quiet_hours': {
                'enabled': False,
                'start': '22:00',
                'end': '06:00'
            },
            'rate_limiting': {
                'max_per_hour': 10,
                'max_per_day': 50
            }
        }
    
    def get_channels_for_notification(self, category: str, priority: str) -> List[str]:
        """Get notification channels based on category and priority."""
        channels = []
        
        # Priority-based channels
        if priority in self.preferences['priority_rules']:
            channels.extend(self.preferences['priority_rules'][priority])
        
        # Category-based channels
        if category in self.preferences['categories']:
            channels.extend(self.preferences['categories'][category])
        
        # Filter by enabled channels
        enabled_channels = [
            ch for ch, enabled in self.preferences['channels'].items() 
            if enabled
        ]
        
        return list(set(channels) & set(enabled_channels))
    
    def is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        if not self.preferences['quiet_hours']['enabled']:
            return False
        
        # Implementation would check current time against quiet hours
        # For now, return False
        return False
    
    def check_rate_limit(self, channel: str) -> bool:
        """Check if user has exceeded rate limits."""
        cache_key = f"notification_rate_{self.user.id}_{channel}"
        current_count = cache.get(cache_key, 0)
        
        # Simple hourly rate limiting
        max_per_hour = self.preferences['rate_limiting']['max_per_hour']
        
        if current_count >= max_per_hour:
            return False
        
        # Increment counter
        cache.set(cache_key, current_count + 1, 3600)  # 1 hour
        return True


class NotificationRouter:
    """Intelligent notification routing system."""
    
    def __init__(self):
        """Initialize notification router."""
        self.handlers = {
            NotificationChannel.EMAIL: EmailNotificationHandler(),
            NotificationChannel.SMS: SMSNotificationHandler(),
            NotificationChannel.PUSH: PushNotificationHandler(),
            NotificationChannel.WEBSOCKET: WebSocketNotificationHandler(),
            NotificationChannel.WEBHOOK: WebhookNotificationHandler()
        }
    
    def send_notification(self, message: NotificationMessage, 
                         recipients: List[NotificationRecipient],
                         channels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send notification through specified channels."""
        results = {}
        
        for recipient in recipients:
            recipient_results = {}
            prefs = NotificationPreferences(User.objects.get(id=recipient.user_id))
            
            # Determine channels to use
            if channels:
                target_channels = channels
            else:
                target_channels = prefs.get_channels_for_notification(
                    message.category, message.priority
                )
            
            # Check quiet hours for non-critical notifications
            if (message.priority not in ['critical', 'emergency'] and 
                prefs.is_quiet_hours()):
                target_channels = ['websocket']  # Only WebSocket during quiet hours
            
            # Send through each channel
            for channel_name in target_channels:
                if channel_name not in self.handlers:
                    continue
                
                # Check rate limiting
                if not prefs.check_rate_limit(channel_name):
                    recipient_results[channel_name] = {
                        'success': False,
                        'error': 'Rate limit exceeded'
                    }
                    continue
                
                # Send notification
                try:
                    channel = NotificationChannel(channel_name)
                    handler = self.handlers[channel]
                    result = handler.send(message, recipient)
                    recipient_results[channel_name] = result
                    
                except Exception as e:
                    logger.error(f"Error sending {channel_name} notification: {e}")
                    recipient_results[channel_name] = {
                        'success': False,
                        'error': str(e)
                    }
            
            results[recipient.user_id] = recipient_results
        
        return results


class BaseNotificationHandler:
    """Base class for notification handlers."""
    
    def send(self, message: NotificationMessage, 
             recipient: NotificationRecipient) -> Dict[str, Any]:
        """Send notification to recipient."""
        raise NotImplementedError()
    
    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate if recipient can receive this type of notification."""
        return True


class EmailNotificationHandler(BaseNotificationHandler):
    """Email notification handler."""
    
    def send(self, message: NotificationMessage, 
             recipient: NotificationRecipient) -> Dict[str, Any]:
        """Send email notification."""
        if not recipient.email:
            return {'success': False, 'error': 'No email address'}
        
        try:
            # Render email content
            context = {
                'recipient_name': recipient.name,
                'message': message,
                'action_url': message.action_url,
                'device_imei': message.device_imei,
                'position': message.position
            }
            
            html_content = render_to_string(
                'notifications/email_notification.html', 
                context
            )
            
            # Send email
            send_mail(
                subject=f"[{message.priority.upper()}] {message.title}",
                message=message.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                html_message=html_content,
                fail_silently=False
            )
            
            return {'success': True, 'message_id': message.id}
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return {'success': False, 'error': str(e)}


class SMSNotificationHandler(BaseNotificationHandler):
    """SMS notification handler."""
    
    def send(self, message: NotificationMessage, 
             recipient: NotificationRecipient) -> Dict[str, Any]:
        """Send SMS notification."""
        if not recipient.phone:
            return {'success': False, 'error': 'No phone number'}
        
        # This would integrate with SMS service (Twilio, AWS SNS, etc.)
        # For now, just log the SMS
        sms_text = f"{message.title}: {message.message}"
        logger.info(f"SMS to {recipient.phone}: {sms_text}")
        
        return {'success': True, 'message_id': message.id}


class PushNotificationHandler(BaseNotificationHandler):
    """Push notification handler."""
    
    def send(self, message: NotificationMessage, 
             recipient: NotificationRecipient) -> Dict[str, Any]:
        """Send push notification."""
        if not recipient.push_token:
            return {'success': False, 'error': 'No push token'}
        
        # This would integrate with FCM/APNS
        # For now, just log the push notification
        logger.info(f"Push notification to {recipient.push_token}: {message.title}")
        
        return {'success': True, 'message_id': message.id}


class WebSocketNotificationHandler(BaseNotificationHandler):
    """WebSocket notification handler."""
    
    def send(self, message: NotificationMessage, 
             recipient: NotificationRecipient) -> Dict[str, Any]:
        """Send WebSocket notification."""
        try:
            notification_data = {
                'type': 'notification',
                'notification': asdict(message),
                'timestamp': timezone.now().isoformat()
            }
            
            # Send to user's WebSocket room
            async_to_sync(channel_layer.group_send)(
                f"gps_user_{recipient.user_id}",
                {
                    'type': 'notification_message',
                    'data': notification_data
                }
            )
            
            return {'success': True, 'message_id': message.id}
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket notification: {e}")
            return {'success': False, 'error': str(e)}


class WebhookNotificationHandler(BaseNotificationHandler):
    """Webhook notification handler."""
    
    def send(self, message: NotificationMessage, 
             recipient: NotificationRecipient) -> Dict[str, Any]:
        """Send webhook notification."""
        # This would send HTTP POST to configured webhook URLs
        logger.info(f"Webhook notification: {message.title}")
        return {'success': True, 'message_id': message.id}


class GPSNotificationService:
    """Main GPS notification service."""
    
    def __init__(self):
        """Initialize notification service."""
        self.router = NotificationRouter()
    
    def send_device_alarm(self, device: GPSDevice, alarm_type: str, 
                         position: Optional[Dict[str, float]] = None,
                         additional_data: Optional[Dict[str, Any]] = None) -> None:
        """Send device alarm notification."""
        # Determine priority based on alarm type
        priority_map = {
            'SOS': NotificationPriority.EMERGENCY,
            'PANIC': NotificationPriority.EMERGENCY,
            'POWER_CUT': NotificationPriority.CRITICAL,
            'BATTERY_LOW': NotificationPriority.HIGH,
            'SPEED_VIOLATION': NotificationPriority.MEDIUM,
            'GEOFENCE_EXIT': NotificationPriority.HIGH,
            'GEOFENCE_ENTER': NotificationPriority.MEDIUM
        }
        
        priority = priority_map.get(alarm_type, NotificationPriority.MEDIUM)
        
        # Create notification message
        message = NotificationMessage(
            id=f"alarm_{device.imei}_{int(timezone.now().timestamp())}",
            title=f"Alarm: {alarm_type}",
            message=f"Device {device.name} ({device.imei}) triggered {alarm_type} alarm",
            category=NotificationCategory.ALARM.value,
            priority=priority.value,
            timestamp=timezone.now(),
            device_imei=str(device.imei),
            position=position,
            data=additional_data,
            action_url=f"/devices/{device.imei}/details"
        )
        
        # Get recipients (device owner and admins)
        recipients = self._get_device_recipients(device)
        
        # Send notification
        self.router.send_notification(message, recipients)
    
    def send_maintenance_alert(self, device: GPSDevice, 
                             maintenance_type: str,
                             predicted_date: Optional[datetime] = None) -> None:
        """Send maintenance alert notification."""
        message = NotificationMessage(
            id=f"maintenance_{device.imei}_{int(timezone.now().timestamp())}",
            title=f"Maintenance Required: {maintenance_type}",
            message=f"Device {device.name} requires {maintenance_type}",
            category=NotificationCategory.MAINTENANCE.value,
            priority=NotificationPriority.MEDIUM.value,
            timestamp=timezone.now(),
            device_imei=str(device.imei),
            data={'predicted_date': predicted_date.isoformat() if predicted_date else None},
            action_url=f"/devices/{device.imei}/maintenance"
        )
        
        recipients = self._get_device_recipients(device)
        self.router.send_notification(message, recipients)
    
    def send_security_alert(self, user: User, alert_type: str, 
                          details: Dict[str, Any]) -> None:
        """Send security alert notification."""
        message = NotificationMessage(
            id=f"security_{user.id}_{int(timezone.now().timestamp())}",
            title=f"Security Alert: {alert_type}",
            message=f"Security event detected for user {user.username}",
            category=NotificationCategory.SECURITY.value,
            priority=NotificationPriority.HIGH.value,
            timestamp=timezone.now(),
            data=details,
            action_url="/security/alerts"
        )
        
        recipients = [self._user_to_recipient(user)]
        self.router.send_notification(message, recipients)
    
    def send_analytics_report(self, user: User, report_type: str, 
                            data: Dict[str, Any]) -> None:
        """Send analytics report notification."""
        message = NotificationMessage(
            id=f"analytics_{user.id}_{int(timezone.now().timestamp())}",
            title=f"Analytics Report: {report_type}",
            message=f"Your {report_type} report is ready",
            category=NotificationCategory.ANALYTICS.value,
            priority=NotificationPriority.LOW.value,
            timestamp=timezone.now(),
            data=data,
            action_url="/analytics/reports"
        )
        
        recipients = [self._user_to_recipient(user)]
        self.router.send_notification(message, recipients, channels=['email'])
    
    def _get_device_recipients(self, device: GPSDevice) -> List[NotificationRecipient]:
        """Get notification recipients for a device."""
        recipients = []
        
        # Add device owner
        if hasattr(device, 'owner') and device.owner:
            recipients.append(self._user_to_recipient(device.owner))
        
        # Add admin users for critical devices
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            recipients.append(self._user_to_recipient(admin))
        
        return recipients
    
    def _user_to_recipient(self, user: User) -> NotificationRecipient:
        """Convert User to NotificationRecipient."""
        return NotificationRecipient(
            user_id=user.id,
            name=user.get_full_name() or user.username,
            email=user.email,
            phone=getattr(user, 'phone', None),
            push_token=getattr(user, 'push_token', None)
        )


# Global notification service instance
notification_service = GPSNotificationService()


# Celery tasks for async notification processing
@shared_task
def send_async_notification(message_data: Dict[str, Any], 
                           recipients_data: List[Dict[str, Any]],
                           channels: Optional[List[str]] = None):
    """Send notification asynchronously via Celery."""
    try:
        # Reconstruct objects
        message = NotificationMessage(**message_data)
        recipients = [NotificationRecipient(**r) for r in recipients_data]
        
        # Send notification
        router = NotificationRouter()
        results = router.send_notification(message, recipients, channels)
        
        logger.info(f"Async notification sent: {message.id}")
        return results
        
    except Exception as e:
        logger.error(f"Failed to send async notification: {e}")
        raise


@shared_task
def process_bulk_notifications(notifications_data: List[Dict[str, Any]]):
    """Process multiple notifications in bulk."""
    results = []
    
    for notification_data in notifications_data:
        try:
            result = send_async_notification.delay(**notification_data)
            results.append({'notification_id': notification_data['message_data']['id'], 'task_id': result.id})
        except Exception as e:
            logger.error(f"Failed to queue notification: {e}")
            results.append({'error': str(e)})
    
    return results 