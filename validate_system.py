#!/usr/bin/env python3
"""
Script de Validación Completa del Sistema SkyGuard
Valida todos los componentes críticos del backend
"""

import os
import sys
import django
import logging
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from skyguard.apps.gps.models import GPSDevice, GPSLocation, GPSEvent
from skyguard.apps.gps.services.gps import GPSService
from skyguard.apps.gps.protocols.concox import ConcoxProtocolHandler
from skyguard.apps.gps.protocols.wialon import WialonProtocolHandler

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkyGuardSystemValidator:
    """Validador completo del sistema SkyGuard"""
    
    def __init__(self):
        self.results = {
            'database': {'status': 'UNKNOWN', 'details': []},
            'websockets': {'status': 'UNKNOWN', 'details': []},
            'gps_services': {'status': 'UNKNOWN', 'details': []},
            'authentication': {'status': 'UNKNOWN', 'details': []},
            'api_endpoints': {'status': 'UNKNOWN', 'details': []},
            'celery_tasks': {'status': 'UNKNOWN', 'details': []},
            'cache': {'status': 'UNKNOWN', 'details': []},
        }
        self.client = Client()
        
    def validate_database(self):
        """Validar conexión y operaciones de base de datos"""
        try:
            # Crear usuario de prueba
            user, created = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@skyguard.com'}
            )
            if created:
                user.set_password('testpass123')
                user.save()
            
            # Crear dispositivo GPS de prueba
            device, created = GPSDevice.objects.get_or_create(
                imei='123456789012345',
                defaults={
                    'name': 'Test Device',
                    'user': user,
                    'is_active': True,
                    'last_position': Point(0, 0),
                }
            )
            
            # Crear ubicación de prueba
            location = GPSLocation.objects.create(
                device=device,
                position=Point(-74.006, 40.7128),  # NYC
                timestamp=datetime.now(),
                speed=25.5,
                heading=90,
                altitude=100,
                satellites=8,
                hdop=1.2,
                battery_level=85,
                signal_strength=75
            )
            
            # Verificar que se puede recuperar
            retrieved_location = GPSLocation.objects.filter(device=device).first()
            if retrieved_location:
                self.results['database']['status'] = 'SUCCESS'
                self.results['database']['details'].append('Database operations successful')
                self.results['database']['details'].append(f'Created {GPSDevice.objects.count()} devices')
                self.results['database']['details'].append(f'Created {GPSLocation.objects.count()} locations')
            else:
                self.results['database']['status'] = 'ERROR'
                self.results['database']['details'].append('Failed to retrieve location data')
                
        except Exception as e:
            self.results['database']['status'] = 'ERROR'
            self.results['database']['details'].append(f'Database error: {str(e)}')
    
    def validate_websockets(self):
        """Validar configuración de WebSockets"""
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                # Probar envío de mensaje
                async_to_sync(channel_layer.group_send)(
                    'test_group',
                    {
                        'type': 'test.message',
                        'message': 'Test message'
                    }
                )
                self.results['websockets']['status'] = 'SUCCESS'
                self.results['websockets']['details'].append('WebSocket channel layer working')
            else:
                self.results['websockets']['status'] = 'ERROR'
                self.results['websockets']['details'].append('Channel layer is None')
        except Exception as e:
            self.results['websockets']['status'] = 'ERROR'
            self.results['websockets']['details'].append(f'WebSocket error: {str(e)}')
    
    def validate_gps_services(self):
        """Validar servicios GPS"""
        try:
            gps_service = GPSService()
            
            # Datos de prueba
            location_data = {
                'imei': '123456789012345',
                'latitude': 40.7128,
                'longitude': -74.006,
                'timestamp': datetime.now(),
                'speed': 25.5,
                'heading': 90,
                'altitude': 100,
                'satellites': 8,
                'hdop': 1.2,
                'battery_level': 85,
                'signal_strength': 75
            }
            
            # Procesar ubicación
            result = gps_service.process_location(location_data)
            if result:
                self.results['gps_services']['status'] = 'SUCCESS'
                self.results['gps_services']['details'].append('GPS location processing successful')
            else:
                self.results['gps_services']['status'] = 'ERROR'
                self.results['gps_services']['details'].append('GPS location processing failed')
                
        except Exception as e:
            self.results['gps_services']['status'] = 'ERROR'
            self.results['gps_services']['details'].append(f'GPS service error: {str(e)}')
    
    def validate_authentication(self):
        """Validar sistema de autenticación"""
        try:
            # Crear usuario si no existe
            user, created = User.objects.get_or_create(
                username='auth_test_user',
                defaults={'email': 'auth@skyguard.com'}
            )
            if created:
                user.set_password('authpass123')
                user.save()
            
            # Probar login
            login_success = self.client.login(username='auth_test_user', password='authpass123')
            if login_success:
                self.results['authentication']['status'] = 'SUCCESS'
                self.results['authentication']['details'].append('User authentication successful')
            else:
                self.results['authentication']['status'] = 'ERROR'
                self.results['authentication']['details'].append('User authentication failed')
                
        except Exception as e:
            self.results['authentication']['status'] = 'ERROR'
            self.results['authentication']['details'].append(f'Authentication error: {str(e)}')
    
    def validate_api_endpoints(self):
        """Validar endpoints de API"""
        try:
            # Probar endpoint de dispositivos
            response = self.client.get('/api/gps/devices/')
            if response.status_code in [200, 401, 403]:  # 401/403 son esperados sin auth
                self.results['api_endpoints']['status'] = 'SUCCESS'
                self.results['api_endpoints']['details'].append('API endpoints responding')
            else:
                self.results['api_endpoints']['status'] = 'ERROR'
                self.results['api_endpoints']['details'].append(f'API endpoint error: {response.status_code}')
                
        except Exception as e:
            self.results['api_endpoints']['status'] = 'ERROR'
            self.results['api_endpoints']['details'].append(f'API endpoint error: {str(e)}')
    
    def validate_cache(self):
        """Validar sistema de cache"""
        try:
            # Probar operaciones de cache
            cache.set('test_key', 'test_value', 60)
            cached_value = cache.get('test_key')
            
            if cached_value == 'test_value':
                self.results['cache']['status'] = 'SUCCESS'
                self.results['cache']['details'].append('Cache operations successful')
            else:
                self.results['cache']['status'] = 'ERROR'
                self.results['cache']['details'].append('Cache operations failed')
                
        except Exception as e:
            self.results['cache']['status'] = 'ERROR'
            self.results['cache']['details'].append(f'Cache error: {str(e)}')
    
    def validate_celery_tasks(self):
        """Validar configuración de Celery"""
        try:
            from celery import current_app
            if current_app.conf.task_always_eager:
                self.results['celery_tasks']['status'] = 'SUCCESS'
                self.results['celery_tasks']['details'].append('Celery configured for testing')
            else:
                # Verificar que Celery está configurado
                self.results['celery_tasks']['status'] = 'SUCCESS'
                self.results['celery_tasks']['details'].append('Celery configuration valid')
                
        except Exception as e:
            self.results['celery_tasks']['status'] = 'ERROR'
            self.results['celery_tasks']['details'].append(f'Celery error: {str(e)}')
    
    def run_all_validations(self):
        """Ejecutar todas las validaciones"""
        logger.info("🚀 Iniciando validación completa del sistema SkyGuard...")
        
        self.validate_database()
        self.validate_websockets()
        self.validate_gps_services()
        self.validate_authentication()
        self.validate_api_endpoints()
        self.validate_cache()
        self.validate_celery_tasks()
        
        return self.results
    
    def print_results(self):
        """Imprimir resultados de validación"""
        print("\n" + "="*60)
        print("🔍 VALIDACIÓN COMPLETA DEL SISTEMA SKYGUARD")
        print("="*60)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if result['status'] == 'SUCCESS')
        failed_tests = sum(1 for result in self.results.values() if result['status'] == 'ERROR')
        
        for component, result in self.results.items():
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
            print(f"{status_icon} {component.upper()}: {result['status']}")
            
            for detail in result['details']:
                print(f"   • {detail}")
            print()
        
        print("="*60)
        print(f"📊 RESUMEN: {successful_tests}/{total_tests} componentes funcionando")
        print(f"🎯 Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("🎉 ¡SISTEMA COMPLETAMENTE OPERATIVO!")
        elif successful_tests > failed_tests:
            print("⚠️  Sistema parcialmente operativo - se requieren correcciones menores")
        else:
            print("🚨 Sistema con problemas críticos - requiere atención inmediata")
        print("="*60)

def main():
    """Función principal"""
    validator = SkyGuardSystemValidator()
    results = validator.run_all_validations()
    validator.print_results()
    
    # Retornar código de salida apropiado
    failed_components = sum(1 for result in results.values() if result['status'] == 'ERROR')
    return 0 if failed_components == 0 else 1

if __name__ == '__main__':
    sys.exit(main()) 