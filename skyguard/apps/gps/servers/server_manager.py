"""
GPS Server Manager - Centralized management of all GPS protocol servers.
"""
import threading
import time
import logging
from typing import Dict, List, Any
from datetime import datetime

from django.conf import settings

from skyguard.apps.gps.servers.concox_server import start_concox_server
from skyguard.apps.gps.servers.meiligao_server import start_meiligao_server
from skyguard.apps.gps.servers.sat_server import SATServer
from skyguard.apps.gps.servers.wialon_server import WialonServer
from skyguard.apps.gps.services.email_processor import process_device_emails


logger = logging.getLogger(__name__)


class GPSServerManager:
    """Centralized GPS server management."""
    
    def __init__(self):
        """Initialize server manager."""
        self.servers = {}
        self.threads = {}
        self.running = False
        self.email_processor_thread = None
        
        # Server configurations
        self.server_configs = {
            'concox': {
                'enabled': True,
                'host': '',
                'port': 55300,
                'protocol': 'TCP',
                'description': 'Concox GPS Tracker Protocol',
                'start_function': start_concox_server
            },
            'meiligao': {
                'enabled': True,
                'host': '',
                'port': 62000,
                'protocol': 'UDP',
                'description': 'Meiligao GPS Tracker Protocol',
                'start_function': start_meiligao_server
            },
            'satellite': {
                'enabled': True,
                'host': '',
                'port': 15557,
                'protocol': 'TCP',
                'description': 'Satellite Communication Protocol',
                'start_function': self._start_sat_server
            },
            'wialon': {
                'enabled': True,
                'host': '',
                'port': 20332,
                'protocol': 'TCP',
                'description': 'Wialon GPS Tracker Protocol',
                'start_function': self._start_wialon_server
            }
        }
        
        # Load configuration from Django settings
        self._load_configuration()
        
    def _load_configuration(self):
        """Load server configuration from Django settings."""
        try:
            gps_config = getattr(settings, 'GPS_SERVERS_CONFIG', {})
            
            for server_name, config in gps_config.items():
                if server_name in self.server_configs:
                    self.server_configs[server_name].update(config)
                    
        except Exception as e:
            logger.warning(f"Failed to load GPS server configuration: {e}")
            
    def _start_sat_server(self, host='', port=15557):
        """Start SAT server."""
        server = SATServer(host=host, port=port)
        server.start()
        
    def _start_wialon_server(self, host='', port=20332):
        """Start Wialon server."""
        server = WialonServer(host=host, port=port)
        server.start()
        
    def start_server(self, server_name: str) -> bool:
        """Start a specific GPS server."""
        try:
            if server_name not in self.server_configs:
                logger.error(f"Unknown server: {server_name}")
                return False
                
            config = self.server_configs[server_name]
            
            if not config.get('enabled', False):
                logger.info(f"Server {server_name} is disabled")
                return False
                
            if server_name in self.threads and self.threads[server_name].is_alive():
                logger.warning(f"Server {server_name} is already running")
                return False
                
            # Start server in separate thread
            start_function = config['start_function']
            thread = threading.Thread(
                target=start_function,
                args=(config['host'], config['port']),
                name=f"GPS-{server_name.upper()}-Server",
                daemon=True
            )
            
            thread.start()
            self.threads[server_name] = thread
            
            logger.info(f"Started {server_name} server on {config['protocol'].lower()}://{config['host'] or '0.0.0.0'}:{config['port']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {server_name} server: {e}")
            return False
            
    def stop_server(self, server_name: str) -> bool:
        """Stop a specific GPS server."""
        try:
            if server_name not in self.threads:
                logger.warning(f"Server {server_name} is not running")
                return False
                
            thread = self.threads[server_name]
            if thread.is_alive():
                # Note: This is a graceful approach, actual implementation
                # would need specific server shutdown mechanisms
                logger.info(f"Requesting shutdown of {server_name} server")
                # In a real implementation, you'd send a shutdown signal to the server
                
            del self.threads[server_name]
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {server_name} server: {e}")
            return False
            
    def start_all_servers(self) -> Dict[str, bool]:
        """Start all enabled GPS servers."""
        results = {}
        
        logger.info("Starting GPS server manager...")
        self.running = True
        
        for server_name, config in self.server_configs.items():
            if config.get('enabled', False):
                results[server_name] = self.start_server(server_name)
            else:
                logger.info(f"Skipping disabled server: {server_name}")
                results[server_name] = False
                
        # Start email processor
        self._start_email_processor()
        
        return results
        
    def stop_all_servers(self) -> Dict[str, bool]:
        """Stop all running GPS servers."""
        results = {}
        
        logger.info("Stopping GPS server manager...")
        self.running = False
        
        for server_name in list(self.threads.keys()):
            results[server_name] = self.stop_server(server_name)
            
        # Stop email processor
        self._stop_email_processor()
        
        return results
        
    def _start_email_processor(self):
        """Start email processor for automatic device registration."""
        try:
            if self.email_processor_thread and self.email_processor_thread.is_alive():
                logger.warning("Email processor is already running")
                return
                
            def email_processor_worker():
                """Email processor worker thread."""
                while self.running:
                    try:
                        logger.info("Processing device registration emails...")
                        count, devices = process_device_emails()
                        
                        if count > 0:
                            logger.info(f"Auto-registered {count} new devices")
                            
                    except Exception as e:
                        logger.error(f"Error in email processor: {e}")
                        
                    # Wait 30 minutes before next check
                    for _ in range(1800):  # 30 * 60 seconds
                        if not self.running:
                            break
                        time.sleep(1)
                        
            self.email_processor_thread = threading.Thread(
                target=email_processor_worker,
                name="GPS-EmailProcessor",
                daemon=True
            )
            self.email_processor_thread.start()
            
            logger.info("Started email processor for automatic device registration")
            
        except Exception as e:
            logger.error(f"Failed to start email processor: {e}")
            
    def _stop_email_processor(self):
        """Stop email processor."""
        try:
            if self.email_processor_thread and self.email_processor_thread.is_alive():
                logger.info("Stopping email processor...")
                # The thread will stop when self.running becomes False
                
        except Exception as e:
            logger.error(f"Error stopping email processor: {e}")
            
    def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all GPS servers."""
        status = {}
        
        for server_name, config in self.server_configs.items():
            thread = self.threads.get(server_name)
            
            status[server_name] = {
                'name': server_name.title(),
                'description': config.get('description', ''),
                'enabled': config.get('enabled', False),
                'protocol': config.get('protocol', 'Unknown'),
                'host': config.get('host', '0.0.0.0'),
                'port': config.get('port', 0),
                'running': thread.is_alive() if thread else False,
                'thread_name': thread.name if thread and thread.is_alive() else None
            }
            
        # Add email processor status
        status['email_processor'] = {
            'name': 'Email Processor',
            'description': 'Automatic device registration from emails',
            'enabled': True,
            'protocol': 'IMAP/SMTP',
            'host': 'imap.zoho.com',
            'port': 993,
            'running': self.email_processor_thread.is_alive() if self.email_processor_thread else False,
            'thread_name': self.email_processor_thread.name if self.email_processor_thread and self.email_processor_thread.is_alive() else None
        }
        
        return status
        
    def restart_server(self, server_name: str) -> bool:
        """Restart a specific GPS server."""
        logger.info(f"Restarting {server_name} server...")
        
        # Stop the server
        stop_result = self.stop_server(server_name)
        
        # Wait a moment
        time.sleep(2)
        
        # Start the server
        start_result = self.start_server(server_name)
        
        return stop_result and start_result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get GPS server statistics."""
        from skyguard.apps.gps.models import GPSDevice, GPSEvent
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        stats = {
            'timestamp': now.isoformat(),
            'total_devices': GPSDevice.objects.count(),
            'active_devices': GPSDevice.objects.filter(is_active=True).count(),
            'events_last_hour': GPSEvent.objects.filter(timestamp__gte=last_hour).count(),
            'events_last_day': GPSEvent.objects.filter(timestamp__gte=last_day).count(),
            'servers': {}
        }
        
        # Server-specific statistics
        for server_name, config in self.server_configs.items():
            protocol = config.get('protocol', '').lower()
            device_count = GPSDevice.objects.filter(protocol=server_name).count()
            
            stats['servers'][server_name] = {
                'devices': device_count,
                'port': config.get('port', 0),
                'protocol': protocol
            }
            
        return stats


# Global server manager instance
server_manager = GPSServerManager()


def start_gps_servers():
    """Start all GPS servers."""
    return server_manager.start_all_servers()


def stop_gps_servers():
    """Stop all GPS servers."""
    return server_manager.stop_all_servers()


def get_server_status():
    """Get status of all GPS servers."""
    return server_manager.get_server_status()


def get_server_statistics():
    """Get GPS server statistics."""
    return server_manager.get_statistics()


if __name__ == "__main__":
    import os
    import django
    import signal
    import sys
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.local')
    django.setup()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        server_manager.stop_all_servers()
        sys.exit(0)
        
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start all servers
        results = server_manager.start_all_servers()
        
        logger.info("GPS Server Manager started successfully")
        logger.info("Server status:")
        for server, started in results.items():
            status = "✓ Started" if started else "✗ Failed"
            logger.info(f"  {server}: {status}")
            
        # Keep the main thread alive
        while server_manager.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down GPS servers...")
        server_manager.stop_all_servers()
    except Exception as e:
        logger.error(f"Error running GPS servers: {e}")
        server_manager.stop_all_servers()
        sys.exit(1) 