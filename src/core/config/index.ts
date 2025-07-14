/**
 * Core configuration management for the GPS tracking system.
 * Migrated from backend Django configuration to TypeScript.
 */

interface ConfigData {
  [key: string]: any;
}

class ConfigurationManager {
  private config: ConfigData = {};
  private defaults: ConfigData = {};

  constructor() {
    this.loadDefaults();
    this.loadFromLocalStorage();
  }

  private loadDefaults(): void {
    this.defaults = {
      // API Configuration
      'api.baseUrl': 'http://localhost:8000/api',
      'api.timeout': 30000,
      'api.retryAttempts': 3,
      'api.retryDelay': 1000,

      // Authentication
      'auth.token': '',
      'auth.refreshToken': '',
      'auth.expiresAt': null,
      'auth.autoRefresh': true,

      // GPS Configuration
      'gps.updateInterval': 5000,
      'gps.maxHistoryPoints': 1000,
      'gps.defaultZoom': 12,
      'gps.defaultCenter': { lat: 19.4326, lng: -99.1332 }, // Mexico City

      // WebSocket Configuration
      'websocket.url': 'ws://localhost:8000/ws/',
      'websocket.reconnectInterval': 5000,
      'websocket.maxReconnectAttempts': 10,

      // Map Configuration
      'map.provider': 'openstreetmap',
      'map.apiKey': '',
      'map.tileUrl': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      'map.attribution': '© OpenStreetMap contributors',

      // Notification Configuration
      'notifications.enabled': true,
      'notifications.sound': true,
      'notifications.desktop': true,
      'notifications.position': 'top-right',

      // Theme Configuration
      'theme.mode': 'light',
      'theme.primaryColor': '#1976d2',
      'theme.secondaryColor': '#dc004e',

      // Language Configuration
      'language.locale': 'en',
      'language.fallback': 'en',

      // Performance Configuration
      'performance.cacheEnabled': true,
      'performance.cacheSize': 100,
      'performance.debounceDelay': 300,
      'performance.throttleDelay': 100,

      // Debug Configuration
      'debug.enabled': false,
      'debug.level': 'info',
      'debug.logToConsole': true,
      'debug.logToFile': false,

      // Security Configuration
      'security.requireSSL': false,
      'security.sessionTimeout': 3600,
      'security.maxLoginAttempts': 5,

      // Database Configuration
      'database.type': 'localStorage',
      'database.name': 'gps_tracker',
      'database.version': 1,

      // Export Configuration
      'export.format': 'json',
      'export.includeMetadata': true,
      'export.compression': false,

      // Backup Configuration
      'backup.enabled': true,
      'backup.autoBackup': true,
      'backup.interval': 86400, // 24 hours
      'backup.maxBackups': 10,

      // Analytics Configuration
      'analytics.enabled': true,
      'analytics.trackingId': '',
      'analytics.anonymize': true,

      // Maintenance Configuration
      'maintenance.autoCheck': true,
      'maintenance.checkInterval': 3600, // 1 hour
      'maintenance.notifyOnIssues': true,

      // Real-time Configuration
      'realtime.enabled': true,
      'realtime.updateInterval': 1000,
      'realtime.maxConnections': 100,

      // Geofencing Configuration
      'geofencing.enabled': true,
      'geofencing.maxGeofences': 50,
      'geofencing.defaultRadius': 100,

      // Alert Configuration
      'alerts.enabled': true,
      'alerts.soundEnabled': true,
      'alerts.visualEnabled': true,
      'alerts.emailEnabled': false,

      // Route Configuration
      'routes.enabled': true,
      'routes.maxRoutes': 20,
      'routes.autoOptimize': true,

      // Driver Configuration
      'drivers.enabled': true,
      'drivers.maxDrivers': 100,
      'drivers.requireLicense': true,

      // Vehicle Configuration
      'vehicles.enabled': true,
      'vehicles.maxVehicles': 50,
      'vehicles.requireRegistration': true,

      // Report Configuration
      'reports.enabled': true,
      'reports.autoGenerate': false,
      'reports.defaultFormat': 'pdf',

      // Monitoring Configuration
      'monitoring.enabled': true,
      'monitoring.checkInterval': 300, // 5 minutes
      'monitoring.alertThreshold': 0.8,

      // Communication Configuration
      'communication.enabled': true,
      'communication.protocols': ['tcp', 'udp', 'http'],
      'communication.maxRetries': 3,

      // Firmware Configuration
      'firmware.enabled': true,
      'firmware.autoUpdate': false,
      'firmware.checkInterval': 86400, // 24 hours

      // Tracking Configuration
      'tracking.enabled': true,
      'tracking.historyRetention': 30, // days
      'tracking.maxSpeed': 200, // km/h
      'tracking.accuracyThreshold': 10, // meters

      // Subsidies Configuration
      'subsidies.enabled': true,
      'subsidies.autoCalculate': true,
      'subsidies.defaultCurrency': 'MXN',

      // Logging Configuration
      'logging.enabled': true,
      'logging.level': 'info',
      'logging.maxEntries': 10000,
      'logging.retentionDays': 30,

      // Cache Configuration
      'cache.enabled': true,
      'cache.maxSize': 100,
      'cache.ttl': 3600, // 1 hour

      // Network Configuration
      'network.timeout': 10000,
      'network.retryAttempts': 3,
      'network.keepAlive': true,

      // Storage Configuration
      'storage.type': 'localStorage',
      'storage.maxSize': 50, // MB
      'storage.compression': true,

      // UI Configuration
      'ui.animations': true,
      'ui.sidebarCollapsed': false,
      'ui.darkMode': false,
      'ui.compactMode': false,

      // Data Configuration
      'data.syncEnabled': true,
      'data.syncInterval': 300, // 5 minutes
      'data.offlineMode': false,
      'data.maxOfflineData': 1000,

      // Privacy Configuration
      'privacy.dataRetention': 90, // days
      'privacy.anonymizeData': false,
      'privacy.allowAnalytics': true,

      // Compliance Configuration
      'compliance.gdpr': false,
      'compliance.ccpa': false,
      'compliance.dataExport': true,

      // Integration Configuration
      'integrations.enabled': true,
      'integrations.thirdParty': false,
      'integrations.webhooks': false,

      // Custom Configuration
      'custom.enabled': false,
      'custom.endpoints': [],
      'custom.headers': {}
    };
  }

  private loadFromLocalStorage(): void {
    try {
      const stored = localStorage.getItem('gps_config');
      if (stored) {
        this.config = { ...this.defaults, ...JSON.parse(stored) };
      } else {
        this.config = { ...this.defaults };
      }
    } catch (error) {
      console.warn('Failed to load configuration from localStorage:', error);
      this.config = { ...this.defaults };
    }
  }

  private saveToLocalStorage(): void {
    try {
      localStorage.setItem('gps_config', JSON.stringify(this.config));
    } catch (error) {
      console.warn('Failed to save configuration to localStorage:', error);
    }
  }

  /**
   * Get a configuration value.
   */
  get(key: string, defaultValue?: any): any {
    const keys = key.split('.');
    let value = this.config;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return defaultValue !== undefined ? defaultValue : this.defaults[key];
      }
    }

    return value;
  }

  /**
   * Set a configuration value.
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
   * Check if a configuration key exists.
   */
  has(key: string): boolean {
    const keys = key.split('.');
    let current = this.config;

    for (const k of keys) {
      if (!(k in current)) {
        return false;
      }
      current = current[k];
    }

    return true;
  }

  /**
   * Delete a configuration key.
   */
  delete(key: string): boolean {
    const keys = key.split('.');
    let current = this.config;

    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!(k in current)) {
        return false;
      }
      current = current[k];
    }

    const lastKey = keys[keys.length - 1];
    if (lastKey in current) {
      delete current[lastKey];
      this.saveToLocalStorage();
      return true;
    }

    return false;
  }

  /**
   * Get all configuration as an object.
   */
  getAll(): ConfigData {
    return { ...this.config };
  }

  /**
   * Reset configuration to defaults.
   */
  reset(): void {
    this.config = { ...this.defaults };
    this.saveToLocalStorage();
  }

  /**
   * Update multiple configuration values at once.
   */
  update(updates: ConfigData): void {
    this.config = { ...this.config, ...updates };
    this.saveToLocalStorage();
  }

  /**
   * Get configuration for a specific section.
   */
  getSection(section: string): ConfigData {
    const sectionConfig: ConfigData = {};
    const prefix = `${section}.`;

    for (const key in this.config) {
      if (key.startsWith(prefix)) {
        const subKey = key.substring(prefix.length);
        sectionConfig[subKey] = this.config[key];
      }
    }

    return sectionConfig;
  }

  /**
   * Set configuration for a specific section.
   */
  setSection(section: string, values: ConfigData): void {
    for (const key in values) {
      this.set(`${section}.${key}`, values[key]);
    }
  }

  /**
   * Validate configuration values.
   */
  validate(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Validate required fields
    const requiredFields = [
      'api.baseUrl',
      'auth.token',
      'gps.updateInterval',
      'websocket.url'
    ];

    for (const field of requiredFields) {
      if (!this.get(field)) {
        errors.push(`Missing required configuration: ${field}`);
      }
    }

    // Validate numeric fields
    const numericFields = [
      { key: 'gps.updateInterval', min: 1000, max: 60000 },
      { key: 'api.timeout', min: 1000, max: 120000 },
      { key: 'gps.maxHistoryPoints', min: 100, max: 10000 }
    ];

    for (const field of numericFields) {
      const value = this.get(field.key);
      if (typeof value === 'number' && (value < field.min || value > field.max)) {
        errors.push(`Invalid value for ${field.key}: ${value} (must be between ${field.min} and ${field.max})`);
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Export configuration to JSON.
   */
  export(): string {
    return JSON.stringify(this.config, null, 2);
  }

  /**
   * Import configuration from JSON.
   */
  import(configJson: string): boolean {
    try {
      const imported = JSON.parse(configJson);
      this.config = { ...this.defaults, ...imported };
      this.saveToLocalStorage();
      return true;
    } catch (error) {
      console.error('Failed to import configuration:', error);
      return false;
    }
  }
}

// Create and export singleton instance
const configManager = new ConfigurationManager();

export function getConfig(): ConfigurationManager {
  return configManager;
}

export default configManager; 