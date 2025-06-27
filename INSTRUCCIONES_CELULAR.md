# 📱 CONECTAR TU CELULAR COMO DISPOSITIVO GPS

**IMEI: 352749380148144**

## 🚀 PASO A PASO - SOLUCIÓN DEL ERROR

Tu error se debía a que el modelo GPS usa `imei` como clave primaria en lugar de `id`. Ya está corregido.

### 1. **CAMBIAR PROTOCOLO** (IMPORTANTE)

Tu dispositivo está usando protocolo `concox` pero para celulares es mejor `wialon`:

```bash
# Cambiar de concox a wialon
python3 cambiar_protocolo.py
```

**Debería mostrar:**
```
✅ ¡Protocolo cambiado exitosamente!
📱 DETALLES DE TU DISPOSITIVO:
   • Nombre: celular oswaldo
   • IMEI: 352749380148144 (Clave primaria)
   • Protocolo: wialon ✅
   • Puerto para conectar: 20332
```

### 2. **VERIFICAR REGISTRO**

```bash
# Probar que todo esté bien
python3 test_mi_celular.py
```

### 3. **INICIAR SERVIDOR GPS**

```bash
# Iniciar servidor completo
python3 start_my_gps.py
```

O manualmente:
```bash
# Solo el servidor GPS
python3 start_gps_server.py
```

## 📱 CONECTAR TU CELULAR

### **Opción A: Aplicación Web (Recomendado)**

1. **En tu celular**, abrir navegador y ir a:
   ```
   http://[IP_DEL_SERVIDOR]/mobile_gps_app/index.html
   ```

2. **Configurar**:
   - **Host/IP**: `192.168.1.XXX` (la IP de tu PC)
   - **Puerto**: `20332`
   - **IMEI**: `352749380148144`
   - **Protocolo**: `Wialon`
   - **Contraseña**: `123456`

3. **Aceptar permisos** de ubicación cuando lo pida el navegador

4. **Presionar "Conectar GPS"**

### **Opción B: Cliente Python en Android**

1. **Instalar Termux** (desde F-Droid, NO Google Play)

2. **En Termux**:
   ```bash
   pkg update && pkg upgrade
   pkg install python python-pip termux-api
   pip install requests
   ```

3. **Configurar permisos**:
   - Settings → Apps → Termux → Permissions → Location ✅
   - Settings → Apps → Termux:API → Permissions → All ✅

4. **Copiar archivos** a Termux:
   - `mobile_gps_app/gps_client.py`
   - `mobile_gps_app/mi_celular_config.json`

5. **Ejecutar**:
   ```bash
   python gps_client.py mi_celular_config.json
   ```

### **Opción C: App GPS Comercial**

Cualquier app que soporte protocolo Wialon:
- **GPS Tracker for Wialon**
- **Ruhavik** (by Gurtam)
- **Mapon GPS**

**Configuración**:
- Server: `[IP_DEL_SERVIDOR]`
- Port: `20332`
- Device ID: `352749380148144`
- Password: `123456`

## 🔧 ENCONTRAR IP DEL SERVIDOR

```bash
# En Linux/WSL
ip addr show | grep "inet 192"

# En Windows
ipconfig | find "192.168"

# Ejemplo de resultado: 192.168.1.100
```

## ✅ VERIFICAR CONEXIÓN

### **En el Servidor:**
```bash
# Ver conexiones GPS
netstat -tlnp | grep 20332

# Ver logs en tiempo real
tail -f logs/django.log
```

### **En el Frontend:**
1. Ir a `http://localhost:3000`
2. Dashboard → Buscar "Mi Celular GPS"
3. Verificar ubicación en mapa

### **Mensajes de Éxito:**
```
📱 Nueva conexión desde: (192.168.1.XXX, puerto)
✅ Login exitoso para IMEI: 352749380148144
📍 Datos GPS recibidos
💗 Ping recibido
```

## 🔥 CONFIGURACIÓN ESPECÍFICA PARA TI

**Archivo: `mobile_gps_app/mi_celular_config.json`**
```json
{
    "host": "192.168.1.100",
    "port": 20332,
    "imei": "352749380148144",
    "password": "123456",
    "protocol": "wialon",
    "device_name": "Mi Celular GPS Real"
}
```

**⚠️ CAMBIAR** `192.168.1.100` por la IP real de tu servidor.

## 🐛 TROUBLESHOOTING

### **Error "Connection refused"**
```bash
# Verificar que el puerto esté abierto
netstat -tlnp | grep 20332

# Si no hay respuesta, iniciar servidor:
python3 start_gps_server.py
```

### **Error de permisos GPS**
- En Android: Settings → Location → ON
- En navegador: Permitir ubicación cuando lo pida
- En Termux: Verificar permisos de ambas apps

### **No aparece en el frontend**
```bash
# Verificar que el dispositivo esté en la DB
python3 test_mi_celular.py

# Verificar usuario logueado en frontend
# Dispositivo debe pertenecer al usuario actual
```

### **Datos GPS no se actualizan**
- Verificar que el GPS esté activado
- Salir al exterior si estás en interior
- Verificar conexión de red
- Revisar logs del servidor

## 📞 SOPORTE

Si tienes problemas:

1. **Ejecutar diagnóstico completo**:
   ```bash
   python3 test_mi_celular.py
   ```

2. **Ver logs detallados**:
   ```bash
   python3 start_gps_server.py
   # Intentar conectar desde celular y ver mensajes
   ```

3. **Verificar firewall**:
   ```bash
   sudo ufw allow 20332/tcp
   ```

---

**🎯 Tu celular con IMEI 352749380148144 ya está registrado y listo para conectarse al sistema SkyGuard como un dispositivo GPS real.** 