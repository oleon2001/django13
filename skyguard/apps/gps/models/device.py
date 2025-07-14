"""
Device models for the GPS application.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils import timezone
import json
import pytz

from .base import BaseDevice, BaseLocation, BaseEvent, BaseGeoFence


def nowtz():
    """Get current time with timezone."""
    return timezone.now()


class GPSDevice(BaseDevice):
    """Model for GPS devices."""
    MODEL_CHOICES = (
        (0, 'Unknown'),
        (1, 'SGB4612'),
        (2, 'SGP4612'),
    )

    GSM_OPERATOR_CHOICES = (
        (0, 'Telcel'),
        (1, 'Movistar'),
        (2, 'IusaCell'),
    )

    ROUTE_CHOICES = (
        (92, "Ruta 4"),
        (112, "Ruta 6"),
        (114, "Ruta 12"),
        (115, "Ruta 31"),
        (90, "Ruta 82"),
        (88, "Ruta 118"),
        (215, "Ruta 140"),
        (89, "Ruta 202"),
        (116, "Ruta 207"),
        (96, "Ruta 400"),
        (97, "Ruta 408"),
    )

    CONNECTION_STATUS_CHOICES = (
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('SLEEPING', 'Sleeping'),
        ('ERROR', 'Error'),
    )

    PROTOCOL_CHOICES = (
        ('concox', 'Concox'),
        ('meiligao', 'Meiligao'),
        ('wialon', 'Wialon'),
    )

    serial = models.IntegerField(_('serial'), default=0)
    model = models.SmallIntegerField(_('model'), default=0, choices=MODEL_CHOICES)
    software_version = models.CharField(_('version'), max_length=4, default='----')
    inputs = models.IntegerField(_('inputs'), default=0)
    outputs = models.IntegerField(_('outputs'), default=0)
    alarm_mask = models.IntegerField(_('alarm mask'), default=0x0141)
    alarms = models.IntegerField(_('alarms'), default=0)
    firmware_file = models.CharField(_('firmware file'), max_length=16, blank=True)
    last_firmware_update = models.DateTimeField(_('last firmware update'), null=True, blank=True)
    comments = models.TextField(_('Comments'), null=True, blank=True)
    sim_card = models.OneToOneField('SimCard', on_delete=models.SET_NULL, null=True, blank=True, related_name='device')
    protocol = models.CharField(_('protocol'), max_length=20, choices=PROTOCOL_CHOICES, default='concox')

    # Migrated fields from old backend
    route = models.IntegerField(_('route'), null=True, blank=True, choices=ROUTE_CHOICES)
    economico = models.IntegerField(_('economic number'), null=True, blank=True)
    harness = models.ForeignKey('DeviceHarness', on_delete=models.PROTECT, null=True, blank=True)
    new_outputs = models.IntegerField(_('new outputs'), null=True, blank=True)
    new_input_flags = models.CharField(_('new inputs'), max_length=32, blank=True)

    # Nuevos campos para manejo de conexiones
    first_connection = models.DateTimeField(_('first connection'), null=True, blank=True)
    last_connection = models.DateTimeField(_('last connection'), null=True, blank=True)
    connection_status = models.CharField(_('connection status'), max_length=20, choices=CONNECTION_STATUS_CHOICES, default='OFFLINE')
    current_ip = models.GenericIPAddressField(_('current IP'), null=True, blank=True)
    current_port = models.IntegerField(_('current port'), null=True, blank=True)
    total_connections = models.IntegerField(_('total connections'), default=0)
    firmware_history = models.JSONField(_('firmware history'), default=list)
    last_error = models.TextField(_('last error'), null=True, blank=True)
    error_count = models.IntegerField(_('error count'), default=0)
    connection_quality = models.FloatField(_('connection quality'), default=0.0)
    last_heartbeat = models.DateTimeField(_('last heartbeat'), null=True, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('GPS device')
        verbose_name_plural = _('GPS devices')
        unique_together = [('name', 'owner')]
        indexes = [
            models.Index(fields=['connection_status']),
            models.Index(fields=['last_connection']),
            models.Index(fields=['route']),
            models.Index(fields=['economico']),
        ]

    def __str__(self):
        return f"{self.imei} - {self.name}"

    def update_connection_status(self, status, ip_address=None, port=None):
        """Update device connection status."""
        self.connection_status = status
        if ip_address:
            self.current_ip = ip_address
        if port:
            self.current_port = port
        self.last_connection = timezone.now()
        self.save()

    def record_error(self, error_message):
        """Record an error for the device."""
        self.last_error = error_message
        self.error_count += 1
        self.connection_status = 'ERROR'
        self.save()

    def update_firmware_history(self, version):
        """Update firmware history."""
        if not self.firmware_history:
            self.firmware_history = []
        self.firmware_history.append({
            'version': version,
            'timestamp': timezone.now().isoformat(),
        })
        self.software_version = version
        self.last_firmware_update = timezone.now()
        self.save()

    def update_heartbeat(self):
        """Update device heartbeat."""
        self.last_heartbeat = timezone.now()
        self.save()

    @property
    def is_online(self):
        """Check if device is online."""
        return self.connection_status == 'ONLINE'

    @property
    def connection_duration(self):
        """Get current connection duration."""
        if self.is_online and self.last_connection:
            return timezone.now() - self.last_connection
        return None


class SimCard(models.Model):
    """Model for SIM cards."""
    iccid = models.BigIntegerField(primary_key=True)
    imsi = models.BigIntegerField(null=True)
    provider = models.SmallIntegerField(default=0, choices=GPSDevice.GSM_OPERATOR_CHOICES)
    phone = models.CharField(max_length=16)

    objects = models.Manager()

    def __str__(self):
        return f"{self.phone} ({self.iccid})"


class DeviceHarness(models.Model):
    """Model for device harness configuration (migrated from old SGHarness)."""
    name = models.CharField(_('name'), max_length=32, unique=True)
    
    # Input configurations
    in00 = models.CharField(_('input 0'), max_length=32, default="PANIC")
    in01 = models.CharField(_('input 1'), max_length=32, default="IGNITION")
    in02 = models.CharField(_('input 2'), max_length=32, blank=True)
    in03 = models.CharField(_('input 3'), max_length=32, blank=True)
    in04 = models.CharField(_('input 4'), max_length=32, blank=True)
    in05 = models.CharField(_('input 5'), max_length=32, blank=True)
    in06 = models.CharField(_('input 6'), max_length=32, default="BAT_DOK")
    in07 = models.CharField(_('input 7'), max_length=32, default="BAT_CHG")
    in08 = models.CharField(_('input 8'), max_length=32, default="BAT_FLT")
    in09 = models.CharField(_('input 9'), max_length=32, blank=True)
    in10 = models.CharField(_('input 10'), max_length=32, blank=True)
    in11 = models.CharField(_('input 11'), max_length=32, blank=True)
    in12 = models.CharField(_('input 12'), max_length=32, blank=True)
    in13 = models.CharField(_('input 13'), max_length=32, blank=True)
    in14 = models.CharField(_('input 14'), max_length=32, blank=True)
    in15 = models.CharField(_('input 15'), max_length=32, blank=True)
    
    # Output configurations
    out00 = models.CharField(_('output 0'), max_length=32, default="MOTOR")
    out01 = models.CharField(_('output 1'), max_length=32, blank=True)
    out02 = models.CharField(_('output 2'), max_length=32, blank=True)
    out03 = models.CharField(_('output 3'), max_length=32, blank=True)
    out04 = models.CharField(_('output 4'), max_length=32, blank=True)
    out05 = models.CharField(_('output 5'), max_length=32, blank=True)
    out06 = models.CharField(_('output 6'), max_length=32, blank=True)
    out07 = models.CharField(_('output 7'), max_length=32, blank=True)
    out08 = models.CharField(_('output 8'), max_length=32, blank=True)
    out09 = models.CharField(_('output 9'), max_length=32, blank=True)
    out10 = models.CharField(_('output 10'), max_length=32, blank=True)
    out11 = models.CharField(_('output 11'), max_length=32, blank=True)
    out12 = models.CharField(_('output 12'), max_length=32, blank=True)
    out13 = models.CharField(_('output 13'), max_length=32, blank=True)
    out14 = models.CharField(_('output 14'), max_length=32, blank=True)
    out15 = models.CharField(_('output 15'), max_length=32, blank=True)
    
    input_config = models.CharField(_('input configuration'), max_length=32, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('device harness')
        verbose_name_plural = _('device harnesses')

    def __str__(self):
        return self.name

    def get_input_cable_name(self, bit):
        """Get input cable name by bit number."""
        input_map = {
            0: self.in00 or 'IN00', 1: self.in01 or 'IN01', 2: self.in02 or 'IN02',
            3: self.in03 or 'IN03', 4: self.in04 or 'IN04', 5: self.in05 or 'IN05',
            6: self.in06 or 'IN06', 7: self.in07 or 'IN07', 8: self.in08 or 'IN08',
            9: self.in09 or 'IN09', 10: self.in10 or 'IN10', 11: self.in11 or 'IN11',
            12: self.in12 or 'IN12', 13: self.in13 or 'IN13', 14: self.in14 or 'IN14',
            15: self.in15 or 'IN15'
        }
        return input_map.get(bit, '')

    def get_output_cable_name(self, bit):
        """Get output cable name by bit number."""
        output_map = {
            0: self.out00 or 'OUT00', 1: self.out01 or 'OUT01', 2: self.out02 or 'OUT02',
            3: self.out03 or 'OUT03', 4: self.out04 or 'OUT04', 5: self.out05 or 'OUT05',
            6: self.out06 or 'OUT06', 7: self.out07 or 'OUT07', 8: self.out08 or 'OUT08',
            9: self.out09 or 'OUT09', 10: self.out10 or 'OUT10', 11: self.out11 or 'OUT11',
            12: self.out12 or 'OUT12', 13: self.out13 or 'OUT13', 14: self.out14 or 'OUT14',
            15: self.out15 or 'OUT15'
        }
        return output_map.get(bit, '')


class ServerSMS(models.Model):
    """Model for server SMS commands (migrated from old backend)."""
    SMS_COMMANDS = (
        (1, "Send SMS"),
        (2, "Send Position"),
        (3, "Execute Command"),
    )

    SMS_DIRECTION = (
        (0, "From Server"),
        (1, "From Device")
    )

    SMS_STATUS = (
        (0, "Pending"),
        (1, "Success"),
        (2, "Failed")
    )

    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='sms_commands')
    command = models.SmallIntegerField(_('command'), default=0, choices=SMS_COMMANDS)
    direction = models.SmallIntegerField(_('direction'), default=0, choices=SMS_DIRECTION)
    status = models.SmallIntegerField(_('status'), default=0, choices=SMS_STATUS)
    message = models.CharField(_('message'), max_length=160, default="New Message")
    sent = models.DateTimeField(_('sent'), null=True, blank=True)
    issued = models.DateTimeField(_('issued'), default=nowtz)

    objects = models.Manager()

    class Meta:
        verbose_name = _('server SMS')
        verbose_name_plural = _('server SMS commands')
        ordering = ['-issued']

    def __str__(self):
        return f"To: {self.device.name} Text: {self.message}"


class DeviceStats(models.Model):
    """Model for device statistics (migrated from old Stats model)."""
    name = models.CharField(_('name'), max_length=20)
    route = models.IntegerField(choices=GPSDevice.ROUTE_CHOICES)
    economico = models.IntegerField()
    date_start = models.DateTimeField(_('start date'), null=True)
    date_end = models.DateTimeField(_('end date'))
    latitude = models.IntegerField(null=True, blank=True)
    longitude = models.IntegerField(null=True, blank=True)
    distance = models.IntegerField(null=True, blank=True)
    sub_del = models.IntegerField(null=True, blank=True)
    baj_del = models.IntegerField(null=True, blank=True)
    sub_tra = models.IntegerField(null=True, blank=True)
    baj_tra = models.IntegerField(null=True, blank=True)
    speed_avg = models.IntegerField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('device statistics')
        verbose_name_plural = _('device statistics')
        ordering = ['-date_end']

    def __str__(self):
        return f"{self.name} - Route {self.route}"


class GPSLocation(BaseLocation):
    """Model for GPS location data."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='gps_locations')
    hdop = models.FloatField(null=True, blank=True)  # Horizontal Dilution of Precision
    pdop = models.FloatField(null=True, blank=True)  # Position Dilution of Precision
    fix_quality = models.IntegerField(null=True, blank=True)
    fix_type = models.CharField(max_length=20, null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('GPS location')
        verbose_name_plural = _('GPS locations')


class GPSEvent(BaseEvent):
    """Model for GPS events."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='gps_events')
    source = models.CharField(max_length=20, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    inputs = models.IntegerField(default=0)
    outputs = models.IntegerField(default=0)
    input_changes = models.IntegerField(default=0)
    output_changes = models.IntegerField(default=0)
    alarm_changes = models.IntegerField(default=0)
    changes_description = models.TextField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('GPS event')
        verbose_name_plural = _('GPS events')


class IOEvent(GPSEvent):
    """Model for Input/Output events (migrated from old backend)."""
    input_delta = models.IntegerField(default=0)
    output_delta = models.IntegerField(default=0)
    alarm_delta = models.IntegerField(default=0)
    changes = models.TextField(blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('IO event')
        verbose_name_plural = _('IO events')


class GSMEvent(GPSEvent):
    """Model for GSM events (migrated from old backend)."""
    # source and text are already in parent GPSEvent

    objects = models.Manager()

    class Meta:
        verbose_name = _('GSM event')
        verbose_name_plural = _('GSM events')


class ResetEvent(GPSEvent):
    """Model for reset events (migrated from old backend)."""
    reason = models.CharField(max_length=180)

    objects = models.Manager()

    class Meta:
        verbose_name = _('reset event')
        verbose_name_plural = _('reset events')


class GeoFence(BaseGeoFence):
    """Model for geofences."""
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notify_on_entry = models.BooleanField(default=True)
    notify_on_exit = models.BooleanField(default=True)
    notify_owners = models.ManyToManyField(User, related_name='notified_fences', blank=True)
    
    # Visual properties for frontend
    color = models.CharField(max_length=7, default='#3388ff', help_text='Fill color in hex format')
    stroke_color = models.CharField(max_length=7, default='#3388ff', help_text='Border color in hex format')
    stroke_width = models.IntegerField(default=2, help_text='Border width in pixels')
    
    # Alert settings
    alert_on_entry = models.BooleanField(default=False, help_text='Show alert when device enters geofence')
    alert_on_exit = models.BooleanField(default=False, help_text='Show alert when device exits geofence')
    
    # Notification settings
    notification_cooldown = models.IntegerField(default=300, help_text='Minimum seconds between notifications')
    notify_emails = models.JSONField(default=list, blank=True, help_text='List of email addresses for notifications')
    notify_sms = models.JSONField(default=list, blank=True, help_text='List of phone numbers for SMS notifications')
    
    # Device relationship
    devices = models.ManyToManyField(GPSDevice, related_name='geofences', blank=True)
    
    # Migrated field from old backend
    base = models.IntegerField(null=True, blank=True, choices=GPSDevice.ROUTE_CHOICES)

    objects = models.Manager()

    class Meta:
        verbose_name = _('geofence')
        verbose_name_plural = _('geofences')


class GeoFenceEvent(models.Model):
    """Model for geofence events."""
    EVENT_TYPES = (
        ('ENTRY', 'Entry'),
        ('EXIT', 'Exit'),
    )

    fence = models.ForeignKey(GeoFence, on_delete=models.CASCADE, related_name='events')
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='fence_events')
    event_type = models.CharField(max_length=5, choices=EVENT_TYPES)
    position = gis_models.PointField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _('geofence event')
        verbose_name_plural = _('geofence events')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"


class AccelerationLog(models.Model):
    """Model for acceleration logs (migrated from AccelLog)."""
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='acceleration_logs')
    position = gis_models.PointField()
    date = models.DateTimeField()
    duration = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    error_duration = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    entry = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    error_entry = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    peak = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    error_exit = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    exit = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)

    objects = models.Manager()

    class Meta:
        verbose_name = _('acceleration log')
        verbose_name_plural = _('acceleration logs')
        ordering = ['device', 'date']

    def __str__(self):
        return f"{self.id} - {self.device}"


class Overlay(models.Model):
    """Model for map overlays (migrated from Overlays)."""
    name = models.CharField(_('name'), max_length=32, unique=True)
    geometry = gis_models.LineStringField(_('line'))
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    base = models.IntegerField(null=True, blank=True, choices=GPSDevice.ROUTE_CHOICES)

    objects = models.Manager()

    class Meta:
        verbose_name = _('overlay')
        verbose_name_plural = _('overlays')
        ordering = ['name']

    def __str__(self):
        return self.name


class AddressCache(models.Model):
    """Model for address caching (migrated from old backend)."""
    position = gis_models.PointField(spatial_index=True)
    date = models.DateTimeField()
    text = models.TextField(default="N/D")

    objects = models.Manager()

    class Meta:
        verbose_name = _('address cache')
        verbose_name_plural = _('address cache')

    def __str__(self):
        return f"[{self.position.y:.4f}:{self.position.x:.4f}]{self.text}" 