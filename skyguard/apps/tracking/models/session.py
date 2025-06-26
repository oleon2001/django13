"""
Session models for the tracking application.
"""
from django.db import models
from skyguard.apps.gps.models import GPSDevice


class UdpSession(models.Model):
    """UDP session for AVL devices."""
    session = models.AutoField('session', primary_key=True)
    imei = models.ForeignKey(GPSDevice, null=False, unique=True, on_delete=models.CASCADE)
    expires = models.DateTimeField('expires', null=False)
    host = models.CharField("host", max_length=128, null=False)
    port = models.IntegerField("port", null=False)
    lastRec = models.IntegerField("rec", default=0)

    class Meta:
        ordering = ('imei',)
        verbose_name = 'UDP Session'
        verbose_name_plural = 'UDP Sessions'

    def __str__(self):
        return f'Session {self.imei.imei:015}-{self.session:010}' 