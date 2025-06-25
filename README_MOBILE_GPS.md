# 🚗 GPS Móvil SkyGuard

## Descripción

Este sistema permite usar tu celular como dispositivo GPS y conectarlo a la aplicación SkyGuard para tracking en tiempo real. Es perfecto para pruebas, desarrollo y casos de uso donde necesitas un GPS real sin hardware especializado.

## 🎯 Características

- ✅ **GPS Real**: Usa el GPS real de tu celular
- ✅ **Interfaz Web Móvil**: Control desde el navegador del celular
- ✅ **Integración SkyGuard**: Se conecta directamente al servidor Bluetooth
- ✅ **Envío Automático**: Actualización automática de posición
- ✅ **Múltiples Protocolos**: Soporte para diferentes formatos GPS
- ✅ **Tiempo Real**: Actualización en tiempo real en SkyGuard

## 🛠️ Requisitos

### Software
- Python 3.7+
- Django (ya instalado en el proyecto)
- Flask
- Requests

### Hardware
- Celular con GPS
- Conexión WiFi o datos móviles
- Computadora con SkyGuard ejecutándose

## 🚀 Instalación y Configuración

### 1. Verificar Dependencias

```bash
# Activar entorno virtual
source venv/bin/activate

# Verificar dependencias
pip install flask requests
```

### 2. Ejecutar Sistema Completo

```bash
# Ejecutar el sistema completo
python test_mobile_gps.py
```

Este comando:
- Inicia el servidor Bluetooth de SkyGuard
- Inicia la interfaz web móvil
- Muestra las instrucciones de uso
- Realiza pruebas de conexión

## 📱 Uso del Sistema

### Paso 1: Iniciar el Sistema

```bash
python test_mobile_gps.py
```

El sistema mostrará:
```
🚗 SKYGUARD GPS MÓVIL - SISTEMA DE PRUEBA
============================================================
✅ Servidor Bluetooth iniciado en puerto 50100
✅ Interfaz web iniciada en: http://192.168.1.100:5000
📱 Abre esta URL en tu celular para controlar el GPS
```

### Paso 2: Conectar desde el Celular

1. **Abrir Navegador**: En tu celular, abre el navegador web
2. **Ir a la URL**: Ve a la URL mostrada (ej: `http://192.168.1.100:5000`)
3. **Permitir Ubicación**: Cuando se solicite, permite acceso a la ubicación
4. **Conectar**: Haz clic en "Conectar" en la interfaz

### Paso 3: Enviar Posición GPS

#### Opción A: GPS Real (Recomendado)
1. Haz clic en "📍 Obtener Ubicación Actual"
2. El sistema obtendrá tu posición GPS real
3. Haz clic en "📡 Enviar Posición"

#### Opción B: Coordenadas Manuales
1. Ingresa las coordenadas manualmente:
   - **Latitud**: 19.4326 (ejemplo: Ciudad de México)
   - **Longitud**: -99.1332
   - **Velocidad**: 25.0 km/h
   - **Dirección**: 90.0 grados
2. Haz clic en "📡 Enviar Posición"

### Paso 4: Verificar en SkyGuard

1. Abre la aplicación SkyGuard
2. Ve al panel de dispositivos
3. Busca el dispositivo con IMEI: `123456789012345`
4. Verás la posición en tiempo real en el mapa

### Paso 5: Envío Automático (Opcional)

Para actualización automática:
1. Activa "Envío automático cada 30 segundos"
2. El GPS se actualizará automáticamente
3. Perfecto para tracking continuo

## 🔧 Componentes del Sistema

### 1. `mobile_gps_simulator.py`
Simulador de GPS que se conecta al servidor SkyGuard:
- Implementa el protocolo Bluetooth de SkyGuard
- Maneja login, ping y envío de posiciones
- Simula movimiento a lo largo de rutas

### 2. `mobile_gps_web_interface.py`
Interfaz web para controlar el GPS desde el celular:
- Servidor Flask con interfaz móvil responsive
- Geolocalización HTML5 para GPS real
- Envío manual y automático de posiciones

### 3. `start_bluetooth_server.py`
Gestor del servidor Bluetooth de SkyGuard:
- Inicia el servidor Bluetooth existente
- Maneja el ciclo de vida del servidor
- Monitoreo de estado y logs

### 4. `test_mobile_gps.py`
Script principal de prueba:
- Orquesta todos los componentes
- Verifica dependencias
- Muestra instrucciones de uso

## 📊 Protocolo de Comunicación

El sistema usa el protocolo Bluetooth existente de SkyGuard:

### Paquete de Login
```
PKTID_LOGIN (1 byte) + IMEI (8 bytes) + MAC (6 bytes)
```

### Paquete de Ping (Posición)
```
PKTID_PING (1 byte) + timestamp (4 bytes) + lat (4 bytes) + 
lon (4 bytes) + speed (1 byte) + inputs (1 byte)
```

### Respuesta del Servidor
```
RSPID_SESSION (1 byte) + session_id (4 bytes) + CMDID_ACK (1 byte)
```

## 🎮 Casos de Uso

### 1. Pruebas de Desarrollo
```bash
# Simular movimiento en una ruta
python mobile_gps_simulator.py
```

### 2. Testing de SkyGuard
```bash
# Probar diferentes protocolos GPS
python test_mobile_gps.py
```

### 3. Demostración en Vivo
```bash
# Usar GPS real del celular
# Abrir interfaz web y conectar
```

### 4. Monitoreo Remoto
```bash
# Envío automático cada 30 segundos
# Tracking continuo sin intervención
```

## 🔍 Solución de Problemas

### Error: "No se pudo conectar al servidor"
- Verifica que el servidor Bluetooth esté ejecutándose
- Comprueba que el puerto 50100 esté disponible
- Revisa los logs del servidor

### Error: "Geolocalización no soportada"
- Asegúrate de usar HTTPS en producción
- Verifica permisos de ubicación en el navegador
- Usa coordenadas manuales como alternativa

### Error: "Timeout en respuesta del ping"
- Verifica la conectividad de red
- Comprueba que el servidor esté respondiendo
- Revisa la configuración de firewall

### El dispositivo no aparece en SkyGuard
- Verifica que el IMEI sea correcto (123456789012345)
- Comprueba que el servidor esté procesando los datos
- Revisa los logs de Django

## 🚀 Optimizaciones

### Para Mejor Rendimiento
1. **Reducir frecuencia de envío**: Cambia el intervalo de 30 a 60 segundos
2. **Usar WiFi**: Mejor estabilidad que datos móviles
3. **Optimizar precisión**: Usar `enableHighAccuracy: true`

### Para Producción
1. **HTTPS**: Configurar certificado SSL
2. **Autenticación**: Agregar sistema de login
3. **Logs**: Implementar logging detallado
4. **Monitoreo**: Agregar métricas de rendimiento

## 📈 Métricas y Monitoreo

### Métricas Disponibles
- **Tiempo de respuesta**: Latencia del servidor
- **Precisión GPS**: Exactitud de las coordenadas
- **Tasa de éxito**: Porcentaje de envíos exitosos
- **Uso de batería**: Impacto en el celular

### Logs del Sistema
```bash
# Ver logs del servidor Bluetooth
tail -f skyguard/apps/tracking/BluServer.log

# Ver logs de Django
python manage.py runserver --verbosity=2
```

## 🔐 Seguridad

### Consideraciones
- **Red local**: Usar solo en redes confiables
- **Firewall**: Configurar reglas de firewall apropiadas
- **IMEI**: Cambiar el IMEI por defecto en producción
- **Autenticación**: Implementar sistema de autenticación

### Recomendaciones
1. Usar solo en redes privadas
2. Cambiar credenciales por defecto
3. Implementar rate limiting
4. Monitorear acceso no autorizado

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios
4. Agrega tests
5. Envía un pull request

## 📄 Licencia

Este proyecto está bajo la misma licencia que SkyGuard.

## 🆘 Soporte

Para soporte técnico:
- Revisa la documentación
- Consulta los logs del sistema
- Abre un issue en el repositorio

---

 