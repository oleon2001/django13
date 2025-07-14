// GPS module index - exports all GPS functionality
// This module provides GPS tracking and device management capabilities

// Interfaces
export * from './interfaces';

// Services
export * from './services';

// Initialize GPS module
import { gpsService } from './services';
import { ServiceFactory } from '../core/factory';

/**
 * Initialize the GPS module
 */
export function initializeGPS(): void {
  try {
    // Register GPS services with the factory
    ServiceFactory.registerService('gpsService', gpsService);
    
    // Register GPS-specific services
    ServiceFactory.registerService('deviceRepository', {
      getDevice: gpsService.getDevice.bind(gpsService),
      getAllDevices: gpsService.getAllDevices.bind(gpsService),
      saveDevice: async () => {}, // Will be implemented
      updateDevicePosition: gpsService.updateDevicePosition.bind(gpsService),
      getDeviceLocations: gpsService.getDeviceLocations.bind(gpsService),
      getDeviceEvents: gpsService.getDeviceEventsExtended.bind(gpsService)
    });

    ServiceFactory.registerService('locationService', {
      processLocation: gpsService.processLocation.bind(gpsService),
      getDeviceHistory: gpsService.getDeviceHistory.bind(gpsService)
    });

    ServiceFactory.registerService('eventService', {
      processEvent: gpsService.processEvent.bind(gpsService),
      getDeviceEvents: gpsService.getDeviceEvents.bind(gpsService)
    });

    console.log('GPS module initialized successfully');
  } catch (error) {
    console.error('Failed to initialize GPS module:', error);
    throw error;
  }
}

/**
 * Check if GPS module is ready
 */
export function isGPSReady(): boolean {
  try {
    return ServiceFactory.getService('gpsService') !== undefined;
  } catch {
    return false;
  }
}

// Auto-initialize when module is imported
if (typeof window !== 'undefined') {
  // Only initialize in browser environment
  initializeGPS();
} 