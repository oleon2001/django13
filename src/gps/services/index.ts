import { 
  ILocationService, 
  IEventService,
  LocationData, 
  EventData,
  Point
} from '../../core/interfaces';

import {
  GPSDevice,
  NetworkEvent,
  DeviceSession,
  GeoFence,
  Vehicle,
  Driver
} from '../interfaces';

import { 
  DeviceNotFoundException, 
  InvalidCoordinatesException,
  ValidationException 
} from '../../core/exceptions';

import { 
  validateCoordinates, 
  generateUniqueId 
} from '../../core/utils';

import { getConfig } from '../../core/config';

/**
 * GPS Service implementation.
 * Handles location processing, event processing, and device history.
 */
export class GPSService implements ILocationService, IEventService {
  private config = getConfig();
  private baseUrl: string;

  constructor() {
    this.baseUrl = this.config.get('api.baseUrl', 'http://localhost:8000/api');
  }

  /**
   * Process location data for a device.
   */
  async processLocation(device: GPSDevice, locationData: LocationData): Promise<void> {
    try {
      if (!validateCoordinates(locationData.latitude, locationData.longitude)) {
        throw new InvalidCoordinatesException(locationData.latitude, locationData.longitude);
      }

      const response = await fetch(`${this.baseUrl}/gps/location/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify({
          device_imei: device.imei,
          ...locationData
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to process location: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error processing location:', error);
      throw error;
    }
  }

  /**
   * Get device location history.
   */
  async getDeviceHistory(imei: string, startTime: Date, endTime: Date): Promise<LocationData[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/gps/device/${imei}/history/?start=${startTime.toISOString()}&end=${endTime.toISOString()}`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.get('auth.token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to get device history: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting device history:', error);
      throw error;
    }
  }

  /**
   * Process event data for a device.
   */
  async processEvent(device: GPSDevice, eventData: EventData): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/event/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify({
          device_imei: device.imei,
          ...eventData
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to process event: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error processing event:', error);
      throw error;
    }
  }

  /**
   * Get device events.
   */
  async getDeviceEvents(imei: string, eventType?: string): Promise<EventData[]> {
    try {
      const params = new URLSearchParams();
      if (eventType) {
        params.append('event_type', eventType);
      }

      const response = await fetch(
        `${this.baseUrl}/gps/device/${imei}/events/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.get('auth.token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to get device events: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting device events:', error);
      throw error;
    }
  }

  /**
   * Get all GPS devices.
   */
  async getDevices(): Promise<GPSDevice[]> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/devices/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get devices: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting devices:', error);
      throw error;
    }
  }

  /**
   * Get device by IMEI.
   */
  async getDevice(imei: string): Promise<GPSDevice | null> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/device/${imei}/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`Failed to get device: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting device:', error);
      throw error;
    }
  }

  /**
   * Get device connections.
   */
  async getDeviceConnections(imei: string): Promise<DeviceSession[]> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/device/${imei}/connections/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get device connections: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting device connections:', error);
      throw error;
    }
  }

  /**
   * Get device connection statistics.
   */
  async getDeviceConnectionStats(imei: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/device/${imei}/connection-stats/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get device connection stats: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting device connection stats:', error);
      throw error;
    }
  }

  /**
   * Get device current status.
   */
  async getDeviceCurrentStatus(imei: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/device/${imei}/status/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get device status: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting device status:', error);
      throw error;
    }
  }

  /**
   * Get active sessions.
   */
  async getActiveSessions(): Promise<DeviceSession[]> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/sessions/active/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get active sessions: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting active sessions:', error);
      throw error;
    }
  }

  /**
   * Cleanup old sessions.
   */
  async cleanupSessions(daysOld: number = 7): Promise<number> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/sessions/cleanup/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify({ days_old: daysOld })
      });

      if (!response.ok) {
        throw new Error(`Failed to cleanup sessions: ${response.statusText}`);
      }

      const result = await response.json();
      return result.deleted_count || 0;
    } catch (error) {
      console.error('Error cleaning up sessions:', error);
      throw error;
    }
  }

  /**
   * Check all devices status.
   */
  async checkAllDevicesStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/devices/check-status/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to check devices status: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking devices status:', error);
      throw error;
    }
  }

  /**
   * Get devices activity status.
   */
  async getDevicesActivityStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/devices/activity-status/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get devices activity status: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting devices activity status:', error);
      throw error;
    }
  }

  /**
   * Get real-time positions.
   */
  async getRealTimePositions(): Promise<GPSDevice[]> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/positions/realtime/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get real-time positions: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting real-time positions:', error);
      throw error;
    }
  }

  /**
   * Get device trail.
   */
  async getDeviceTrail(imei: string, startTime?: Date, endTime?: Date): Promise<LocationData[]> {
    try {
      const params = new URLSearchParams();
      if (startTime) {
        params.append('start', startTime.toISOString());
      }
      if (endTime) {
        params.append('end', endTime.toISOString());
      }

      const response = await fetch(
        `${this.baseUrl}/gps/device/${imei}/trail/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.get('auth.token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to get device trail: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting device trail:', error);
      throw error;
    }
  }

  /**
   * Test device connection.
   */
  async testDeviceConnection(imei: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/device/${imei}/test-connection/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to test device connection: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error testing device connection:', error);
      throw error;
    }
  }

  /**
   * Get vehicles.
   */
  async getVehicles(): Promise<Vehicle[]> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/vehicles/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get vehicles: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting vehicles:', error);
      throw error;
    }
  }

  /**
   * Get drivers.
   */
  async getDrivers(): Promise<Driver[]> {
    try {
      const response = await fetch(`${this.baseUrl}/gps/drivers/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get drivers: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting drivers:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const gpsService = new GPSService(); 