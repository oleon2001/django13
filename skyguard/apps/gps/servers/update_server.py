from skyguard.apps.gps.servers.base import BaseGPSRequestHandler, BaseGPSServer

class UpdateRequestHandler(BaseGPSRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        print(f"UpdateServer data received: {data}")
        # TODO: Decodificar y procesar datos de actualización OTA


def start_update_server(host='', port=60020):
    server = BaseGPSServer(host, port, UpdateRequestHandler)
    server.start() 