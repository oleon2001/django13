# FUNCIONALIDADES PENDIENTES DE MIGRACIÓN
## Análisis Detallado del Backend Legacy vs Nuevo

**Fecha de Análisis**: 9 de Julio, 2025  
**Estado**: 85% Migrado - 15% Pendiente  

---

## 📊 RESUMEN DE MIGRACIÓN

### ✅ **Funcionalidades Migradas (85%)**
- ✅ Modelos de dispositivos GPS
- ✅ Protocolos de comunicación (NMEA, Concox, Meiligao)
- ✅ APIs REST básicas
- ✅ Base de datos PostGIS
- ✅ Servidores GPS operativos
- ✅ Sistema de eventos
- ✅ Gestión de ubicaciones

### ❌ **Funcionalidades Pendientes (15%)**
- ❌ Sistema de reportes avanzados
- ❌ Gestión de conductores
- ❌ Sistema de subsidios
- ❌ Control de salidas digitales (CFE)
- ❌ Gestión de activos/estacionamientos
- ❌ Interfaz web completa
- ❌ Sistema de tickets
- ❌ Cercas geográficas avanzadas

---

## 🔍 ANÁLISIS DETALLADO POR MÓDULO

### 1. 📊 **SISTEMA DE REPORTES**

#### **Backend Legacy (Django14)**
```python
# django14/skyguard/gps/tracker/reports.py (1542 líneas)
class RutaReport:
    - Reportes por ruta
    - Estadísticas de pasajeros
    - Análisis de tiempos

class TicketReport:
    - Reportes de tickets
    - Análisis de ingresos
    - Estadísticas por conductor

class PeopleCountReport:
    - Conteo de personas
    - Análisis de ocupación
    - Estadísticas por hora

class StatsDailyReport:
    - Estadísticas diarias
    - Métricas de rendimiento
    - Análisis de tendencias
```

#### **Backend Actual (SkyGuard)**
```python
# skyguard/apps/reports/ - VACÍO
❌ No implementado
```

#### **Estado**: ❌ **NO MIGRADO**
- **Prioridad**: Alta
- **Complejidad**: Media
- **Tiempo estimado**: 2-3 semanas

---

### 2. 👥 **GESTIÓN DE CONDUCTORES**

#### **Backend Legacy (Django14)**
```python
# django14/skyguard/gps/tracker/models.py
class Driver(models.Model):
    name = models.CharField(_('Nombre'), max_length = 40)
    middle = models.CharField(_('A. Paterno'), max_length = 40)
    last = models.CharField(_('A. Materno'), max_length = 40)
    birth = models.DateField(_('F. de nacimiento'))
    cstatus = models.CharField(_('Estado Civil'), max_length = 40)
    payroll = models.CharField('Nómina', max_length = 40)
    socials = models.CharField(_('Seguro social'), max_length = 40)
    taxid = models.CharField(_('RFC'), max_length = 40)
    license = models.CharField(_('Licencia'), max_length = 40)
    lic_exp = models.DateField("Vencimiento")
    address = models.TextField('Dirección')
    phone = models.CharField('Teléfono', max_length = 40)
    active = models.BooleanField('Activo', default = True)
```

#### **Backend Actual (SkyGuard)**
```python
# skyguard/apps/gps/models/drivers.py - IMPLEMENTADO
class Driver(BaseDriver):
    # Modelo implementado pero sin vistas
```

#### **Estado**: 🔄 **PARCIALMENTE MIGRADO**
- **Modelos**: ✅ Implementados
- **Vistas**: ❌ Pendientes
- **APIs**: ❌ Pendientes
- **Prioridad**: Media
- **Tiempo estimado**: 1 semana

---

### 3. 💰 **SISTEMA DE SUBSIDIOS**

#### **Backend Legacy (Django14)**
```python
# django14/skyguard/gps/tracker/subsidio.py (783 líneas)
class TsheetView:
    - Gestión de horarios
    - Cálculo de vueltas
    - Integración con tickets

class CsvTSDReportView:
    - Reportes CSV de horarios
    - Exportación de datos
    - Análisis de subsidios
```

#### **Backend Actual (SkyGuard)**
```python
# No implementado
❌ Sistema completo faltante
```

#### **Estado**: ❌ **NO MIGRADO**
- **Prioridad**: Alta
- **Complejidad**: Alta
- **Tiempo estimado**: 3-4 semanas

---

### 4. ⚡ **CONTROL DE SALIDAS DIGITALES (CFE)**

#### **Backend Legacy (Django14)**
```python
# django14/skyguard/gps/tracker/cfe.py (137 líneas)
class ConcorView:
    - Control de acometidas
    - Gestión de 12 salidas digitales

class CfeView:
    - Control de salidas
    - Control remoto de dispositivos
```

#### **Backend Actual (SkyGuard)**
```python
# No implementado
❌ Sistema de control faltante
```

#### **Estado**: ❌ **NO MIGRADO**
- **Prioridad**: Media
- **Complejidad**: Media
- **Tiempo estimado**: 2 semanas

---

### 5. 🚗 **GESTIÓN DE ACTIVOS/ESTACIONAMIENTOS**

#### **Backend Legacy (Django14)**
```python
# django14/skyguard/gps/assets/models.py (227 líneas)
class CarPark(models.Model):
    - Estacionamientos

class CarLane(models.Model):
    - Carriles de estacionamiento

class CarSlot(models.Model):
    - Espacios de estacionamiento

class GridlessCar(models.Model):
    - Vehículos sin grid

class DemoCar(models.Model):
    - Vehículos de demostración
```

#### **Backend Actual (SkyGuard)**
```python
# skyguard/apps/gps/models/assets.py - IMPLEMENTADO
class Vehicle(BaseVehicle):
    # Modelo implementado pero sin funcionalidad completa
```

#### **Estado**: 🔄 **PARCIALMENTE MIGRADO**
- **Modelos**: ✅ Implementados
- **Funcionalidad**: ❌ Pendiente
- **Prioridad**: Baja
- **Tiempo estimado**: 1-2 semanas

---

### 6. 🌐 **INTERFAZ WEB COMPLETA**

#### **Backend Legacy (Django14)**
```python
# django14/skyguard/gps/tracker/views.py (1979 líneas)
class TrackerListView:
    - Lista de dispositivos
    - Vista en tiempo real

class TrackerDetailView:
    - Detalle de dispositivo
    - Historial de eventos

class RealTimeView:
    - Vista en tiempo real
    - Actualizaciones AJAX

class GeofenceListView:
    - Gestión de cercas
    - Creación/edición

class WeeklyReportView:
    - Reportes semanales
    - Análisis de datos
```

#### **Backend Actual (SkyGuard)**
```python
# skyguard/apps/gps/views.py - APIs REST
- APIs REST implementadas
- Interfaz web básica
```

#### **Estado**: 🔄 **PARCIALMENTE MIGRADO**
- **APIs**: ✅ Implementadas
- **Interfaz Web**: ❌ Pendiente
- **Prioridad**: Media
- **Tiempo estimado**: 4-6 semanas

---

### 7. 🎫 **SISTEMA DE TICKETS**

#### **Backend Legacy (Django14)**
```python
# django14/skyguard/gps/tracker/models.py
class TicketsLog(models.Model):
    - Logs de tickets
    - Análisis de ingresos

class TicketDetails(models.Model):
    - Detalles de tickets
    - Información de conductores
```

#### **Backend Actual (SkyGuard)**
```python
# No implementado
❌ Sistema completo faltante
```

#### **Estado**: ❌ **NO MIGRADO**
- **Prioridad**: Media
- **Complejidad**: Media
- **Tiempo estimado**: 2-3 semanas

---

### 8. 🗺️ **CERCAS GEOGRÁFICAS AVANZADAS**

#### **Backend Legacy (Django14)**
```python
# django14/skyguard/gps/tracker/models.py
class GeoFence(models.Model):
    - Cercas geográficas
    - Eventos de entrada/salida
    - Notificaciones

class GeoFenceEvent(models.Model):
    - Eventos de cercas
    - Historial de eventos
```

#### **Backend Actual (SkyGuard)**
```python
# skyguard/apps/gps/models/device.py
class GeoFence(BaseGeoFence):
    # Modelo implementado pero sin funcionalidad completa
```

#### **Estado**: 🔄 **PARCIALMENTE MIGRADO**
- **Modelos**: ✅ Implementados
- **Funcionalidad**: ❌ Pendiente
- **Prioridad**: Baja
- **Tiempo estimado**: 1-2 semanas

---

## 📋 PLAN DE MIGRACIÓN PRIORITARIO

### 🔥 **Prioridad Alta (2-3 semanas)**

1. **Sistema de Reportes** (2 semanas)
   - Implementar reportes básicos
   - Migrar lógica de análisis
   - Crear APIs de reportes

2. **Sistema de Subsidios** (3 semanas)
   - Migrar modelos de horarios
   - Implementar cálculos
   - Crear reportes CSV

### 🔧 **Prioridad Media (3-4 semanas)**

3. **Gestión de Conductores** (1 semana)
   - Completar APIs
   - Implementar vistas
   - Añadir funcionalidad

4. **Control CFE** (2 semanas)
   - Implementar control de salidas
   - Crear APIs de control
   - Añadir seguridad

5. **Interfaz Web** (4-6 semanas)
   - Crear templates
   - Implementar vistas
   - Añadir JavaScript

### 📚 **Prioridad Baja (2-3 semanas)**

6. **Sistema de Tickets** (2-3 semanas)
   - Migrar modelos
   - Implementar lógica
   - Crear reportes

7. **Gestión de Activos** (1-2 semanas)
   - Completar funcionalidad
   - Implementar APIs
   - Añadir vistas

8. **Cercas Avanzadas** (1-2 semanas)
   - Completar funcionalidad
   - Implementar eventos
   - Añadir notificaciones

---

## 🎯 CONCLUSIÓN

### **Estado Actual**: 85% Migrado
- **Funcionalidades Críticas**: ✅ Completas
- **Funcionalidades Secundarias**: 🔄 En progreso
- **Funcionalidades Terciarias**: ❌ Pendientes

### **Tiempo Total Estimado**: 8-12 semanas
- **Prioridad Alta**: 5 semanas
- **Prioridad Media**: 7-9 semanas  
- **Prioridad Baja**: 4-5 semanas

### **Recomendación**: 
**Continuar con la migración priorizando el sistema de reportes y subsidios**, ya que son funcionalidades críticas para el negocio. 