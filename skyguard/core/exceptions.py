"""
Custom exceptions for the application.
"""

class SkyGuardError(Exception):
    """Base exception for SkyGuard application."""
    pass


class DeviceError(SkyGuardError):
    """Base exception for device-related errors."""
    pass


class DeviceNotFoundError(DeviceError):
    """Raised when a device is not found."""
    pass


class InvalidDeviceDataError(DeviceError):
    """Raised when device data is invalid."""
    pass


class ProtocolError(SkyGuardError):
    """Base exception for protocol-related errors."""
    pass


class UnsupportedProtocolError(ProtocolError):
    """Raised when a protocol is not supported."""
    pass


class InvalidPacketError(ProtocolError):
    """Raised when a packet is invalid."""
    pass


class LocationError(SkyGuardError):
    """Base exception for location-related errors."""
    pass


class InvalidLocationDataError(LocationError):
    """Raised when location data is invalid."""
    pass


class EventError(SkyGuardError):
    """Base exception for event-related errors."""
    pass


class InvalidEventDataError(EventError):
    """Raised when event data is invalid."""
    pass 