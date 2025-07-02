# Integración Backend-Frontend SkyGuard

## Resumen

Se ha completado la integración completa del backend Django con el frontend React, creando un sistema unificado que incluye:

- **Tipos TypeScript unificados** que reflejan todos los modelos del backend
- **Servicios de API unificados** que encapsulan todas las operaciones CRUD
- **Hooks personalizados** que integran React Query para gestión de estado
- **Componentes de ejemplo** que demuestran el uso de la integración

## Estructura de Archivos

### 1. Tipos Unificados (`src/types/unified.ts`)

Contiene todas las interfaces TypeScript que representan los modelos del backend:

- **Base Types**: `BaseEntity`, `Position`, `Point`
- **User & Authentication**: `User`, `AuthTokens`, `LoginCredentials`
- **GPS Devices**: `GPSDevice`, `DeviceStats`
- **Location & Tracking**: `Location`, `GPSLocation`
- **Events & Network**: `NetworkEvent`, `DeviceEvent`
- **Vehicles & Drivers**: `Vehicle`, `Driver`
- **Geofencing**: `GeoFence`, `GeofenceEvent`
- **Tracking & Monitoring**: `Alert`, `Route`, `DeviceStatus`
- **Sessions & Protocols**: `GPRSSession`, `UDPSession`
- **Assets & Parking**: `CarPark`, `CarLane`, `CarSlot`
- **Reports & Statistics**: `Report`, `Statistics`
- **Communication**: `CellTower`, `ServerSMS`
- **Tickets & Logs**: `TicketDetail`
- **UI & Components**: `Column`, `ServerSettings`, `Protocol`
- **API Responses**: `ApiResponse`, `PaginatedResponse`, `DeviceStats`
- **Filters & Query Params**: `DeviceFilters`, `VehicleFilters`, `DriverFilters`
- **Real-time Data**: `RealTimePosition`, `DeviceTrail`
- **Commands & Actions**: `DeviceCommand`, `GeofenceAction`

### 2. Servicios de API Unificados (`src/services/unifiedApi.ts`)

Encapsula todas las operaciones de API organizadas por módulos:

#### Autenticación
- `authService.login()` - Inicio de sesión
- `authService.register()` - Registro de usuarios
- `authService.logout()` - Cierre de sesión
- `authService.getCurrentUser()` - Obtener usuario actual
- `authService.refreshToken()` - Refrescar token

#### Dispositivos GPS
- `deviceService.getDevices()` - Listar dispositivos con filtros
- `deviceService.getDevice()` - Obtener dispositivo específico
- `deviceService.createDevice()` - Crear nuevo dispositivo
- `deviceService.updateDevice()` - Actualizar dispositivo
- `deviceService.deleteDevice()` - Eliminar dispositivo
- `deviceService.getDeviceHistory()` - Historial de ubicaciones
- `deviceService.getDeviceEvents()` - Eventos del dispositivo
- `deviceService.getDeviceTrail()` - Ruta del dispositivo
- `deviceService.sendCommand()` - Enviar comandos

#### Vehículos
- `vehicleService.getVehicles()` - Listar vehículos
- `vehicleService.createVehicle()` - Crear vehículo
- `vehicleService.updateVehicle()` - Actualizar vehículo
- `vehicleService.deleteVehicle()` - Eliminar vehículo
- `vehicleService.assignDevice()` - Asignar dispositivo
- `vehicleService.assignDriver()` - Asignar conductor

#### Conductores
- `driverService.getDrivers()` - Listar conductores
- `driverService.createDriver()` - Crear conductor
- `driverService.updateDriver()` - Actualizar conductor
- `driverService.deleteDriver()` - Eliminar conductor
- `driverService.assignVehicle()` - Asignar vehículo

#### Geofencing
- `geofenceService.getGeofences()` - Listar geocercas
- `geofenceService.createGeofence()` - Crear geocerca
- `geofenceService.updateGeofence()` - Actualizar geocerca
- `geofenceService.deleteGeofence()` - Eliminar geocerca
- `geofenceService.getGeofenceEvents()` - Eventos de geocerca
- `geofenceService.monitorGeofences()` - Monitoreo en tiempo real

#### Tracking y Monitoreo
- `trackingService.getRealTimePositions()` - Posiciones en tiempo real
- `trackingService.getActiveSessions()` - Sesiones activas
- `trackingService.getAlerts()` - Alertas del sistema
- `trackingService.acknowledgeAlert()` - Reconocer alertas
- `trackingService.getDeviceRoutes()` - Rutas de dispositivos

#### Reportes
- `reportService.getReports()` - Listar reportes
- `reportService.createReport()` - Crear reporte
- `reportService.generateRouteReport()` - Reporte de ruta
- `reportService.generateDriverReport()` - Reporte de conductor
- `reportService.generateDeviceReport()` - Reporte de dispositivo

#### Parqueo
- `parkingService.getCarParks()` - Listar parqueos
- `parkingService.getCarLanes()` - Listar carriles
- `parkingService.getCarSlots()` - Listar espacios
- `parkingService.assignCarToSlot()` - Asignar vehículo a espacio
- `parkingService.removeCarFromSlot()` - Remover vehículo de espacio

#### Comunicación
- `communicationService.getCellTowers()` - Torres celulares
- `communicationService.sendSMS()` - Enviar SMS
- `communicationService.getSMSHistory()` - Historial de SMS

#### Tickets
- `ticketService.getTicketDetails()` - Detalles de tickets
- `ticketService.createTicketDetail()` - Crear ticket

#### Coordenadas
- `coordinateService.getCoordinates()` - Obtener coordenadas
- `coordinateService.getLatestCoordinates()` - Últimas coordenadas
- `coordinateService.generateTestData()` - Generar datos de prueba

### 3. Hooks Personalizados (`src/hooks/unifiedHooks.ts`)

Hooks de React Query que proporcionan:

#### Gestión de Estado
- Cache automático con React Query
- Invalidación automática de queries
- Reintentos automáticos en errores
- Actualizaciones en tiempo real
- Gestión de estados de carga y error

#### Hooks por Módulo

**Autenticación:**
- `useCurrentUser()` - Usuario actual
- `useLogin()` - Inicio de sesión
- `useLogout()` - Cierre de sesión

**Dispositivos:**
- `useDevices()` - Listar dispositivos
- `useDevice()` - Dispositivo específico
- `useCreateDevice()` - Crear dispositivo
- `useUpdateDevice()` - Actualizar dispositivo
- `useDeleteDevice()` - Eliminar dispositivo
- `useDeviceHistory()` - Historial
- `useDeviceEvents()` - Eventos
- `useDeviceTrail()` - Ruta
- `useDeviceStatus()` - Estado
- `useSendDeviceCommand()` - Enviar comandos

**Vehículos:**
- `useVehicles()` - Listar vehículos
- `useVehicle()` - Vehículo específico
- `useCreateVehicle()` - Crear vehículo
- `useUpdateVehicle()` - Actualizar vehículo
- `useDeleteVehicle()` - Eliminar vehículo
- `useAvailableDevices()` - Dispositivos disponibles
- `useAvailableDrivers()` - Conductores disponibles
- `useAssignDeviceToVehicle()` - Asignar dispositivo
- `useAssignDriverToVehicle()` - Asignar conductor

**Conductores:**
- `useDrivers()` - Listar conductores
- `useDriver()` - Conductor específico
- `useCreateDriver()` - Crear conductor
- `useUpdateDriver()` - Actualizar conductor
- `useDeleteDriver()` - Eliminar conductor
- `useAvailableVehicles()` - Vehículos disponibles
- `useAssignVehicleToDriver()` - Asignar vehículo

**Geofencing:**
- `useGeofences()` - Listar geocercas
- `useGeofence()` - Geocerca específica
- `useCreateGeofence()` - Crear geocerca
- `useUpdateGeofence()` - Actualizar geocerca
- `useDeleteGeofence()` - Eliminar geocerca
- `useGeofenceEvents()` - Eventos de geocerca
- `useGeofenceStats()` - Estadísticas
- `useMonitorGeofences()` - Monitoreo

**Tracking:**
- `useRealTimePositions()` - Posiciones en tiempo real
- `useActiveSessions()` - Sesiones activas
- `useAlerts()` - Alertas
- `useAcknowledgeAlert()` - Reconocer alertas
- `useDeviceRoutes()` - Rutas de dispositivos
- `useTrackingDeviceStatus()` - Estado de dispositivo
- `useAllDevicesStatus()` - Estado de todos los dispositivos
- `useDevicesActivity()` - Actividad de dispositivos

**Reportes:**
- `useReports()` - Listar reportes
- `useReport()` - Reporte específico
- `useCreateReport()` - Crear reporte
- `useGenerateRouteReport()` - Reporte de ruta
- `useGenerateDriverReport()` - Reporte de conductor
- `useGenerateDeviceReport()` - Reporte de dispositivo

**Parqueo:**
- `useCarParks()` - Listar parqueos
- `useCarPark()` - Parqueo específico
- `useCarLanes()` - Listar carriles
- `useCarSlots()` - Listar espacios
- `useAssignCarToSlot()` - Asignar vehículo
- `useRemoveCarFromSlot()` - Remover vehículo

**Comunicación:**
- `useCellTowers()` - Torres celulares
- `useSMSHistory()` - Historial de SMS
- `useSendSMS()` - Enviar SMS

**Tickets:**
- `useTicketDetails()` - Detalles de tickets
- `useCreateTicketDetail()` - Crear ticket

**Coordenadas:**
- `useCoordinates()` - Obtener coordenadas
- `useLatestCoordinates()` - Últimas coordenadas
- `useGenerateTestData()` - Generar datos de prueba

### 4. Provider de React Query (`src/providers/QueryProvider.tsx`)

Configuración global de React Query con:

- **Configuración de cache**: 5 minutos stale time, 10 minutos gc time
- **Reintentos inteligentes**: No reintenta errores 4xx, hasta 3 reintentos para otros
- **Notificaciones**: Toast notifications para éxito y error
- **DevTools**: Herramientas de desarrollo en modo desarrollo

### 5. Componente de Ejemplo (`src/components/examples/DeviceManagement.tsx`)

Demuestra el uso completo de los hooks para gestión de dispositivos:

- **Lista de dispositivos** con filtros
- **CRUD completo** (Crear, Leer, Actualizar, Eliminar)
- **Estado en tiempo real** del dispositivo
- **Historial de ubicaciones** y eventos
- **Envío de comandos** al dispositivo
- **Modales** para formularios
- **Gestión de estados** de carga y error

## Características Principales

### 1. Tipado Completo
- Todas las interfaces reflejan exactamente los modelos del backend
- Tipado estricto en todas las operaciones
- Autocompletado y validación en tiempo de desarrollo

### 2. Gestión de Estado Avanzada
- **React Query** para cache y sincronización
- **Invalidación automática** de queries relacionadas
- **Optimistic updates** para mejor UX
- **Background refetching** para datos actualizados

### 3. Manejo de Errores Robusto
- **Reintentos automáticos** con configuración inteligente
- **Notificaciones de error** con toast
- **Estados de error** en componentes
- **Fallbacks** para datos no disponibles

### 4. Tiempo Real
- **Refetch automático** para datos críticos
- **WebSocket ready** para actualizaciones instantáneas
- **Polling configurable** para diferentes tipos de datos

### 5. Performance Optimizada
- **Cache inteligente** con React Query
- **Lazy loading** de datos
- **Paginación** para listas grandes
- **Debouncing** en búsquedas

## Uso Básico

### 1. Configurar el Provider

```tsx
import { QueryProvider } from './providers/QueryProvider';

function App() {
  return (
    <QueryProvider>
      {/* Tu aplicación aquí */}
    </QueryProvider>
  );
}
```

### 2. Usar Hooks en Componentes

```tsx
import { useDevices, useCreateDevice } from '../hooks/unifiedHooks';

function DeviceList() {
  const { data: devices, isLoading, error } = useDevices();
  const createDevice = useCreateDevice();

  if (isLoading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {devices?.map(device => (
        <div key={device.imei}>{device.name}</div>
      ))}
    </div>
  );
}
```

### 3. Mutaciones

```tsx
import { useCreateDevice } from '../hooks/unifiedHooks';

function CreateDeviceForm() {
  const createDevice = useCreateDevice();

  const handleSubmit = async (data) => {
    try {
      await createDevice.mutateAsync(data);
      // Éxito automático con toast notification
    } catch (error) {
      // Error automático con toast notification
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Formulario aquí */}
    </form>
  );
}
```

## Endpoints del Backend Integrados

### GPS App (`/gps/`)
- `GET /devices/` - Listar dispositivos
- `POST /devices/` - Crear dispositivo
- `GET /devices/{imei}/` - Obtener dispositivo
- `PATCH /devices/{imei}/` - Actualizar dispositivo
- `DELETE /devices/{imei}/` - Eliminar dispositivo
- `GET /devices/{imei}/history/` - Historial
- `GET /devices/{imei}/events/` - Eventos
- `GET /devices/{imei}/trail/` - Ruta
- `POST /devices/{imei}/command/` - Enviar comando
- `GET /vehicles/` - Listar vehículos
- `POST /vehicles/` - Crear vehículo
- `GET /vehicles/{id}/` - Obtener vehículo
- `PUT /vehicles/{id}/` - Actualizar vehículo
- `DELETE /vehicles/{id}/` - Eliminar vehículo
- `GET /drivers/` - Listar conductores
- `POST /drivers/` - Crear conductor
- `GET /drivers/{id}/` - Obtener conductor
- `PUT /drivers/{id}/` - Actualizar conductor
- `DELETE /drivers/{id}/` - Eliminar conductor
- `GET /positions/real-time/` - Posiciones en tiempo real
- `GET /sessions/active/` - Sesiones activas

### Geofencing App (`/geofencing/`)
- `GET /geofences/` - Listar geocercas
- `POST /geofences/` - Crear geocerca
- `GET /geofences/{id}/` - Obtener geocerca
- `PUT /geofences/{id}/` - Actualizar geocerca
- `DELETE /geofences/{id}/` - Eliminar geocerca
- `GET /geofences/{id}/events/` - Eventos de geocerca
- `GET /geofences/{id}/statistics/` - Estadísticas
- `GET /geofences/monitor/` - Monitoreo

### Tracking App (`/tracking/`)
- `GET /alerts/` - Listar alertas
- `POST /alerts/{id}/acknowledge/` - Reconocer alerta
- `GET /routes/` - Listar rutas
- `GET /device-status/{id}/` - Estado de dispositivo

### Reports App (`/reports/`)
- `GET /reports/` - Listar reportes
- `POST /reports/` - Crear reporte
- `GET /reports/{id}/` - Obtener reporte
- `POST /route-report/` - Generar reporte de ruta
- `POST /driver-report/` - Generar reporte de conductor
- `POST /device-report/` - Generar reporte de dispositivo

### Coordinates App (`/coordinates/`)
- `GET /coordinates/` - Listar coordenadas
- `GET /coordinates/get_latest/` - Últimas coordenadas
- `GET /coordinates/generate_test_data/` - Generar datos de prueba

## Próximos Pasos

1. **Implementar WebSockets** para actualizaciones en tiempo real
2. **Añadir autenticación JWT** completa
3. **Implementar paginación** en listas grandes
4. **Añadir filtros avanzados** y búsqueda
5. **Crear componentes reutilizables** para formularios
6. **Implementar tests** unitarios y de integración
7. **Optimizar bundle** con code splitting
8. **Añadir PWA** capabilities

## Dependencias Instaladas

- `@tanstack/react-query` - Gestión de estado y cache
- `@tanstack/react-query-devtools` - Herramientas de desarrollo
- `react-hot-toast` - Notificaciones toast

## Configuración Requerida

1. **Variables de entorno** en `.env`:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

2. **CORS** configurado en el backend Django

3. **Autenticación** configurada en el backend

## Conclusión

La integración proporciona una base sólida y escalable para el desarrollo de la aplicación SkyGuard, con:

- **Arquitectura limpia** y mantenible
- **Tipado completo** para prevenir errores
- **Gestión de estado eficiente** con React Query
- **Componentes reutilizables** y modulares
- **Documentación completa** para desarrollo futuro

El sistema está listo para el desarrollo de nuevas funcionalidades y la integración con componentes de UI más avanzados. 