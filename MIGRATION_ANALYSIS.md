# ANÁLISIS DE MIGRACIÓN: Backend Legacy → Moderno

## MAPEO DE MODELOS

### Legacy → Nuevo
| Legacy Model | Nuevo Model | Estado | Notas |
|-------------|-------------|---------|-------|
| `SGAvl` | `GPSDevice` | ✅ Migrado | Campos adicionales para conexiones |
| `Device` | `BaseDevice` | ✅ Migrado | Clase base abstracta |
| `SGHarness` | `DeviceHarness` | ✅ Migrado | Misma funcionalidad |
| `SimCard` | `SimCard` | ✅ Migrado | Estructura idéntica |
| `GeoFence` | `GeoFence` | ⚠️ Mejorado | Nuevas funcionalidades de notificación |
| `ServerSMS` | `ServerSMS` | ✅ Migrado | Campos adicionales de estado |
| `AccelLog` | `AccelerationLog` | ✅ Migrado | Nombres más descriptivos |
| `Overlays` | `Overlay` | ✅ Migrado | Estructura similar |

## MAPEO DE VISTAS

### Legacy → Nuevo
| Legacy View | Nueva API | Método | Estado |
|------------|-----------|---------|---------|
| `TrackerListView` | `/api/gps/devices/` | GET | ✅ Implementado |
| `GeofenceListView` | `/api/gps/geofences/` | GET | ✅ Implementado |
| `GeofenceView` | `/api/gps/geofences/{id}/` | GET/POST | ✅ Implementado |
| `TicketView` | `/api/gps/reports/tickets/` | GET | 🔄 En progreso |
| Reportes PDF | `/api/gps/reports/` | GET | ❌ Pendiente |

## FUNCIONALIDADES CRÍTICAS A MIGRAR

### 1. Sistema de Reportes
- **Legacy**: `reports.py.old` (36KB, 998 líneas)
- **Nuevo**: Necesita implementación completa
- **Prioridad**: ALTA

### 2. Procesamiento de Eventos GPS
- **Legacy**: Lógica mezclada en views
- **Nuevo**: Servicios separados (`GPSService`, `GPSDeviceRepository`)
- **Estado**: ✅ Arquitectura lista

### 3. Autenticación y Permisos
- **Legacy**: Autenticación de sesión Django
- **Nuevo**: JWT + REST Framework
- **Estado**: ✅ Implementado

### 4. Conexiones de Dispositivos
- **Legacy**: Manejo básico
- **Nuevo**: Sistema avanzado con estados de conexión
- **Estado**: ✅ Mejorado

## DATOS A MIGRAR

### Tablas con Datos Críticos
1. `tracker_sgavl` → `gps_gpsdevice`
2. `tracker_geofence` → `gps_geofence`  
3. `tracker_simcard` → `gps_simcard`
4. `tracker_sgharness` → `gps_deviceharness`
5. Logs y eventos históricos

### Estimación de Registros
- Dispositivos GPS: ~500-1000 registros
- Eventos/Ubicaciones: ~1M+ registros
- Geocercas: ~100-200 registros
- Configuraciones: ~50-100 registros

## RIESGOS IDENTIFICADOS

### Alto Riesgo
- **Pérdida de datos históricos** durante migración
- **Incompatibilidad de protocolos** GPS existentes
- **Downtime prolongado** durante switchover

### Medio Riesgo  
- **Cambios en APIs** requieren actualización frontend
- **Configuraciones de dispositivos** pueden requerir reconfiguración
- **Reportes PDF** necesitan reimplementación completa

### Bajo Riesgo
- **Autenticación** - JWT backward compatible
- **Base de datos** - PostGIS compatible
- **Deployment** - Docker/uwsgi similar

## ESTRATEGIA DE MIGRACIÓN RECOMENDADA

### Opción 1: Big Bang (No recomendada)
- Migración completa en un fin de semana
- **Riesgo**: MUY ALTO
- **Downtime**: 24-48 horas

### Opción 2: Migración Gradual (Recomendada)
- Coexistencia de ambos sistemas
- Migración por módulos
- **Riesgo**: BAJO-MEDIO  
- **Downtime**: Mínimo

### Opción 3: Híbrida
- APIs nuevas para funcionalidades nuevas
- Legacy para reportes críticos
- **Riesgo**: MEDIO
- **Complejidad**: ALTA 