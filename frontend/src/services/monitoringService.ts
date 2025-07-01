import api from './api';

export interface AlarmLog {
  id: number;
  device_id: number;
  device_name: string;
  alarm_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  acknowledged: boolean;
  acknowledged_by?: number;
  acknowledged_at?: string;
  location?: {
    latitude: number;
    longitude: number;
  };
}

export interface SystemHealth {
  overall_status: 'healthy' | 'warning' | 'critical';
  components: {
    database: 'healthy' | 'warning' | 'critical';
    gps_server: 'healthy' | 'warning' | 'critical';
    communication: 'healthy' | 'warning' | 'critical';
    storage: 'healthy' | 'warning' | 'critical';
  };
  metrics: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    active_connections: number;
    error_rate: number;
  };
  last_check: string;
}

export interface PerformanceMetrics {
  device_id: number;
  device_name: string;
  response_time: number;
  uptime: number;
  error_count: number;
  last_activity: string;
  connection_quality: number;
  battery_level?: number;
  signal_strength?: number;
}

export interface MonitoringAlert {
  id: number;
  type: 'system' | 'device' | 'network' | 'security';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  timestamp: string;
  resolved: boolean;
  resolved_at?: string;
  resolved_by?: number;
  metadata?: any;
}

class MonitoringService {
  // Alarm Management
  async getAlarmLogs(filters?: {
    device_id?: number;
    alarm_type?: string;
    severity?: string;
    acknowledged?: boolean;
    start_date?: string;
    end_date?: string;
  }): Promise<AlarmLog[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.device_id) params.append('device_id', filters.device_id.toString());
      if (filters?.alarm_type) params.append('alarm_type', filters.alarm_type);
      if (filters?.severity) params.append('severity', filters.severity);
      if (filters?.acknowledged !== undefined) params.append('acknowledged', filters.acknowledged.toString());
      if (filters?.start_date) params.append('start_date', filters.start_date);
      if (filters?.end_date) params.append('end_date', filters.end_date);
      
      const response = await api.get(`/api/monitoring/alarms/?${params.toString()}`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching alarm logs:', error);
      return [];
    }
  }

  async acknowledgeAlarm(alarmId: number): Promise<boolean> {
    try {
      const response = await api.post(`/api/monitoring/alarms/${alarmId}/acknowledge/`);
      return response.data.success || false;
    } catch (error) {
      console.error('Error acknowledging alarm:', error);
      return false;
    }
  }

  async getActiveAlarms(): Promise<AlarmLog[]> {
    try {
      const response = await api.get('/api/monitoring/alarms/active/');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching active alarms:', error);
      return [];
    }
  }

  async createAlarm(data: {
    device_id: number;
    alarm_type: string;
    severity: string;
    message: string;
    location?: { latitude: number; longitude: number };
  }): Promise<AlarmLog | null> {
    try {
      const response = await api.post('/api/monitoring/alarms/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating alarm:', error);
      return null;
    }
  }

  // System Health Monitoring
  async getSystemHealth(): Promise<SystemHealth | null> {
    try {
      const response = await api.get('/api/monitoring/health/');
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      return null;
    }
  }

  async getPerformanceMetrics(deviceId?: number): Promise<PerformanceMetrics[]> {
    try {
      const url = deviceId ? `/api/monitoring/performance/${deviceId}/` : '/api/monitoring/performance/';
      const response = await api.get(url);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      return [];
    }
  }

  async getDeviceHealth(deviceId: number): Promise<any> {
    try {
      const response = await api.get(`/api/monitoring/devices/${deviceId}/health/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching device health:', error);
      return null;
    }
  }

  // Monitoring Alerts
  async getMonitoringAlerts(filters?: {
    type?: string;
    severity?: string;
    resolved?: boolean;
    start_date?: string;
    end_date?: string;
  }): Promise<MonitoringAlert[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.append('type', filters.type);
      if (filters?.severity) params.append('severity', filters.severity);
      if (filters?.resolved !== undefined) params.append('resolved', filters.resolved.toString());
      if (filters?.start_date) params.append('start_date', filters.start_date);
      if (filters?.end_date) params.append('end_date', filters.end_date);
      
      const response = await api.get(`/api/monitoring/alerts/?${params.toString()}`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching monitoring alerts:', error);
      return [];
    }
  }

  async resolveAlert(alertId: number): Promise<boolean> {
    try {
      const response = await api.post(`/api/monitoring/alerts/${alertId}/resolve/`);
      return response.data.success || false;
    } catch (error) {
      console.error('Error resolving alert:', error);
      return false;
    }
  }

  async createMonitoringAlert(data: {
    type: string;
    severity: string;
    title: string;
    message: string;
    metadata?: any;
  }): Promise<MonitoringAlert | null> {
    try {
      const response = await api.post('/api/monitoring/alerts/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating monitoring alert:', error);
      return null;
    }
  }

  // Real-time Monitoring
  startHealthMonitoring(
    callback: (health: SystemHealth) => void,
    interval: number = 30000
  ): () => void {
    let isActive = true;
    let timeoutId: NodeJS.Timeout | null = null;
    
    const poll = async () => {
      if (!isActive) return;
      
      try {
        const health = await this.getSystemHealth();
        if (health && isActive) {
          setTimeout(() => {
            if (isActive) callback(health);
          }, 50);
        }
      } catch (error) {
        console.error('Error polling health monitoring:', error);
        if (isActive) {
          const backoffDelay = Math.min(interval * 2, 60000);
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

  startAlarmMonitoring(
    callback: (alarms: AlarmLog[]) => void,
    interval: number = 10000
  ): () => void {
    let isActive = true;
    let timeoutId: NodeJS.Timeout | null = null;
    
    const poll = async () => {
      if (!isActive) return;
      
      try {
        const alarms = await this.getActiveAlarms();
        if (isActive) {
          setTimeout(() => {
            if (isActive) callback(alarms);
          }, 50);
        }
      } catch (error) {
        console.error('Error polling alarm monitoring:', error);
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
  async getMonitoringConfig(): Promise<any> {
    try {
      const response = await api.get('/api/monitoring/config/');
      return response.data;
    } catch (error) {
      console.error('Error fetching monitoring config:', error);
      return null;
    }
  }

  async updateMonitoringConfig(config: any): Promise<boolean> {
    try {
      const response = await api.patch('/api/monitoring/config/', config);
      return response.data.success || false;
    } catch (error) {
      console.error('Error updating monitoring config:', error);
      return false;
    }
  }

  // Statistics and Reports
  async getMonitoringStats(days: number = 7): Promise<any> {
    try {
      const response = await api.get(`/api/monitoring/stats/?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching monitoring stats:', error);
      return null;
    }
  }

  async exportAlarmReport(
    startDate: string,
    endDate: string,
    format: 'csv' | 'json' = 'csv'
  ): Promise<Blob | null> {
    try {
      const response = await api.get('/api/monitoring/alarms/export/', {
        params: { start_date: startDate, end_date: endDate, format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting alarm report:', error);
      return null;
    }
  }

  // Email Notifications
  async sendAlarmEmail(alarmId: number, recipients: string[]): Promise<boolean> {
    try {
      const response = await api.post(`/api/monitoring/alarms/${alarmId}/email/`, {
        recipients
      });
      return response.data.success || false;
    } catch (error) {
      console.error('Error sending alarm email:', error);
      return false;
    }
  }

  async getEmailTemplates(): Promise<any[]> {
    try {
      const response = await api.get('/api/monitoring/email/templates/');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching email templates:', error);
      return [];
    }
  }

  async updateEmailTemplate(templateId: number, template: any): Promise<boolean> {
    try {
      const response = await api.patch(`/api/monitoring/email/templates/${templateId}/`, template);
      return response.data.success || false;
    } catch (error) {
      console.error('Error updating email template:', error);
      return false;
    }
  }
}

export const monitoringService = new MonitoringService(); 