from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from datetime import datetime, timedelta
from decimal import Decimal
import pytz

class Route(models.Model):
    """Modelo para gestionar rutas de transporte"""
    RUTA_CHOICES = (
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
    
    code = models.IntegerField(choices=RUTA_CHOICES, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'reports'
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Driver(models.Model):
    """Modelo para conductores"""
    EDOCIVIL_CHOICES = (
        ("SOL", "Soltero"),
        ("CAS", "Casado"),
        ("VIU", "Viudo"),
        ("DIV", "Divorciado")
    )
    
    name = models.CharField(max_length=40)
    middle = models.CharField(max_length=40)  # Apellido paterno
    last = models.CharField(max_length=40)    # Apellido materno
    birth = models.DateField()
    cstatus = models.CharField(max_length=40, choices=EDOCIVIL_CHOICES)
    payroll = models.CharField(max_length=40)
    socials = models.CharField(max_length=40)  # Seguro social
    taxid = models.CharField(max_length=40)    # RFC
    license = models.CharField(max_length=40, null=True, blank=True)
    lic_exp = models.DateField(null=True, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=40)
    phone1 = models.CharField(max_length=40, null=True, blank=True)
    phone2 = models.CharField(max_length=40, null=True, blank=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'reports'
        verbose_name = 'Conductor'
        verbose_name_plural = 'Conductores'
        ordering = ('middle', 'last', 'name')
    
    def __str__(self):
        return f"{self.middle} {self.last} {self.name}"

class Ticket(models.Model):
    """Modelo para tickets de transporte"""
    device = models.ForeignKey('gps.GPSDevice', on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    date = models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    received = models.DecimalField(max_digits=10, decimal_places=2)
    ticket_data = models.TextField()  # Datos del ticket
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'reports'
    
    def __str__(self):
        return f"Ticket {self.id} - {self.device.name} - {self.date.date()}"

class TimeSheet(models.Model):
    """Modelo para horarios de trabajo"""
    device = models.ForeignKey('gps.GPSDevice', on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    date = models.DateField()
    laps = models.IntegerField(default=0)  # Número de vueltas
    times_data = models.JSONField()  # Datos de tiempos en formato JSON
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'reports'
    
    def __str__(self):
        return f"Horario {self.device.name} - {self.date}"

class GeoFence(models.Model):
    """Modelo para cercas geográficas"""
    name = models.CharField(max_length=32, unique=True)
    fence = gis_models.PolygonField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        app_label = 'reports'
    
    def __str__(self):
        return self.name

class Statistics(models.Model):
    """Modelo para estadísticas diarias"""
    device = models.ForeignKey('gps.GPSDevice', on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    date = models.DateField()
    distance = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # km
    avg_speed = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # km/h
    passengers_up = models.IntegerField(default=0)  # Pasajeros subidos
    passengers_down = models.IntegerField(default=0)  # Pasajeros bajados
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'reports'
        unique_together = ('device', 'date')
    
    def __str__(self):
        return f"Stats {self.device.name} - {self.date}"

class SensorData(models.Model):
    """Modelo para datos de sensores (peso, etc.)"""
    device = models.ForeignKey('gps.GPSDevice', on_delete=models.CASCADE)
    sensor_id = models.CharField(max_length=32)
    date = models.DateTimeField()
    value1 = models.DecimalField(max_digits=10, decimal_places=2)
    value2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        app_label = 'reports'
        ordering = ('-date',)
    
    def __str__(self):
        return f"Sensor {self.sensor_id} - {self.device.name} - {self.date}" 