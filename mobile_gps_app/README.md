# 📱 Falkon GPS Device Simulator

Convierte tu teléfono en un dispositivo GPS que se conecta al servidor Falkon y envía ubicaciones en tiempo real.

## 🎯 ¿Qué es esto?

Este proyecto te permite simular un dispositivo GPS real usando tu teléfono móvil. Envía datos de ubicación al servidor Falkon usando protocolos GPS estándar (Wialon, Concox, etc.).

## 🚀 Opciones de Uso

### Opción 1: Aplicación Web (PWA) - Más Simple
Una aplicación web que funciona en cualquier navegador móvil.

**Características:**
- ✅ Funciona en cualquier teléfono con navegador
- ✅ Acceso al GPS nativo del teléfono
- ✅ Interfaz moderna y responsive
- ❌ Solo simula el protocolo (no conexión TCP real)

### Opción 2: Cliente Python - Más Completo
Un script de Python que realmente se conecta al servidor GPS.

**Características:**
- ✅ Conexión TCP real al servidor
- ✅ Protocolo GPS completo (Wialon)
- ✅ Funciona en Android con Termux
- ✅ GPS real + ubicación por IP + datos simulados

## 📋 Protocolos Soportados

Tu servidor Falkon soporta estos protocolos en los siguientes puertos:

| Protocolo | Puerto | Descripción |
|-----------|--------|-------------|
| **Wialon** | 20332 | Protocolo simple y confiable (Recomendado) |
| Concox | 55300 | Para dispositivos Concox |
| Meiligao | 62000 | Para dispositivos Meiligao |
| Satellite | 15557 | Comunicación satelital |

## 🌐 Opción 1: Aplicación Web (PWA)

### Instalación
1. Abre tu navegador móvil
2. Ve a: `http://TU_SERVIDOR_IP/mobile_gps_app/`
3. El navegador te pedirá permisos de ubicación - acepta
4. Opcionalmente, agrega la app a tu pantalla de inicio

### Uso
1. **Configurar Servidor:**
   - IP del servidor: La IP donde está corriendo Falkon
   - Puerto: 20332 (Wialon recomendado)
   - IMEI: Un número único de 15 dígitos
   - Contraseña: La contraseña del dispositivo

2. **Conectar:**
   - Presiona "Conectar"
   - La app comenzará a simular el protocolo GPS

3. **Enviar Ubicaciones:**
   - Presiona "Enviar Ubicación" manualmente
   - O deja que se envíe automáticamente cada 10 segundos

## 🐍 Opción 2: Cliente Python (Recomendado)

### Instalación en Android (Termux)

1. **Instalar Termux:**
   ```bash
   # Descarga Termux desde F-Droid o GitHub
   # NO uses Google Play (versión desactualizada)
   ```

2. **Configurar Termux:**
   ```bash
   # Actualizar paquetes
   pkg update && pkg upgrade
   
   # Instalar Python y dependencias
   pkg install python
   pkg install python-pip
   
   # Instalar librerías necesarias
   pip install requests
   
   # Para acceso completo al GPS (opcional)
   pkg install termux-api
   ```

3. **Descargar y configurar:**
   ```bash
   # Crear directorio
   mkdir falkon-gps
   cd falkon-gps
   
   # Descargar archivos (copia el contenido manualmente)
   # gps_client.py
   # gps_config.json
   ```

### Instalación en PC/Laptop

```bash
# Clonar archivos
git clone [tu-repo] falkon-gps
cd falkon-gps/mobile_gps_app

# Instalar dependencias
pip install requests

# Ejecutar
python gps_client.py
```

### Configuración

Edita `gps_config.json`:

```json
{
    "host": "192.168.1.100",     // IP de tu servidor Falkon
    "port": 20332,               // Puerto Wialon
    "imei": "123456789012345",   // IMEI único (15 dígitos)
    "password": "123456",        // Contraseña del dispositivo
    "interval": 10,              // Segundos entre envíos
    "protocol": "wialon",        // Protocolo a usar
    "device_name": "Mi Telefono GPS",
    "auto_register": true
}
```

### Uso

```bash
# Ejecutar cliente GPS
python gps_client.py
```

El cliente intentará obtener ubicación de:
1. **GPS nativo de Android** (si está en Termux)
2. **Ubicación por IP** (aproximada)
3. **Datos simulados** (para pruebas)

## 🛠️ Configuración del Servidor

### 1. Verificar que los servidores GPS estén corriendo

```bash
# En tu servidor Falkon
cd /path/to/skyguard
python manage.py shell

# En el shell de Django
from skyguard.apps.gps.servers.server_manager import GPSServerManager
manager = GPSServerManager()
status = manager.get_server_status()
print(status)
```

### 2. Iniciar servidores GPS

```bash
# Método 1: Comando de Django
python manage.py runserver_gps

# Método 2: Programáticamente
from skyguard.apps.gps.servers.server_manager import start_gps_servers
start_gps_servers()
```

### 3. Crear dispositivo en la base de datos

```python
# En Django shell
from skyguard.apps.gps.models import GPSDevice

device = GPSDevice.objects.create(
    imei='123456789012345',
    name='Mi Telefono GPS',
    device_type='mobile',
    is_active=True
)
print(f"Dispositivo creado: {device.id}")
```

## 🔧 Troubleshooting

### Problemas de Conexión

1. **"Connection refused"**
   ```bash
   # Verificar que el servidor esté corriendo
   netstat -tlnp | grep 20332
   
   # Verificar firewall
   sudo ufw allow 20332
   ```

2. **"Permission denied" (GPS)**
   ```bash
   # En Termux
   termux-setup-storage
   
   # Verificar permisos en Android
   # Configuración > Apps > Termux > Permisos > Ubicación
   ```

3. **"Module not found"**
   ```bash
   # Instalar dependencias faltantes
   pip install requests
   pkg install termux-api  # Solo en Termux
   ```

### Verificar que lleguen los datos

```bash
# En el servidor, monitorear logs
tail -f /path/to/logs/gps.log

# O en Django shell
from skyguard.apps.gps.models import GPSLocation
recent_locations = GPSLocation.objects.filter(
    device__imei='123456789012345'
).order_by('-timestamp')[:10]

for loc in recent_locations:
    print(f"{loc.timestamp}: {loc.position}")
```

## 📊 Protocolo Wialon (Detalles Técnicos)

### Paquete de Login
```
#L#[IMEI];[PASSWORD]\r\n
Ejemplo: #L#123456789012345;123456\r\n
```

### Paquete de Datos
```
#D#[DATE];[TIME];[LAT1];[LAT2];[LON1];[LON2];[SPEED];[COURSE];[HEIGHT];[SATS];[HDOP];[INPUTS];[OUTPUTS];[ADC];[IBUTTON];[PARAMS]\r\n

Ejemplo: #D#041223;143052;19;25.9560;99;7.9920;45;180;2240;8;1.0;0;0;0;;NA\r\n
```

### Campos:
- **DATE**: ddmmyy (041223 = 4 dic 2023)
- **TIME**: hhmmss (143052 = 14:30:52)
- **LAT1/LAT2**: Latitud en grados y minutos
- **LON1/LON2**: Longitud en grados y minutos
- **SPEED**: Velocidad en km/h
- **COURSE**: Rumbo en grados (0-360)
- **HEIGHT**: Altitud en metros
- **SATS**: Número de satélites

## 🌍 Ubicaciones de Prueba

Para pruebas, puedes usar estas coordenadas:

```json
{
    "cdmx": {"lat": 19.4326, "lon": -99.1332, "name": "Ciudad de México"},
    "madrid": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid"},
    "london": {"lat": 51.5074, "lon": -0.1278, "name": "Londres"},
    "tokyo": {"lat": 35.6762, "lon": 139.6503, "name": "Tokio"}
}
```

## 🔒 Seguridad

- Cambia el IMEI y contraseña por defecto
- Usa HTTPS cuando sea posible
- No expongas el servidor GPS a internet sin firewall
- Considera VPN para conexiones remotas

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs del servidor GPS
2. Verifica la conectividad de red
3. Confirma que los puertos estén abiertos
4. Valida la configuración del dispositivo en la base de datos

---

¡Tu teléfono ya puede actuar como un dispositivo GPS profesional! 🚀📱 