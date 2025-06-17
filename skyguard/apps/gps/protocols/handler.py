"""
GPS protocol handler factory.
"""
from typing import Dict, Type

from skyguard.apps.gps.protocols.base import BaseProtocol
from skyguard.apps.gps.protocols.handlers import (
    ConcoxProtocolHandler,
    MeiligaoProtocolHandler,
    WialonProtocolHandler
)


class GPSProtocolHandler:
    """Factory class for GPS protocol handlers."""
    
    def __init__(self):
        """Initialize protocol handlers mapping."""
        self._handlers: Dict[str, Type[BaseProtocol]] = {
            'concox': ConcoxProtocolHandler,
            'meiligao': MeiligaoProtocolHandler,
            'wialon': WialonProtocolHandler,
        }
    
    def get_handler(self, protocol: str) -> BaseProtocol:
        """
        Get a protocol handler instance.
        
        Args:
            protocol: Protocol name
            
        Returns:
            Protocol handler instance
            
        Raises:
            ValueError: If protocol is not supported
        """
        handler_class = self._handlers.get(protocol.lower())
        if not handler_class:
            raise ValueError(f'Unsupported protocol: {protocol}')
        return handler_class() 