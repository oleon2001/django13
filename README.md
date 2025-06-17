# SkyGuard GPS Tracking System

## Descripción General
SkyGuard es un sistema de monitoreo GPS que permite rastrear y gestionar dispositivos GPS en tiempo real. El sistema está diseñado con una arquitectura moderna que separa el frontend (React) del backend (Django) para una mejor escalabilidad y mantenimiento.

## Arquitectura del Sistema

### 1. Componentes Principales

#### Frontend (React)
- **URL Base**: `http://localhost:3000`
- **Características**:
  - Interfaz de usuario moderna y responsiva
  - Visualización de dispositivos en tiempo real
  - Panel de control para gestión de dispositivos
  - Mapa interactivo para visualización de ubicaciones
  - Gestión de usuarios y permisos

#### Backend (Django)
- **URL Base**: `http://localhost:8000/api/gps`
- **Características**:
  - API RESTful para gestión de dispositivos
  - Sistema de protocolos para comunicación GPS
  - Autenticación y autorización
  - Base de datos PostgreSQL con soporte geoespacial

### 2. Sistema de Protocolos GPS

El sistema implementa un patrón Factory para manejar diferentes protocolos GPS:

```
GPSProtocolHandler (Factory)
    │
    ├── ConcoxProtocolHandler
    ├── MeiligaoProtocolHandler
    └── WialonProtocolHandler
```

#### Características de los Protocol Handlers

1. **GPSProtocolHandler (Factory)**
   - Gestiona la creación de handlers específicos
   - Mapea protocolos a sus implementaciones
   - Proporciona interfaz común para todos los protocolos

2. **Protocol Handlers Específicos**
   Cada handler implementa:
   - `decode_packet`: Decodifica datos del dispositivo
   - `encode_command`: Codifica comandos para el dispositivo
   - `validate_packet`: Valida integridad de paquetes
   - `send_ping`: Prueba conexión y verifica ubicación

### 3. Flujo de Comunicación

#### Prueba de Conexión
1. **Inicio**
   ```python
   # Frontend envía solicitud
   POST /api/gps/devices/{imei}/test-connection/
   ```

2. **Procesamiento en Backend**
   ```python
   # 1. Obtener handler apropiado
   handler = GPSProtocolHandler().get_handler(device.protocol)
   
   # 2. Enviar comando de prueba
   result = handler.send_ping(device)
   ```

3. **Comunicación con Dispositivo**
   ```python
   # Envío de comando
   command = struct.pack('>BB', 0x78, 0x78)  # Start bits
   command += struct.pack('>B', 0x23)  # Protocol number
   # ... más bytes del comando
   ```

4. **Validación de Respuesta**
   - Verificación de respuesta
   - Decodificación de datos
   - Validación de coordenadas
   - Actualización de base de datos

### 4. Estructura de Datos

#### Dispositivo GPS
```python
class GPSDevice:
    imei: str              # Identificador único
    protocol: str          # Protocolo de comunicación
    ip_address: str        # Dirección IP
    port: int             # Puerto de comunicación
    last_known_position: Point  # Última ubicación
    last_known_position_time: datetime  # Timestamp
```

#### Respuesta de Prueba de Conexión
```python
{
    'success': bool,
    'response_time': float,
    'error_message': str,
    'position': Point,
    'timestamp': datetime
}
```

### 5. Manejo de Errores

El sistema implementa un manejo de errores robusto:

1. **Errores de Comunicación**
   - Timeout en conexión
   - No respuesta del dispositivo
   - Datos corruptos

2. **Errores de Validación**
   - Coordenadas inválidas
   - Datos de ubicación faltantes
   - Protocolo no soportado

3. **Errores de Sistema**
   - Errores de base de datos
   - Errores de permisos
   - Errores de configuración

### 6. Seguridad

#### Autenticación
- JWT (JSON Web Tokens)
- Tokens de refresco
- Expiración de sesiones

#### Autorización
- Roles de usuario
- Permisos por dispositivo
- Validación de acceso

#### Comunicación Segura
- Validación de protocolos
- Sanitización de datos
- Protección contra inyección

### 7. Logging y Monitoreo

El sistema implementa logging detallado:

```python
# Ejemplo de logs
[DEBUG] Iniciando prueba de conexión para dispositivo {imei}
[DEBUG] Enviando comando de heartbeat a {ip}:{port}
[DEBUG] Respuesta recibida del dispositivo {imei}
[ERROR] No se recibió respuesta del dispositivo {imei}
```

### 8. Requisitos del Sistema

#### Backend
- Python 3.8+
- Django 3.2+
- PostgreSQL 12+
- PostGIS 3.0+

#### Frontend
- Node.js 14+
- React 17+
- Material-UI 5+

### 9. Instalación

1. **Backend**
   ```bash
   # Crear entorno virtual
   python -m venv venv
   source venv/bin/activate
   
   # Instalar dependencias
   pip install -r requirements.txt
   
   # Configurar base de datos
   python manage.py migrate
   
   # Iniciar servidor
   python manage.py runserver
   ```

2. **Frontend**
   ```bash
   # Instalar dependencias
   npm install
   
   # Iniciar servidor de desarrollo
   npm start
   ```

### 10. Próximos Pasos

1. **Mejoras Planificadas**
   - Implementación de WebSocket para actualizaciones en tiempo real
   - Soporte para más protocolos GPS
   - Mejoras en la visualización de mapas
   - Sistema de alertas y notificaciones

2. **Optimizaciones**
   - Caché de ubicaciones
   - Compresión de datos
   - Mejoras en el rendimiento de consultas

### 11. Contribución

1. Fork el repositorio
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### 12. Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

Para soporte o consultas, por favor contactar a:
- Email: soporte@skyguard.com
- Sitio web: https://skyguard.com 