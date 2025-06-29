from skyguard.apps.gps.servers.base import BaseGPSRequestHandler, BaseGPSServer

class SGAvlRequestHandler(BaseGPSRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        print(f"SGAvl data received: {data}")
        # TODO: Decodificar y procesar datos SGAvl


def start_sgavl_server(host='', port=60010):
    server = BaseGPSServer(host, port, SGAvlRequestHandler)
    server.start() 