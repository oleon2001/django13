"""
GPS protocol handler factory.
"""
from typing import Dict, Type

from skyguard.apps.gps.protocols.base import BaseProtocol
from skyguard.apps.gps.protocols.concox import ConcoxProtocol
from skyguard.apps.gps.protocols.meiligao import MeiligaoProtocol
from skyguard.apps.gps.protocols.catm1 import CatM1Protocol
from skyguard.apps.gps.protocols.cyacd import CYACDProtocol
from skyguard.apps.gps.protocols.bluetooth import BluetoothProtocol


class GPSProtocolHandler:
    """Factory class for GPS protocol handlers."""
    
    def __init__(self):
        """Initialize protocol handlers mapping."""
        self._handlers: Dict[str, Type[BaseProtocol]] = {
            'concox': ConcoxProtocol,
            'meiligao': MeiligaoProtocol,
            'catm1': CatM1Protocol,
            'cyacd': CYACDProtocol,
            'bluetooth': BluetoothProtocol,
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