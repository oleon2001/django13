#!/usr/bin/python
# -*- coding: utf-8 -*-
# SGAvl server

import socket
import struct
import SocketServer
import threading
import sys
from datetime import datetime
from pytz import utc

from django.db import transaction, DatabaseError, IntegrityError, connection
from django.contrib.gis.geos import Point
from django.conf import settings
from gps.tracker.models import SGAvl, Event

settings.DEBUG = False

class SATRequestHandler(SocketServer.BaseRequestHandler):
    """Handler for satellite communication requests."""
    
    def setup(self):
        """Setup the request handler."""
        print("*" * 80)
        print(datetime.now().ctime(), self.client_address, 'connected!')

    def handle(self):
        """Handle incoming satellite data."""
        self.imei = None

        data = self.request.recv(2048)
        n_bytes = len(data)
        if n_bytes < 38:
            raise ValueError(f"Invalid Length {len(data)}")
        
        self.imei = int(data[10:25])
        pack_n, = struct.unpack("<H", data[26:28])
        print(f"IMEI: {self.imei}")
        print(f"Seq: {pack_n}")
        
        # Log the raw data
        with open(f'satlog_{pack_n}', "w") as log:
            log.write(data)
            
        data = data[38:]
        avl = SGAvl.objects.get(imei=self.imei)
        
        while data:
            print(f"Payload length: {len(data)}")
            ym, tm = struct.unpack("<BH", data[0:3])
            lat, lon = struct.unpack("<ff", data[3:11])
            
            # Parse date components
            year = (ym >> 4) + 2007
            month = ym & 0x0F
            day = (tm >> 11) & 0x1F
            hour = (tm >> 6) & 0x1F
            minute = tm & 0x3F
            
            dt = datetime(year, month, day, hour, minute, tzinfo=utc)
            print(f"Date: {dt}")
            print(f"Lat, Lon: {lat}, {lon}")
            
            pos = Point(lon, lat)
            avl.position = pos
            avl.lastLog = avl.date = dt
            
            track = Event(
                imei=avl,
                type="TRACK",
                position=pos,
                date=dt,
                speed=0,
                course=0,
                altitude=0,
                odom=0
            )
            
            avl.save()
            track.save()
            data = data[12:]

    def finish(self):
        """Clean up after handling the request."""
        pass

def start_server(host='', port=15557):
    """Start the satellite server."""
    try:
        server = SocketServer.ThreadingTCPServer((host, port), SATRequestHandler)
        print("_" * 80)
        print("Server Started.")
        print("-" * 80)
        sys.stdout.flush()
        server.serve_forever()
    except KeyboardInterrupt:
        print("_" * 80)
        print("Server received signal, exiting.")
        print("-" * 80)
        sys.stdout.flush()

if __name__ == "__main__":
    start_server() 