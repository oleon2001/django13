# 🚀 SkyGuard Backend Management System

Sistema completo de gestión automática del backend SkyGuard. Incluye scripts para iniciar, detener y monitorear todos los servicios del sistema de rastreo GPS.

## 📋 Servicios Incluidos

### 🏗️ **Infraestructura Base**
- **Redis Server** - Cache y message broker para Celery
- **PostgreSQL** - Base de datos principal del sistema

### ⚙️ **Backend Core**
- **Django HTTP Server** - API REST en puerto 8000
- **Django WebSocket Server (Daphne)** - Comunicaciones en tiempo real en puerto 8001
- **Celery Worker** - Procesamiento de tareas en background
- **Celery Beat** - Programador de tareas periódicas

### 📡 **Servicios GPS**
- **GPS Protocol Servers** - Servidores para múltiples protocolos:
  - Wialon (puerto 20332)
  - Concox (puerto 55300)
  - Meiligao (puerto 62000)
  - Satellite (puerto 15557)

### 📊 **Monitoreo**
- **Device Monitor** - Monitor de dispositivos GPS (opcional)

## 🛠️ Scripts Disponibles

### 1. `start_skyguard_backend.py` - **INICIAR SISTEMA**

Script maestro que inicia todo el backend del sistema SkyGuard.

```bash
# Ejecutar
./start_skyguard_backend.py

# O con Python
python3 start_skyguard_backend.py
```

**Características:**
- ✅ Verificación automática de prerequisitos
- ✅ Ejecución automática de migraciones Django
- ✅ Inicio ordenado de todos los servicios
- ✅ Verificación de salud de servicios
- ✅ Monitoreo continuo y auto-reinicio
- ✅ Logging completo en archivos separados
- ✅ Manejo graceful de señales (Ctrl+C)
- ✅ Reinicio automático de servicios críticos

**Orden de inicio:**
1. Verificación de prerequisitos
2. Migraciones Django
3. Redis Server
4. PostgreSQL
5. Django HTTP Server
6. Django WebSocket Server (Daphne)
7. Celery Worker
8. Celery Beat
9. GPS Protocol Servers
10. Device Monitor (opcional)

### 2. `stop_skyguard_backend.py` - **DETENER SISTEMA**

Script para detener todos los servicios de manera segura.

```bash
# Ejecutar
./stop_skyguard_backend.py

# O con Python
python3 stop_skyguard_backend.py
```

**Características:**
- 🛑 Detección automática de procesos por PID
- 🛑 Búsqueda de procesos por nombre si no hay PID
- 🛑 Terminación graceful (SIGTERM) primero
- 🛑 Terminación forzada (SIGKILL) si es necesario
- 🛑 Limpieza de archivos PID
- 🛑 Verificación final de procesos restantes

### 3. `check_skyguard_status.py` - **VERIFICAR ESTADO**

Script para verificar el estado completo del sistema.

```bash
# Ejecutar
./check_skyguard_status.py

# O con Python
python3 check_skyguard_status.py
```

**Información mostrada:**
- 📊 Estado de cada servicio (corriendo/detenido)
- 🌐 Estado de puertos (abierto/cerrado)
- 🔄 Procesos activos con PID, CPU y memoria
- 💻 Recursos del sistema (CPU, RAM, disco)
- 🎯 Estado del proceso principal
- 🌐 URLs disponibles
- 📋 Resumen general del sistema

## 📁 Estructura de Archivos Generados

```
logs/
├── backend_manager.log      # Log principal del gestor
├── redis.log               # Logs de Redis
├── postgresql.log          # Logs de PostgreSQL
├── django.log              # Logs del servidor Django
├── daphne.log              # Logs del servidor WebSocket
├── celery_worker.log       # Logs del worker Celery
├── celery_beat.log         # Logs del scheduler Celery
├── gps_servers.log         # Logs de servidores GPS
└── device_monitor.log      # Logs del monitor de dispositivos

skyguard_backend.pid        # PID del proceso principal
```

## 🚀 Uso Rápido

### Iniciar el sistema completo:
```bash
./start_skyguard_backend.py
```

### Verificar estado:
```bash
./check_skyguard_status.py
```

### Detener el sistema:
```bash
./stop_skyguard_backend.py
```

## 🔧 Configuración Avanzada

### Variables de Entorno

El sistema utiliza las siguientes variables de entorno:

```bash
# Django
DJANGO_SETTINGS_MODULE=skyguard.settings.dev

# Base de datos
DB_NAME=skyguard
DB_USER=skyguard
DB_PASSWORD=skyguard123
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Configuración de Servicios

Puedes modificar la configuración de servicios editando el diccionario `services_config` en `start_skyguard_backend.py`:

```python
self.services_config = {
    'service_name': {
        'name': 'Display Name',
        'command': ['command', 'args'],
        'port': 8000,  # Puerto opcional
        'required': True,  # Si es crítico
        'startup_delay': 5,  # Segundos de espera
        'log_file': 'service.log',
        'env_vars': {'VAR': 'value'}  # Variables específicas
    }
}
```

## 🌐 Puertos Utilizados

| Servicio | Puerto | Protocolo | Descripción |
|----------|--------|-----------|-------------|
| Django HTTP | 8000 | HTTP | API REST principal |
| Django WebSocket | 8001 | WebSocket | Comunicaciones en tiempo real |
| Redis | 6379 | TCP | Cache y message broker |
| PostgreSQL | 5432 | TCP | Base de datos |
| GPS Wialon | 20332 | TCP | Protocolo Wialon |
| GPS Concox | 55300 | TCP | Protocolo Concox |
| GPS Meiligao | 62000 | UDP | Protocolo Meiligao |
| GPS Satellite | 15557 | TCP | Protocolo Satellite |

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. **Error: Puerto ya en uso**
```bash
# Verificar qué está usando el puerto
sudo netstat -tlnp | grep :8000

# Detener proceso específico
sudo kill -9 <PID>
```

#### 2. **Error: Redis no disponible**
```bash
# Verificar estado de Redis
redis-cli ping

# Iniciar Redis manualmente
sudo systemctl start redis-server
```

#### 3. **Error: PostgreSQL no disponible**
```bash
# Verificar estado
sudo systemctl status postgresql

# Iniciar PostgreSQL
sudo systemctl start postgresql
```

#### 4. **Error: Celery worker no inicia**
```bash
# Verificar logs
cat logs/celery_worker.log

# Verificar configuración de Celery
python3 -c "from skyguard.celery import app; print('OK')"
```

### Logs de Depuración

Todos los logs se guardan en el directorio `logs/`. Para depuración:

```bash
# Ver logs en tiempo real
tail -f logs/backend_manager.log

# Ver logs de un servicio específico
tail -f logs/django.log

# Ver todos los logs
tail -f logs/*.log
```

### Reinicio de Servicios Específicos

Si necesitas reiniciar solo un servicio:

```bash
# 1. Verificar estado
./check_skyguard_status.py

# 2. Detener solo un proceso
kill <PID_del_servicio>

# 3. El sistema lo reiniciará automáticamente
# O reinicia todo el sistema:
./stop_skyguard_backend.py
./start_skyguard_backend.py
```

## 🎯 Características Avanzadas

### Auto-Reinicio de Servicios Críticos

El sistema monitorea continuamente los servicios y reinicia automáticamente aquellos marcados como `required: True` si se detienen inesperadamente.

### Verificación de Salud

Cada servicio tiene verificaciones específicas:
- **Puertos**: Comprueba si están abiertos
- **Procesos**: Verifica que estén corriendo
- **Comandos**: Ejecuta comandos de verificación específicos

### Gestión de Recursos

El sistema muestra y monitorea:
- Uso de CPU
- Uso de memoria RAM
- Uso de disco
- Load average del sistema

### Logs Centralizados

Todos los servicios escriben a archivos de log separados para facilitar la depuración:
- Formato estándar con timestamps
- Rotación automática (configurable)
- Separación por servicio

## 🚨 Consideraciones de Producción

Para un entorno de producción, considera:

1. **Systemd Services**: Convierte los scripts en servicios systemd
2. **Process Manager**: Usa supervisord o systemd para gestión robusta
3. **Reverse Proxy**: Configura nginx delante de Django
4. **SSL/TLS**: Habilita HTTPS para el frontend
5. **Firewall**: Configura iptables/ufw apropiadamente
6. **Monitoring**: Integra con Prometheus/Grafana
7. **Backup**: Configura backups automáticos de PostgreSQL

## 📞 Soporte

Para problemas o preguntas:
1. Revisa los logs en el directorio `logs/`
2. Ejecuta `./check_skyguard_status.py` para diagnóstico
3. Verifica la configuración de servicios
4. Consulta la documentación de Django y Celery

---

**🎉 ¡El sistema SkyGuard está listo para funcionar!**

Disfruta de un sistema de rastreo GPS robusto y completamente automatizado. 