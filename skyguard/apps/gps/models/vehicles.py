"""
Vehicle models for GPS system (migrated from old backend).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .device import GPSDevice
from .drivers import Driver


class Vehicle(models.Model):
    """Model for vehicles linked to GPS devices and drivers."""
    VEHICLE_TYPE_CHOICES = (
        ("CAR", "Automóvil"),
        ("TRUCK", "Camión"),
        ("MOTORCYCLE", "Motocicleta"),
        ("BUS", "Autobús"),
        ("VAN", "Camioneta"),
        ("OTHER", "Otro")
    )

    VEHICLE_STATUS_CHOICES = (
        ("ACTIVE", "Activo"),
        ("INACTIVE", "Inactivo"),
        ("MAINTENANCE", "En mantenimiento"),
        ("REPAIR", "En reparación")
    )

    # Basic information
    plate = models.CharField(_('license plate'), max_length=20, unique=True)
    make = models.CharField(_('make'), max_length=50)
    model = models.CharField(_('model'), max_length=50)
    year = models.IntegerField(_('year'))
    color = models.CharField(_('color'), max_length=30)
    vehicle_type = models.CharField(_('vehicle type'), max_length=20, choices=VEHICLE_TYPE_CHOICES, default="CAR")
    status = models.CharField(_('status'), max_length=20, choices=VEHICLE_STATUS_CHOICES, default="ACTIVE")
    
    # Vehicle identification
    vin = models.CharField(_('VIN'), max_length=17, unique=True, null=True, blank=True)
    economico = models.CharField(_('economic number'), max_length=20, null=True, blank=True)
    
    # Fuel and engine info
    fuel_type = models.CharField(_('fuel type'), max_length=20, choices=[
        ("GASOLINE", "Gasolina"),
        ("DIESEL", "Diesel"),
        ("ELECTRIC", "Eléctrico"),
        ("HYBRID", "Híbrido"),
        ("GAS", "Gas")
    ], default="GASOLINE")
    engine_size = models.CharField(_('engine size'), max_length=20, null=True, blank=True)
    
    # Capacity and dimensions
    passenger_capacity = models.IntegerField(_('passenger capacity'), null=True, blank=True)
    cargo_capacity = models.FloatField(_('cargo capacity (kg)'), null=True, blank=True)
    
    # Insurance and documentation
    insurance_policy = models.CharField(_('insurance policy'), max_length=50, null=True, blank=True)
    insurance_expiry = models.DateField(_('insurance expiry'), null=True, blank=True)
    registration_expiry = models.DateField(_('registration expiry'), null=True, blank=True)
    
    # GPS Device relationship
    device = models.OneToOneField(
        GPSDevice, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='vehicle',
        verbose_name=_('GPS device')
    )
    
    # Driver relationship
    driver = models.ForeignKey(
        Driver, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='vehicles',
        verbose_name=_('assigned driver')
    )
    
    # Maintenance and operation
    mileage = models.FloatField(_('mileage (km)'), default=0)
    last_service_date = models.DateField(_('last service date'), null=True, blank=True)
    next_service_date = models.DateField(_('next service date'), null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager
    objects = models.Manager()

    class Meta:
        verbose_name = _('vehicle')
        verbose_name_plural = _('vehicles')
        ordering = ['plate']

    def __str__(self):
        return f"{self.plate} - {self.make} {self.model} ({self.year})"

    @property
    def is_gps_enabled(self):
        """Check if vehicle has GPS device assigned."""
        return self.device is not None

    @property
    def has_driver_assigned(self):
        """Check if vehicle has driver assigned."""
        return self.driver is not None

    @property
    def current_location(self):
        """Get current GPS location if available."""
        if self.device and self.device.position:
            return {
                'latitude': self.device.position.y,
                'longitude': self.device.position.x,
                'last_update': self.device.last_heartbeat
            }
        return None

    @property
    def is_online(self):
        """Check if vehicle's GPS device is online."""
        return self.device.connection_status == 'ONLINE' if self.device else False

    def assign_gps_device(self, device):
        """Assign GPS device to vehicle."""
        # Remove device from previous vehicle if exists
        if device.vehicle:
            device.vehicle.device = None
            device.vehicle.save()
        
        self.device = device
        self.save()

    def assign_driver(self, driver):
        """Assign driver to vehicle."""
        self.driver = driver
        self.save() 