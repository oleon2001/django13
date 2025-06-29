import socketserver
from skyguard.apps.gps.servers.base import BaseGPSRequestHandler

class BLUBootRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data, sock = self.request
        print(f"BLU Bootloader data received: {data}")
        # TODO: Decodificar y procesar datos de bootloader


def start_blu_boot_server(host='', port=60000):
    server = socketserver.ThreadingUDPServer((host, port), BLUBootRequestHandler)
    print(f"BLU Bootloader UDP server started on port {port}")
    server.serve_forever() 