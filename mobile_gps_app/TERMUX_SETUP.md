# 🔧 Guía de Configuración de Termux para Falkon GPS

## Problema: "termux: API is not yet available"

Este error ocurre cuando Termux no puede acceder a las APIs del sistema Android.

## Solución Paso a Paso

### 1. Instalación Correcta

**❌ Evitar Google Play Store** (versión desactualizada)

**✅ Instalar desde fuentes oficiales:**
- **F-Droid**: https://f-droid.org/packages/com.termux/
- **GitHub**: https://github.com/termux/termux-app/releases

Necesitas **DOS** aplicaciones:
1. **Termux** (terminal principal)
2. **Termux:API** (acceso a APIs del sistema)

### 2. Configuración Inicial

```bash
# 1. Actualizar repositorios
pkg update && pkg upgrade

# 2. Instalar Python y herramientas básicas
pkg install python
pkg install python-pip
pkg install git

# 3. Instalar Termux:API (paquete)
pkg install termux-api

# 4. Configurar acceso al almacenamiento
termux-setup-storage
```

### 3. Verificar Instalación

```bash
# Verificar que termux-api funciona
termux-location -h

# Si muestra ayuda, está funcionando
# Si da error, revisar permisos
```

### 4. Configurar Permisos

**En Android (fuera de Termux):**
1. Configuración → Aplicaciones → Termux → Permisos
2. Activar:
   - ✅ Ubicación
   - ✅ Almacenamiento
   - ✅ Teléfono (opcional)
   - ✅ Cámara (opcional)

**En Android (fuera de Termux):**
1. Configuración → Aplicaciones → Termux:API → Permisos
2. Activar todos los permisos disponibles

### 5. Instalar Dependencias del Proyecto

```bash
# Navegar al directorio del proyecto
cd /storage/emulated/0/falkon-gps  # O donde tengas el proyecto

# Instalar dependencias Python
pip install requests

# Instalar dependencias específicas de Android
pip install python-android-support
```

### 6. Solución de Problemas Comunes

#### Error: "termux-api command not found"
```bash
# Reinstalar termux-api
pkg uninstall termux-api
pkg install termux-api

# Verificar instalación
which termux-location
```

#### Error: "Permission denied"
```bash
# Configurar permisos de almacenamiento
termux-setup-storage

# Verificar permisos de ubicación
termux-location -p gps
```

#### Error: "No location provider available"
```bash
# Verificar GPS en el dispositivo
# Configuración → Ubicación → Activar GPS

# Probar con diferentes proveedores
termux-location -p network  # Wi-Fi/datos móviles
termux-location -p gps      # GPS puro
termux-location -p passive  # Modo pasivo
```

### 7. Configuración Específica para Falkon GPS

```bash
# Crear directorio de trabajo
mkdir -p ~/falkon-gps
cd ~/falkon-gps

# Configurar el archivo de configuración
cat > gps_config.json << 'EOF'
{
    "host": "192.168.1.XXX",
    "port": 20332,
    "imei": "123456789012345",
    "password": "123456",
    "interval": 10,
    "protocol": "wialon",
    "device_name": "Android GPS",
    "auto_register": true,
    "use_android_gps": true,
    "fallback_to_ip": true,
    "fallback_to_mock": true
}
EOF

# Copiar el script GPS client
# (Necesitas copiar gps_client.py a este directorio)
```

### 8. Probar la Configuración

```bash
# Probar acceso a ubicación
termux-location

# Ejecutar cliente GPS
python gps_client.py
```

### 9. Comandos Útiles para Diagnóstico

```bash
# Ver información del sistema
termux-info

# Probar todas las APIs disponibles
termux-api-help

# Verificar permisos específicos
termux-location -p gps -r once

# Ver logs de errores
logcat | grep -i termux
```

### 10. Alternativas si No Funciona

Si Termux:API sigue sin funcionar:

1. **Usar ubicación por IP** (menos precisa)
2. **Usar datos simulados** (para pruebas)
3. **Usar la versión web** (PWA en el navegador)

El cliente GPS de Falkon tiene soporte para múltiples fuentes de ubicación:
- Android GPS nativo (más preciso)
- Ubicación por IP (aproximada)
- Datos simulados (para pruebas)

### 11. Verificación Final

Si todo está correcto, deberías ver algo así:

```bash
$ python gps_client.py
✅ Permisos de ubicación solicitados
🔄 Conectando a 192.168.1.100:20332...
📤 Enviado login: #L#123456789012345;123456
📥 Respuesta del servidor: #AL#1
✅ ¡Conectado al servidor!
📍 Ubicación obtenida: android_gps (19.4326, -99.1332)
📤 Enviando ubicación...
✅ Ubicación enviada correctamente
```

### 12. Soporte Adicional

Si sigues teniendo problemas:
1. Verifica que ambas apps (Termux + Termux:API) estén instaladas
2. Reinicia el dispositivo
3. Verifica que el GPS esté activado en Android
4. Usa `adb logcat` para ver logs detallados
5. Considera usar la versión web como alternativa

---

¡Con esta configuración tu teléfono Android debería funcionar perfectamente como dispositivo GPS! 🚀📱 