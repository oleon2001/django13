import socketserver
from skyguard.apps.gps.servers.base import BaseGPSRequestHandler

class BLURequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data, sock = self.request
        print(f"BLU data received: {data}")
        # TODO: Decodificar y procesar datos BLU


def start_blu_server(host='', port=50100):
    server = socketserver.ThreadingUDPServer((host, port), BLURequestHandler)
    print(f"BLU UDP server started on port {port}")
    server.serve_forever() 