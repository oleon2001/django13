"""
Notification system for GPS tracking and geofence events.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)

# Safely import and initialize channel layer
def get_safe_channel_layer():
    """Get channel layer safely without causing connection errors."""
    try:
        from channels.layers import get_channel_layer
        return get_channel_layer()
    except Exception as e:
        logger.debug(f"Channel layer not available: {e}")
        return None


class GeofenceNotificationService:
    """Service for sending geofence-related notifications."""
    
    def __init__(self):
        """Initialize the notification service."""
        self.logger = logger
    
    def send_geofence_notification(self, event, geofence, device):
        """
        Send notifications for a geofence event.
        
        Args:
            event: GeoFenceEvent instance
            geofence: GeoFence instance
            device: GPSDevice instance
        """
        # Prepare notification data
        notification_data = self._prepare_notification_data(event, geofence, device)
        
        # Send email notifications
        if geofence.notify_emails:
            self._send_email_notifications(notification_data, geofence.notify_emails)
        
        # Send SMS notifications (if configured)
        if geofence.notify_sms:
            self._send_sms_notifications(notification_data, geofence.notify_sms)
        
        # Send push notifications to notify_owners
        if geofence.notify_owners.exists():
            self._send_push_notifications(notification_data, geofence.notify_owners.all())
        
        # Send real-time alerts if configured
        if ((event.event_type == 'ENTRY' and geofence.alert_on_entry) or 
            (event.event_type == 'EXIT' and geofence.alert_on_exit)):
            self._send_realtime_alert(notification_data, geofence.owner.id)
    
    def _prepare_notification_data(self, event, geofence, device) -> Dict[str, Any]:
        """
        Prepare notification data from event.
        
        Args:
            event: GeoFenceEvent instance
            geofence: GeoFence instance
            device: GPSDevice instance
            
        Returns:
            Dictionary with notification data
        """
        action_text = "entró en" if event.event_type == 'ENTRY' else "salió de"
        
        return {
            'event_type': event.event_type,
            'action_text': action_text,
            'device_name': device.name,
            'device_imei': device.imei,
            'geofence_name': geofence.name,
            'timestamp': event.timestamp,
            'timestamp_formatted': event.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
            'position': {
                'lat': device.position.y if device.position else 0,
                'lng': device.position.x if device.position else 0
            },
            'speed': device.speed,
            'course': device.course,
            'alert_level': 'warning' if event.event_type == 'EXIT' else 'info'
        }
    
    def _send_email_notifications(self, data: Dict[str, Any], email_addresses: List[str]):
        """
        Send email notifications.
        
        Args:
            data: Notification data
            email_addresses: List of email addresses
        """
        try:
            subject = f"Alerta de Geocerca: {data['device_name']} {data['action_text']} {data['geofence_name']}"
            
            # Prepare email context
            context = {
                'device_name': data['device_name'],
                'device_imei': data['device_imei'],
                'geofence_name': data['geofence_name'],
                'action_text': data['action_text'],
                'timestamp': data['timestamp_formatted'],
                'event_type': data['event_type'],
                'position': data['position'],
                'speed': data['speed'],
                'course': data['course']
            }
            
            # Render email template
            html_message = render_to_string('gps/emails/geofence_alert.html', context)
            plain_message = render_to_string('gps/emails/geofence_alert.txt', context)
            
            # Send email to all addresses
            for email in email_addresses:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False
                )
            
            self.logger.info(f"Sent geofence email notification to {len(email_addresses)} recipients")
                    
        except Exception as e:
            self.logger.error(f"Error sending email notifications: {e}")
    
    def _send_sms_notifications(self, data: Dict[str, Any], phone_numbers: List[str]):
        """
        Send SMS notifications.
        
        Args:
            data: Notification data
            phone_numbers: List of phone numbers
        """
        try:
            message = (
                f"SkyGuard Alert: {data['device_name']} {data['action_text']} "
                f"{data['geofence_name']} a las {data['timestamp_formatted']}"
            )
            
            # TODO: Implement SMS sending service (Twilio, AWS SNS, etc.)
            # For now, just log the message
            for phone in phone_numbers:
                self.logger.info(f"SMS to {phone}: {message}")
            
            self.logger.info(f"Would send SMS notifications to {len(phone_numbers)} recipients")
            
        except Exception as e:
            self.logger.error(f"Error sending SMS notifications: {e}")
    
    def _send_push_notifications(self, data: Dict[str, Any], users):
        """
        Send push notifications to users.
        
        Args:
            data: Notification data
            users: QuerySet of User objects
        """
        try:
            notification_message = {
                'type': 'geofence_notification',
                'title': f"Alerta de Geocerca",
                'message': f"{data['device_name']} {data['action_text']} {data['geofence_name']}",
                'data': data,
                'timestamp': data['timestamp'].isoformat()
            }
            
            # Send to each user via WebSocket (safely)
            channel_layer = get_safe_channel_layer()
            if channel_layer:
                try:
                    from asgiref.sync import async_to_sync
                    for user in users:
                        try:
                            async_to_sync(channel_layer.group_send)(
                                f"notifications_user_{user.id}",
                                notification_message
                            )
                        except Exception as e:
                            self.logger.warning(f"Error sending push notification to user {user.id}: {e}")
                except Exception as e:
                    self.logger.warning(f"Error with WebSocket push notifications: {e}")
            else:
                self.logger.debug("Channel layer not available, skipping push notifications")
            
            self.logger.info(f"Attempted push notifications to {users.count()} users")
            
        except Exception as e:
            self.logger.warning(f"Error sending push notifications: {e}")
    
    def _send_realtime_alert(self, data: Dict[str, Any], user_id: int):
        """
        Send real-time alert for immediate attention.
        
        Args:
            data: Notification data
            user_id: User ID to send alert to
        """
        try:
            alert_message = {
                'type': 'geofence_alert',
                'alert_level': data['alert_level'],
                'title': 'Alerta de Geocerca',
                'message': f"{data['device_name']} {data['action_text']} {data['geofence_name']}",
                'data': data,
                'timestamp': data['timestamp'].isoformat(),
                'auto_close': False,  # Require manual dismissal
                'sound': True  # Play alert sound
            }
            
            # Safely get channel layer for alerts
            channel_layer = get_safe_channel_layer()
            if channel_layer:
                try:
                    from asgiref.sync import async_to_sync
                    async_to_sync(channel_layer.group_send)(
                        f"alerts_user_{user_id}",
                        alert_message
                    )
                except Exception as e:
                    self.logger.warning(f"Error sending real-time alert to user {user_id}: {e}")
            else:
                self.logger.debug(f"Channel layer not available for real-time alerts to user {user_id}")
            
            self.logger.info(f"Attempted real-time alert to user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error sending real-time alert: {e}")


class NotificationService:
    """General notification service for the GPS system."""
    
    def __init__(self):
        """Initialize the notification service."""
        self.geofence_service = GeofenceNotificationService()
        self.logger = logger
    
    def send_device_alert(self, device, alert_type: str, message: str, user_id: int):
        """
        Send device-related alert.
        
        Args:
            device: GPSDevice instance
            alert_type: Type of alert
            message: Alert message
            user_id: User ID to send to
        """
        try:
            alert_data = {
                'type': 'device_alert',
                'alert_type': alert_type,
                'device_name': device.name,
                'device_imei': device.imei,
                'message': message,
                'timestamp': timezone.now().isoformat()
            }
            
            # Safely get channel layer for alerts
            channel_layer = get_safe_channel_layer()
            if channel_layer:
                try:
                    from asgiref.sync import async_to_sync
                    async_to_sync(channel_layer.group_send)(
                        f"alerts_user_{user_id}",
                        alert_data
                    )
                except Exception as e:
                    self.logger.warning(f"Error sending device alert to user {user_id}: {e}")
            else:
                self.logger.debug(f"Channel layer not available for device alerts to user {user_id}")
            
            self.logger.info(f"Attempted device alert {alert_type} for device {device.name}")
            
        except Exception as e:
            self.logger.error(f"Error sending device alert: {e}")
    
    def send_system_notification(self, message: str, notification_type: str = 'info', user_id: int = None):
        """
        Send system notification.
        
        Args:
            message: Notification message
            notification_type: Type of notification (info, warning, error)
            user_id: User ID to send to (None for broadcast)
        """
        try:
            notification_data = {
                'type': 'system_notification',
                'notification_type': notification_type,
                'message': message,
                'timestamp': timezone.now().isoformat()
            }
            
            # Safely get channel layer for notifications
            channel_layer = get_safe_channel_layer()
            if channel_layer:
                try:
                    from asgiref.sync import async_to_sync
                    if user_id:
                        # Send to specific user
                        async_to_sync(channel_layer.group_send)(
                            f"notifications_user_{user_id}",
                            notification_data
                        )
                    else:
                        # Broadcast to all users
                        async_to_sync(channel_layer.group_send)(
                            "system_notifications",
                            notification_data
                        )
                except Exception as e:
                    self.logger.warning(f"Error sending system notification to user {user_id}: {e}")
            else:
                self.logger.debug(f"Channel layer not available for system notifications to user {user_id}")
            
            self.logger.info(f"Attempted system notification: {message}")
            
        except Exception as e:
            self.logger.error(f"Error sending system notification: {e}")

    
# Global instances
notification_service = NotificationService()
geofence_notification_service = GeofenceNotificationService() 