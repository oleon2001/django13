from django.db import models

class Coordinate(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Device {self.device_id} at {self.latitude}, {self.longitude}" 