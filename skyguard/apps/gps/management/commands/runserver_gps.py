"""
Django management command to start GPS servers.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import signal
import sys

from skyguard.apps.gps.servers.server_manager import GPSServerManager


class Command(BaseCommand):
    """Start GPS tracking servers."""
    
    help = 'Start GPS tracking servers for all supported protocols'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--servers',
            type=str,
            help='Comma-separated list of servers to start (wialon,concox,meiligao,satellite)',
            default='all'
        )
        
        parser.add_argument(
            '--list-servers',
            action='store_true',
            help='List available servers and their status'
        )
        
        parser.add_argument(
            '--host',
            type=str,
            default='',
            help='Host to bind servers to (default: all interfaces)'
        )
        
        parser.add_argument(
            '--background',
            action='store_true',
            help='Run servers in background (daemon mode)'
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        manager = GPSServerManager()
        
        # List servers if requested
        if options['list_servers']:
            self.list_servers(manager)
            return
        
        # Determine which servers to start
        servers_to_start = self.get_servers_to_start(options['servers'])
        
        # Setup signal handlers
        self.setup_signal_handlers(manager)
        
        # Start servers
        self.start_servers(manager, servers_to_start, options)
    
    def list_servers(self, manager):
        """List available servers and their configurations."""
        self.stdout.write(self.style.SUCCESS('Available GPS Servers:'))
        self.stdout.write('-' * 60)
        
        for name, config in manager.server_configs.items():
            status = "✅ Enabled" if config.get('enabled', False) else "❌ Disabled"
            self.stdout.write(
                f"{name.upper():12} | {config['protocol']:8} | "
                f"Port {config['port']:5} | {status}"
            )
            self.stdout.write(f"             | {config['description']}")
            self.stdout.write('')
        
        # Show current status
        current_status = manager.get_server_status()
        self.stdout.write(self.style.WARNING('Current Status:'))
        self.stdout.write('-' * 60)
        
        for server, status in current_status.items():
            state = "🟢 Running" if status.get('running', False) else "🔴 Stopped"
            self.stdout.write(f"{server.upper():12} | {state}")
    
    def get_servers_to_start(self, servers_option):
        """Get list of servers to start."""
        if servers_option == 'all':
            return None  # Start all enabled servers
        
        return [s.strip().lower() for s in servers_option.split(',')]
    
    def setup_signal_handlers(self, manager):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.stdout.write('\n' + self.style.WARNING('Shutting down GPS servers...'))
            manager.stop_all_servers()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_servers(self, manager, servers_to_start, options):
        """Start the GPS servers."""
        self.stdout.write(self.style.SUCCESS('Starting Falkon GPS Servers...'))
        self.stdout.write('=' * 60)
        
        # Show configuration
        self.stdout.write(f"Host: {options['host'] or 'All interfaces (0.0.0.0)'}")
        self.stdout.write(f"Servers: {servers_to_start or 'All enabled'}")
        self.stdout.write(f"Background mode: {options['background']}")
        self.stdout.write('')
        
        try:
            if servers_to_start:
                # Start specific servers
                results = {}
                for server_name in servers_to_start:
                    if server_name in manager.server_configs:
                        results[server_name] = manager.start_server(server_name)
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"Unknown server: {server_name}")
                        )
            else:
                # Start all enabled servers
                results = manager.start_all_servers()
            
            # Show results
            self.show_startup_results(results)
            
            if not options['background']:
                # Keep running and show status
                self.stdout.write(self.style.SUCCESS('\nServers are running...'))
                self.stdout.write('Press Ctrl+C to stop all servers')
                self.stdout.write('-' * 60)
                
                # Keep the process alive
                try:
                    while True:
                        # Show periodic status updates
                        import time
                        time.sleep(30)
                        self.show_server_statistics(manager)
                except KeyboardInterrupt:
                    pass
            else:
                self.stdout.write(self.style.SUCCESS('Servers started in background mode'))
                
        except Exception as e:
            raise CommandError(f'Failed to start GPS servers: {e}')
    
    def show_startup_results(self, results):
        """Show startup results."""
        self.stdout.write('Startup Results:')
        self.stdout.write('-' * 30)
        
        for server, success in results.items():
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {server.upper()}: Started successfully")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ {server.upper()}: Failed to start")
                )
    
    def show_server_statistics(self, manager):
        """Show periodic server statistics."""
        try:
            stats = manager.get_statistics()
            
            self.stdout.write(f"\n[{stats['timestamp']}] Server Statistics:")
            self.stdout.write(f"  Total connections: {stats['total_connections']}")
            self.stdout.write(f"  Active devices: {stats['active_devices']}")
            self.stdout.write(f"  Messages processed: {stats['messages_processed']}")
            
            for server, server_stats in stats.get('servers', {}).items():
                if server_stats.get('running'):
                    self.stdout.write(
                        f"  {server}: {server_stats.get('connections', 0)} connections"
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Could not get statistics: {e}")
            ) 