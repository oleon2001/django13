"""
SAT server implementation for GPS tracking.
"""
import struct
from datetime import datetime
from pytz import utc
from django.contrib.gis.geos import Point

from skyguard.apps.gps.servers.base import BaseGPSRequestHandler, BaseGPSServer
from skyguard.apps.gps.models import Device, Location


class SATRequestHandler(BaseGPSRequestHandler):
    """Handler for SAT protocol connections."""
    
    def handle(self):
        """Handle incoming SAT protocol data."""
        self.imei = None
        data = self.request.recv(2048)
        
        if len(data) < 38:
            raise ValueError(f"Invalid Length {len(data)}")
            
        # Extract IMEI and packet number
        self.imei = int(data[10:25])
        pack_n, = struct.unpack("<H", data[26:28])
        
        print(f"IMEI: {self.imei}")
        print(f"Seq: {pack_n}")
        
        # Get or create device
        try:
            self.device = Device.objects.get(imei=self.imei)
        except Device.DoesNotExist:
            self.device = Device.objects.create(
                imei=self.imei,
                name=f"SAT-{self.imei}",
                is_active=True
            )
        
        # Process remaining data
        data = data[38:]
        while data:
            print(f"Payload length: {len(data)}")
            
            # Extract date and time
            ym, tm = struct.unpack("<BH", data[0:3])
            year = (ym >> 4) + 2007
            month = ym & 0x0F
            day = (tm >> 11) & 0x1F
            hour = (tm >> 6) & 0x1F
            minute = tm & 0x3F
            dt = datetime(year, month, day, hour, minute, tzinfo=utc)
            
            # Extract position
            lat, lon = struct.unpack("<ff", data[3:11])
            position = Point(lon, lat)
            
            print(f"Date: {dt}")
            print(f"Lat, Lon: {lat}, {lon}")
            
            # Save location
            self.save_location(
                position=position,
                speed=0,
                course=0,
                altitude=0,
                satellites=0,
                accuracy=0
            )
            
            # Move to next record
            data = data[12:]


class SATServer(BaseGPSServer):
    """SAT protocol server."""
    
    def __init__(self, host='', port=15557):
        """Initialize the SAT server."""
        super().__init__(host=host, port=port, handler_class=SATRequestHandler)


if __name__ == "__main__":
    server = SATServer()
    server.start() 