"""
GPS models package.
"""
# Base models
from .base import BaseDevice, BaseLocation, BaseEvent, BaseGeoFence

# Core device models
from .device import (
    GPSDevice, SimCard, DeviceHarness, ServerSMS, DeviceStats,
    GPSLocation, GPSEvent, IOEvent, GSMEvent, ResetEvent,
    GeoFence, GeoFenceEvent, AccelerationLog, Overlay, AddressCache
)

# Location and event models
from .location import Location
from .event import NetworkEvent
from .session import DeviceSession

# Sensor models
from .sensors import (
    PressureSensorCalibration, PressureWeightLog, AlarmLog, Tracking
)

# Driver and ticket models
from .drivers import (
    Driver, TicketLog, TicketDetail, TimeSheetCapture, CardTransaction
)

# Vehicle models
from .vehicles import Vehicle

# Asset management models
from .assets import (
    CarPark, CarLane, CarSlot, GridlessCar, DemoCar
)

# Protocol models
from .protocols import (
    GPRSSession, GPRSPacket, GPRSRecord, UDPSession, ProtocolLog
)

__all__ = [
    # Base models
    'BaseDevice', 'BaseLocation', 'BaseEvent', 'BaseGeoFence',
    
    # Core device models
    'GPSDevice', 'SimCard', 'DeviceHarness', 'ServerSMS', 'DeviceStats',
    'GPSLocation', 'GPSEvent', 'IOEvent', 'GSMEvent', 'ResetEvent',
    'GeoFence', 'GeoFenceEvent', 'AccelerationLog', 'Overlay', 'AddressCache',
    
    # Location and event models
    'Location', 'NetworkEvent', 'DeviceSession',
    
    # Sensor models
    'PressureSensorCalibration', 'PressureWeightLog', 'AlarmLog', 'Tracking',
    
    # Driver and ticket models
    'Driver', 'TicketLog', 'TicketDetail', 'TimeSheetCapture', 'CardTransaction',
    
    # Vehicle models
    'Vehicle',
    
    # Asset management models
    'CarPark', 'CarLane', 'CarSlot', 'GridlessCar', 'DemoCar',
    
    # Protocol models
    'GPRSSession', 'GPRSPacket', 'GPRSRecord', 'UDPSession', 'ProtocolLog',
] 