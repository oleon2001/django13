"""
Wialon protocol server.
"""
import socket
import threading
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from django.utils import timezone
from django.contrib.gis.geos import Point

from skyguard.core.interfaces import IDeviceServer
from skyguard.apps.gps.models.device import GPSDevice
from skyguard.apps.gps.protocols.wialon import WialonProtocolHandler

logger = logging.getLogger(__name__)

class WialonServer(IDeviceServer):
    """Server for Wialon protocol devices."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 20332):
        """Initialize the server."""
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clients = {}
        self.protocol = WialonProtocolHandler()
        
    def start(self):
        """Start the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            logger.info(f"Wialon server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
                    
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            self.stop()
            
    def stop(self):
        """Stop the server."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        logger.info("Wialon server stopped")
        
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle a client connection."""
        try:
            logger.info(f"New connection from {address}")
            buffer = b''
            
            while self.running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                        
                    buffer += data
                    
                    # Process complete packets
                    while b'\r\n' in buffer:
                        packet, buffer = buffer.split(b'\r\n', 1)
                        packet += b'\r\n'
                        
                        if not self.protocol.validate_packet(packet):
                            logger.warning(f"Invalid packet from {address}: {packet}")
                            continue
                            
                        decoded = self.protocol.decode_packet(packet)
                        if not decoded:
                            continue
                            
                        if decoded['type'] == 'login':
                            self._handle_login(client_socket, address, decoded)
                        elif decoded['type'] == 'data':
                            self._handle_data(client_socket, address, decoded)
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Error handling client {address}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error in client handler for {address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            logger.info(f"Connection closed for {address}")
            
    def _handle_login(self, client_socket: socket.socket, address: tuple, data: Dict[str, Any]):
        """Handle a login packet."""
        try:
            imei = data['imei']
            password = data['password']
            
            # Find or create device
            try:
                device = GPSDevice.objects.get(imei=imei)
                logger.info(f"Device found: {device.name} (IMEI: {imei})")
            except GPSDevice.DoesNotExist:
                device = GPSDevice.objects.create(
                    imei=imei,
                    name=f"Wialon-{imei}",
                    protocol='wialon'
                )
                logger.info(f"Created new device: {device.name} (IMEI: {imei})")
            
            # Store client info
            self.clients[address] = {
                'device': device,
                'last_seen': timezone.now()
            }
            
            # Send login response
            response = b'#AL#1\r\n'  # 1 = success
            client_socket.send(response)
            
            # Update device status
            device.update_connection_status('ONLINE', address[0], address[1])
            
        except Exception as e:
            logger.error(f"Error handling login from {address}: {e}")
            response = b'#AL#0\r\n'  # 0 = failure
            try:
                client_socket.send(response)
            except:
                pass
            
    def _handle_data(self, client_socket: socket.socket, address: tuple, data: Dict[str, Any]):
        """Handle a data packet."""
        try:
            client_info = self.clients.get(address)
            if not client_info:
                logger.warning(f"Data packet from unknown client {address}")
                return
                
            device = client_info['device']
            client_info['last_seen'] = timezone.now()
            
            # Update device position and status
            device.position = data['position']
            device.speed = data['speed']
            device.course = data['course']
            device.altitude = data['altitude']
            device.last_log = data['timestamp']
            device.save()
            
            # Send data response
            response = b'#AD#1\r\n'  # 1 = success
            client_socket.send(response)
            
        except Exception as e:
            logger.error(f"Error handling data from {address}: {e}")
            response = b'#AD#0\r\n'  # 0 = failure
            try:
                client_socket.send(response)
            except:
                pass 