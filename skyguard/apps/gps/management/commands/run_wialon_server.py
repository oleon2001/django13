from django.core.management.base import BaseCommand
from skyguard.apps.gps.Wialon import BLURequestHandler, SocketServer, queue, threading, worker

class Command(BaseCommand):
    help = 'Runs the Wialon GPS server'

    def handle(self, *args, **options):
        try:
            server = SocketServer.ThreadingUDPServer(('', 60001), BLURequestHandler)
            self.stdout.write(self.style.SUCCESS('_'*80))
            self.stdout.write(self.style.SUCCESS('Server Started.'))
            self.stdout.write(self.style.SUCCESS('-'*80))
            
            theQueue = queue.Queue()
            thread = threading.Thread(target=worker, args=(theQueue,))
            thread.start()
            
            server.serve_forever()
        except KeyboardInterrupt:
            theQueue.put(None)
            thread.join()
            self.stdout.write(self.style.SUCCESS('_'*80))
            self.stdout.write(self.style.SUCCESS('Server received signal, exiting.'))
            self.stdout.write(self.style.SUCCESS('-'*80)) 