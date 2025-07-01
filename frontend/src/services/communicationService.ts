import api from './api';

export interface BluetoothDevice {
  id: number;
  name: string;
  address: string;
  device_type: string;
  status: 'connected' | 'disconnected' | 'error';
  last_seen: string;
  signal_strength: number;
  battery_level?: number;
}

export interface SatelliteConnection {
  id: number;
  device_id: number;
  satellite_id: string;
  status: 'connected' | 'disconnected' | 'connecting' | 'error';
  signal_strength: number;
  last_contact: string;
  message_count: number;
  error_count: number;
}

export interface CommunicationMessage {
  id: number;
  device_id: number;
  message_type: 'command' | 'data' | 'status' | 'alert';
  content: string;
  timestamp: string;
  status: 'sent' | 'delivered' | 'failed' | 'pending';
  channel: 'bluetooth' | 'satellite' | 'cellular';
  priority: 'low' | 'medium' | 'high' | 'critical';
}

export interface CommunicationStats {
  total_messages: number;
  successful_messages: number;
  failed_messages: number;
  bluetooth_devices: number;
  satellite_connections: number;
  avg_response_time: number;
  last_24h_messages: number;
}

class CommunicationService {
  // Bluetooth Operations
  async getBluetoothDevices(): Promise<BluetoothDevice[]> {
    try {
      const response = await api.get('/api/communication/bluetooth/devices/');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching bluetooth devices:', error);
      return [];
    }
  }

  async connectBluetoothDevice(deviceId: number): Promise<boolean> {
    try {
      const response = await api.post(`/api/communication/bluetooth/devices/${deviceId}/connect/`);
      return response.data.success || false;
    } catch (error) {
      console.error('Error connecting to bluetooth device:', error);
      return false;
    }
  }

  async disconnectBluetoothDevice(deviceId: number): Promise<boolean> {
    try {
      const response = await api.post(`/api/communication/bluetooth/devices/${deviceId}/disconnect/`);
      return response.data.success || false;
    } catch (error) {
      console.error('Error disconnecting bluetooth device:', error);
      return false;
    }
  }

  async sendBluetoothMessage(deviceId: number, message: string): Promise<boolean> {
    try {
      const response = await api.post(`/api/communication/bluetooth/devices/${deviceId}/send/`, {
        message
      });
      return response.data.success || false;
    } catch (error) {
      console.error('Error sending bluetooth message:', error);
      return false;
    }
  }

  async scanBluetoothDevices(): Promise<BluetoothDevice[]> {
    try {
      const response = await api.post('/api/communication/bluetooth/scan/');
      return response.data.devices || [];
    } catch (error) {
      console.error('Error scanning bluetooth devices:', error);
      return [];
    }
  }

  // Satellite Operations
  async getSatelliteConnections(): Promise<SatelliteConnection[]> {
    try {
      const response = await api.get('/api/communication/satellite/connections/');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching satellite connections:', error);
      return [];
    }
  }

  async connectSatellite(deviceId: number): Promise<boolean> {
    try {
      const response = await api.post(`/api/communication/satellite/connect/`, {
        device_id: deviceId
      });
      return response.data.success || false;
    } catch (error) {
      console.error('Error connecting to satellite:', error);
      return false;
    }
  }

  async disconnectSatellite(connectionId: number): Promise<boolean> {
    try {
      const response = await api.post(`/api/communication/satellite/connections/${connectionId}/disconnect/`);
      return response.data.success || false;
    } catch (error) {
      console.error('Error disconnecting satellite:', error);
      return false;
    }
  }

  async sendSatelliteMessage(connectionId: number, message: string): Promise<boolean> {
    try {
      const response = await api.post(`/api/communication/satellite/connections/${connectionId}/send/`, {
        message
      });
      return response.data.success || false;
    } catch (error) {
      console.error('Error sending satellite message:', error);
      return false;
    }
  }

  async getSatelliteStatus(): Promise<any> {
    try {
      const response = await api.get('/api/communication/satellite/status/');
      return response.data;
    } catch (error) {
      console.error('Error fetching satellite status:', error);
      return null;
    }
  }

  // Message Management
  async getMessages(filters?: {
    device_id?: number;
    message_type?: string;
    channel?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<CommunicationMessage[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.device_id) params.append('device_id', filters.device_id.toString());
      if (filters?.message_type) params.append('message_type', filters.message_type);
      if (filters?.channel) params.append('channel', filters.channel);
      if (filters?.status) params.append('status', filters.status);
      if (filters?.start_date) params.append('start_date', filters.start_date);
      if (filters?.end_date) params.append('end_date', filters.end_date);
      
      const response = await api.get(`/api/communication/messages/?${params.toString()}`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching messages:', error);
      return [];
    }
  }

  async sendMessage(data: {
    device_id: number;
    message_type: string;
    content: string;
    channel: string;
    priority?: string;
  }): Promise<CommunicationMessage | null> {
    try {
      const response = await api.post('/api/communication/messages/', data);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      return null;
    }
  }

  async getMessageStatus(messageId: number): Promise<string> {
    try {
      const response = await api.get(`/api/communication/messages/${messageId}/status/`);
      return response.data.status || 'unknown';
    } catch (error) {
      console.error('Error fetching message status:', error);
      return 'unknown';
    }
  }

  // Statistics and Monitoring
  async getCommunicationStats(): Promise<CommunicationStats | null> {
    try {
      const response = await api.get('/api/communication/stats/');
      return response.data;
    } catch (error) {
      console.error('Error fetching communication stats:', error);
      return null;
    }
  }

  async getDeviceCommunicationHistory(deviceId: number, days: number = 7): Promise<CommunicationMessage[]> {
    try {
      const response = await api.get(`/api/communication/devices/${deviceId}/history/?days=${days}`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching device communication history:', error);
      return [];
    }
  }

  // Real-time monitoring
  startCommunicationMonitoring(
    callback: (data: { bluetooth: BluetoothDevice[], satellite: SatelliteConnection[] }) => void,
    interval: number = 10000
  ): () => void {
    let isActive = true;
    let timeoutId: NodeJS.Timeout | null = null;
    
    const poll = async () => {
      if (!isActive) return;
      
      try {
        const [bluetoothDevices, satelliteConnections] = await Promise.all([
          this.getBluetoothDevices(),
          this.getSatelliteConnections()
        ]);
        
        if (isActive) {
          setTimeout(() => {
            if (isActive) callback({ bluetooth: bluetoothDevices, satellite: satelliteConnections });
          }, 50);
        }
      } catch (error) {
        console.error('Error polling communication monitoring:', error);
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

  // Configuration
  async getCommunicationConfig(): Promise<any> {
    try {
      const response = await api.get('/api/communication/config/');
      return response.data;
    } catch (error) {
      console.error('Error fetching communication config:', error);
      return null;
    }
  }

  async updateCommunicationConfig(config: any): Promise<boolean> {
    try {
      const response = await api.patch('/api/communication/config/', config);
      return response.data.success || false;
    } catch (error) {
      console.error('Error updating communication config:', error);
      return false;
    }
  }

  // Health Check
  async checkCommunicationHealth(): Promise<{
    bluetooth: boolean;
    satellite: boolean;
    overall: boolean;
    details: any;
  }> {
    try {
      const response = await api.get('/api/communication/health/');
      return response.data;
    } catch (error) {
      console.error('Error checking communication health:', error);
      return {
        bluetooth: false,
        satellite: false,
        overall: false,
        details: { error: (error as Error).message }
      };
    }
  }
}

export const communicationService = new CommunicationService(); 