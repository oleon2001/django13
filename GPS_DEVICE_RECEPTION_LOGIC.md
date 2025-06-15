# 🛰️ Lógica Completa de Recepción de Dispositivos GPS

## 📋 Resumen del Flujo

```
Hardware GPS → Internet → Endpoint Verificación → Autenticación → Validación → Procesamiento → Base de Datos
```

## 🔄 1. PUNTOS DE ENTRADA DISPONIBLES

### A. Endpoints HTTP (Actual)
```bash
# Endpoint simple para ubicaciones
POST /api/gps/location/
Content-Type: application/x-www-form-urlencoded
Body: imei=123456789012345&latitude=-34.6037&longitude=-58.3816&speed=50

# Endpoint completo para eventos (con autenticación)
POST /api/gps/event/
Headers: X-Device-Token: tu_token_secreto
Body: imei=123456789012345&type=LOCATION&latitude=-34.6037&longitude=-58.3816&speed=50&course=90
```

### B. Servidores Socket (Protocolos Binarios)
```bash
# Concox Protocol
UDP/TCP Port: 8841
Protocol: Binario Concox

# Meiligao Protocol  
UDP Port: 9955
Protocol: Binario Meiligao

# SAT Protocol
TCP Port: 8080
Protocol: Binario SAT
```

## 🔐 2. VERIFICACIÓN DE DISPOSITIVO

### Paso 1: Validación de IMEI
```python
def verify_device_exists(imei: str):
    # 1. Validar formato IMEI (15 dígitos numéricos)
    if not imei.isdigit() or len(imei) != 15:
        return False, "IMEI format invalid"
    
    # 2. Buscar en base de datos
    device = GPSDevice.objects.filter(imei=int(imei)).first()
    if not device:
        return False, "Device not found in system"
    
    # 3. Verificar estado activo
    if not device.is_active:
        return False, "Device is inactive"
    
    return True, device
```

### Paso 2: Estados de Dispositivo
- ✅ **REGISTERED**: Dispositivo registrado en el sistema
- ✅ **ACTIVE**: Dispositivo activo y autorizado para enviar datos
- ❌ **INACTIVE**: Dispositivo deshabilitado temporalmente
- ❌ **BLOCKED**: Dispositivo bloqueado permanentemente
- ⚠️ **PENDING**: Dispositivo pendiente de activación

## 🔒 3. AUTENTICACIÓN

### Métodos de Autenticación Soportados:

#### A. Token en Headers (Recomendado)
```http
POST /api/gps/event/
X-Device-Token: your_secret_token_here
Content-Type: application/x-www-form-urlencoded
```

#### B. Token en POST Data (Compatibilidad)
```http
POST /api/gps/event/
Content-Type: application/x-www-form-urlencoded

imei=123456789012345&token=your_secret_token&latitude=-34.6037...
```

#### C. Whitelist por IP (Opcional)
```python
# En settings.py
GPS_DEVICE_IP_WHITELIST = [
    '192.168.1.100',  # IP del dispositivo GPS
    '10.0.0.50',      # Otra IP autorizada
]
```

## ✅ 4. VALIDACIÓN DE DATOS GPS

### Campos Requeridos Mínimos:
```json
{
    "imei": "123456789012345",     // IMEI del dispositivo (15 dígitos)
    "latitude": -34.6037,          // Latitud (-90 a 90)
    "longitude": -58.3816          // Longitud (-180 a 180)
}
```

### Campos Opcionales:
```json
{
    "speed": 50.5,                 // Velocidad en km/h
    "course": 90.0,                // Rumbo en grados (0-360)
    "altitude": 100.0,             // Altitud en metros
    "timestamp": "2025-01-15T10:30:00Z",  // Timestamp ISO o Unix
    "satellites": 8,               // Número de satélites
    "accuracy": 5.0,               // Precisión en metros
    "battery": 85.5,               // Nivel de batería (%)
    "signal": 75,                  // Intensidad de señal (%)
    "type": "LOCATION",            // Tipo de evento
    "odometer": 15000.5            // Odómetro en km
}
```

### Validaciones Aplicadas:
```python
# Coordenadas válidas
-90 <= latitude <= 90
-180 <= longitude <= 180

# Velocidad razonable
0 <= speed <= 300  # km/h

# Rumbo válido
0 <= course <= 360  # grados

# Número de satélites
0 <= satellites <= 24
```

## ⚙️ 5. PROCESAMIENTO DE DATOS

### Flujo de Procesamiento:
```python
def process_device_data(device, validated_data):
    # 1. Crear punto geográfico
    position = Point(longitude, latitude)
    
    # 2. Crear registro de ubicación
    location = GPSLocation.objects.create(
        device=device,
        position=position,
        speed=validated_data['speed'],
        timestamp=validated_data['timestamp'],
        # ... otros campos
    )
    
    # 3. Crear evento de seguimiento
    event = GPSEvent.objects.create(
        device=device,
        type=validated_data['event_type'],
        position=position,
        timestamp=validated_data['timestamp'],
        # ... otros campos
    )
    
    # 4. Actualizar estado del dispositivo
    device.position = position
    device.connection_status = 'ONLINE'
    device.last_heartbeat = timezone.now()
    device.save()
    
    return location, event
```

## 📡 6. CONFIGURACIÓN DEL HARDWARE

### Para Dispositivos HTTP (Más común):
```json
{
    "server_url": "https://tu-servidor.com/api/gps/event/",
    "method": "POST",
    "headers": {
        "X-Device-Token": "tu_token_secreto"
    },
    "interval": 30,  // segundos entre envíos
    "format": "form-data"
}
```

### Ejemplo de configuración Concox:
```
Server: tu-servidor.com
Port: 8841
Protocol: TCP
IMEI: 123456789012345
Interval: 30s
```

### Ejemplo de configuración Meiligao:
```
Server: tu-servidor.com  
Port: 9955
Protocol: UDP
IMEI: 123456789012345
Heartbeat: 60s
```

## 🔍 7. VERIFICACIÓN Y DIAGNÓSTICO

### A. Verificar que el endpoint existe:
```bash
# Test básico de conectividad
curl -X POST http://localhost:8000/api/gps/event/ \
  -H "X-Device-Token: tu_token" \
  -d "imei=123456789012345&latitude=-34.6037&longitude=-58.3816"
```

### B. Respuestas esperadas:
```json
// ✅ Éxito
{
    "status": "success",
    "device_id": 123,
    "timestamp": "2025-01-15T10:30:00Z",
    "position": {
        "latitude": -34.6037,
        "longitude": -58.3816
    }
}

// ❌ Error de autenticación
{
    "error": "Invalid authentication token",
    "status": 401
}

// ❌ Dispositivo no encontrado
{
    "error": "Device not found",
    "status": 404
}

// ❌ Datos inválidos
{
    "error": "Invalid latitude",
    "status": 400
}
```

## 🛠️ 8. IMPLEMENTACIÓN PRÁCTICA

### Paso 1: Registrar el dispositivo
```python
# En Django Admin o programáticamente
device = GPSDevice.objects.create(
    imei=123456789012345,
    name="Tracker Vehicle 001",
    is_active=True,
    owner=user
)
```

### Paso 2: Configurar token de autenticación
```python
# En settings.py
GPS_DEVICE_TOKEN = "tu_token_super_secreto_aqui"
```

### Paso 3: Configurar el hardware GPS
- **URL del servidor**: `https://tu-dominio.com/api/gps/event/`
- **Método**: POST
- **Token**: `tu_token_super_secreto_aqui`
- **Intervalo**: 30 segundos

### Paso 4: Monitorear recepción
```python
# Verificar últimos datos recibidos
device = GPSDevice.objects.get(imei=123456789012345)
print(f"Last seen: {device.last_heartbeat}")
print(f"Position: {device.position}")
print(f"Status: {device.connection_status}")
```

## 🚨 9. TROUBLESHOOTING

### Problemas Comunes:

#### A. "Device not found"
```bash
# Solución: Registrar el dispositivo primero
python manage.py shell
>>> from skyguard.apps.gps.models import GPSDevice
>>> GPSDevice.objects.create(imei=123456789012345, name="Test Device")
```

#### B. "Invalid authentication token"
```bash
# Solución: Verificar token en settings.py
GPS_DEVICE_TOKEN = "token_correcto"
```

#### C. "Connection refused"
```bash
# Solución: Verificar que Django esté ejecutándose
python manage.py runserver 0.0.0.0:8000
```

#### D. "Invalid coordinates"
```bash
# Solución: Verificar formato de coordenadas
# Latitud: -90 a 90
# Longitud: -180 a 180
```

## 📊 10. MONITOREO EN TIEMPO REAL

### Endpoints de diagnóstico:
```bash
# Ver dispositivos activos
GET /api/gps/devices/

# Ver estado de conexión específico
GET /api/gps/devices/{imei}/status/

# Ver sesiones activas
GET /api/gps/sessions/active/
```

### Logs importantes:
```bash
# Ver logs de Django
tail -f django.log

# Buscar errores específicos
grep "GPS" django.log | grep "ERROR"
```

---

## 🎯 RESUMEN DE IMPLEMENTACIÓN

1. **✅ Hardware configurado** → URL + Token + Intervalo
2. **✅ Dispositivo registrado** → IMEI en base de datos + Activo
3. **✅ Endpoint disponible** → `/api/gps/event/` funcionando
4. **✅ Autenticación configurada** → Token válido
5. **✅ Datos siendo recibidos** → Logs + Base de datos actualizada

**¡Tu dispositivo GPS ya puede enviar datos al sistema!** 🚀 