"""
Network models for the GPS application.
"""
from django.db import models


class CellTower(models.Model):
    """Model for storing cell tower information."""
    mcc = models.IntegerField()  # Mobile Country Code
    mnc = models.IntegerField()  # Mobile Network Code
    lac = models.IntegerField()  # Location Area Code
    cell_id = models.BigIntegerField()  # Cell ID
    signal_strength = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cell Tower'
        verbose_name_plural = 'Cell Towers'
        unique_together = ['mcc', 'mnc', 'lac', 'cell_id']

    def __str__(self):
        return f"{self.mcc}-{self.mnc} {self.lac}-{self.cell_id}"


class WiFiAccessPoint(models.Model):
    """Model for storing WiFi access point information."""
    mac_address = models.CharField(max_length=17)
    signal_strength = models.IntegerField()
    ssid = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'WiFi Access Point'
        verbose_name_plural = 'WiFi Access Points'
        unique_together = ['mac_address']

    def __str__(self):
        return f"{self.mac_address} ({self.ssid or 'Unknown'})" 