import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// ============================================================================
// CONFIG TYPES - Tipos para configuración
// ============================================================================

export interface AppConfig {
  // Configuración general
  appName: string;
  appVersion: string;
  appDescription: string;
  companyName: string;
  companyLogo: string;
  supportEmail: string;
  supportPhone: string;
  
  // Configuración de API
  apiBaseUrl: string;
  apiTimeout: number;
  apiRetries: number;
  
  // Configuración de paginación
  defaultPageSize: number;
  maxPageSize: number;
  pageSizeOptions: number[];
  
  // Configuración de mapas
  mapProvider: 'google' | 'openstreetmap' | 'mapbox';
  mapApiKey: string;
  defaultMapCenter: {
    lat: number;
    lng: number;
  };
  defaultMapZoom: number;
  
  // Configuración de notificaciones
  notificationTimeout: number;
  maxNotifications: number;
  enableSound: boolean;
  enablePush: boolean;
  
  // Configuración de monitoreo
  pollingInterval: number;
  realtimeEnabled: boolean;
  maxRealtimeConnections: number;
  
  // Configuración de reportes
  reportFormats: string[];
  maxReportSize: number;
  reportRetentionDays: number;
  
  // Configuración de seguridad
  sessionTimeout: number;
  maxLoginAttempts: number;
  passwordMinLength: number;
  requireTwoFactor: boolean;
  
  // Configuración de archivos
  maxFileSize: number;
  allowedFileTypes: string[];
  fileStorageProvider: 'local' | 's3' | 'gcs';
  
  // Configuración de logs
  logLevel: 'debug' | 'info' | 'warn' | 'error';
  logRetentionDays: number;
  enableAuditLog: boolean;
  
  // Configuración de backup
  backupEnabled: boolean;
  backupFrequency: 'daily' | 'weekly' | 'monthly';
  backupRetentionDays: number;
  
  // Configuración de integración
  integrations: {
    email: boolean;
    sms: boolean;
    webhook: boolean;
    api: boolean;
  };
  
  // Configuración de características
  features: {
    geofencing: boolean;
    routeOptimization: boolean;
    driverBehavior: boolean;
    fuelMonitoring: boolean;
    maintenanceTracking: boolean;
    costAnalysis: boolean;
    predictiveAnalytics: boolean;
    mobileApp: boolean;
  };
}

export interface ConfigContextType {
  config: AppConfig;
  updateConfig: (updates: Partial<AppConfig>) => void;
  resetConfig: () => void;
  getConfigValue: <K extends keyof AppConfig>(key: K) => AppConfig[K];
  setConfigValue: <K extends keyof AppConfig>(key: K, value: AppConfig[K]) => void;
  isFeatureEnabled: (feature: keyof AppConfig['features']) => boolean;
  isIntegrationEnabled: (integration: keyof AppConfig['integrations']) => boolean;
}

// ============================================================================
// DEFAULT CONFIG - Configuración por defecto
// ============================================================================

const defaultConfig: AppConfig = {
  // Configuración general
  appName: 'SkyGuard',
  appVersion: '1.0.0',
  appDescription: 'Sistema de Monitoreo y Gestión de Flotas',
  companyName: 'SkyGuard Technologies',
  companyLogo: '/logo.png',
  supportEmail: 'support@skyguard.com',
  supportPhone: '+1-800-SKYGUARD',
  
  // Configuración de API
  apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  apiTimeout: 30000,
  apiRetries: 3,
  
  // Configuración de paginación
  defaultPageSize: 20,
  maxPageSize: 100,
  pageSizeOptions: [10, 20, 50, 100],
  
  // Configuración de mapas
  mapProvider: 'openstreetmap',
  mapApiKey: process.env.REACT_APP_MAP_API_KEY || '',
  defaultMapCenter: {
    lat: 40.7128,
    lng: -74.0060,
  },
  defaultMapZoom: 10,
  
  // Configuración de notificaciones
  notificationTimeout: 5000,
  maxNotifications: 5,
  enableSound: true,
  enablePush: false,
  
  // Configuración de monitoreo
  pollingInterval: 30000,
  realtimeEnabled: true,
  maxRealtimeConnections: 100,
  
  // Configuración de reportes
  reportFormats: ['pdf', 'excel', 'csv'],
  maxReportSize: 50 * 1024 * 1024, // 50MB
  reportRetentionDays: 365,
  
  // Configuración de seguridad
  sessionTimeout: 3600000, // 1 hora
  maxLoginAttempts: 5,
  passwordMinLength: 8,
  requireTwoFactor: false,
  
  // Configuración de archivos
  maxFileSize: 10 * 1024 * 1024, // 10MB
  allowedFileTypes: ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'],
  fileStorageProvider: 'local',
  
  // Configuración de logs
  logLevel: 'info',
  logRetentionDays: 30,
  enableAuditLog: true,
  
  // Configuración de backup
  backupEnabled: true,
  backupFrequency: 'daily',
  backupRetentionDays: 30,
  
  // Configuración de integración
  integrations: {
    email: true,
    sms: true,
    webhook: true,
    api: true,
  },
  
  // Configuración de características
  features: {
    geofencing: true,
    routeOptimization: true,
    driverBehavior: true,
    fuelMonitoring: true,
    maintenanceTracking: true,
    costAnalysis: true,
    predictiveAnalytics: false,
    mobileApp: true,
  },
};

// ============================================================================
// CONFIG CONTEXT - Contexto para configuración
// ============================================================================

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

// ============================================================================
// CONFIG PROVIDER - Provider para configuración
// ============================================================================

interface ConfigProviderProps {
  children: ReactNode;
  initialConfig?: Partial<AppConfig>;
}

export const ConfigProvider: React.FC<ConfigProviderProps> = ({ 
  children, 
  initialConfig = {} 
}) => {
  const [config, setConfig] = useState<AppConfig>({
    ...defaultConfig,
    ...initialConfig,
  });

  // Cargar configuración guardada
  useEffect(() => {
    const savedConfig = localStorage.getItem('appConfig');
    if (savedConfig) {
      try {
        const parsedConfig = JSON.parse(savedConfig);
        setConfig(prevConfig => ({
          ...prevConfig,
          ...parsedConfig,
        }));
      } catch (error) {
        console.error('Error loading saved config:', error);
      }
    }
  }, []);

  // Guardar configuración cuando cambie
  useEffect(() => {
    localStorage.setItem('appConfig', JSON.stringify(config));
  }, [config]);

  // Actualizar configuración
  const updateConfig = (updates: Partial<AppConfig>) => {
    setConfig(prevConfig => ({
      ...prevConfig,
      ...updates,
    }));
  };

  // Resetear configuración
  const resetConfig = () => {
    setConfig(defaultConfig);
    localStorage.removeItem('appConfig');
  };

  // Obtener valor de configuración
  const getConfigValue = <K extends keyof AppConfig>(key: K): AppConfig[K] => {
    return config[key];
  };

  // Establecer valor de configuración
  const setConfigValue = <K extends keyof AppConfig>(key: K, value: AppConfig[K]) => {
    setConfig(prevConfig => ({
      ...prevConfig,
      [key]: value,
    }));
  };

  // Verificar si una característica está habilitada
  const isFeatureEnabled = (feature: keyof AppConfig['features']): boolean => {
    return config.features[feature];
  };

  // Verificar si una integración está habilitada
  const isIntegrationEnabled = (integration: keyof AppConfig['integrations']): boolean => {
    return config.integrations[integration];
  };

  const value: ConfigContextType = {
    config,
    updateConfig,
    resetConfig,
    getConfigValue,
    setConfigValue,
    isFeatureEnabled,
    isIntegrationEnabled,
  };

  return (
    <ConfigContext.Provider value={value}>
      {children}
    </ConfigContext.Provider>
  );
};

// ============================================================================
// CONFIG HOOK - Hook para usar el contexto de configuración
// ============================================================================

export const useConfig = () => {
  const context = useContext(ConfigContext);
  
  if (context === undefined) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  
  return context;
};

// ============================================================================
// CONFIG UTILITIES - Utilidades para configuración
// ============================================================================

export const getApiUrl = (endpoint: string): string => {
  const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
  return `${baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
};

export const getMapConfig = () => {
  const config = defaultConfig;
  return {
    provider: config.mapProvider,
    apiKey: config.mapApiKey,
    center: config.defaultMapCenter,
    zoom: config.defaultMapZoom,
  };
};

export const getNotificationConfig = () => {
  const config = defaultConfig;
  return {
    timeout: config.notificationTimeout,
    maxCount: config.maxNotifications,
    enableSound: config.enableSound,
    enablePush: config.enablePush,
  };
};

export const getSecurityConfig = () => {
  const config = defaultConfig;
  return {
    sessionTimeout: config.sessionTimeout,
    maxLoginAttempts: config.maxLoginAttempts,
    passwordMinLength: config.passwordMinLength,
    requireTwoFactor: config.requireTwoFactor,
  };
}; 