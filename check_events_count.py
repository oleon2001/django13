#!/usr/bin/env python3
"""
Script para verificar eventos legacy en la base de datos
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings.dev')
django.setup()

from skyguard.gps.tracker.models import Event, IOEvent, GsmEvent, ResetEvent
from skyguard.apps.gps.models import GPSEvent

print("=== ANÁLISIS DE EVENTOS LEGACY ===")
print(f"Events totales (legacy): {Event.objects.count()}")
print(f"IOEvents (legacy): {IOEvent.objects.count()}")
print(f"GsmEvents (legacy): {GsmEvent.objects.count()}")
print(f"ResetEvents (legacy): {ResetEvent.objects.count()}")
print(f"\nGPSEvents (nuevo): {GPSEvent.objects.count()}") 