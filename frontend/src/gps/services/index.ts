// GPS service migrated from Django backend
// Based on skyguard/apps/gps/services.py

import { 
  ILocationService, 
  IEventService, 
  GPSDevice, 
  LocationData, 
  EventData,
  Point
} from '../../core/interfaces';

import { 
  ExtendedGPSDevice,
  ExtendedGPSLocation,
  ExtendedGPSEvent,
  NetworkEvent,
  NetworkSession,
  GeoFence,
  Vehicle,
  Driver
} from '../interfaces';

import { 
  DeviceNotFoundException, 
  InvalidCoordinatesException
} from '../../core/exceptions';

import { 
  validateCoordinates
} from '../../core/utils';

import { getConfig } from '../../core/config';

/**
 * GPS Service implementation
 */
export class GPSService implements ILocationService, IEventService {
  private config = getConfig();
  private apiBaseUrl: string;

  constructor() {
    this.apiBaseUrl = this.config.get('api.baseUrl', 'http://localhost:8000');
  }

  /**
   * Process location data from device
   */
  async processLocation(device: GPSDevice, locationData: LocationData): Promise<void> {
    try {
      // Validate coordinates
      if (!validateCoordinates(locationData.latitude, locationData.longitude)) {
        throw new InvalidCoordinatesException(locationData.latitude, locationData.longitude);
      }

      // Create location object
      const location: ExtendedGPSLocation = {
        id: 0, // Will be set by backend
        device,
        timestamp: locationData.timestamp,
        position: { x: locationData.longitude, y: locationData.latitude },
        speed: locationData.speed,
        course: locationData.course,
        altitude: locationData.altitude,
        satellites: locationData.satellites,
        accuracy: locationData.accuracy,
        hdop: locationData.hdop,
        pdop: locationData.pdop,
        fix_quality: locationData.fix_quality,
        fix_type: locationData.fix_type,
        created_at: new Date().toISOString()
      };

      // Send to backend
      await this.sendLocationToBackend(location);

      // Update device position
      await this.updateDevicePosition(device.imei, location.position);

      // Log location processing
      console.log(`Processed location for device ${device.imei}: ${locationData.latitude}, ${locationData.longitude}`);

    } catch (error) {
      console.error(`Error processing location for device ${device.imei}:`, error);
      throw error;
    }
  }

  /**
   * Process event data from device
   */
  async processEvent(device: GPSDevice, eventData: EventData): Promise<void> {
    try {
      // Create event object
      const event: ExtendedGPSEvent = {
        id: 0, // Will be set by backend
        device,
        type: eventData.type,
        position: eventData.position,
        speed: eventData.speed,
        course: eventData.course,
        altitude: eventData.altitude,
        timestamp: eventData.timestamp,
        odometer: eventData.odometer,
        raw_data: JSON.stringify(eventData),
        source: eventData.source,
        text: eventData.text,
        inputs: eventData.inputs,
        outputs: eventData.outputs,
        input_changes: eventData.input_changes,
        output_changes: eventData.output_changes,
        alarm_changes: eventData.alarm_changes,
        changes_description: eventData.changes_description,
        created_at: new Date().toISOString()
      };

      // Send to backend
      await this.sendEventToBackend(event);

      // Handle specific event types
      await this.handleSpecificEvent(device, event);

      // Log event processing
      console.log(`Processed event ${eventData.type} for device ${device.imei}`);

    } catch (error) {
      console.error(`Error processing event for device ${device.imei}:`, error);
      throw error;
    }
  }

  /**
   * Get device history
   */
  async getDeviceHistory(imei: number, startTime: string, endTime: string): Promise<LocationData[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/gps/devices/${imei}/history/?start_time=${startTime}&end_time=${endTime}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new DeviceNotFoundException(imei);
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.locations || [];

    } catch (error) {
      console.error(`Error getting device history for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Get device events
   */
  async getDeviceEvents(imei: number, eventType?: string): Promise<EventData[]> {
    try {
      let url = `${this.apiBaseUrl}/api/gps/devices/${imei}/events/`;
      if (eventType) {
        url += `?event_type=${eventType}`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new DeviceNotFoundException(imei);
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.events || [];

    } catch (error) {
      console.error(`Error getting device events for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Get all devices
   */
  async getAllDevices(): Promise<ExtendedGPSDevice[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/gps/devices/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.devices || [];

    } catch (error) {
      console.error('Error getting all devices:', error);
      throw error;
    }
  }

  /**
   * Get device by IMEI
   */
  async getDevice(imei: number): Promise<ExtendedGPSDevice | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/gps/devices/${imei}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.device;

    } catch (error) {
      console.error(`Error getting device ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Update device position
   */
  async updateDevicePosition(imei: number, position: Point): Promise<void> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/gps/devices/${imei}/position/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          latitude: position.y,
          longitude: position.x
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error(`Error updating device position for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Get device locations
   */
  async getDeviceLocations(imei: number, startTime?: string, endTime?: string): Promise<ExtendedGPSLocation[]> {
    try {
      let url = `${this.apiBaseUrl}/api/gps/devices/${imei}/locations/`;
      const params = new URLSearchParams();
      
      if (startTime) params.append('start_time', startTime);
      if (endTime) params.append('end_time', endTime);
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.locations || [];

    } catch (error) {
      console.error(`Error getting device locations for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Get device events
   */
  async getDeviceEventsExtended(imei: number, eventType?: string): Promise<ExtendedGPSEvent[]> {
    try {
      let url = `${this.apiBaseUrl}/api/gps/devices/${imei}/events/`;
      if (eventType) {
        url += `?event_type=${eventType}`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.events || [];

    } catch (error) {
      console.error(`Error getting device events for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Get network events for device
   */
  async getDeviceNetworkEvents(imei: number): Promise<NetworkEvent[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/gps/devices/${imei}/network-events/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.network_events || [];

    } catch (error) {
      console.error(`Error getting network events for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Get active sessions for device
   */
  async getDeviceSessions(imei: number): Promise<NetworkSession[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/gps/devices/${imei}/sessions/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.sessions || [];

    } catch (error) {
      console.error(`Error getting sessions for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Get geofences for device
   */
  async getDeviceGeofences(imei: number): Promise<GeoFence[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/gps/devices/${imei}/geofences/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.geofences || [];

    } catch (error) {
      console.error(`Error getting geofences for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Get vehicle for device
   */
  async getDeviceVehicle(imei: number): Promise<Vehicle | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/gps/devices/${imei}/vehicle/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.vehicle;

    } catch (error) {
      console.error(`Error getting vehicle for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Get driver for device
   */
  async getDeviceDriver(imei: number): Promise<Driver | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/gps/devices/${imei}/driver/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.driver;

    } catch (error) {
      console.error(`Error getting driver for ${imei}:`, error);
      throw error;
    }
  }

  /**
   * Send location to backend
   */
  private async sendLocationToBackend(location: ExtendedGPSLocation): Promise<void> {
    const response = await fetch(`${this.apiBaseUrl}/api/gps/locations/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify(location)
    });

    if (!response.ok) {
      throw new Error(`Failed to send location: HTTP ${response.status}`);
    }
  }

  /**
   * Send event to backend
   */
  private async sendEventToBackend(event: ExtendedGPSEvent): Promise<void> {
    const response = await fetch(`${this.apiBaseUrl}/api/gps/events/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify(event)
    });

    if (!response.ok) {
      throw new Error(`Failed to send event: HTTP ${response.status}`);
    }
  }

  /**
   * Handle specific event types
   */
  private async handleSpecificEvent(device: GPSDevice, event: ExtendedGPSEvent): Promise<void> {
    switch (event.type) {
      case 'ALARM':
        await this.handleAlarmEvent(device, event);
        break;
      case 'GEOFENCE_ENTRY':
      case 'GEOFENCE_EXIT':
        await this.handleGeofenceEvent(device, event);
        break;
      case 'SPEED_LIMIT':
        await this.handleSpeedLimitEvent(device, event);
        break;
      case 'BATTERY_LOW':
        await this.handleBatteryEvent(device, event);
        break;
      default:
        // Handle other event types
        break;
    }
  }

  /**
   * Handle alarm events
   */
  private async handleAlarmEvent(device: GPSDevice, event: ExtendedGPSEvent): Promise<void> {
    // Send notification
    const notificationService = await import('../../core/factory').then(m => m.getNotificationService());
    await notificationService.sendDeviceAlarm(device, 'ALARM', event.position);
  }

  /**
   * Handle geofence events
   */
  private async handleGeofenceEvent(device: GPSDevice, event: ExtendedGPSEvent): Promise<void> {
    // Send notification
    const notificationService = await import('../../core/factory').then(m => m.getNotificationService());
    await notificationService.sendDeviceAlarm(device, 'GEOFENCE', event.position);
  }

  /**
   * Handle speed limit events
   */
  private async handleSpeedLimitEvent(device: GPSDevice, event: ExtendedGPSEvent): Promise<void> {
    // Send notification
    const notificationService = await import('../../core/factory').then(m => m.getNotificationService());
    await notificationService.sendDeviceAlarm(device, 'SPEED', event.position);
  }

  /**
   * Handle battery events
   */
  private async handleBatteryEvent(device: GPSDevice, event: ExtendedGPSEvent): Promise<void> {
    // Send notification
    const notificationService = await import('../../core/factory').then(m => m.getNotificationService());
    await notificationService.sendDeviceAlarm(device, 'BATTERY', event.position);
  }

  /**
   * Get authentication token
   */
  private getAuthToken(): string {
    return localStorage.getItem('auth_token') || '';
  }
}

// Export singleton instance
export const gpsService = new GPSService(); 