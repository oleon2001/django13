#!/usr/bin/env python3
"""
Script para implementar los endpoints CRUD faltantes para dispositivos GPS
Este script agrega las funcionalidades que faltan en el backend para que el frontend funcione.
"""

# ==========================================
# 1. VIEWS FALTANTES PARA AGREGAR A views.py
# ==========================================

CRUD_VIEWS = '''
# ==========================================
# DEVICE CRUD ENDPOINTS (AGREGAR A views.py)
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_device(request):
    """
    Crear nuevo dispositivo GPS desde el frontend.
    
    Expected payload:
    {
        "imei": "123456789012345",
        "name": "My GPS Device",
        "description": "Optional description"
    }
    """
    try:
        # Validar datos de entrada
        imei = request.data.get('imei')
        name = request.data.get('name')
        
        if not imei:
            return Response({'error': 'IMEI is required'}, status=400)
            
        # Validar formato IMEI
        try:
            imei_int = int(imei)
            if len(str(imei)) != 15:
                return Response({'error': 'IMEI must be exactly 15 digits'}, status=400)
        except ValueError:
            return Response({'error': 'IMEI must be numeric'}, status=400)
            
        # Verificar si el dispositivo ya existe
        if GPSDevice.objects.filter(imei=imei_int).exists():
            return Response({'error': 'Device with this IMEI already exists'}, status=409)
            
        # Crear el dispositivo
        device = GPSDevice.objects.create(
            imei=imei_int,
            name=name or f'Device_{imei}',
            owner=request.user,
            is_active=True,
            connection_status='OFFLINE',
            serial=0,  # Default value
            model=0,   # Unknown model
            software_version='----'
        )
        
        # Preparar respuesta
        device_data = {
            'id': device.id,
            'imei': device.imei,
            'name': device.name,
            'serial': device.serial,
            'model': device.model,
            'software_version': device.software_version,
            'route': device.route,
            'economico': device.economico,
            'position': None,  # No position initially
            'speed': device.speed,
            'course': device.course,
            'altitude': device.altitude,
            'odometer': device.odometer,
            'connection_status': device.connection_status,
            'current_ip': device.current_ip,
            'current_port': device.current_port,
            'last_connection': None,
            'last_heartbeat': None,
            'total_connections': device.total_connections,
            'created_at': device.created_at.isoformat(),
            'updated_at': device.updated_at.isoformat()
        }
        
        return Response(device_data, status=201)
        
    except Exception as e:
        return Response({'error': f'Internal server error: {str(e)}'}, status=500)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_device(request, imei):
    """
    Actualizar dispositivo GPS existente.
    
    Args:
        imei: IMEI del dispositivo a actualizar
        
    Expected payload:
    {
        "name": "Updated Name",
        "route": 92,
        "economico": 123
    }
    """
    try:
        # Buscar el dispositivo
        try:
            device = GPSDevice.objects.get(imei=imei)
        except GPSDevice.DoesNotExist:
            return Response({'error': 'Device not found'}, status=404)
            
        # Verificar permisos (solo el propietario o staff)
        if not request.user.is_staff and device.owner != request.user:
            return Response({'error': 'Permission denied'}, status=403)
            
        # Actualizar campos permitidos
        updateable_fields = ['name', 'route', 'economico', 'is_active']
        for field in updateable_fields:
            if field in request.data:
                setattr(device, field, request.data[field])
                
        device.save()
        
        # Preparar respuesta
        device_data = {
            'id': device.id,
            'imei': device.imei,
            'name': device.name,
            'serial': device.serial,
            'model': device.model,
            'software_version': device.software_version,
            'route': device.route,
            'economico': device.economico,
            'position': {
                'latitude': device.position.y,
                'longitude': device.position.x
            } if device.position else None,
            'speed': device.speed,
            'course': device.course,
            'altitude': device.altitude,
            'odometer': device.odometer,
            'connection_status': device.connection_status,
            'current_ip': device.current_ip,
            'current_port': device.current_port,
            'last_connection': device.last_connection.isoformat() if device.last_connection else None,
            'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
            'total_connections': device.total_connections,
            'created_at': device.created_at.isoformat(),
            'updated_at': device.updated_at.isoformat()
        }
        
        return Response(device_data)
        
    except Exception as e:
        return Response({'error': f'Internal server error: {str(e)}'}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_device(request, imei):
    """
    Eliminar dispositivo GPS.
    
    Args:
        imei: IMEI del dispositivo a eliminar
    """
    try:
        # Buscar el dispositivo
        try:
            device = GPSDevice.objects.get(imei=imei)
        except GPSDevice.DoesNotExist:
            return Response({'error': 'Device not found'}, status=404)
            
        # Verificar permisos (solo el propietario o staff)
        if not request.user.is_staff and device.owner != request.user:
            return Response({'error': 'Permission denied'}, status=403)
            
        # Guardar información para respuesta
        device_info = {
            'imei': device.imei,
            'name': device.name,
            'deleted_at': timezone.now().isoformat()
        }
        
        # Eliminar el dispositivo (esto también eliminará eventos y ubicaciones relacionadas)
        device.delete()
        
        return Response({
            'message': 'Device deleted successfully',
            'device': device_info
        })
        
    except Exception as e:
        return Response({'error': f'Internal server error: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_device_connection(request, imei):
    """
    Probar conectividad con un dispositivo GPS.
    
    Args:
        imei: IMEI del dispositivo a probar
    """
    try:
        # Buscar el dispositivo
        try:
            device = GPSDevice.objects.get(imei=imei)
        except GPSDevice.DoesNotExist:
            return Response({'error': 'Device not found'}, status=404)
            
        # Verificar el último heartbeat
        if device.last_heartbeat:
            time_since_heartbeat = timezone.now() - device.last_heartbeat
            if time_since_heartbeat.total_seconds() < 60:  # 1 minuto
                device.update_connection_status('ONLINE')
                return Response({
                    'success': True,
                    'message': 'Device is online',
                    'last_seen': device.last_heartbeat.isoformat(),
                    'status': 'ONLINE'
                })
                
        # Si no hay heartbeat reciente, marcar como offline
        device.update_connection_status('OFFLINE')
        return Response({
            'success': False,
            'message': 'Device appears to be offline',
            'last_seen': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
            'status': 'OFFLINE'
        })
        
    except Exception as e:
        return Response({'error': f'Internal server error: {str(e)}'}, status=500)
'''

# ==========================================
# 2. URLS FALTANTES PARA AGREGAR A urls.py
# ==========================================

NEW_URLS = '''
# ==========================================
# NUEVAS URLs PARA AGREGAR A urls.py
# ==========================================

# Device CRUD endpoints (AGREGAR DESPUÉS DE LA LÍNEA devices/)
path('devices/', views.list_devices, name='list_devices'),  # GET (ya existe)
path('devices/create/', views.create_device, name='create_device'),  # POST
path('devices/<int:imei>/', views.update_device, name='update_device'),  # PATCH
path('devices/<int:imei>/delete/', views.delete_device, name='delete_device'),  # DELETE
path('devices/<int:imei>/test/', views.test_device_connection, name='test_device_connection'),  # POST
'''

# ==========================================
# 3. AJUSTES AL FRONTEND
# ==========================================

FRONTEND_FIXES = '''
# ==========================================
# AJUSTES PARA deviceService.ts
# ==========================================

// Cambiar estos métodos en frontend/src/services/deviceService.ts:

createDevice: async (data: Partial<Device>): Promise<Device> => {
  const response = await api.post('/api/gps/devices/create/', data);
  return response.data;
},

updateDevice: async (imei: number, data: Partial<Device>): Promise<Device> => {
  const response = await api.patch(`/api/gps/devices/${imei}/`, data);
  return response.data;
},

deleteDevice: async (imei: number): Promise<void> => {
  await api.delete(`/api/gps/devices/${imei}/delete/`);
},

// NUEVO: Agregar método de test
testConnection: async (imei: number) => {
  const response = await api.post(`/api/gps/devices/${imei}/test/`);
  return response.data;
},
'''

# ==========================================
# 4. INSTRUCCIONES DE IMPLEMENTACIÓN
# ==========================================

IMPLEMENTATION_STEPS = '''
# ==========================================
# PASOS PARA IMPLEMENTAR LA SOLUCIÓN
# ==========================================

1. BACKEND - Agregar Views:
   • Abrir: skyguard/apps/gps/views.py
   • Agregar al final del archivo las funciones:
     - create_device()
     - update_device()
     - delete_device() 
     - test_device_connection()

2. BACKEND - Agregar URLs:
   • Abrir: skyguard/apps/gps/urls.py
   • Agregar las nuevas rutas en urlpatterns

3. FRONTEND - Ajustar URLs:
   • Abrir: frontend/src/services/deviceService.ts
   • Cambiar las URLs de los métodos CRUD

4. TESTING:
   • Reiniciar servidor Django
   • Reiniciar servidor React
   • Probar registro de dispositivo desde UI

5. VERIFICACIÓN:
   • ✅ Crear dispositivo desde frontend
   • ✅ Editar dispositivo
   • ✅ Eliminar dispositivo
   • ✅ Test de conectividad
'''

def main():
    print("🔧 Fix Device CRUD - Missing Backend Endpoints")
    print("=" * 60)
    
    print("\n📝 1. VIEWS TO ADD TO views.py:")
    print(CRUD_VIEWS)
    
    print("\n🌐 2. URLS TO ADD TO urls.py:")
    print(NEW_URLS)
    
    print("\n🎨 3. FRONTEND ADJUSTMENTS:")
    print(FRONTEND_FIXES)
    
    print("\n📋 4. IMPLEMENTATION STEPS:")
    print(IMPLEMENTATION_STEPS)
    
    print("\n🎯 SUMMARY:")
    print("The frontend has all the UI components but the backend is missing")
    print("the CRUD endpoints. Add the views and URLs above to fix the issue.")

if __name__ == "__main__":
    main() 