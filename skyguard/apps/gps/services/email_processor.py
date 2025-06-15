"""
Email processor service for automatic GPS device registration.
Migrated from old backend IMAP functionality.
"""
import logging
from typing import List, Tuple, Set
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl

from imapclient import IMAPClient
from django.conf import settings
from django.utils import timezone

from skyguard.apps.gps.models import GPSDevice, GPSEvent


logger = logging.getLogger(__name__)


class EmailDeviceProcessor:
    """Process emails for automatic device registration."""
    
    def __init__(self, config=None):
        """Initialize email processor with configuration."""
        self.config = config or getattr(settings, 'GPS_EMAIL_CONFIG', {})
        
        # Default configuration
        self.imap_host = self.config.get('IMAP_HOST', 'imap.zoho.com')
        self.imap_username = self.config.get('IMAP_USERNAME', 'admin@ensambles.net')
        self.imap_password = self.config.get('IMAP_PASSWORD', 'l6moSa5mgCpg')
        self.imap_ssl = self.config.get('IMAP_SSL', True)
        self.sender_filter = self.config.get('SENDER_FILTER', 'Bonafont')
        
    def connect_imap(self):
        """Connect to IMAP server."""
        try:
            server = IMAPClient(
                self.imap_host, 
                use_uid=True, 
                ssl=self.imap_ssl
            )
            server.login(self.imap_username, self.imap_password)
            return server
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            raise
            
    def extract_imei_from_message(self, message_data: dict) -> List[str]:
        """Extract IMEI numbers from email message."""
        imeis = []
        
        try:
            # Check if message is from expected sender
            envelope = message_data.get(b'ENVELOPE')
            if not envelope or not envelope.from_:
                return imeis
                
            sender_name = envelope.from_[0].name if envelope.from_[0].name else ''
            if self.sender_filter not in sender_name:
                return imeis
                
            # Extract body text
            body_text = message_data.get(b'BODY[TEXT]', b'')
            if isinstance(body_text, bytes):
                body_text = body_text.decode('utf-8', errors='ignore')
                
            # Parse IMEI from message body
            # Expected format: word1 word2 imei word3
            words = body_text.split()
            if len(words) >= 4:
                # Extract IMEI-like numbers (typically 15 digits)
                potential_imei = f"{words[0]},{words[2]},{words[3]}"
                
                # Validate IMEI format
                try:
                    # Simple validation - check if it contains valid IMEI
                    parts = potential_imei.split(',')
                    if len(parts) == 3:
                        # Check if any part looks like an IMEI (15 digits)
                        for part in parts:
                            clean_part = ''.join(filter(str.isdigit, part))
                            if len(clean_part) == 15:
                                imeis.append(potential_imei)
                                break
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error extracting IMEI from message: {e}")
            
        return imeis
        
    def process_inbox_messages(self) -> Set[str]:
        """Process messages in inbox and extract device IMEIs."""
        imeis = set()
        
        try:
            server = self.connect_imap()
            
            # Select inbox
            select_info = server.select_folder('INBOX')
            logger.info(f"{select_info['EXISTS']} messages in INBOX")
            
            # Search for undeleted messages
            messages = server.search(['NOT', 'DELETED'])
            logger.info(f"{len(messages)} messages that aren't deleted")
            
            if not messages:
                return imeis
                
            # Fetch message data
            response = server.fetch(messages, ['ENVELOPE', 'BODY[TEXT]'])
            
            for msgid, data in response.items():
                extracted_imeis = self.extract_imei_from_message(data)
                imeis.update(extracted_imeis)
                
            server.logout()
            
        except Exception as e:
            logger.error(f"Error processing inbox messages: {e}")
            
        return imeis
        
    def process_trash_messages(self) -> Set[str]:
        """Process messages in trash to exclude already processed devices."""
        processed_imeis = set()
        
        try:
            server = self.connect_imap()
            
            # Select trash folder
            select_info = server.select_folder('Trash')
            logger.info(f"{select_info['EXISTS']} messages in TRASH")
            
            # Search for undeleted messages
            messages = server.search(['NOT', 'DELETED'])
            logger.info(f"{len(messages)} messages in trash that aren't deleted")
            
            if not messages:
                return processed_imeis
                
            # Fetch message data
            response = server.fetch(messages, ['ENVELOPE', 'BODY[TEXT]'])
            
            for msgid, data in response.items():
                extracted_imeis = self.extract_imei_from_message(data)
                processed_imeis.update(extracted_imeis)
                
            server.logout()
            
        except Exception as e:
            logger.error(f"Error processing trash messages: {e}")
            
        return processed_imeis
        
    def create_device_from_imei(self, imei_data: str) -> bool:
        """Create GPS device from IMEI data."""
        try:
            # Parse IMEI data (format: "word1,word2,imei")
            parts = imei_data.split(',')
            if len(parts) != 3:
                return False
                
            # Extract IMEI from the parts
            imei = None
            for part in parts:
                clean_part = ''.join(filter(str.isdigit, part))
                if len(clean_part) == 15:
                    imei = int(clean_part)
                    break
                    
            if not imei:
                logger.warning(f"No valid IMEI found in data: {imei_data}")
                return False
                
            # Check if device already exists
            if GPSDevice.objects.filter(imei=imei).exists():
                logger.info(f"Device with IMEI {imei} already exists")
                return False
                
            # Create new device
            device = GPSDevice.objects.create(
                imei=imei,
                name=f"AUTO_{imei:015d}",
                device_type="GPS_TRACKER",
                protocol="auto_detected",
                is_active=True,
                description=f"Auto-registered from email: {imei_data}"
            )
            
            # Create registration event
            GPSEvent.objects.create(
                device=device,
                event_type="REGISTRATION",
                timestamp=timezone.now(),
                data=f"Auto-registered from email: {imei_data}"
            )
            
            logger.info(f"Created device: {device.name} (IMEI: {imei})")
            return True
            
        except Exception as e:
            logger.error(f"Error creating device from IMEI {imei_data}: {e}")
            return False
            
    def process_new_devices(self) -> Tuple[int, List[str]]:
        """Process new device registrations from email."""
        try:
            logger.info("Starting email device processing...")
            
            # Get IMEIs from inbox
            inbox_imeis = self.process_inbox_messages()
            logger.info(f"Found {len(inbox_imeis)} potential devices in inbox")
            
            # Get already processed IMEIs from trash
            processed_imeis = self.process_trash_messages()
            logger.info(f"Found {len(processed_imeis)} already processed in trash")
            
            # Find new devices (in inbox but not in trash)
            new_imeis = inbox_imeis - processed_imeis
            logger.info(f"Found {len(new_imeis)} new devices to process")
            
            # Create devices
            created_devices = []
            for imei_data in new_imeis:
                if self.create_device_from_imei(imei_data):
                    created_devices.append(imei_data)
                    
            logger.info(f"Successfully created {len(created_devices)} new devices")
            return len(created_devices), created_devices
            
        except Exception as e:
            logger.error(f"Error processing new devices: {e}")
            return 0, []
            
    def send_notification_email(self, created_devices: List[str]):
        """Send notification email about newly created devices."""
        try:
            if not created_devices:
                return
                
            # Email configuration
            smtp_host = self.config.get('SMTP_HOST', 'smtp.zoho.com')
            smtp_port = self.config.get('SMTP_PORT', 587)
            smtp_username = self.config.get('SMTP_USERNAME', self.imap_username)
            smtp_password = self.config.get('SMTP_PASSWORD', self.imap_password)
            notification_email = self.config.get('NOTIFICATION_EMAIL', 'admin@ensambles.net')
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = notification_email
            msg['Subject'] = f"SkyGuard: {len(created_devices)} nuevos dispositivos registrados"
            
            body = "Se han registrado automáticamente los siguientes dispositivos GPS:\n\n"
            for device in created_devices:
                body += f"- {device}\n"
                
            body += f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            body += "\n\nSkyGuard GPS Tracking System"
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls(context=context)
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                
            logger.info(f"Notification email sent for {len(created_devices)} devices")
            
        except Exception as e:
            logger.error(f"Error sending notification email: {e}")


def process_device_emails():
    """Main function to process device registration emails."""
    processor = EmailDeviceProcessor()
    count, devices = processor.process_new_devices()
    
    if count > 0:
        processor.send_notification_email(devices)
        logger.info(f"Processing complete: {count} devices created")
    else:
        logger.info("No new devices to process")
        
    return count, devices


if __name__ == "__main__":
    import os
    import django
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
    django.setup()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Process emails
    try:
        count, devices = process_device_emails()
        print(f"Processed {count} new devices")
        for device in devices:
            print(f"  - {device}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc() 