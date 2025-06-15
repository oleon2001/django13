# 🔧 Fix: Endpoints CRUD Faltantes para Dispositivos

## 🚨 PROBLEMA IDENTIFICADO

El **frontend tiene UI completa** pero el **backend NO tiene los endpoints CRUD** necesarios.

### ❌ Endpoints que faltan:
- `POST /api/gps/devices/` - Crear dispositivo
- `PATCH /api/gps/devices/{imei}/` - Actualizar dispositivo  
- `DELETE /api/gps/devices/{imei}/` - Eliminar dispositivo

---

## 🛠️ SOLUCIÓN INMEDIATA

### 1. 📝 Agregar Views al Backend

**Archivo:** `skyguard/apps/gps/views.py`

**Agregar al final del archivo:**

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_device(request):
    """Crear nuevo dispositivo GPS desde el frontend."""
    try:
        imei = request.data.get('imei')
        name = request.data.get('name')
        
        if not imei or len(str(imei)) != 15:
            return Response({'error': 'IMEI must be 15 digits'}, status=400)
            
        if GPSDevice.objects.filter(imei=int(imei)).exists():
            return Response({'error': 'Device already exists'}, status=409)
            
        device = GPSDevice.objects.create(
            imei=int(imei),
            name=name or f'Device_{imei}',
            owner=request.user,
            is_active=True,
            connection_status='OFFLINE'
        )
        
        return Response({
            'id': device.id,
            'imei': device.imei,
            'name': device.name,
            'connection_status': device.connection_status,
            'created_at': device.created_at.isoformat(),
            'updated_at': device.updated_at.isoformat()
        }, status=201)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_device(request, imei):
    """Actualizar dispositivo GPS existente."""
    try:
        device = GPSDevice.objects.get(imei=imei)
        
        # Actualizar campos permitidos
        if 'name' in request.data:
            device.name = request.data['name']
        if 'route' in request.data:
            device.route = request.data['route']
        if 'economico' in request.data:
            device.economico = request.data['economico']
            
        device.save()
        
        return Response({
            'id': device.id,
            'imei': device.imei,
            'name': device.name,
            'route': device.route,
            'economico': device.economico,
            'updated_at': device.updated_at.isoformat()
        })
        
    except GPSDevice.DoesNotExist:
        return Response({'error': 'Device not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_device(request, imei):
    """Eliminar dispositivo GPS."""
    try:
        device = GPSDevice.objects.get(imei=imei)
        device_name = device.name
        device.delete()
        
        return Response({
            'message': f'Device {device_name} deleted successfully'
        })
        
    except GPSDevice.DoesNotExist:
        return Response({'error': 'Device not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
```

### 2. 🌐 Agregar URLs al Backend

**Archivo:** `skyguard/apps/gps/urls.py`

**Modificar urlpatterns para incluir:**

```python
urlpatterns = [
    # Device CRUD endpoints
    path('devices/', views.list_devices, name='list_devices'),  # GET (ya existe)
    path('devices/create/', views.create_device, name='create_device'),  # POST (NUEVO)
    path('devices/<int:imei>/', views.update_device, name='update_device'),  # PATCH (NUEVO)
    path('devices/<int:imei>/delete/', views.delete_device, name='delete_device'),  # DELETE (NUEVO)
    
    # ... resto de URLs existentes ...
]
```

### 3. 🎨 Ajustar Frontend URLs

**Archivo:** `frontend/src/services/deviceService.ts`

**Cambiar estos métodos:**

```typescript
createDevice: async (data: Partial<Device>): Promise<Device> => {
  const response = await api.post('/api/gps/devices/create/', data);  // Cambiar URL
  return response.data;
},

updateDevice: async (imei: number, data: Partial<Device>): Promise<Device> => {
  const response = await api.patch(`/api/gps/devices/${imei}/`, data);  // Ya correcta
  return response.data;
},

deleteDevice: async (imei: number): Promise<void> => {
  await api.delete(`/api/gps/devices/${imei}/delete/`);  // Cambiar URL
},
```

---

## 🧪 Testing

### 1. Reiniciar Servidores
```bash
# Backend
wsl -e bash -c "cd /mnt/c/Users/oswaldo/Desktop/django13 && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"

# Frontend
cd frontend && npm start
```

### 2. Probar Funcionalidad
1. ✅ Ir a `/devices` en el frontend
2. ✅ Hacer clic en "Add Device"
3. ✅ Llenar formulario con IMEI válido
4. ✅ Verificar que se crea correctamente
5. ✅ Probar editar y eliminar

---

## 🎯 RESULTADO ESPERADO

Después de implementar estos cambios:

- ✅ **Crear dispositivos** desde el frontend funcionará
- ✅ **Editar dispositivos** funcionará
- ✅ **Eliminar dispositivos** funcionará
- ✅ **Listado de dispositivos** ya funciona
- ✅ **Recepción de datos GPS** ya funciona

---

## 🔍 Verificación Rápida

Para verificar que los endpoints existen después de la implementación:

```bash
# Test crear dispositivo
curl -X POST http://localhost:8000/api/gps/devices/create/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"imei": "123456789012345", "name": "Test Device"}'

# Test actualizar dispositivo  
curl -X PATCH http://localhost:8000/api/gps/devices/123456789012345/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Test eliminar dispositivo
curl -X DELETE http://localhost:8000/api/gps/devices/123456789012345/delete/ \
  -H "Authorization: Bearer <token>"
```

**¡Con estos cambios, la gestión de dispositivos desde el frontend funcionará completamente!** 🚀 