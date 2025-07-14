import {
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
 * Subsidies Service implementation.
 * Handles driver management, daily logs, cash receipts, and subsidy calculations.
 */
export class SubsidiesService {
  private config = getConfig();
  private baseUrl: string;

  constructor() {
    this.baseUrl = this.config.get('api.baseUrl', 'http://localhost:8000/api');
  }

  /**
   * Get all drivers.
   */
  async getDrivers(): Promise<Driver[]> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/drivers/`, {
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

  /**
   * Get driver by ID.
   */
  async getDriver(driverId: number): Promise<Driver | null> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/drivers/${driverId}/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`Failed to get driver: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting driver:', error);
      throw error;
    }
  }

  /**
   * Create a new driver.
   */
  async createDriver(driverData: Partial<Driver>): Promise<Driver> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/drivers/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify(driverData)
      });

      if (!response.ok) {
        throw new Error(`Failed to create driver: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating driver:', error);
      throw error;
    }
  }

  /**
   * Update a driver.
   */
  async updateDriver(driverId: number, driverData: Partial<Driver>): Promise<Driver> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/drivers/${driverId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify(driverData)
      });

      if (!response.ok) {
        throw new Error(`Failed to update driver: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating driver:', error);
      throw error;
    }
  }

  /**
   * Delete a driver.
   */
  async deleteDriver(driverId: number): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/drivers/${driverId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to delete driver: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error deleting driver:', error);
      throw error;
    }
  }

  /**
   * Get daily logs for a driver.
   */
  async getDailyLogs(driverId: number, startDate?: Date, endDate?: Date): Promise<DailyLog[]> {
    try {
      const params = new URLSearchParams();
      if (startDate) {
        params.append('start_date', startDate.toISOString());
      }
      if (endDate) {
        params.append('end_date', endDate.toISOString());
      }

      const response = await fetch(
        `${this.baseUrl}/subsidies/drivers/${driverId}/daily-logs/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.get('auth.token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to get daily logs: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting daily logs:', error);
      throw error;
    }
  }

  /**
   * Create a daily log.
   */
  async createDailyLog(driverId: number, logData: Partial<DailyLog>): Promise<DailyLog> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/drivers/${driverId}/daily-logs/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify(logData)
      });

      if (!response.ok) {
        throw new Error(`Failed to create daily log: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating daily log:', error);
      throw error;
    }
  }

  /**
   * Get cash receipts for a driver.
   */
  async getCashReceipts(driverId: number): Promise<CashReceipt[]> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/drivers/${driverId}/cash-receipts/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get cash receipts: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting cash receipts:', error);
      throw error;
    }
  }

  /**
   * Create a cash receipt.
   */
  async createCashReceipt(driverId: number, receiptData: Partial<CashReceipt>): Promise<CashReceipt> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/drivers/${driverId}/cash-receipts/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify(receiptData)
      });

      if (!response.ok) {
        throw new Error(`Failed to create cash receipt: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating cash receipt:', error);
      throw error;
    }
  }

  /**
   * Get time sheet captures.
   */
  async getTimeSheetCaptures(startDate?: Date, endDate?: Date): Promise<TimeSheetCapture[]> {
    try {
      const params = new URLSearchParams();
      if (startDate) {
        params.append('start_date', startDate.toISOString());
      }
      if (endDate) {
        params.append('end_date', endDate.toISOString());
      }

      const response = await fetch(
        `${this.baseUrl}/subsidies/timesheet-captures/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.get('auth.token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to get time sheet captures: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting time sheet captures:', error);
      throw error;
    }
  }

  /**
   * Create a time sheet capture.
   */
  async createTimeSheetCapture(captureData: Partial<TimeSheetCapture>): Promise<TimeSheetCapture> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/timesheet-captures/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify(captureData)
      });

      if (!response.ok) {
        throw new Error(`Failed to create time sheet capture: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating time sheet capture:', error);
      throw error;
    }
  }

  /**
   * Get subsidy routes.
   */
  async getSubsidyRoutes(): Promise<SubsidyRoute[]> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/routes/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get subsidy routes: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting subsidy routes:', error);
      throw error;
    }
  }

  /**
   * Get subsidy route by ID.
   */
  async getSubsidyRoute(routeId: number): Promise<SubsidyRoute | null> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/routes/${routeId}/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`Failed to get subsidy route: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting subsidy route:', error);
      throw error;
    }
  }

  /**
   * Create a subsidy route.
   */
  async createSubsidyRoute(routeData: Partial<SubsidyRoute>): Promise<SubsidyRoute> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/routes/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify(routeData)
      });

      if (!response.ok) {
        throw new Error(`Failed to create subsidy route: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating subsidy route:', error);
      throw error;
    }
  }

  /**
   * Update a subsidy route.
   */
  async updateSubsidyRoute(routeId: number, routeData: Partial<SubsidyRoute>): Promise<SubsidyRoute> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/routes/${routeId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify(routeData)
      });

      if (!response.ok) {
        throw new Error(`Failed to update subsidy route: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating subsidy route:', error);
      throw error;
    }
  }

  /**
   * Delete a subsidy route.
   */
  async deleteSubsidyRoute(routeId: number): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/routes/${routeId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to delete subsidy route: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error deleting subsidy route:', error);
      throw error;
    }
  }

  /**
   * Generate a subsidy report.
   */
  async generateReport(reportType: ReportType, routeId: number, startDate: Date, endDate: Date): Promise<SubsidyReport> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/reports/generate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify({
          report_type: reportType,
          route_id: routeId,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to generate report: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  }

  /**
   * Get subsidy reports.
   */
  async getSubsidyReports(routeId?: number, startDate?: Date, endDate?: Date): Promise<SubsidyReport[]> {
    try {
      const params = new URLSearchParams();
      if (routeId) {
        params.append('route_id', routeId.toString());
      }
      if (startDate) {
        params.append('start_date', startDate.toISOString());
      }
      if (endDate) {
        params.append('end_date', endDate.toISOString());
      }

      const response = await fetch(
        `${this.baseUrl}/subsidies/reports/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.get('auth.token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to get subsidy reports: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting subsidy reports:', error);
      throw error;
    }
  }

  /**
   * Get economic mappings.
   */
  async getEconomicMappings(): Promise<EconomicMapping[]> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/economic-mappings/`, {
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get economic mappings: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting economic mappings:', error);
      throw error;
    }
  }

  /**
   * Create an economic mapping.
   */
  async createEconomicMapping(mappingData: Partial<EconomicMapping>): Promise<EconomicMapping> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/economic-mappings/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify(mappingData)
      });

      if (!response.ok) {
        throw new Error(`Failed to create economic mapping: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating economic mapping:', error);
      throw error;
    }
  }

  /**
   * Update an economic mapping.
   */
  async updateEconomicMapping(mappingId: number, mappingData: Partial<EconomicMapping>): Promise<EconomicMapping> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/economic-mappings/${mappingId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify(mappingData)
      });

      if (!response.ok) {
        throw new Error(`Failed to update economic mapping: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating economic mapping:', error);
      throw error;
    }
  }

  /**
   * Delete an economic mapping.
   */
  async deleteEconomicMapping(mappingId: number): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/economic-mappings/${mappingId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to delete economic mapping: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error deleting economic mapping:', error);
      throw error;
    }
  }

  /**
   * Calculate subsidies for a driver.
   */
  async calculateSubsidies(driverId: number, startDate: Date, endDate: Date): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/subsidies/calculate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.get('auth.token')}`
        },
        body: JSON.stringify({
          driver_id: driverId,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to calculate subsidies: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error calculating subsidies:', error);
      throw error;
    }
  }

  /**
   * Get subsidy analytics.
   */
  async getSubsidyAnalytics(startDate: Date, endDate: Date): Promise<any> {
    try {
      const params = new URLSearchParams({
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString()
      });

      const response = await fetch(
        `${this.baseUrl}/subsidies/analytics/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${this.config.get('auth.token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to get subsidy analytics: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting subsidy analytics:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const subsidiesService = new SubsidiesService(); 