// Subsidies service migrated from Django backend
// Based on skyguard/apps/subsidies/services.py

import { 
  ISubsidyService,
  Driver,
  DailyLog,
  CashReceipt,
  TimeSheetCapture,
  SubsidyRoute,
  SubsidyReport,
  EconomicMapping,
  ReportType
} from '../interfaces';

import { getConfig } from '../../core/config';

/**
 * Subsidies Service implementation
 */
export class SubsidyService implements ISubsidyService {
  private config = getConfig();
  private apiBaseUrl: string;

  constructor() {
    this.apiBaseUrl = this.config.get('api.baseUrl', 'http://localhost:8000');
  }

  // Driver Management
  async getDrivers(): Promise<Driver[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/drivers/`, {
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
      return data.drivers || [];

    } catch (error) {
      console.error('Error getting drivers:', error);
      throw error;
    }
  }

  async getDriver(id: number): Promise<Driver | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/drivers/${id}/`, {
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
      console.error(`Error getting driver ${id}:`, error);
      throw error;
    }
  }

  async createDriver(driver: Partial<Driver>): Promise<Driver> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/drivers/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(driver)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.driver;

    } catch (error) {
      console.error('Error creating driver:', error);
      throw error;
    }
  }

  async updateDriver(id: number, driver: Partial<Driver>): Promise<Driver> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/drivers/${id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(driver)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.driver;

    } catch (error) {
      console.error(`Error updating driver ${id}:`, error);
      throw error;
    }
  }

  async deleteDriver(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/drivers/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error(`Error deleting driver ${id}:`, error);
      throw error;
    }
  }

  // Daily Log Management
  async getDailyLogs(driverId?: number, startDate?: string, endDate?: string): Promise<DailyLog[]> {
    try {
      let url = `${this.apiBaseUrl}/api/subsidies/daily-logs/`;
      const params = new URLSearchParams();
      
      if (driverId) params.append('driver_id', driverId.toString());
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
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
      return data.daily_logs || [];

    } catch (error) {
      console.error('Error getting daily logs:', error);
      throw error;
    }
  }

  async getDailyLog(id: number): Promise<DailyLog | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/daily-logs/${id}/`, {
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
      return data.daily_log;

    } catch (error) {
      console.error(`Error getting daily log ${id}:`, error);
      throw error;
    }
  }

  async createDailyLog(log: Partial<DailyLog>): Promise<DailyLog> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/daily-logs/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(log)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.daily_log;

    } catch (error) {
      console.error('Error creating daily log:', error);
      throw error;
    }
  }

  async updateDailyLog(id: number, log: Partial<DailyLog>): Promise<DailyLog> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/daily-logs/${id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(log)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.daily_log;

    } catch (error) {
      console.error(`Error updating daily log ${id}:`, error);
      throw error;
    }
  }

  async deleteDailyLog(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/daily-logs/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error(`Error deleting daily log ${id}:`, error);
      throw error;
    }
  }

  // Cash Receipt Management
  async getCashReceipts(driverId?: number): Promise<CashReceipt[]> {
    try {
      let url = `${this.apiBaseUrl}/api/subsidies/cash-receipts/`;
      if (driverId) {
        url += `?driver_id=${driverId}`;
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
      return data.cash_receipts || [];

    } catch (error) {
      console.error('Error getting cash receipts:', error);
      throw error;
    }
  }

  async getCashReceipt(id: number): Promise<CashReceipt | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/cash-receipts/${id}/`, {
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
      return data.cash_receipt;

    } catch (error) {
      console.error(`Error getting cash receipt ${id}:`, error);
      throw error;
    }
  }

  async createCashReceipt(receipt: Partial<CashReceipt>): Promise<CashReceipt> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/cash-receipts/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(receipt)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.cash_receipt;

    } catch (error) {
      console.error('Error creating cash receipt:', error);
      throw error;
    }
  }

  async updateCashReceipt(id: number, receipt: Partial<CashReceipt>): Promise<CashReceipt> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/cash-receipts/${id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(receipt)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.cash_receipt;

    } catch (error) {
      console.error(`Error updating cash receipt ${id}:`, error);
      throw error;
    }
  }

  async deleteCashReceipt(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/cash-receipts/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error(`Error deleting cash receipt ${id}:`, error);
      throw error;
    }
  }

  // Time Sheet Management
  async getTimeSheets(startDate?: string, endDate?: string): Promise<TimeSheetCapture[]> {
    try {
      let url = `${this.apiBaseUrl}/api/subsidies/time-sheets/`;
      const params = new URLSearchParams();
      
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
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
      return data.time_sheets || [];

    } catch (error) {
      console.error('Error getting time sheets:', error);
      throw error;
    }
  }

  async getTimeSheet(id: number): Promise<TimeSheetCapture | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/time-sheets/${id}/`, {
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
      return data.time_sheet;

    } catch (error) {
      console.error(`Error getting time sheet ${id}:`, error);
      throw error;
    }
  }

  async createTimeSheet(timesheet: Partial<TimeSheetCapture>): Promise<TimeSheetCapture> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/time-sheets/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(timesheet)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.time_sheet;

    } catch (error) {
      console.error('Error creating time sheet:', error);
      throw error;
    }
  }

  async updateTimeSheet(id: number, timesheet: Partial<TimeSheetCapture>): Promise<TimeSheetCapture> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/time-sheets/${id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(timesheet)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.time_sheet;

    } catch (error) {
      console.error(`Error updating time sheet ${id}:`, error);
      throw error;
    }
  }

  async deleteTimeSheet(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/time-sheets/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error(`Error deleting time sheet ${id}:`, error);
      throw error;
    }
  }

  // Route Management
  async getRoutes(): Promise<SubsidyRoute[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/routes/`, {
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
      return data.routes || [];

    } catch (error) {
      console.error('Error getting routes:', error);
      throw error;
    }
  }

  async getRoute(id: number): Promise<SubsidyRoute | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/routes/${id}/`, {
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
      return data.route;

    } catch (error) {
      console.error(`Error getting route ${id}:`, error);
      throw error;
    }
  }

  async createRoute(route: Partial<SubsidyRoute>): Promise<SubsidyRoute> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/routes/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(route)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.route;

    } catch (error) {
      console.error('Error creating route:', error);
      throw error;
    }
  }

  async updateRoute(id: number, route: Partial<SubsidyRoute>): Promise<SubsidyRoute> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/routes/${id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(route)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.route;

    } catch (error) {
      console.error(`Error updating route ${id}:`, error);
      throw error;
    }
  }

  async deleteRoute(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/routes/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error(`Error deleting route ${id}:`, error);
      throw error;
    }
  }

  // Report Management
  async getReports(routeId?: number, reportType?: ReportType): Promise<SubsidyReport[]> {
    try {
      let url = `${this.apiBaseUrl}/api/subsidies/reports/`;
      const params = new URLSearchParams();
      
      if (routeId) params.append('route_id', routeId.toString());
      if (reportType) params.append('report_type', reportType);
      
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
      return data.reports || [];

    } catch (error) {
      console.error('Error getting reports:', error);
      throw error;
    }
  }

  async getReport(id: number): Promise<SubsidyReport | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/reports/${id}/`, {
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
      return data.report;

    } catch (error) {
      console.error(`Error getting report ${id}:`, error);
      throw error;
    }
  }

  async generateReport(reportType: ReportType, routeId: number, startDate: string, endDate: string): Promise<SubsidyReport> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/reports/generate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          report_type: reportType,
          route_id: routeId,
          start_date: startDate,
          end_date: endDate
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.report;

    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  }

  async downloadReport(id: number): Promise<Blob> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/reports/${id}/download/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.blob();

    } catch (error) {
      console.error(`Error downloading report ${id}:`, error);
      throw error;
    }
  }

  // Economic Mapping Management
  async getEconomicMappings(): Promise<EconomicMapping[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/economic-mappings/`, {
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
      return data.economic_mappings || [];

    } catch (error) {
      console.error('Error getting economic mappings:', error);
      throw error;
    }
  }

  async getEconomicMapping(id: number): Promise<EconomicMapping | null> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/economic-mappings/${id}/`, {
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
      return data.economic_mapping;

    } catch (error) {
      console.error(`Error getting economic mapping ${id}:`, error);
      throw error;
    }
  }

  async createEconomicMapping(mapping: Partial<EconomicMapping>): Promise<EconomicMapping> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/economic-mappings/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(mapping)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.economic_mapping;

    } catch (error) {
      console.error('Error creating economic mapping:', error);
      throw error;
    }
  }

  async updateEconomicMapping(id: number, mapping: Partial<EconomicMapping>): Promise<EconomicMapping> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/economic-mappings/${id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(mapping)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.economic_mapping;

    } catch (error) {
      console.error(`Error updating economic mapping ${id}:`, error);
      throw error;
    }
  }

  async deleteEconomicMapping(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/economic-mappings/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      console.error(`Error deleting economic mapping ${id}:`, error);
      throw error;
    }
  }

  // Analytics
  async getDriverAnalytics(driverId: number, startDate: string, endDate: string): Promise<Record<string, any>> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/analytics/driver/${driverId}/?start_date=${startDate}&end_date=${endDate}`, {
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
      return data.analytics;

    } catch (error) {
      console.error(`Error getting driver analytics for ${driverId}:`, error);
      throw error;
    }
  }

  async getRouteAnalytics(routeId: number, startDate: string, endDate: string): Promise<Record<string, any>> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/analytics/route/${routeId}/?start_date=${startDate}&end_date=${endDate}`, {
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
      return data.analytics;

    } catch (error) {
      console.error(`Error getting route analytics for ${routeId}:`, error);
      throw error;
    }
  }

  async getSystemAnalytics(startDate: string, endDate: string): Promise<Record<string, any>> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/subsidies/analytics/system/?start_date=${startDate}&end_date=${endDate}`, {
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
      return data.analytics;

    } catch (error) {
      console.error('Error getting system analytics:', error);
      throw error;
    }
  }

  /**
   * Get authentication token
   */
  private getAuthToken(): string {
    return localStorage.getItem('auth_token') || '';
  }
}

// Export singleton instance
export const subsidyService = new SubsidyService(); 