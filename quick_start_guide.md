# 🚀 Guía Rápida: PC como Dispositivo GPS - SkyGuard

## 📋 Resumen
Esta guía te permite configurar tu PC para que actúe como un dispositivo GPS y envíe la ubicación real al sistema SkyGuard.

## 🎯 ¿Qué lograrás?
- ✅ Tu PC aparecerá como un dispositivo GPS en el sistema
- ✅ Enviará ubicación real obtenida por IP/WiFi
- ✅ Se mostrará en tiempo real en el frontend
- ✅ Funcionará como cualquier dispositivo GPS físico

## 🚀 Inicio Rápido (5 minutos)

### 1. Configuración Automática
```bash
# Configurar PC como dispositivo GPS
python setup_pc_gps.py

# Esto creará:
# - Registro en base de datos
# - Archivo pc_gps_config.json
# - Script start_pc_gps.py
```

### 2. Iniciar Sistema Completo
```bash
# Opción A: Sistema completo automático
python start_complete_system.py

# Opción B: Manual (en terminales separadas)
python start_gps_server.py     # Terminal 1
python start_pc_gps.py         # Terminal 2
cd frontend && npm start       # Terminal 3
```

### 3. Verificar Funcionamiento
```bash
# Ver dispositivo registrado
python test_mi_celular.py

# Abrir frontend
# http://localhost:3000
```

## 📂 Archivos Principales

### Configuración
- `pc_gps_config.json` - Configuración del simulador
- `setup_pc_gps.py` - Configuración automática
- `start_complete_system.py` - Inicio de todo el sistema

### Simulador GPS
- `pc_gps_simulator.py` - Simulador principal
- `start_pc_gps.py` - Script de inicio rápido

### Servicios del Sistema
- `start_gps_server.py` - Servidor GPS (puerto 20332)
- `start_bluetooth_server.py` - Servidor Bluetooth
- `start_gps_monitor.py` - Monitor de dispositivos

## 🔧 Configuración Detallada

### Archivo `pc_gps_config.json`
```json
{
    "host": "localhost",
    "port": 20332,
    "imei": "PC123456789012345",
    "device_name": "PC-GPS-Simulator",
    "interval": 10,
    "use_real_location": true,
    "debug": true
}
```

### Métodos de Ubicación
1. **IP Geolocation** - Más confiable (~5km precisión)
2. **WiFi Scanning** - Escaneo de redes WiFi (~100m precisión)
3. **Mock Realistic** - Ubicaciones simuladas realistas

## 🌐 URLs del Sistema

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:3000 | Interfaz principal |
| Backend API | http://localhost:8000 | API REST |
| Admin Django | http://localhost:8000/admin | Panel administrativo |
| GPS Mobile App | http://localhost:8000/mobile_gps_app/ | App móvil |

## 📊 Monitoreo y Verificación

### Verificar Dispositivo
```bash
# Ver información del dispositivo PC
python -c "
import os, django, sys
sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'skyguard.settings'
django.setup()
from skyguard.apps.gps.models.device import GPSDevice
device = GPSDevice.objects.filter(imei__startswith='PC').first()
if device:
    print(f'Dispositivo: {device.name}')
    print(f'IMEI: {device.imei}')
    print(f'Estado: {device.connection_status}')
    print(f'Última conexión: {device.last_connection}')
else:
    print('No se encontró dispositivo PC')
"
```

### Ver Logs en Tiempo Real
```bash
# Logs del sistema
tail -f django.log

# Logs del simulador GPS
python pc_gps_simulator.py  # con debug=true
```

### Verificar Conexiones
```bash
# Ver puertos GPS activos
netstat -tlnp | grep 20332

# Probar conexión al servidor
telnet localhost 20332
```

## 🔍 Solución de Problemas

### Problema: "No se puede conectar al servidor"
```bash
# Verificar que el servidor GPS esté corriendo
python start_gps_server.py

# Verificar puerto
netstat -tlnp | grep 20332
```

### Problema: "Dispositivo no aparece en frontend"
```bash
# Verificar registro en BD
python test_mi_celular.py

# Re-registrar dispositivo
python setup_pc_gps.py
```

### Problema: "No obtiene ubicación real"
```bash
# Verificar conexión a internet
ping google.com

# Probar manualmente
python -c "
import requests
r = requests.get('http://ip-api.com/json/')
print(r.json())
"
```

### Problema: "Frontend no carga"
```bash
# Verificar Node.js
node --version
npm --version

# Reinstalar dependencias
cd frontend
npm install
npm start
```

## 📱 Simulación de Movimiento

### Configuración de Movimiento Realista
```json
{
    "movement_simulation": {
        "enabled": true,
        "max_speed": 80,
        "realistic_paths": true,
        "city_bounds": {
            "north": 19.5,
            "south": 19.3,
            "east": -99.0,
            "west": -99.3
        }
    }
}
```

### Rutas Predefinidas
El simulador incluye rutas realistas:
- 🏙️ Centro de Ciudad de México
- 🏢 Santa Fe (zona empresarial)
- 🏛️ Polanco
- 🌆 Guadalajara
- 🏭 Monterrey

## 🎛️ Comandos Avanzados

### Simulador con Parámetros Personalizados
```bash
# Intervalo personalizado
python pc_gps_simulator.py --interval 5

# Servidor remoto
python pc_gps_simulator.py --host 192.168.1.100

# Modo debug completo
python pc_gps_simulator.py --debug --verbose
```

### Múltiples Dispositivos PC
```bash
# Crear múltiples configuraciones
cp pc_gps_config.json pc_gps_config_2.json
# Editar IMEI y nombre en el segundo archivo

# Ejecutar múltiples simuladores
python pc_gps_simulator.py pc_gps_config.json &
python pc_gps_simulator.py pc_gps_config_2.json &
```

## 🔐 Seguridad y Permisos

### Permisos Necesarios
- **Windows**: Acceso a WiFi y red
- **Linux**: Puede requerir sudo para iwlist
- **macOS**: Permisos de ubicación del sistema

### Configuración de Firewall
```bash
# Permitir puerto GPS (si es necesario)
# Windows
netsh advfirewall firewall add rule name="GPS Server" dir=in action=allow protocol=TCP localport=20332

# Linux (ufw)
sudo ufw allow 20332

# Linux (iptables)
sudo iptables -A INPUT -p tcp --dport 20332 -j ACCEPT
```

## 📈 Métricas y Estadísticas

### Ver Estadísticas del Dispositivo
```bash
python -c "
import os, django, sys
sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'skyguard.settings'
django.setup()
from skyguard.apps.gps.models.device import GPSDevice
from skyguard.apps.gps.models.event import GPSEvent
device = GPSDevice.objects.filter(imei__startswith='PC').first()
if device:
    events = GPSEvent.objects.filter(device=device).count()
    print(f'Eventos GPS: {events}')
    last_event = GPSEvent.objects.filter(device=device).last()
    if last_event:
        print(f'Última ubicación: {last_event.latitude}, {last_event.longitude}')
        print(f'Último evento: {last_event.timestamp}')
"
```

## 🎯 Casos de Uso

### 1. Desarrollo y Pruebas
- Probar el sistema sin dispositivos físicos
- Simular múltiples vehículos
- Verificar alertas y geofences

### 2. Demostración
- Mostrar el sistema en funcionamiento
- Presentaciones a clientes
- Capacitación de usuarios

### 3. Monitoreo Personal
- Rastrear tu PC como si fuera un vehículo
- Monitoreo de equipos de trabajo
- Seguimiento de laptops empresariales

## 📞 Soporte

### Logs de Debug
```bash
# Habilitar debug completo
export DJANGO_DEBUG=True
export GPS_DEBUG=True

# Ejecutar con logs detallados
python pc_gps_simulator.py 2>&1 | tee gps_debug.log
```

### Información del Sistema
```bash
# Generar reporte del sistema
python -c "
import platform, sys, os
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Directorio: {os.getcwd()}')
print(f'Variables: {dict(os.environ)}' if 'DEBUG' in os.environ else 'Variables: OK')
"
```

---

## ✅ Checklist de Verificación

- [ ] Python 3.7+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos migrada (`python manage.py migrate`)
- [ ] Dispositivo PC registrado (`python setup_pc_gps.py`)
- [ ] Servidor GPS corriendo (`python start_gps_server.py`)
- [ ] Simulador PC corriendo (`python start_pc_gps.py`)
- [ ] Frontend accesible (http://localhost:3000)
- [ ] Dispositivo visible en el mapa
- [ ] Ubicación actualizándose en tiempo real

¡Listo! Tu PC ahora funciona como un dispositivo GPS completo en el sistema SkyGuard. 🎉 