"""
Device command module for GPS devices.
"""
import socket
import struct
from enum import Enum
from typing import Optional, Dict, Any
from django.conf import settings
from skyguard.apps.gps.models import Device


class CommandType(Enum):
    """Enum for device command types."""
    LOGIN = 0x01
    PING = 0x02
    DEVICE_INFO = 0x03
    DATA = 0x04
    SESSION = 0x10
    LOGIN_RESPONSE = 0x11
    DEVICE_INFO_CMD = 0x20
    DATA_CMD = 0x21
    ACK = 0x22
    MOTOR_ON = 0x23
    MOTOR_OFF = 0x24
    RESET = 0x25


class DeviceCommand:
    """Base class for device commands."""
    
    def __init__(self, device: Device, command_type: CommandType, data: Optional[Dict[str, Any]] = None):
        """Initialize the command."""
        self.device = device
        self.command_type = command_type
        self.data = data or {}
        
    def encode(self) -> bytes:
        """Encode the command for transmission."""
        raise NotImplementedError("Subclasses must implement encode()")
        
    def send(self, host: str, port: int) -> None:
        """Send the command to the device."""
        data = self.encode()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (host, port))
        sock.close()


class BluetoothCommand(DeviceCommand):
    """Bluetooth-specific device commands."""
    
    def encode(self) -> bytes:
        """Encode the command for Bluetooth transmission."""
        if not hasattr(self.device, 'session'):
            raise ValueError("Device has no active session")
            
        session = self.device.session
        return struct.pack("<BLB", CommandType.SESSION.value, session.session, self.command_type.value)


class ConcoxCommand(DeviceCommand):
    """Concox-specific device commands."""
    
    def encode(self) -> bytes:
        """Encode the command for Concox transmission."""
        # Implement Concox-specific command encoding
        pass


class MeiligaoCommand(DeviceCommand):
    """Meiligao-specific device commands."""
    
    def encode(self) -> bytes:
        """Encode the command for Meiligao transmission."""
        # Implement Meiligao-specific command encoding
        pass


def send_command(device_name: str, command_type: CommandType, protocol: str = 'bluetooth') -> None:
    """Send a command to a device.
    
    Args:
        device_name: Name of the device
        command_type: Type of command to send
        protocol: Protocol to use (bluetooth, concox, meiligao)
    """
    try:
        device = Device.objects.get(name=device_name)
    except Device.DoesNotExist:
        raise ValueError(f"Device {device_name} not found")
        
    command_classes = {
        'bluetooth': BluetoothCommand,
        'concox': ConcoxCommand,
        'meiligao': MeiligaoCommand
    }
    
    if protocol not in command_classes:
        raise ValueError(f"Unsupported protocol: {protocol}")
        
    command_class = command_classes[protocol]
    command = command_class(device, command_type)
    
    if not hasattr(device, 'session'):
        raise ValueError(f"Device {device_name} has no active session")
        
    command.send(device.session.host, device.session.port) 