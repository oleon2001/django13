// Core service factory migrated from Django backend
// Based on skyguard/apps/core/factory.py

import { 
  IDeviceRepository, 
  ILocationService, 
  IEventService, 
  INotificationService,
  ISecurityService,
  IConnectionService,
  ILoggingService,
  IHealthCheckService,
  IConfigurationService,
  IAnalyticsService,
  IReportService
} from '../interfaces';

import { getConfig } from '../config';

/**
 * Service factory for creating and managing service instances
 */
class ServiceFactory {
  private static instances: Map<string, any> = new Map();
  private static initialized = false;

  /**
   * Initialize the service factory
   */
  static initialize(): void {
    if (this.initialized) {
      return;
    }

    try {
      // Initialize core services
      this.initializeCoreServices();
      
      // Initialize GPS services
      this.initializeGPSServices();
      
      // Initialize communication services
      this.initializeCommunicationServices();
      
      // Initialize monitoring services
      this.initializeMonitoringServices();
      
      // Initialize report services
      this.initializeReportServices();
      
      this.initialized = true;
      console.log('Service factory initialized successfully');
    } catch (error) {
      console.error('Failed to initialize service factory:', error);
      throw error;
    }
  }

  /**
   * Initialize core services
   */
  private static initializeCoreServices(): void {
    // Configuration service is already available via getConfig()
    this.instances.set('configuration', getConfig());
  }

  /**
   * Initialize GPS services
   */
  private static initializeGPSServices(): void {
    // Device repository
    this.instances.set('deviceRepository', this.createDeviceRepository());
    
    // Location service
    this.instances.set('locationService', this.createLocationService());
    
    // Event service
    this.instances.set('eventService', this.createEventService());
    
    // Analytics service
    this.instances.set('analyticsService', this.createAnalyticsService());
  }

  /**
   * Initialize communication services
   */
  private static initializeCommunicationServices(): void {
    // Notification service
    this.instances.set('notificationService', this.createNotificationService());
    
    // Security service
    this.instances.set('securityService', this.createSecurityService());
    
    // Connection service
    this.instances.set('connectionService', this.createConnectionService());
  }

  /**
   * Initialize monitoring services
   */
  private static initializeMonitoringServices(): void {
    // Logging service
    this.instances.set('loggingService', this.createLoggingService());
    
    // Health check service
    this.instances.set('healthCheckService', this.createHealthCheckService());
  }

  /**
   * Initialize report services
   */
  private static initializeReportServices(): void {
    // Report service
    this.instances.set('reportService', this.createReportService());
  }

  /**
   * Create device repository instance
   */
  private static createDeviceRepository(): IDeviceRepository {
    // This will be implemented in the GPS module
    return {
      getDevice: async () => null,
      getAllDevices: async () => [],
      saveDevice: async () => {},
      updateDevicePosition: async () => {},
      getDeviceLocations: async () => [],
      getDeviceEvents: async () => []
    };
  }

  /**
   * Create location service instance
   */
  private static createLocationService(): ILocationService {
    // This will be implemented in the GPS module
    return {
      processLocation: async () => {},
      getDeviceHistory: async () => []
    };
  }

  /**
   * Create event service instance
   */
  private static createEventService(): IEventService {
    // This will be implemented in the GPS module
    return {
      processEvent: async () => {},
      getDeviceEvents: async () => []
    };
  }

  /**
   * Create notification service instance
   */
  private static createNotificationService(): INotificationService {
    // This will be implemented in the communication module
    return {
      sendNotification: async () => ({ success: false }),
      sendDeviceAlarm: async () => {}
    };
  }

  /**
   * Create security service instance
   */
  private static createSecurityService(): ISecurityService {
    // This will be implemented in the security module
    return {
      signCommand: async () => ({}),
      verifyCommand: async () => ({}),
      getCommandRiskLevel: () => 'LOW'
    };
  }

  /**
   * Create connection service instance
   */
  private static createConnectionService(): IConnectionService {
    // This will be implemented in the communication module
    return {
      registerConnection: async () => ({ id: '', device: {} as any, start_time: '', ip_address: '', port: 0, protocol: '', is_active: false, last_activity: '', bytes_sent: 0, bytes_received: 0, packets_sent: 0, packets_received: 0, created_at: '', updated_at: '' }),
      registerDisconnection: async () => {},
      getActiveSessions: async () => [],
      cleanupOldSessions: async () => 0
    };
  }

  /**
   * Create logging service instance
   */
  private static createLoggingService(): ILoggingService {
    // This will be implemented in the monitoring module
    return {
      logDeviceEvent: async () => {},
      logSystemEvent: async () => {},
      getDeviceLogs: async () => []
    };
  }

  /**
   * Create health check service instance
   */
  private static createHealthCheckService(): IHealthCheckService {
    // This will be implemented in the monitoring module
    return {
      checkSystemHealth: async () => ({}),
      checkDeviceHealth: async () => ({}),
      checkDatabaseHealth: async () => ({}),
      checkNetworkHealth: async () => ({})
    };
  }

  /**
   * Create analytics service instance
   */
  private static createAnalyticsService(): IAnalyticsService {
    // This will be implemented in the analytics module
    return {
      generateRealTimeMetrics: async () => ({
        total_devices: 0,
        online_devices: 0,
        offline_devices: 0,
        avg_speed: 0,
        max_speed: 0,
        total_distance: 0,
        alerts_count: 0,
        battery_avg: 0,
        signal_avg: 0,
        anomalies_detected: 0,
        efficiency_score: 0
      }),
      analyzeDevicePerformance: async () => ({
        device_imei: '',
        total_locations: 0,
        avg_speed: 0,
        max_speed: 0,
        distance_traveled: 0,
        uptime_percentage: 0,
        battery_health: '',
        signal_quality: '',
        anomaly_score: 0,
        efficiency_rating: ''
      }),
      detectDrivingPatterns: async () => ({})
    };
  }

  /**
   * Create report service instance
   */
  private static createReportService(): IReportService {
    // This will be implemented in the reports module
    return {
      generateReport: async () => new Blob(),
      getAvailableReports: async () => []
    };
  }

  /**
   * Get service instance by name
   */
  static getService<T>(serviceName: string): T {
    this.ensureInitialized();
    
    const service = this.instances.get(serviceName);
    if (!service) {
      throw new Error(`Service '${serviceName}' not found`);
    }
    
    return service as T;
  }

  /**
   * Get device repository
   */
  static getDeviceRepository(): IDeviceRepository {
    return this.getService<IDeviceRepository>('deviceRepository');
  }

  /**
   * Get location service
   */
  static getLocationService(): ILocationService {
    return this.getService<ILocationService>('locationService');
  }

  /**
   * Get event service
   */
  static getEventService(): IEventService {
    return this.getService<IEventService>('eventService');
  }

  /**
   * Get notification service
   */
  static getNotificationService(): INotificationService {
    return this.getService<INotificationService>('notificationService');
  }

  /**
   * Get security service
   */
  static getSecurityService(): ISecurityService {
    return this.getService<ISecurityService>('securityService');
  }

  /**
   * Get connection service
   */
  static getConnectionService(): IConnectionService {
    return this.getService<IConnectionService>('connectionService');
  }

  /**
   * Get logging service
   */
  static getLoggingService(): ILoggingService {
    return this.getService<ILoggingService>('loggingService');
  }

  /**
   * Get health check service
   */
  static getHealthCheckService(): IHealthCheckService {
    return this.getService<IHealthCheckService>('healthCheckService');
  }

  /**
   * Get configuration service
   */
  static getConfigurationService(): IConfigurationService {
    return this.getService<IConfigurationService>('configuration');
  }

  /**
   * Get analytics service
   */
  static getAnalyticsService(): IAnalyticsService {
    return this.getService<IAnalyticsService>('analyticsService');
  }

  /**
   * Get report service
   */
  static getReportService(): IReportService {
    return this.getService<IReportService>('reportService');
  }

  /**
   * Register service instance
   */
  static registerService<T>(name: string, service: T): void {
    this.instances.set(name, service);
  }

  /**
   * Unregister service instance
   */
  static unregisterService(name: string): boolean {
    return this.instances.delete(name);
  }

  /**
   * Reset factory (for testing)
   */
  static reset(): void {
    this.instances.clear();
    this.initialized = false;
  }

  /**
   * Get all registered service names
   */
  static getRegisteredServices(): string[] {
    return Array.from(this.instances.keys());
  }

  /**
   * Ensure factory is initialized
   */
  private static ensureInitialized(): void {
    if (!this.initialized) {
      this.initialize();
    }
  }
}

// Convenience functions
export function getDeviceRepository(): IDeviceRepository {
  return ServiceFactory.getDeviceRepository();
}

export function getLocationService(): ILocationService {
  return ServiceFactory.getLocationService();
}

export function getEventService(): IEventService {
  return ServiceFactory.getEventService();
}

export function getNotificationService(): INotificationService {
  return ServiceFactory.getNotificationService();
}

export function getSecurityService(): ISecurityService {
  return ServiceFactory.getSecurityService();
}

export function getConnectionService(): IConnectionService {
  return ServiceFactory.getConnectionService();
}

export function getLoggingService(): ILoggingService {
  return ServiceFactory.getLoggingService();
}

export function getHealthCheckService(): IHealthCheckService {
  return ServiceFactory.getHealthCheckService();
}

export function getConfigurationService(): IConfigurationService {
  return ServiceFactory.getConfigurationService();
}

export function getAnalyticsService(): IAnalyticsService {
  return ServiceFactory.getAnalyticsService();
}

export function getReportService(): IReportService {
  return ServiceFactory.getReportService();
}

export function getService<T>(serviceName: string): T {
  return ServiceFactory.getService<T>(serviceName);
}

// Export the factory class
export { ServiceFactory }; 