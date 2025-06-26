"""
Enhanced Security Module for GPS Command Processing
Provides cryptographic command signing, validation, and audit logging.
"""
import hashlib
import hmac
import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import secrets

from .models import GPSDevice, GPSEvent

logger = logging.getLogger(__name__)


class CommandSecurityError(Exception):
    """Base exception for command security errors."""
    pass


class InvalidCommandSignature(CommandSecurityError):
    """Raised when command signature validation fails."""
    pass


class CommandExpiredError(CommandSecurityError):
    """Raised when command has expired."""
    pass


class UnauthorizedCommandError(CommandSecurityError):
    """Raised when user is not authorized for command."""
    pass


class GPSCommandSecurity:
    """Enhanced security for GPS command processing."""
    
    # Command risk levels
    RISK_LEVELS = {
        'LOW': ['ping', 'get_status', 'get_position', 'get_version'],
        'MEDIUM': ['set_interval', 'set_apn', 'restart_gps'],
        'HIGH': ['cut_oil', 'cut_power', 'factory_reset', 'remote_shutdown'],
        'CRITICAL': ['emergency_stop', 'disable_engine', 'format_device']
    }
    
    # Command timeout settings (seconds)
    COMMAND_TIMEOUTS = {
        'LOW': 300,      # 5 minutes
        'MEDIUM': 180,   # 3 minutes  
        'HIGH': 60,      # 1 minute
        'CRITICAL': 30   # 30 seconds
    }
    
    def __init__(self):
        """Initialize security module."""
        self.secret_key = self._get_secret_key()
        self.fernet = self._get_fernet_cipher()
        
    def _get_secret_key(self) -> str:
        """Get or generate secret key for command signing."""
        secret = getattr(settings, 'GPS_COMMAND_SECRET_KEY', None)
        if not secret:
            # Generate a new secret if not configured
            secret = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            logger.warning("GPS_COMMAND_SECRET_KEY not configured, using generated key")
        return secret
    
    def _get_fernet_cipher(self) -> Fernet:
        """Get Fernet cipher for encryption."""
        # Use a key derivation function for better security
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'gps_command_salt',  # In production, use a random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return Fernet(key)
    
    def get_command_risk_level(self, command: str) -> str:
        """Determine risk level of command."""
        command_lower = command.lower()
        
        for risk_level, commands in self.RISK_LEVELS.items():
            if any(cmd in command_lower for cmd in commands):
                return risk_level
        
        # Default to HIGH for unknown commands
        return 'HIGH'
    
    def sign_command(self, command: str, device_imei: str, user_id: int, 
                    additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sign a GPS command with enhanced security."""
        timestamp = int(time.time())
        risk_level = self.get_command_risk_level(command)
        
        # Create command payload
        payload = {
            'command': command,
            'device_imei': str(device_imei),
            'user_id': user_id,
            'timestamp': timestamp,
            'risk_level': risk_level,
            'nonce': secrets.token_hex(16),
            'expires_at': timestamp + self.COMMAND_TIMEOUTS[risk_level]
        }
        
        if additional_data:
            payload['additional_data'] = additional_data
        
        # Create signature
        signature = self._create_signature(payload)
        
        # Encrypt sensitive commands
        if risk_level in ['HIGH', 'CRITICAL']:
            encrypted_command = self.fernet.encrypt(command.encode())
            payload['encrypted_command'] = base64.urlsafe_b64encode(encrypted_command).decode()
            # Remove plain command for security
            del payload['command']
        
        return {
            'payload': payload,
            'signature': signature,
            'security_level': risk_level
        }
    
    def verify_command(self, signed_command: Dict[str, Any], device: GPSDevice, 
                      user: User) -> Dict[str, Any]:
        """Verify and validate a signed GPS command."""
        payload = signed_command.get('payload', {})
        signature = signed_command.get('signature', '')
        
        # Verify signature
        if not self._verify_signature(payload, signature):
            raise InvalidCommandSignature("Command signature validation failed")
        
        # Check expiration
        current_time = int(time.time())
        if current_time > payload.get('expires_at', 0):
            raise CommandExpiredError("Command has expired")
        
        # Verify user authorization
        if payload.get('user_id') != user.id:
            raise UnauthorizedCommandError("User not authorized for this command")
        
        # Verify device ownership/access
        if not self._verify_device_access(device, user):
            raise UnauthorizedCommandError("User does not have access to this device")
        
        # Decrypt command if encrypted
        command = payload.get('command')
        if not command and 'encrypted_command' in payload:
            encrypted_data = base64.urlsafe_b64decode(payload['encrypted_command'])
            command = self.fernet.decrypt(encrypted_data).decode()
        
        # Additional security checks for high-risk commands
        risk_level = payload.get('risk_level', 'HIGH')
        if risk_level in ['HIGH', 'CRITICAL']:
            self._perform_additional_security_checks(command, device, user, payload)
        
        # Log command execution attempt
        self._log_command_attempt(command, device, user, payload, success=True)
        
        return {
            'command': command,
            'device_imei': payload['device_imei'],
            'risk_level': risk_level,
            'additional_data': payload.get('additional_data')
        }
    
    def _create_signature(self, payload: Dict[str, Any]) -> str:
        """Create HMAC signature for command payload."""
        # Sort payload for consistent signing
        sorted_payload = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        signature = hmac.new(
            self.secret_key.encode(),
            sorted_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify HMAC signature."""
        try:
            expected_signature = self._create_signature(payload)
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def _verify_device_access(self, device: GPSDevice, user: User) -> bool:
        """Verify user has access to device."""
        # Check if user owns the device
        if hasattr(device, 'owner') and device.owner == user:
            return True
        
        # Check if user is staff/admin
        if user.is_staff or user.is_superuser:
            return True
        
        # Additional access control logic can be added here
        # (e.g., group-based permissions, organization access)
        
        return False
    
    def _perform_additional_security_checks(self, command: str, device: GPSDevice, 
                                          user: User, payload: Dict[str, Any]) -> None:
        """Perform additional security checks for high-risk commands."""
        # Rate limiting for critical commands
        if payload.get('risk_level') == 'CRITICAL':
            self._check_rate_limiting(user, device)
        
        # Require recent authentication for critical commands
        if payload.get('risk_level') == 'CRITICAL':
            self._require_recent_authentication(user)
        
        # Check device status
        if device.connection_status != 'ONLINE':
            raise CommandSecurityError("Device must be online for this command")
        
        # Log security check
        logger.info(f"Additional security checks passed for {command} on device {device.imei}")
    
    def _check_rate_limiting(self, user: User, device: GPSDevice) -> None:
        """Check rate limiting for critical commands."""
        cache_key = f"critical_commands_{user.id}_{device.imei}"
        command_count = cache.get(cache_key, 0)
        
        # Allow max 3 critical commands per hour per device per user
        if command_count >= 3:
            raise CommandSecurityError("Rate limit exceeded for critical commands")
        
        # Increment counter
        cache.set(cache_key, command_count + 1, 3600)  # 1 hour timeout
    
    def _require_recent_authentication(self, user: User) -> None:
        """Require recent authentication for critical commands."""
        # This would integrate with Django's session framework
        # For now, we'll implement a simple check
        last_login_key = f"last_critical_auth_{user.id}"
        last_auth = cache.get(last_login_key)
        
        if not last_auth:
            raise CommandSecurityError("Recent authentication required for critical commands")
        
        # Require authentication within last 10 minutes for critical commands
        if time.time() - last_auth > 600:
            raise CommandSecurityError("Authentication too old for critical commands")
    
    def update_authentication_timestamp(self, user: User) -> None:
        """Update authentication timestamp for critical command validation."""
        cache_key = f"last_critical_auth_{user.id}"
        cache.set(cache_key, time.time(), 1800)  # 30 minute timeout
    
    def _log_command_attempt(self, command: str, device: GPSDevice, user: User, 
                           payload: Dict[str, Any], success: bool) -> None:
        """Log command execution attempt for audit purposes."""
        try:
            # Create audit log entry
            GPSEvent.objects.create(
                device=device,
                type='COMMAND_AUDIT',
                timestamp=timezone.now(),
                source='security_module',
                text=f"Command '{command}' by user {user.username}",
                data={
                    'command': command,
                    'user_id': user.id,
                    'username': user.username,
                    'risk_level': payload.get('risk_level'),
                    'success': success,
                    'timestamp': payload.get('timestamp'),
                    'nonce': payload.get('nonce')
                }
            )
            
            # Also log to application logger
            log_message = f"GPS Command Audit: {command} on device {device.imei} by {user.username} - {'SUCCESS' if success else 'FAILED'}"
            if success:
                logger.info(log_message)
            else:
                logger.warning(log_message)
                
        except Exception as e:
            logger.error(f"Failed to log command attempt: {e}")


# Global instance
gps_security = GPSCommandSecurity()


def secure_gps_command(command: str, device_imei: str, user_id: int, 
                      additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to sign a GPS command."""
    return gps_security.sign_command(command, device_imei, user_id, additional_data)


def verify_gps_command(signed_command: Dict[str, Any], device: GPSDevice, 
                      user: User) -> Dict[str, Any]:
    """Convenience function to verify a GPS command."""
    return gps_security.verify_command(signed_command, device, user) 