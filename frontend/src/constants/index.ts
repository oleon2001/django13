// Configuración de la aplicación
export const APP_CONFIG = {
  name: 'SkyGuard',
  version: '1.0.0',
  description: 'Sistema de monitoreo GPS y gestión de flotas',
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  pollingInterval: parseInt(process.env.REACT_APP_POLLING_INTERVAL || '30000'),
  enableDevTools: process.env.REACT_APP_ENABLE_DEVTOOLS === 'true',
} as const;

// Estados de dispositivos
export const DEVICE_STATUS = {
  ONLINE: 'online',
  OFFLINE: 'offline',
  MOVING: 'moving',
  STOPPED: 'stopped',
  IDLE: 'idle',
  MAINTENANCE: 'maintenance',
  ERROR: 'error',
} as const;

// Tipos de eventos
export const EVENT_TYPES = {
  IGNITION_ON: 'ignition_on',
  IGNITION_OFF: 'ignition_off',
  GEOFENCE_ENTER: 'geofence_enter',
  GEOFENCE_EXIT: 'geofence_exit',
  SPEED_LIMIT_EXCEEDED: 'speed_limit_exceeded',
  LOW_BATTERY: 'low_battery',
  MAINTENANCE_DUE: 'maintenance_due',
  EMERGENCY: 'emergency',
  LOCATION_UPDATE: 'location_update',
  STATUS_CHANGE: 'status_change',
} as const;

// Tipos de alertas
export const ALERT_TYPES = {
  SPEED: 'speed',
  GEOFENCE: 'geofence',
  BATTERY: 'battery',
  MAINTENANCE: 'maintenance',
  EMERGENCY: 'emergency',
  SYSTEM: 'system',
} as const;

// Niveles de severidad
export const SEVERITY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const;

// Estados de vehículos
export const VEHICLE_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  MAINTENANCE: 'maintenance',
  RETIRED: 'retired',
} as const;

// Estados de conductores
export const DRIVER_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  SUSPENDED: 'suspended',
  ON_LEAVE: 'on_leave',
} as const;

// Tipos de reportes
export const REPORT_TYPES = {
  ROUTE: 'route',
  DRIVER: 'driver',
  DEVICE: 'device',
  GEOFENCE: 'geofence',
  MAINTENANCE: 'maintenance',
  FUEL: 'fuel',
  COST: 'cost',
} as const;

// Tipos de geocercas
export const GEOFENCE_TYPES = {
  CIRCLE: 'circle',
  POLYGON: 'polygon',
  RECTANGLE: 'rectangle',
} as const;

// Estados de sesiones
export const SESSION_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  EXPIRED: 'expired',
} as const;

// Protocolos de comunicación
export const PROTOCOLS = {
  HTTP: 'http',
  HTTPS: 'https',
  TCP: 'tcp',
  UDP: 'udp',
  MQTT: 'mqtt',
} as const;

// Tipos de comandos
export const COMMAND_TYPES = {
  LOCATION_REQUEST: 'location_request',
  STATUS_REQUEST: 'status_request',
  CONFIG_UPDATE: 'config_update',
  RESTART: 'restart',
  FACTORY_RESET: 'factory_reset',
} as const;

// Estados de tickets
export const TICKET_STATUS = {
  OPEN: 'open',
  IN_PROGRESS: 'in_progress',
  RESOLVED: 'resolved',
  CLOSED: 'closed',
  CANCELLED: 'cancelled',
} as const;

// Prioridades de tickets
export const TICKET_PRIORITIES = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  URGENT: 'urgent',
} as const;

// Tipos de usuarios
export const USER_TYPES = {
  ADMIN: 'admin',
  MANAGER: 'manager',
  OPERATOR: 'operator',
  VIEWER: 'viewer',
} as const;

// Permisos
export const PERMISSIONS = {
  // Dispositivos
  VIEW_DEVICES: 'view_devices',
  CREATE_DEVICES: 'create_devices',
  EDIT_DEVICES: 'edit_devices',
  DELETE_DEVICES: 'delete_devices',
  SEND_COMMANDS: 'send_commands',
  
  // Vehículos
  VIEW_VEHICLES: 'view_vehicles',
  CREATE_VEHICLES: 'create_vehicles',
  EDIT_VEHICLES: 'edit_vehicles',
  DELETE_VEHICLES: 'delete_vehicles',
  
  // Conductores
  VIEW_DRIVERS: 'view_drivers',
  CREATE_DRIVERS: 'create_drivers',
  EDIT_DRIVERS: 'edit_drivers',
  DELETE_DRIVERS: 'delete_drivers',
  
  // Geocercas
  VIEW_GEOFENCES: 'view_geofences',
  CREATE_GEOFENCES: 'create_geofences',
  EDIT_GEOFENCES: 'edit_geofences',
  DELETE_GEOFENCES: 'delete_geofences',
  
  // Reportes
  VIEW_REPORTS: 'view_reports',
  CREATE_REPORTS: 'create_reports',
  EXPORT_REPORTS: 'export_reports',
  
  // Alertas
  VIEW_ALERTS: 'view_alerts',
  ACKNOWLEDGE_ALERTS: 'acknowledge_alerts',
  
  // Usuarios
  VIEW_USERS: 'view_users',
  CREATE_USERS: 'create_users',
  EDIT_USERS: 'edit_users',
  DELETE_USERS: 'delete_users',
  
  // Configuración
  VIEW_SETTINGS: 'view_settings',
  EDIT_SETTINGS: 'edit_settings',
} as const;

// Configuración de mapas
export const MAP_CONFIG = {
  defaultCenter: {
    lat: parseFloat(process.env.REACT_APP_MAP_CENTER_LAT || '40.7128'),
    lng: parseFloat(process.env.REACT_APP_MAP_CENTER_LNG || '-74.0060'),
  },
  defaultZoom: parseInt(process.env.REACT_APP_MAP_ZOOM || '10'),
  apiKey: process.env.REACT_APP_MAP_API_KEY || '',
} as const;

// Configuración de paginación
export const PAGINATION_CONFIG = {
  defaultPageSize: 20,
  pageSizeOptions: [10, 20, 50, 100],
  maxPageSize: 1000,
} as const;

// Configuración de cache
export const CACHE_CONFIG = {
  staleTime: 5 * 60 * 1000, // 5 minutos
  gcTime: 10 * 60 * 1000, // 10 minutos
  refetchOnWindowFocus: false,
  retry: 3,
  retryDelay: 1000,
} as const;

// Configuración de notificaciones
export const NOTIFICATION_CONFIG = {
  position: 'top-right' as const,
  duration: 4000,
  maxToasts: 5,
} as const;

// Configuración de WebSocket
export const WEBSOCKET_CONFIG = {
  url: process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws/',
  reconnectInterval: 5000,
  maxReconnectAttempts: 10,
} as const;

// Configuración de autenticación
export const AUTH_CONFIG = {
  storageKey: process.env.REACT_APP_AUTH_STORAGE_KEY || 'skyguard_auth',
  tokenRefreshInterval: parseInt(process.env.REACT_APP_TOKEN_REFRESH_INTERVAL || '300000'),
  sessionTimeout: 30 * 60 * 1000, // 30 minutos
} as const;

// Configuración de filtros
export const FILTER_CONFIG = {
  debounceDelay: 300,
  maxDateRange: 365, // días
  minDateRange: 1, // días
} as const;

// Configuración de exportación
export const EXPORT_CONFIG = {
  supportedFormats: ['csv', 'xlsx', 'pdf'] as const,
  maxRecords: 10000,
  defaultFormat: 'csv' as const,
} as const;

// Configuración de monitoreo
export const MONITORING_CONFIG = {
  updateInterval: 5000, // 5 segundos
  historyPoints: 100,
  alertThresholds: {
    speed: 80, // km/h
    battery: 20, // %
    temperature: 50, // °C
  },
} as const;

// Configuración de geocercas
export const GEOFENCE_CONFIG = {
  maxRadius: 50000, // metros
  minRadius: 10, // metros
  maxPolygonPoints: 100,
  defaultRadius: 1000, // metros
} as const;

// Configuración de comandos
export const COMMAND_CONFIG = {
  timeout: 30000, // 30 segundos
  maxRetries: 3,
  retryDelay: 5000, // 5 segundos
} as const;

// Configuración de reportes
export const REPORT_CONFIG = {
  maxDateRange: 90, // días
  defaultDateRange: 30, // días
  supportedPeriods: ['daily', 'weekly', 'monthly', 'yearly'] as const,
} as const;

// Configuración de tickets
export const TICKET_CONFIG = {
  autoCloseDays: 30,
  maxAttachments: 5,
  maxAttachmentSize: 10 * 1024 * 1024, // 10MB
} as const;

// Configuración de usuarios
export const USER_CONFIG = {
  minPasswordLength: 8,
  requireSpecialChars: true,
  maxLoginAttempts: 5,
  lockoutDuration: 15 * 60 * 1000, // 15 minutos
} as const;

// Configuración de sistema
export const SYSTEM_CONFIG = {
  maxFileUploadSize: 50 * 1024 * 1024, // 50MB
  supportedImageFormats: ['jpg', 'jpeg', 'png', 'gif'] as const,
  supportedDocumentFormats: ['pdf', 'doc', 'docx', 'xls', 'xlsx'] as const,
  maxConcurrentUploads: 5,
} as const;

// Mensajes de error comunes
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Error de conexión. Verifique su conexión a internet.',
  UNAUTHORIZED: 'No tiene permisos para realizar esta acción.',
  FORBIDDEN: 'Acceso denegado.',
  NOT_FOUND: 'El recurso solicitado no fue encontrado.',
  VALIDATION_ERROR: 'Los datos proporcionados no son válidos.',
  SERVER_ERROR: 'Error interno del servidor. Intente más tarde.',
  TIMEOUT_ERROR: 'La solicitud ha excedido el tiempo límite.',
  UNKNOWN_ERROR: 'Ha ocurrido un error inesperado.',
} as const;

// Mensajes de éxito comunes
export const SUCCESS_MESSAGES = {
  CREATED: 'Registro creado exitosamente.',
  UPDATED: 'Registro actualizado exitosamente.',
  DELETED: 'Registro eliminado exitosamente.',
  SAVED: 'Cambios guardados exitosamente.',
  SENT: 'Mensaje enviado exitosamente.',
  EXPORTED: 'Datos exportados exitosamente.',
  IMPORTED: 'Datos importados exitosamente.',
} as const;

// Configuración de colores
export const COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  info: '#2196f3',
  light: '#f5f5f5',
  dark: '#333333',
  white: '#ffffff',
  black: '#000000',
  gray: '#9e9e9e',
  transparent: 'transparent',
} as const;

// Configuración de iconos
export const ICONS = {
  device: 'gps_fixed',
  vehicle: 'directions_car',
  driver: 'person',
  geofence: 'location_on',
  alert: 'warning',
  report: 'assessment',
  settings: 'settings',
  user: 'account_circle',
  logout: 'logout',
  menu: 'menu',
  close: 'close',
  edit: 'edit',
  delete: 'delete',
  add: 'add',
  search: 'search',
  filter: 'filter_list',
  sort: 'sort',
  download: 'download',
  upload: 'upload',
  refresh: 'refresh',
  visibility: 'visibility',
  visibilityOff: 'visibility_off',
  check: 'check',
  cancel: 'cancel',
  save: 'save',
  send: 'send',
  location: 'location_on',
  speed: 'speed',
  battery: 'battery_full',
  time: 'schedule',
  date: 'event',
  phone: 'phone',
  email: 'email',
  web: 'language',
  map: 'map',
  route: 'route',
  traffic: 'traffic',
  weather: 'cloud',
  temperature: 'thermostat',
  fuel: 'local_gas_station',
  maintenance: 'build',
  emergency: 'emergency',
  security: 'security',
  analytics: 'analytics',
  dashboard: 'dashboard',
  list: 'list',
  grid: 'grid_view',
  calendar: 'calendar_today',
  notification: 'notifications',
  help: 'help',
  info: 'info',
  error: 'error',
  success: 'check_circle',
  warning: 'warning',
} as const; 