"""
Django management command for GPS servers.
"""
import time
import signal
import sys
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from skyguard.apps.gps.servers.server_manager import server_manager


class Command(BaseCommand):
    """Management command for GPS servers."""
    
    help = 'Manage GPS tracking servers (Concox, Meiligao, Satellite, etc.)'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            'action',
            choices=['start', 'stop', 'restart', 'status', 'stats'],
            help='Action to perform'
        )
        
        parser.add_argument(
            '--server',
            type=str,
            help='Specific server to control (concox, meiligao, satellite)'
        )
        
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run servers in daemon mode (for start action)'
        )
        
        parser.add_argument(
            '--email-only',
            action='store_true',
            help='Process device registration emails only'
        )
        
    def handle(self, *args, **options):
        """Handle the command."""
        action = options['action']
        server_name = options.get('server')
        daemon_mode = options.get('daemon', False)
        email_only = options.get('email_only', False)
        
        try:
            if action == 'start':
                self._handle_start(server_name, daemon_mode, email_only)
            elif action == 'stop':
                self._handle_stop(server_name)
            elif action == 'restart':
                self._handle_restart(server_name)
            elif action == 'status':
                self._handle_status(server_name)
            elif action == 'stats':
                self._handle_stats()
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nShutting down...'))
            if server_manager.running:
                server_manager.stop_all_servers()
        except Exception as e:
            raise CommandError(f'Error: {e}')
            
    def _handle_start(self, server_name, daemon_mode, email_only):
        """Handle start action."""
        if email_only:
            self._process_emails_only()
            return
            
        if server_name:
            # Start specific server
            self.stdout.write(f'Starting {server_name} server...')
            success = server_manager.start_server(server_name)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {server_name} server started successfully')
                )
            else:
                raise CommandError(f'Failed to start {server_name} server')
                
        else:
            # Start all servers
            self.stdout.write('Starting all GPS servers...')
            results = server_manager.start_all_servers()
            
            # Display results
            self.stdout.write('\nServer startup results:')
            for server, started in results.items():
                status = '✓ Started' if started else '✗ Failed'
                style = self.style.SUCCESS if started else self.style.ERROR
                self.stdout.write(f'  {server}: {style(status)}')
                
        if daemon_mode:
            self._run_daemon_mode()
            
    def _handle_stop(self, server_name):
        """Handle stop action."""
        if server_name:
            # Stop specific server
            self.stdout.write(f'Stopping {server_name} server...')
            success = server_manager.stop_server(server_name)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {server_name} server stopped')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ {server_name} server was not running')
                )
        else:
            # Stop all servers
            self.stdout.write('Stopping all GPS servers...')
            results = server_manager.stop_all_servers()
            
            self.stdout.write('\nServer shutdown results:')
            for server, stopped in results.items():
                status = '✓ Stopped' if stopped else '⚠ Not running'
                style = self.style.SUCCESS if stopped else self.style.WARNING
                self.stdout.write(f'  {server}: {style(status)}')
                
    def _handle_restart(self, server_name):
        """Handle restart action."""
        if server_name:
            # Restart specific server
            self.stdout.write(f'Restarting {server_name} server...')
            success = server_manager.restart_server(server_name)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {server_name} server restarted')
                )
            else:
                raise CommandError(f'Failed to restart {server_name} server')
        else:
            # Restart all servers
            self.stdout.write('Restarting all GPS servers...')
            server_manager.stop_all_servers()
            time.sleep(3)  # Wait for graceful shutdown
            results = server_manager.start_all_servers()
            
            self.stdout.write('\nServer restart results:')
            for server, started in results.items():
                status = '✓ Restarted' if started else '✗ Failed'
                style = self.style.SUCCESS if started else self.style.ERROR
                self.stdout.write(f'  {server}: {style(status)}')
                
    def _handle_status(self, server_name):
        """Handle status action."""
        status = server_manager.get_server_status()
        
        if server_name:
            # Show specific server status
            if server_name in status:
                self._display_server_status(server_name, status[server_name])
            else:
                raise CommandError(f'Unknown server: {server_name}')
        else:
            # Show all server status
            self.stdout.write(self.style.HTTP_INFO('GPS Server Status'))
            self.stdout.write('=' * 50)
            
            for name, info in status.items():
                self._display_server_status(name, info)
                
    def _handle_stats(self):
        """Handle stats action."""
        stats = server_manager.get_statistics()
        
        self.stdout.write(self.style.HTTP_INFO('GPS Server Statistics'))
        self.stdout.write('=' * 50)
        
        # General statistics
        self.stdout.write(f'Timestamp: {stats["timestamp"]}')
        self.stdout.write(f'Total Devices: {stats["total_devices"]}')
        self.stdout.write(f'Active Devices: {stats["active_devices"]}')
        self.stdout.write(f'Events (Last Hour): {stats["events_last_hour"]}')
        self.stdout.write(f'Events (Last Day): {stats["events_last_day"]}')
        
        # Server statistics
        self.stdout.write('\nServer Statistics:')
        for server_name, server_stats in stats["servers"].items():
            self.stdout.write(
                f'  {server_name.title()}: {server_stats["devices"]} devices '
                f'(Port {server_stats["port"]}, {server_stats["protocol"].upper()})'
            )
            
    def _display_server_status(self, name, info):
        """Display status for a single server."""
        running_status = '🟢 Running' if info['running'] else '🔴 Stopped'
        enabled_status = '✓ Enabled' if info['enabled'] else '✗ Disabled'
        
        self.stdout.write(f'\n{info["name"]}:')
        self.stdout.write(f'  Description: {info["description"]}')
        self.stdout.write(f'  Protocol: {info["protocol"]}')
        self.stdout.write(f'  Address: {info["host"] or "0.0.0.0"}:{info["port"]}')
        self.stdout.write(f'  Status: {running_status}')
        self.stdout.write(f'  Enabled: {enabled_status}')
        
        if info['thread_name']:
            self.stdout.write(f'  Thread: {info["thread_name"]}')
            
    def _run_daemon_mode(self):
        """Run servers in daemon mode."""
        def signal_handler(signum, frame):
            self.stdout.write(self.style.WARNING('\nReceived shutdown signal'))
            server_manager.stop_all_servers()
            sys.exit(0)
            
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ GPS servers running in daemon mode')
        )
        self.stdout.write('Press Ctrl+C to stop all servers')
        
        # Keep the main thread alive
        try:
            while server_manager.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nShutting down servers...'))
            server_manager.stop_all_servers()
            
    def _process_emails_only(self):
        """Process device registration emails only."""
        from skyguard.apps.gps.services.email_processor import process_device_emails
        
        self.stdout.write('Processing device registration emails...')
        
        try:
            count, devices = process_device_emails()
            
            if count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Auto-registered {count} new devices:')
                )
                for device in devices:
                    self.stdout.write(f'  - {device}')
            else:
                self.stdout.write(
                    self.style.WARNING('No new devices found in emails')
                )
                
        except Exception as e:
            raise CommandError(f'Error processing emails: {e}') 