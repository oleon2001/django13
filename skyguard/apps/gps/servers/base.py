"""
Base server class for GPS protocols.
"""
import socket
import struct
import SocketServer
import threading
import sys
import os
from datetime import datetime
from django.conf import settings
from django.db import transaction
from django.contrib.gis.geos import Point

from skyguard.apps.gps.models import Device, Location


class BaseGPSRequestHandler(SocketServer.BaseRequestHandler):
    """Base class for GPS protocol handlers."""
    
    def setup(self):
        """Initialize the handler."""
        self.stdout = sys.stdout
        self.device = None
        self.imei = None
        print("*" * 80)
        print(f"{datetime.now().ctime()} {self.client_address} connected!")

    def handle(self):
        """Handle the incoming connection."""
        raise NotImplementedError("Subclasses must implement handle()")

    def finish(self):
        """Clean up after handling the request."""
        if self.device:
            self.device.last_log = datetime.now()
            self.device.save()

    def save_location(self, position, speed=0, course=0, altitude=0, satellites=0, accuracy=0):
        """Save a location record for the device."""
        if not self.device:
            return

        with transaction.atomic():
            location = Location.objects.create(
                device=self.device,
                position=position,
                speed=speed,
                course=course,
                altitude=altitude,
                satellites=satellites,
                accuracy=accuracy,
                timestamp=datetime.now()
            )
            
            self.device.position = position
            self.device.speed = speed
            self.device.course = course
            self.device.altitude = altitude
            self.device.save()

        return location


class BaseGPSServer:
    """Base class for GPS servers."""
    
    def __init__(self, host='', port=0, handler_class=None):
        """Initialize the server."""
        if not handler_class:
            raise ValueError("handler_class must be provided")
            
        self.server = SocketServer.ThreadingTCPServer((host, port), handler_class)
        self.port = self.server.server_address[1]
        
    def start(self):
        """Start the server."""
        print("_" * 80)
        print(f"Server started on port {self.port}")
        print("-" * 80)
        sys.stdout.flush()
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("_" * 80)
            print("Server received signal, exiting.")
            print("-" * 80)
            sys.stdout.flush()
            
    def stop(self):
        """Stop the server."""
        self.server.shutdown()
        self.server.server_close() 