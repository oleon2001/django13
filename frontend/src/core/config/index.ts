// Core configuration service migrated from Django backend
// Based on skyguard/apps/core/config.py

export interface CoreConfigData {
  database?: DatabaseConfig;
  security?: SecurityConfig;
  notifications?: NotificationsConfig;
  tracking?: TrackingConfig;
  analytics?: AnalyticsConfig;
  monitoring?: MonitoringConfig;
  websocket?: WebSocketConfig;
  fileUpload?: FileUploadConfig;
  [key: string]: any;
}

export interface DatabaseConfig {
  host: string;
  port: number;
  name: string;
  user: string;
  password: string;
  engine: string;
}

export interface SecurityConfig {
  secretKey: string;
  algorithm: string;
  accessTokenExpiry: number;
  refreshTokenExpiry: number;
  maxLoginAttempts: number;
  lockoutDuration: number;
}

export interface NotificationsConfig {
  emailEnabled: boolean;
  smsEnabled: boolean;
  pushEnabled: boolean;
  webhookEnabled: boolean;
  defaultChannels: string[];
  rateLimit: number;
}

export interface TrackingConfig {
  realTimeEnabled: boolean;
  historyRetentionDays: number;
  maxDevicesPerUser: number;
  geofenceEnabled: boolean;
  alertsEnabled: boolean;
}

export interface AnalyticsConfig {
  enabled: boolean;
  dataRetentionDays: number;
  realTimeMetrics: boolean;
  anomalyDetection: boolean;
  performanceMonitoring: boolean;
}

export interface MonitoringConfig {
  healthCheckInterval: number;
  deviceStatusCheckInterval: number;
  logRetentionDays: number;
  alertThresholds: Record<string, number>;
}

export interface WebSocketConfig {
  enabled: boolean;
  port: number;
  maxConnections: number;
  heartbeatInterval: number;
  reconnectAttempts: number;
}

export interface FileUploadConfig {
  maxFileSize: number;
  allowedExtensions: string[];
  uploadPath: string;
  tempPath: string;
}

class CoreConfig {
  private config: CoreConfigData = {};
  private initialized = false;

  constructor() {
    this.loadConfig();
  }

  /**
   * Load configuration from environment and localStorage
   */
  private loadConfig(): void {
    // Load from environment variables
    this.loadEnvConfig();
    
    // Load from localStorage if available
    this.loadLocalConfig();
    
    // Set defaults
    this.setDefaults();
    
    this.initialized = true;
  }

  /**
   * Load configuration from environment variables
   */
  private loadEnvConfig(): void {
    const env = process.env;
    
    this.config.database = {
      host: env.REACT_APP_DB_HOST || 'localhost',
      port: parseInt(env.REACT_APP_DB_PORT || '5432'),
      name: env.REACT_APP_DB_NAME || 'skyguard',
      user: env.REACT_APP_DB_USER || 'postgres',
      password: env.REACT_APP_DB_PASSWORD || '',
      engine: env.REACT_APP_DB_ENGINE || 'postgresql'
    };

    this.config.security = {
      secretKey: env.REACT_APP_SECRET_KEY || 'your-secret-key-here',
      algorithm: env.REACT_APP_JWT_ALGORITHM || 'HS256',
      accessTokenExpiry: parseInt(env.REACT_APP_ACCESS_TOKEN_EXPIRY || '3600'),
      refreshTokenExpiry: parseInt(env.REACT_APP_REFRESH_TOKEN_EXPIRY || '86400'),
      maxLoginAttempts: parseInt(env.REACT_APP_MAX_LOGIN_ATTEMPTS || '5'),
      lockoutDuration: parseInt(env.REACT_APP_LOCKOUT_DURATION || '300')
    };

    this.config.notifications = {
      emailEnabled: env.REACT_APP_EMAIL_ENABLED === 'true',
      smsEnabled: env.REACT_APP_SMS_ENABLED === 'true',
      pushEnabled: env.REACT_APP_PUSH_ENABLED === 'true',
      webhookEnabled: env.REACT_APP_WEBHOOK_ENABLED === 'true',
      defaultChannels: env.REACT_APP_DEFAULT_CHANNELS?.split(',') || ['email'],
      rateLimit: parseInt(env.REACT_APP_NOTIFICATION_RATE_LIMIT || '100')
    };

    this.config.tracking = {
      realTimeEnabled: env.REACT_APP_REALTIME_ENABLED === 'true',
      historyRetentionDays: parseInt(env.REACT_APP_HISTORY_RETENTION_DAYS || '30'),
      maxDevicesPerUser: parseInt(env.REACT_APP_MAX_DEVICES_PER_USER || '100'),
      geofenceEnabled: env.REACT_APP_GEOFENCE_ENABLED === 'true',
      alertsEnabled: env.REACT_APP_ALERTS_ENABLED === 'true'
    };

    this.config.analytics = {
      enabled: env.REACT_APP_ANALYTICS_ENABLED === 'true',
      dataRetentionDays: parseInt(env.REACT_APP_ANALYTICS_RETENTION_DAYS || '90'),
      realTimeMetrics: env.REACT_APP_REALTIME_METRICS === 'true',
      anomalyDetection: env.REACT_APP_ANOMALY_DETECTION === 'true',
      performanceMonitoring: env.REACT_APP_PERFORMANCE_MONITORING === 'true'
    };

    this.config.monitoring = {
      healthCheckInterval: parseInt(env.REACT_APP_HEALTH_CHECK_INTERVAL || '300'),
      deviceStatusCheckInterval: parseInt(env.REACT_APP_DEVICE_STATUS_CHECK_INTERVAL || '60'),
      logRetentionDays: parseInt(env.REACT_APP_LOG_RETENTION_DAYS || '30'),
      alertThresholds: {
        cpu: parseFloat(env.REACT_APP_CPU_THRESHOLD || '80'),
        memory: parseFloat(env.REACT_APP_MEMORY_THRESHOLD || '80'),
        disk: parseFloat(env.REACT_APP_DISK_THRESHOLD || '90')
      }
    };

    this.config.websocket = {
      enabled: env.REACT_APP_WEBSOCKET_ENABLED === 'true',
      port: parseInt(env.REACT_APP_WEBSOCKET_PORT || '8001'),
      maxConnections: parseInt(env.REACT_APP_WEBSOCKET_MAX_CONNECTIONS || '1000'),
      heartbeatInterval: parseInt(env.REACT_APP_WEBSOCKET_HEARTBEAT_INTERVAL || '30'),
      reconnectAttempts: parseInt(env.REACT_APP_WEBSOCKET_RECONNECT_ATTEMPTS || '5')
    };

    this.config.fileUpload = {
      maxFileSize: parseInt(env.REACT_APP_MAX_FILE_SIZE || '10485760'), // 10MB
      allowedExtensions: env.REACT_APP_ALLOWED_EXTENSIONS?.split(',') || ['jpg', 'png', 'pdf', 'csv'],
      uploadPath: env.REACT_APP_UPLOAD_PATH || '/uploads',
      tempPath: env.REACT_APP_TEMP_PATH || '/tmp'
    };
  }

  /**
   * Load configuration from localStorage
   */
  private loadLocalConfig(): void {
    try {
      const stored = localStorage.getItem('skyguard_config');
      if (stored) {
        const localConfig = JSON.parse(stored);
        this.config = { ...this.config, ...localConfig };
      }
    } catch (error) {
      console.warn('Failed to load local config:', error);
    }
  }

  /**
   * Set default configuration values
   */
  private setDefaults(): void {
    const defaults: CoreConfigData = {
      api: {
        baseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
        timeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '30000'),
        retryAttempts: parseInt(process.env.REACT_APP_API_RETRY_ATTEMPTS || '3')
      },
      map: {
        defaultCenter: { lat: 19.4326, lng: -99.1332 }, // Mexico City
        defaultZoom: 10,
        tileLayer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '© OpenStreetMap contributors'
      },
      ui: {
        theme: 'light',
        language: 'es',
        timezone: 'America/Mexico_City',
        dateFormat: 'DD/MM/YYYY',
        timeFormat: 'HH:mm:ss'
      }
    };

    this.config = { ...defaults, ...this.config };
  }

  /**
   * Get configuration value
   */
  get(key: string, defaultValue?: any): any {
    const keys = key.split('.');
    let value = this.config;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return defaultValue;
      }
    }
    
    return value;
  }

  /**
   * Set configuration value
   */
  set(key: string, value: any): void {
    const keys = key.split('.');
    let current = this.config;
    
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!(k in current) || typeof current[k] !== 'object') {
        current[k] = {};
      }
      current = current[k];
    }
    
    current[keys[keys.length - 1]] = value;
    this.saveToLocalStorage();
  }

  /**
   * Get entire configuration section
   */
  getSection(section: string): Record<string, any> {
    return this.config[section] || {};
  }

  /**
   * Update entire configuration section
   */
  updateSection(section: string, values: Record<string, any>): void {
    this.config[section] = { ...this.config[section], ...values };
    this.saveToLocalStorage();
  }

  /**
   * Reload configuration
   */
  reload(): void {
    this.initialized = false;
    this.loadConfig();
  }

  /**
   * Export configuration
   */
  export(): CoreConfigData {
    return { ...this.config };
  }

  /**
   * Validate configuration
   */
  validate(): boolean {
    try {
      // Check required fields
      const required = [
        'database.host',
        'database.name',
        'security.secretKey',
        'api.baseUrl'
      ];
      
      for (const field of required) {
        if (!this.get(field)) {
          console.error(`Missing required config field: ${field}`);
          return false;
        }
      }
      
      return true;
    } catch (error) {
      console.error('Configuration validation failed:', error);
      return false;
    }
  }

  /**
   * Get database configuration
   */
  getDatabaseConfig(): DatabaseConfig {
    return this.config.database!;
  }

  /**
   * Get security configuration
   */
  getSecurityConfig(): SecurityConfig {
    return this.config.security!;
  }

  /**
   * Get notifications configuration
   */
  getNotificationsConfig(): NotificationsConfig {
    return this.config.notifications!;
  }

  /**
   * Get tracking configuration
   */
  getTrackingConfig(): TrackingConfig {
    return this.config.tracking!;
  }

  /**
   * Get analytics configuration
   */
  getAnalyticsConfig(): AnalyticsConfig {
    return this.config.analytics!;
  }

  /**
   * Get monitoring configuration
   */
  getMonitoringConfig(): MonitoringConfig {
    return this.config.monitoring!;
  }

  /**
   * Get WebSocket configuration
   */
  getWebSocketConfig(): WebSocketConfig {
    return this.config.websocket!;
  }

  /**
   * Get file upload configuration
   */
  getFileUploadConfig(): FileUploadConfig {
    return this.config.fileUpload!;
  }

  /**
   * Save configuration to localStorage
   */
  private saveToLocalStorage(): void {
    try {
      localStorage.setItem('skyguard_config', JSON.stringify(this.config));
    } catch (error) {
      console.warn('Failed to save config to localStorage:', error);
    }
  }

  /**
   * Check if configuration is initialized
   */
  isInitialized(): boolean {
    return this.initialized;
  }
}

// Singleton instance
let configInstance: CoreConfig | null = null;

/**
 * Get configuration instance
 */
export function getConfig(): CoreConfig {
  if (!configInstance) {
    configInstance = new CoreConfig();
  }
  return configInstance;
}

/**
 * Get configuration value
 */
export function getConfigValue(key: string, defaultValue?: any): any {
  return getConfig().get(key, defaultValue);
}

/**
 * Set configuration value
 */
export function setConfigValue(key: string, value: any): void {
  getConfig().set(key, value);
}

/**
 * Reload configuration
 */
export function reloadConfig(): void {
  getConfig().reload();
}

/**
 * Validate configuration
 */
export function validateConfig(): boolean {
  return getConfig().validate();
}

// Export the CoreConfig class for testing
export { CoreConfig }; 