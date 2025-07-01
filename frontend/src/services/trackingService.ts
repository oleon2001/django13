import api from './api';

export interface TrackingSession {
  id: number;
  device_id: number;
  device_name: string;
  start_time: string;
  end_time?: string;
  status: 'active' | 'completed' | 'paused' | 'cancelled';
  total_distance: number;
  total_duration: number;
  start_location: {
    latitude: number;
    longitude: number;
  };
  end_location?: {
    latitude: number;
    longitude: number;
  };
  waypoints: TrackingWaypoint[];
  metadata?: any;
}

export interface TrackingWaypoint {
  id: number;
  session_id: number;
  latitude: number;
  longitude: number;
  timestamp: string;
  speed: number;
  heading: number;
  altitude?: number;
  accuracy?: number;
  battery_level?: number;
  signal_strength?: number;
}

export interface TrackingRoute {
  id: number;
  name: string;
  description?: string;
  waypoints: {
    latitude: number;
    longitude: number;
    order: number;
  }[];
  total_distance: number;
  estimated_duration: number;
  created_at: string;
  updated_at: string;
}

export interface TrackingCommand {
  id: number;
  device_id: number;
  command_type: string;
  parameters: any;
  status: 'pending' | 'sent' | 'delivered' | 'executed' | 'failed';
  sent_at: string;
  delivered_at?: string;
  executed_at?: string;
  error_message?: string;
}

export interface TrackingStats {
  total_sessions: number;
  active_sessions: number;
  total_distance: number;
  total_duration: number;
  avg_speed: number;
  devices_tracked: number;
  last_24h_sessions: number;
}

class TrackingService {
  // Session Management
  async getTrackingSessions(filters?: {
    device_id?: number;
    status?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<TrackingSession[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.device_id) params.append('device_id', filters.device_id.toString());
      if (filters?.status) params.append('status', filters.status);
      if (filters?.start_date) params.append('start_date', filters.start_date);
      if (filters?.end_date) params.append('end_date', filters.end_date);
      
      const response = await api.get(`/api/tracking/sessions/?${params.toString()}`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching tracking sessions:', error);
      return [];
    }
  }

  async getTrackingSession(sessionId: number): Promise<TrackingSession | null> {
    try {
      const response = await api.get(`/api/tracking/sessions/${sessionId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tracking session:', error);
      return null;
    }
  }

  async startTrackingSession(data: {
    device_id: number;
    start_location: { latitude: number; longitude: number };
    metadata?: any;
  }): Promise<TrackingSession | null> {
    try {
      const response = await api.post('/api/tracking/sessions/', data);
      return response.data;
    } catch (error) {
      console.error('Error starting tracking session:', error);
      return null;
    }
  }

  async endTrackingSession(sessionId: number, endLocation?: { latitude: number; longitude: number }): Promise<boolean> {
    try {
      const data = endLocation ? { end_location: endLocation } : {};
      const response = await api.patch(`/api/tracking/sessions/${sessionId}/end/`, data);
      return response.data.success || false;
    } catch (error) {
      console.error('Error ending tracking session:', error);
      return false;
    }
  }

  async pauseTrackingSession(sessionId: number): Promise<boolean> {
    try {
      const response = await api.patch(`/api/tracking/sessions/${sessionId}/pause/`);
      return response.data.success || false;
    } catch (error) {
      console.error('Error pausing tracking session:', error);
      return false;
    }
  }

  async resumeTrackingSession(sessionId: number): Promise<boolean> {
    try {
      const response = await api.patch(`/api/tracking/sessions/${sessionId}/resume/`);
      return response.data.success || false;
    } catch (error) {
      console.error('Error resuming tracking session:', error);
      return false;
    }
  }

  // Waypoint Management
  async getSessionWaypoints(sessionId: number): Promise<TrackingWaypoint[]> {
    try {
      const response = await api.get(`/api/tracking/sessions/${sessionId}/waypoints/`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching session waypoints:', error);
      return [];
    }
  }

  async addWaypoint(sessionId: number, waypoint: {
    latitude: number;
    longitude: number;
    speed: number;
    heading: number;
    altitude?: number;
    accuracy?: number;
    battery_level?: number;
    signal_strength?: number;
  }): Promise<TrackingWaypoint | null> {
    try {
      const response = await api.post(`/api/tracking/sessions/${sessionId}/waypoints/`, waypoint);
      return response.data;
    } catch (error) {
      console.error('Error adding waypoint:', error);
      return null;
    }
  }

  async getWaypoint(waypointId: number): Promise<TrackingWaypoint | null> {
    try {
      const response = await api.get(`/api/tracking/waypoints/${waypointId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching waypoint:', error);
      return null;
    }
  }

  // Route Management
  async getTrackingRoutes(): Promise<TrackingRoute[]> {
    try {
      const response = await api.get('/api/tracking/routes/');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching tracking routes:', error);
      return [];
    }
  }

  async getTrackingRoute(routeId: number): Promise<TrackingRoute | null> {
    try {
      const response = await api.get(`/api/tracking/routes/${routeId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tracking route:', error);
      return null;
    }
  }

  async createTrackingRoute(data: {
    name: string;
    description?: string;
    waypoints: { latitude: number; longitude: number; order: number }[];
  }): Promise<TrackingRoute | null> {
    try {
      const response = await api.post('/api/tracking/routes/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating tracking route:', error);
      return null;
    }
  }

  async updateTrackingRoute(routeId: number, data: Partial<TrackingRoute>): Promise<TrackingRoute | null> {
    try {
      const response = await api.patch(`/api/tracking/routes/${routeId}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating tracking route:', error);
      return null;
    }
  }

  async deleteTrackingRoute(routeId: number): Promise<boolean> {
    try {
      await api.delete(`/api/tracking/routes/${routeId}/`);
      return true;
    } catch (error) {
      console.error('Error deleting tracking route:', error);
      return false;
    }
  }

  // Command Management
  async getTrackingCommands(deviceId?: number): Promise<TrackingCommand[]> {
    try {
      const url = deviceId ? `/api/tracking/commands/?device_id=${deviceId}` : '/api/tracking/commands/';
      const response = await api.get(url);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching tracking commands:', error);
      return [];
    }
  }

  async sendTrackingCommand(data: {
    device_id: number;
    command_type: string;
    parameters: any;
  }): Promise<TrackingCommand | null> {
    try {
      const response = await api.post('/api/tracking/commands/', data);
      return response.data;
    } catch (error) {
      console.error('Error sending tracking command:', error);
      return null;
    }
  }

  async getCommandStatus(commandId: number): Promise<string> {
    try {
      const response = await api.get(`/api/tracking/commands/${commandId}/status/`);
      return response.data.status || 'unknown';
    } catch (error) {
      console.error('Error fetching command status:', error);
      return 'unknown';
    }
  }

  // Statistics and Analytics
  async getTrackingStats(days: number = 7): Promise<TrackingStats | null> {
    try {
      const response = await api.get(`/api/tracking/stats/?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tracking stats:', error);
      return null;
    }
  }

  async getDeviceTrackingHistory(deviceId: number, startDate: string, endDate: string): Promise<TrackingSession[]> {
    try {
      const params = new URLSearchParams();
      params.append('start_date', startDate);
      params.append('end_date', endDate);
      
      const response = await api.get(`/api/tracking/devices/${deviceId}/history/?${params.toString()}`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching device tracking history:', error);
      return [];
    }
  }

  async getDistanceReport(deviceId: number, startDate: string, endDate: string): Promise<any> {
    try {
      const params = new URLSearchParams();
      params.append('start_date', startDate);
      params.append('end_date', endDate);
      
      const response = await api.get(`/api/tracking/devices/${deviceId}/distance/?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching distance report:', error);
      return null;
    }
  }

  // Real-time Tracking
  startSessionTracking(
    sessionId: number,
    callback: (waypoint: TrackingWaypoint) => void,
    interval: number = 5000
  ): () => void {
    let isActive = true;
    let timeoutId: NodeJS.Timeout | null = null;
    let lastWaypointId = 0;
    
    const poll = async () => {
      if (!isActive) return;
      
      try {
        const waypoints = await this.getSessionWaypoints(sessionId);
        const newWaypoints = waypoints.filter(w => w.id > lastWaypointId);
        
        if (newWaypoints.length > 0) {
          lastWaypointId = Math.max(...newWaypoints.map(w => w.id));
          
          if (isActive) {
            setTimeout(() => {
              if (isActive) {
                newWaypoints.forEach(waypoint => callback(waypoint));
              }
            }, 50);
          }
        }
      } catch (error) {
        console.error('Error polling session tracking:', error);
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
  async exportSessionData(
    sessionId: number,
    format: 'csv' | 'json' | 'gpx' = 'csv'
  ): Promise<Blob | null> {
    try {
      const response = await api.get(`/api/tracking/sessions/${sessionId}/export/`, {
        params: { format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting session data:', error);
      return null;
    }
  }

  async exportRouteData(
    routeId: number,
    format: 'csv' | 'json' | 'gpx' = 'csv'
  ): Promise<Blob | null> {
    try {
      const response = await api.get(`/api/tracking/routes/${routeId}/export/`, {
        params: { format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting route data:', error);
      return null;
    }
  }

  // Configuration
  async getTrackingConfig(): Promise<any> {
    try {
      const response = await api.get('/api/tracking/config/');
      return response.data;
    } catch (error) {
      console.error('Error fetching tracking config:', error);
      return null;
    }
  }

  async updateTrackingConfig(config: any): Promise<boolean> {
    try {
      const response = await api.patch('/api/tracking/config/', config);
      return response.data.success || false;
    } catch (error) {
      console.error('Error updating tracking config:', error);
      return false;
    }
  }
}

export const trackingService = new TrackingService(); 