#!/usr/bin/env python3
"""
Script de evaluación completa del backend SkyGuard.
Evalúa todos los componentes principales del sistema.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.core.exceptions import ValidationError

from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
from skyguard.apps.gps.services import GPSService
from skyguard.apps.gps.repositories import GPSDeviceRepository
from skyguard.apps.gps.protocols import GPSProtocolHandler, ConcoxProtocolHandler, WialonProtocolHandler
from skyguard.apps.gps.tasks import check_devices_heartbeat, update_device_connection_quality


class SystemEvaluator:
    """Evaluador completo del sistema SkyGuard."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0
            }
        }
        self.client = Client()
    
    def log_test(self, test_name, status, details=None, error=None):
        """Registra el resultado de una prueba."""
        self.results['tests'][test_name] = {
            'status': status,
            'details': details,
            'error': str(error) if error else None,
            'timestamp': datetime.now().isoformat()
        }
        
        if status == 'PASS':
            self.results['summary']['passed'] += 1
        elif status == 'FAIL':
            self.results['summary']['failed'] += 1
        else:
            self.results['summary']['errors'] += 1
        
        self.results['summary']['total_tests'] += 1
        
        # Imprimir resultado
        status_icon = "✅" if status == 'PASS' else "❌" if status == 'FAIL' else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
        if error:
            print(f"   🚨 Error: {error}")
    
    def test_database_connection(self):
        """Prueba la conexión a la base de datos."""
        try:
            # Verificar que podemos acceder a la base de datos
            device_count = GPSDevice.objects.count()
            user_count = User.objects.count()
            
            details = f"Dispositivos: {device_count}, Usuarios: {user_count}"
            self.log_test("Database Connection", "PASS", details)
            
        except Exception as e:
            self.log_test("Database Connection", "ERROR", error=e)
    
    def test_models_creation(self):
        """Prueba la creación de modelos."""
        try:
            # Crear un usuario de prueba
            user, created = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@example.com'}
            )
            
            # Crear un dispositivo de prueba
            device = GPSDevice.objects.create(
                imei=999999999999999,
                name='Test Device',
                protocol='concox',
                position=Point(0, 0),
                is_active=True,
                owner=user
            )
            
            # Crear una ubicación de prueba
            location = GPSLocation.objects.create(
                device=device,
                position=Point(1, 1),
                speed=50.0,
                course=90.0,
                altitude=100.0,
                satellites=8,
                accuracy=5.0,
                timestamp=timezone.now()
            )
            
            # Crear un evento de prueba
            event = GPSEvent.objects.create(
                device=device,
                type='TRACK',
                position=Point(1, 1),
                speed=50.0,
                course=90.0,
                altitude=100.0,
                timestamp=timezone.now()
            )
            
            details = f"Usuario: {user.username}, Dispositivo: {device.imei}, Ubicaciones: 1, Eventos: 1"
            self.log_test("Models Creation", "PASS", details)
            
            # Limpiar datos de prueba
            event.delete()
            location.delete()
            device.delete()
            if created:
                user.delete()
                
        except Exception as e:
            self.log_test("Models Creation", "ERROR", error=e)
    
    def test_protocol_handlers(self):
        """Prueba los manejadores de protocolos."""
        try:
            handler = GPSProtocolHandler()
            
            # Probar selección de protocolos
            concox_handler = handler.get_handler('concox')
            wialon_handler = handler.get_handler('wialon')
            
            # Verificar tipos
            assert isinstance(concox_handler, ConcoxProtocolHandler)
            assert isinstance(wialon_handler, WialonProtocolHandler)
            
            # Probar validación de paquetes
            valid_packet = b'\x78\x78\x0B\x01\x03\x51\x08\x42\x70\x00\x32\x01\x00\x0D\x0A'
            is_valid = concox_handler.validate_packet(valid_packet)
            
            # Probar decodificación
            data = concox_handler.decode_packet(valid_packet)
            
            details = f"Concox: {type(concox_handler).__name__}, Wialon: {type(wialon_handler).__name__}, Valid packet: {is_valid}"
            self.log_test("Protocol Handlers", "PASS", details)
            
        except Exception as e:
            self.log_test("Protocol Handlers", "ERROR", error=e)
    
    def test_services(self):
        """Prueba los servicios del sistema."""
        try:
            repository = GPSDeviceRepository()
            service = GPSService(repository)
            
            # Crear dispositivo de prueba
            user = User.objects.first()
            device = GPSDevice.objects.create(
                imei=888888888888888,
                name='Service Test Device',
                protocol='concox',
                position=Point(0, 0),
                is_active=True,
                owner=user
            )
            
            # Probar procesamiento de ubicación
            location_data = {
                'latitude': 1.0,
                'longitude': 1.0,
                'timestamp': timezone.now(),
                'speed': 50.0,
                'course': 90.0,
                'altitude': 100.0,
                'satellites': 8,
                'accuracy': 5.0,
                'hdop': 1.0,
                'pdop': 2.0,
                'fix_quality': 1,
                'fix_type': 3
            }
            
            service.process_location(device, location_data)
            
            # Verificar que se creó la ubicación
            location_count = GPSLocation.objects.filter(device=device).count()
            
            # Probar procesamiento de eventos
            event_data = {
                'type': 'TRACK',
                'timestamp': timezone.now(),
                'position': Point(2, 2),
                'speed': 60.0,
                'course': 180.0,
                'altitude': 150.0,
                'odometer': 1000.0
            }
            
            service.process_event(device, event_data)
            
            # Verificar que se creó el evento
            event_count = GPSEvent.objects.filter(device=device).count()
            
            details = f"Ubicaciones creadas: {location_count}, Eventos creados: {event_count}"
            self.log_test("Services", "PASS", details)
            
            # Limpiar
            device.delete()
            
        except Exception as e:
            self.log_test("Services", "ERROR", error=e)
    
    def test_api_endpoints(self):
        """Prueba los endpoints de la API."""
        try:
            # Crear usuario y dispositivo de prueba
            user = User.objects.create_user(
                username='api_test_user',
                password='testpass123',
                email='api@example.com'
            )
            
            device = GPSDevice.objects.create(
                imei=777777777777777,
                name='API Test Device',
                protocol='concox',
                position=Point(0, 0),
                is_active=True,
                owner=user
            )
            
            # Autenticar cliente
            self.client.force_login(user)
            
            # Probar endpoint de dispositivos
            response = self.client.get('/api/gps/devices/')
            devices_accessible = response.status_code == 200
            
            # Probar endpoint de estado del dispositivo
            response = self.client.get(f'/api/gps/devices/{device.imei}/status/')
            status_accessible = response.status_code == 200
            
            # Probar endpoint de sesiones activas
            response = self.client.get('/api/gps/sessions/active/')
            sessions_accessible = response.status_code == 200
            
            details = f"Devices: {devices_accessible}, Status: {status_accessible}, Sessions: {sessions_accessible}"
            self.log_test("API Endpoints", "PASS", details)
            
            # Limpiar
            device.delete()
            user.delete()
            
        except Exception as e:
            self.log_test("API Endpoints", "ERROR", error=e)
    
    def test_celery_tasks(self):
        """Prueba las tareas de Celery."""
        try:
            # Probar tarea de heartbeat
            heartbeat_result = check_devices_heartbeat()
            
            # Probar tarea de calidad de conexión
            quality_result = update_device_connection_quality()
            
            details = f"Heartbeat: {heartbeat_result.get('devices_checked', 0)} devices, Quality: {quality_result.get('devices_updated', 0)} updated"
            self.log_test("Celery Tasks", "PASS", details)
            
        except Exception as e:
            self.log_test("Celery Tasks", "ERROR", error=e)
    
    def test_authentication(self):
        """Prueba el sistema de autenticación."""
        try:
            # Crear usuario de prueba
            user = User.objects.create_user(
                username='auth_test_user',
                password='testpass123',
                email='auth@example.com'
            )
            
            # Probar login
            login_success = self.client.login(username='auth_test_user', password='testpass123')
            
            # Probar acceso a endpoint protegido
            if login_success:
                response = self.client.get('/api/gps/devices/')
                endpoint_accessible = response.status_code == 200
            else:
                endpoint_accessible = False
            
            details = f"Login: {login_success}, Endpoint access: {endpoint_accessible}"
            self.log_test("Authentication", "PASS", details)
            
            # Limpiar
            user.delete()
            
        except Exception as e:
            self.log_test("Authentication", "ERROR", error=e)
    
    def test_websocket_signals(self):
        """Prueba los signals de WebSocket."""
        try:
            # Crear dispositivo de prueba
            user = User.objects.first()
            device = GPSDevice.objects.create(
                imei=666666666666666,
                name='Signal Test Device',
                protocol='concox',
                position=Point(0, 0),
                is_active=True,
                owner=user
            )
            
            # Probar signal de cambio de estado
            device.connection_status = 'ONLINE'
            device.save()
            
            # Probar signal de nueva ubicación
            location = GPSLocation.objects.create(
                device=device,
                position=Point(1, 1),
                speed=50.0,
                course=90.0,
                altitude=100.0,
                satellites=8,
                accuracy=5.0,
                timestamp=timezone.now()
            )
            
            details = f"Device status signal: OK, Location signal: OK"
            self.log_test("WebSocket Signals", "PASS", details)
            
            # Limpiar
            location.delete()
            device.delete()
            
        except Exception as e:
            self.log_test("WebSocket Signals", "ERROR", error=e)
    
    def test_data_integrity(self):
        """Prueba la integridad de los datos."""
        try:
            # Verificar dispositivos existentes
            devices = GPSDevice.objects.all()
            
            integrity_issues = []
            
            for device in devices:
                # Verificar que los dispositivos tienen IMEI válido
                if not device.imei or device.imei <= 0:
                    integrity_issues.append(f"Invalid IMEI: {device.imei}")
                
                # Verificar que tienen nombre
                if not device.name:
                    integrity_issues.append(f"Missing name for device {device.imei}")
                
                # Verificar que tienen protocolo válido
                if device.protocol not in ['concox', 'meiligao', 'wialon']:
                    integrity_issues.append(f"Invalid protocol for device {device.imei}: {device.protocol}")
            
            if integrity_issues:
                details = f"Issues found: {len(integrity_issues)}"
                self.log_test("Data Integrity", "FAIL", details)
                for issue in integrity_issues:
                    print(f"   ⚠️ {issue}")
            else:
                details = f"All {devices.count()} devices have valid data"
                self.log_test("Data Integrity", "PASS", details)
                
        except Exception as e:
            self.log_test("Data Integrity", "ERROR", error=e)
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas."""
        print("🚀 INICIANDO EVALUACIÓN COMPLETA DEL SISTEMA SKYGUARD")
        print("=" * 60)
        
        tests = [
            self.test_database_connection,
            self.test_models_creation,
            self.test_protocol_handlers,
            self.test_services,
            self.test_api_endpoints,
            self.test_celery_tasks,
            self.test_authentication,
            self.test_websocket_signals,
            self.test_data_integrity,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "ERROR", error=e)
        
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Imprime el resumen de la evaluación."""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE EVALUACIÓN")
        print("=" * 60)
        
        summary = self.results['summary']
        total = summary['total_tests']
        passed = summary['passed']
        failed = summary['failed']
        errors = summary['errors']
        
        print(f"Total de pruebas: {total}")
        print(f"✅ Exitosas: {passed}")
        print(f"❌ Fallidas: {failed}")
        print(f"⚠️ Errores: {errors}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        # Determinar estado general
        if errors > 0:
            print("🔴 ESTADO: CRÍTICO - Errores en el sistema")
        elif failed > 0:
            print("🟡 ESTADO: PROBLEMAS - Algunas funcionalidades fallan")
        else:
            print("🟢 ESTADO: FUNCIONAL - Sistema operativo")
    
    def save_results(self):
        """Guarda los resultados en un archivo."""
        filename = f"system_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Resultados guardados en: {filename}")


def main():
    """Función principal."""
    evaluator = SystemEvaluator()
    evaluator.run_all_tests()


if __name__ == '__main__':
    main() 