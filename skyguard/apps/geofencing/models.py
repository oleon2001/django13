"""
Modelos para el sistema de geofencing SkyGuard
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point, Polygon
from django.utils import timezone


class GeoFence(models.Model):
    """
    Modelo para geofences (cercas geográficas)
    """
    name = models.CharField(max_length=100, verbose_name="Nombre")
    polygon = gis_models.PolygonField(verbose_name="Polígono")
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Propietario"
    )
    route = models.ForeignKey(
        'reports.Route',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Ruta asociada"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        app_label = 'geofencing'
        verbose_name = "Geofence"
        verbose_name_plural = "Geofences"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.owner.username}"
    
    @property
    def center_point(self):
        """
        Obtener el punto central del geofence
        """
        return self.polygon.centroid
    
    @property
    def area(self):
        """
        Obtener el área del geofence en metros cuadrados
        """
        return self.polygon.area


class GeofenceEvent(models.Model):
    """
    Modelo para eventos de entrada/salida de geofences
    """
    EVENT_TYPES = [
        ('entry', 'Entrada'),
        ('exit', 'Salida'),
    ]
    
    device = models.ForeignKey(
        'gps.GPSDevice',
        on_delete=models.CASCADE,
        verbose_name="Dispositivo"
    )
    geofence = models.ForeignKey(
        GeoFence,
        on_delete=models.CASCADE,
        verbose_name="Geofence"
    )
    event_type = models.CharField(
        max_length=10,
        choices=EVENT_TYPES,
        verbose_name="Tipo de evento"
    )
    location = gis_models.PointField(verbose_name="Ubicación")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    
    class Meta:
        app_label = 'geofencing'
        verbose_name = "Evento de Geofence"
        verbose_name_plural = "Eventos de Geofences"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'geofence', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.device.name} - {self.event_type} - {self.geofence.name}"


class GeofenceAlert(models.Model):
    """
    Modelo para alertas de geofencing
    """
    ALERT_TYPES = [
        ('entry', 'Entrada no autorizada'),
        ('exit', 'Salida no autorizada'),
        ('duration', 'Tiempo excesivo dentro'),
        ('speed', 'Velocidad excesiva'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    device = models.ForeignKey(
        'gps.GPSDevice',
        on_delete=models.CASCADE,
        verbose_name="Dispositivo"
    )
    geofence = models.ForeignKey(
        GeoFence,
        on_delete=models.CASCADE,
        verbose_name="Geofence"
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        verbose_name="Tipo de alerta"
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='medium',
        verbose_name="Severidad"
    )
    message = models.TextField(verbose_name="Mensaje")
    location = gis_models.PointField(verbose_name="Ubicación")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    acknowledged = models.BooleanField(default=False, verbose_name="Reconocida")
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Reconocida por"
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de reconocimiento")
    
    class Meta:
        app_label = 'geofencing'
        verbose_name = "Alerta de Geofence"
        verbose_name_plural = "Alertas de Geofences"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'geofence', 'timestamp']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['acknowledged', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.device.name} - {self.alert_type} - {self.geofence.name}"
    
    def acknowledge(self, user):
        """
        Marcar alerta como reconocida
        """
        self.acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()


class GeofenceRule(models.Model):
    """
    Modelo para reglas de geofencing
    """
    RULE_TYPES = [
        ('entry_allowed', 'Entrada permitida'),
        ('exit_allowed', 'Salida permitida'),
        ('speed_limit', 'Límite de velocidad'),
        ('time_limit', 'Límite de tiempo'),
        ('schedule', 'Horario permitido'),
    ]
    
    geofence = models.ForeignKey(
        GeoFence,
        on_delete=models.CASCADE,
        verbose_name="Geofence"
    )
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPES,
        verbose_name="Tipo de regla"
    )
    devices = models.ManyToManyField(
        'gps.GPSDevice',
        blank=True,
        verbose_name="Dispositivos aplicables"
    )
    value = models.JSONField(verbose_name="Valor de la regla")
    active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        app_label = 'geofencing'
        verbose_name = "Regla de Geofence"
        verbose_name_plural = "Reglas de Geofences"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.geofence.name} - {self.rule_type}" 