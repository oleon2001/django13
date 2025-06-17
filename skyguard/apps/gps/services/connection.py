"""
Connection service for GPS devices.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Max, Min

from ..models import GPSDevice, NetworkEvent, DeviceSession
from ..repositories import GPSDeviceRepository


class DeviceConnectionService:
    """Service for managing device connections."""

    def __init__(self, repository: GPSDeviceRepository):
        """Initialize the service."""
        self.repository = repository

    def register_connection(self, device: GPSDevice, ip_address: str, port: int, protocol: str) -> DeviceSession:
        """Register a new device connection."""
        # Crear nueva sesión
        session = DeviceSession.objects.create(
            device=device,
            start_time=timezone.now(),
            ip_address=ip_address,
            port=port,
            protocol=protocol,
            session_id=f"{device.imei}_{timezone.now().timestamp()}"
        )

        # Registrar evento de conexión
        NetworkEvent.objects.create(
            device=device,
            event_type='CONNECT',
            timestamp=timezone.now(),
            ip_address=ip_address,
            port=port,
            protocol=protocol,
            session_id=session.session_id
        )

        # Actualizar estado del dispositivo
        device.update_connection_status('ONLINE', ip_address, port)
        device.update_heartbeat()

        return session

    def register_disconnection(self, device: GPSDevice, session_id: str, reason: str = None) -> None:
        """Register a device disconnection."""
        try:
            session = DeviceSession.objects.get(session_id=session_id, is_active=True)
            session.end_session()

            # Registrar evento de desconexión
            NetworkEvent.objects.create(
                device=device,
                event_type='DISCONNECT',
                timestamp=timezone.now(),
                ip_address=session.ip_address,
                port=session.port,
                protocol=session.protocol,
                session_id=session_id,
                duration=session.duration,
                error_message=reason
            )

            # Actualizar estado del dispositivo
            device.update_connection_status('OFFLINE')
        except DeviceSession.DoesNotExist:
            pass

    def register_error(self, device: GPSDevice, error_message: str, session_id: str = None) -> None:
        """Register a device error."""
        NetworkEvent.objects.create(
            device=device,
            type='OTHER',
            timestamp=timezone.now(),
            data={
                'error_message': error_message,
                'session_id': session_id,
                'ip_address': getattr(device, 'current_ip', None),
                'port': getattr(device, 'current_port', None),
                'protocol': getattr(device, 'protocol', None),
            }
        )
        device.record_error(error_message)

    def get_connection_history(self, device: GPSDevice, start_time: Optional[datetime] = None, 
                             end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get device connection history."""
        query = NetworkEvent.objects.filter(device=device)
        if start_time:
            query = query.filter(timestamp__gte=start_time)
        if end_time:
            query = query.filter(timestamp__lte=end_time)

        events = query.order_by('-timestamp')
        return [{
            'event_type': event.event_type,
            'timestamp': event.timestamp,
            'ip_address': event.ip_address,
            'port': event.port,
            'protocol': event.protocol,
            'session_id': event.session_id,
            'duration': event.duration,
            'error_message': event.error_message
        } for event in events]

    def get_connection_stats(self, device: GPSDevice) -> Dict[str, Any]:
        """Get device connection statistics."""
        # Obtener eventos de los últimos 30 días
        thirty_days_ago = timezone.now() - timedelta(days=30)
        events = NetworkEvent.objects.filter(
            device=device,
            timestamp__gte=thirty_days_ago
        )

        # Calcular estadísticas
        total_connections = events.filter(event_type='CONNECT').count()
        total_disconnections = events.filter(event_type='DISCONNECT').count()
        total_errors = events.filter(event_type='ERROR').count()

        # Calcular tiempo promedio de conexión
        sessions = DeviceSession.objects.filter(
            device=device,
            start_time__gte=thirty_days_ago
        )
        avg_duration = sessions.aggregate(avg_duration=Avg('end_time' - 'start_time'))['avg_duration']

        return {
            'total_connections': total_connections,
            'total_disconnections': total_disconnections,
            'total_errors': total_errors,
            'current_status': device.connection_status,
            'last_connection': device.last_connection,
            'first_connection': device.first_connection,
            'average_session_duration': avg_duration,
            'error_count': device.error_count,
            'connection_quality': device.connection_quality
        }

    def get_active_sessions(self) -> List[DeviceSession]:
        """Get all active device sessions."""
        return DeviceSession.objects.filter(is_active=True).select_related('device')

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up old sessions."""
        cutoff_date = timezone.now() - timedelta(days=days)
        old_sessions = DeviceSession.objects.filter(
            end_time__lt=cutoff_date,
            is_active=False
        )
        count = old_sessions.count()
        old_sessions.delete()
        return count 