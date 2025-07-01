import api from './api';

export interface GeoFence {
  id: number;
  name: string;
  polygon: {
    coordinates: number[][][];
    type: string;
  };
  owner: number;
  route?: number;
  created_at: string;
  updated_at: string;
}

export interface GeofenceEvent {
  id: number;
  device: {
    id: number;
    name: string;
    imei: number;
  };
  geofence: {
    id: number;
    name: string;
  };
  event_type: 'entry' | 'exit';
  location: {
    latitude: number;
    longitude: number;
  };
  timestamp: string;
}

export interface GeofenceAlert {
  id: number;
  device: {
    id: number;
    name: string;
    imei: number;
  };
  geofence: {
    id: number;
    name: string;
  };
  alert_type: 'entry' | 'exit' | 'duration' | 'speed';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  location: {
    latitude: number;
    longitude: number;
  };
  timestamp: string;
  acknowledged: boolean;
  acknowledged_by?: number;
  acknowledged_at?: string;
}

export interface GeofenceRule {
  id: number;
  geofence: number;
  rule_type: 'entry_allowed' | 'exit_allowed' | 'speed_limit' | 'time_limit' | 'schedule';
  devices: number[];
  value: any;
  created_at: string;
  updated_at: string;
}

export interface GeofenceStatistics {
  geofence: GeoFence;
  date_range: string;
  total_events: number;
  enter_events: number;
  exit_events: number;
  unique_devices: number;
  devices_currently_inside: number;
  events: GeofenceEvent[];
}

export interface MonitoringData {
  geofence: GeoFence;
  devices_inside: number;
  devices_list: any[];
  last_checked: string;
}

class GeofencingService {
  // CRUD Operations
  async getAllGeofences(ownerId?: number, routeId?: number): Promise<GeoFence[]> {
    try {
      const params = new URLSearchParams();
      if (ownerId) params.append('owner_id', ownerId.toString());
      if (routeId) params.append('route_id', routeId.toString());
      
      const response = await api.get(`/api/geofencing/geofences/?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching geofences:', error);
      return [];
    }
  }

  async getGeofence(id: number): Promise<GeoFence | null> {
    try {
      const response = await api.get(`/api/geofencing/geofences/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching geofence:', error);
      return null;
    }
  }

  async createGeofence(data: {
    name: string;
    coordinates: number[][];
    owner: number;
    route?: number;
  }): Promise<GeoFence | null> {
    try {
      const geofenceData = {
        name: data.name,
        polygon: {
          type: 'Polygon',
          coordinates: [data.coordinates]
        },
        owner: data.owner,
        route: data.route
      };
      
      const response = await api.post('/api/geofencing/geofences/', geofenceData);
      return response.data;
    } catch (error) {
      console.error('Error creating geofence:', error);
      return null;
    }
  }

  async updateGeofence(id: number, data: Partial<GeoFence>): Promise<GeoFence | null> {
    try {
      const response = await api.patch(`/api/geofencing/geofences/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating geofence:', error);
      return null;
    }
  }

  async deleteGeofence(id: number): Promise<boolean> {
    try {
      await api.delete(`/api/geofencing/geofences/${id}/`);
      return true;
    } catch (error) {
      console.error('Error deleting geofence:', error);
      return false;
    }
  }

  // Events and Monitoring
  async getGeofenceEvents(
    geofenceId: number,
    startDate?: string,
    endDate?: string
  ): Promise<GeofenceEvent[]> {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const response = await api.get(`/api/geofencing/geofences/${geofenceId}/events/?${params.toString()}`);
      return response.data.data || [];
    } catch (error) {
      console.error('Error fetching geofence events:', error);
      return [];
    }
  }

  async getDevicesInside(geofenceId: number): Promise<any[]> {
    try {
      const response = await api.get(`/api/geofencing/geofences/${geofenceId}/devices_inside/`);
      return response.data.data || [];
    } catch (error) {
      console.error('Error fetching devices inside geofence:', error);
      return [];
    }
  }

  async getGeofenceStatistics(
    geofenceId: number,
    startDate?: string,
    endDate?: string
  ): Promise<GeofenceStatistics | null> {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const response = await api.get(`/api/geofencing/geofences/${geofenceId}/statistics/?${params.toString()}`);
      return response.data.data || null;
    } catch (error) {
      console.error('Error fetching geofence statistics:', error);
      return null;
    }
  }

  async monitorGeofences(): Promise<MonitoringData[]> {
    try {
      const response = await api.get('/api/geofencing/geofences/monitor/');
      return response.data.data || [];
    } catch (error) {
      console.error('Error monitoring geofences:', error);
      return [];
    }
  }

  async checkDeviceInGeofence(deviceId: number, geofenceId: number): Promise<boolean> {
    try {
      const response = await api.post('/api/geofencing/geofences/check_device/', {
        device_id: deviceId,
        geofence_id: geofenceId
      });
      return response.data.is_inside || false;
    } catch (error) {
      console.error('Error checking device in geofence:', error);
      return false;
    }
  }

  // Real-time monitoring with polling
  startGeofenceMonitoring(
    callback: (data: MonitoringData[]) => void,
    interval: number = 10000
  ): () => void {
    let isActive = true;
    let timeoutId: NodeJS.Timeout | null = null;
    
    const poll = async () => {
      if (!isActive) return;
      
      try {
        const data = await this.monitorGeofences();
        if (isActive) {
          setTimeout(() => {
            if (isActive) callback(data);
          }, 50);
        }
      } catch (error) {
        console.error('Error polling geofence monitoring:', error);
        if (isActive) {
          const backoffDelay = Math.min(interval * 2, 30000);
          timeoutId = setTimeout(() => {
            if (isActive) poll();
          }, backoffDelay);
          return;
        }
      }
      
      if (isActive) {
        timeoutId = setTimeout(poll, interval);
      }
    };

    timeoutId = setTimeout(poll, 200);
    
    return () => {
      isActive = false;
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
    };
  }

  // Export functionality
  async exportGeofenceData(
    geofenceId: number,
    startDate: string,
    endDate: string,
    format: 'csv' | 'json' = 'csv'
  ): Promise<Blob | null> {
    try {
      const response = await api.get(`/api/geofencing/geofences/${geofenceId}/export/`, {
        params: { start_date: startDate, end_date: endDate, format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting geofence data:', error);
      return null;
    }
  }
}

export const geofencingService = new GeofencingService(); 