"""
GPS server initialization.
"""
from typing import Dict, Type
import logging

from skyguard.core.interfaces import IDeviceServer
from skyguard.apps.gps.servers.wialon_server import WialonServer

logger = logging.getLogger(__name__)

# Map of protocol names to server classes
SERVER_CLASSES: Dict[str, Type[IDeviceServer]] = {
    'wialon': WialonServer
}

def get_server(protocol: str) -> IDeviceServer:
    """Get a server instance for the given protocol."""
    server_class = SERVER_CLASSES.get(protocol.lower())
    if not server_class:
        raise ValueError(f"Unsupported protocol: {protocol}")
    return server_class() 