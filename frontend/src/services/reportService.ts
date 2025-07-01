import api from './api';

export interface Report {
  id: number;
  title: string;
  type: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  data?: any;
}

export interface RouteReport {
  route: {
    code: number;
    name: string;
  };
  date: string;
  devices_count: number;
  tickets_count: number;
  total_revenue: number;
  total_received: number;
  total_laps: number;
  tickets: any[];
  timesheets: any[];
}

export interface DriverReport {
  driver: {
    id: number;
    name: string;
    full_name: string;
  };
  date_range: string;
  total_tickets: number;
  total_revenue: number;
  total_laps: number;
  avg_laps_per_day: number;
  tickets: any[];
  timesheets: any[];
}

export interface DeviceStatistics {
  device: any;
  total_locations: number;
  total_distance: number;
  avg_speed: number;
  first_location: any;
  last_location: any;
  date_range: string;
}

export interface DailyStatistics {
  date: string;
  devices_processed: number;
  statistics: DeviceStatistics[];
}

class ReportService {
  // Basic CRUD operations
  async getAll(): Promise<Report[]> {
    try {
      const response = await api.get('/api/reports/');
      return response.data;
    } catch (error) {
      console.error('Error fetching reports:', error);
      return [];
    }
  }

  async getById(id: number): Promise<Report | null> {
    try {
      const response = await api.get(`/api/reports/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching report:', error);
      return null;
    }
  }

  async create(data: Partial<Report>): Promise<Report | null> {
    try {
      const response = await api.post('/api/reports/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating report:', error);
      return null;
    }
  }

  async download(id: number): Promise<Blob | null> {
    try {
      const response = await api.get(`/api/reports/${id}/download/`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error downloading report:', error);
      return null;
    }
  }

  // Route Reports
  async getRouteReport(routeId: number, date: string): Promise<RouteReport | null> {
    try {
      const response = await api.get(`/api/reports/routes/${routeId}/report/?date=${date}`);
      return response.data.data || null;
    } catch (error) {
      console.error('Error fetching route report:', error);
      return null;
    }
  }

  async exportRouteCSV(routeId: number, date: string): Promise<Blob | null> {
    try {
      const response = await api.get(`/api/reports/routes/${routeId}/export_csv/?date=${date}`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting route CSV:', error);
      return null;
    }
  }

  // Driver Reports
  async getDriverReport(
    driverId: number,
    startDate: string,
    endDate: string
  ): Promise<DriverReport | null> {
    try {
      const params = new URLSearchParams();
      params.append('start_date', startDate);
      params.append('end_date', endDate);
      
      const response = await api.get(`/api/reports/drivers/${driverId}/report/?${params.toString()}`);
      return response.data.data || null;
    } catch (error) {
      console.error('Error fetching driver report:', error);
      return null;
    }
  }

  // Device Statistics
  async getDeviceStatistics(
    deviceId: number,
    startDate: string,
    endDate: string
  ): Promise<DeviceStatistics | null> {
    try {
      const params = new URLSearchParams();
      params.append('start_date', startDate);
      params.append('end_date', endDate);
      
      const response = await api.get(`/api/reports/statistics/device/${deviceId}/?${params.toString()}`);
      return response.data || null;
    } catch (error) {
      console.error('Error fetching device statistics:', error);
      return null;
    }
  }

  // Daily Statistics
  async calculateDailyStatistics(date: string): Promise<DailyStatistics | null> {
    try {
      const response = await api.post('/api/reports/statistics/calculate_daily/', { date });
      return response.data || null;
    } catch (error) {
      console.error('Error calculating daily statistics:', error);
      return null;
    }
  }

  async getDailyStatistics(date?: string): Promise<DeviceStatistics[]> {
    try {
      const params = new URLSearchParams();
      if (date) params.append('date', date);
      
      const response = await api.get(`/api/reports/statistics/device_stats/?${params.toString()}`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching daily statistics:', error);
      return [];
    }
  }

  // Tickets Management
  async getTickets(filters?: {
    route_code?: number;
    driver_id?: number;
    date_from?: string;
    date_to?: string;
  }): Promise<any[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.route_code) params.append('route_code', filters.route_code.toString());
      if (filters?.driver_id) params.append('driver_id', filters.driver_id.toString());
      if (filters?.date_from) params.append('date_from', filters.date_from);
      if (filters?.date_to) params.append('date_to', filters.date_to);
      
      const response = await api.get(`/api/reports/tickets/?${params.toString()}`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching tickets:', error);
      return [];
    }
  }

  async createTicket(data: any): Promise<any | null> {
    try {
      const response = await api.post('/api/reports/tickets/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating ticket:', error);
      return null;
    }
  }

  // TimeSheets Management
  async getTimeSheets(filters?: {
    device_id?: number;
    driver_id?: number;
    date_from?: string;
    date_to?: string;
  }): Promise<any[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.device_id) params.append('device_id', filters.device_id.toString());
      if (filters?.driver_id) params.append('driver_id', filters.driver_id.toString());
      if (filters?.date_from) params.append('date_from', filters.date_from);
      if (filters?.date_to) params.append('date_to', filters.date_to);
      
      const response = await api.get(`/api/reports/timesheets/?${params.toString()}`);
      return response.data || [];
    } catch (error) {
      console.error('Error fetching timesheets:', error);
      return [];
    }
  }

  async createTimeSheet(data: any): Promise<any | null> {
    try {
      const response = await api.post('/api/reports/timesheets/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating timesheet:', error);
      return null;
    }
  }

  // Routes Management
  async getRoutes(): Promise<any[]> {
    try {
      const response = await api.get('/api/reports/routes/');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching routes:', error);
      return [];
    }
  }

  async getRoute(id: number): Promise<any | null> {
    try {
      const response = await api.get(`/api/reports/routes/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching route:', error);
      return null;
    }
  }

  async createRoute(data: any): Promise<any | null> {
    try {
      const response = await api.post('/api/reports/routes/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating route:', error);
      return null;
    }
  }

  // Drivers Management
  async getDrivers(): Promise<any[]> {
    try {
      const response = await api.get('/api/reports/drivers/');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching drivers:', error);
      return [];
    }
  }

  async getDriver(id: number): Promise<any | null> {
    try {
      const response = await api.get(`/api/reports/drivers/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching driver:', error);
      return null;
    }
  }

  async createDriver(data: any): Promise<any | null> {
    try {
      const response = await api.post('/api/reports/drivers/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating driver:', error);
      return null;
    }
  }

  // Export functionality
  async exportReport(
    reportType: 'route' | 'driver' | 'device' | 'daily',
    params: any,
    format: 'csv' | 'json' | 'pdf' = 'csv'
  ): Promise<Blob | null> {
    try {
      const response = await api.get(`/api/reports/export/${reportType}/`, {
        params: { ...params, format },
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting report:', error);
      return null;
    }
  }

  // Summary Reports
  async getSummaryReport(filters?: {
    date_from?: string;
    date_to?: string;
    route_code?: number;
    driver_id?: number;
  }): Promise<any | null> {
    try {
      const params = new URLSearchParams();
      if (filters?.date_from) params.append('date_from', filters.date_from);
      if (filters?.date_to) params.append('date_to', filters.date_to);
      if (filters?.route_code) params.append('route_code', filters.route_code.toString());
      if (filters?.driver_id) params.append('driver_id', filters.driver_id.toString());
      
      const response = await api.get(`/api/reports/summary/?${params.toString()}`);
      return response.data || null;
    } catch (error) {
      console.error('Error fetching summary report:', error);
      return null;
    }
  }
}

export const reportService = new ReportService(); 