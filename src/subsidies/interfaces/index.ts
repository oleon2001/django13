/**
 * Subsidies interfaces for the tracking system.
 * Migrated from backend Django models to TypeScript.
 */

export interface Driver {
  id: number;
  name: string;
  middle: string;
  last: string;
  birth: Date;
  cstatus: string;
  payroll: string;
  socials: string;
  taxid: string;
  license?: string;
  licExp?: Date;
  address: string;
  phone: string;
  phone1?: string;
  phone2?: string;
  active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface DailyLog {
  id: number;
  driver: number;
  route?: number;
  start: Date;
  stop: Date;
  regular: number;
  preferent: number;
  total: number;
  due: number;
  payed: number;
  difference: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface CashReceipt {
  id: number;
  driver: number;
  ticket1: number;
  ticket2?: number;
  payed1?: number;
  payed2?: number;
  payed3?: number;
  payed4?: number;
  payed5?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface TimeSheetCapture {
  id: number;
  date: Date;
  name: string;
  times: any[];
  driver?: string;
  route?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface SubsidyRoute {
  id: number;
  name: string;
  routeCode: string;
  company: string;
  branch?: string;
  flag: string;
  units: any[];
  km: number;
  frequency: number;
  timeMinutes: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface SubsidyReport {
  id: number;
  route: number;
  reportType: string;
  startDate: Date;
  endDate: Date;
  generatedBy: number;
  filePath?: string;
  reportData: any;
  createdAt: Date;
}

export interface EconomicMapping {
  id: number;
  unitName: string;
  economicNumber: string;
  route?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export type ReportType = 'daily' | 'weekly' | 'monthly' | 'timesheet' | 'cash';

export interface DriverAnalytics {
  driverId: number;
  totalTrips: number;
  totalDistance: number;
  totalEarnings: number;
  averageSpeed: number;
  efficiencyScore: number;
  peakHours: string[];
  preferredRoutes: number[];
  maintenanceAlerts: string[];
  performanceTrend: {
    date: string;
    value: number;
  }[];
}

export interface RouteAnalytics {
  routeId: number;
  totalDrivers: number;
  totalTrips: number;
  totalDistance: number;
  averageEarnings: number;
  peakUsageHours: string[];
  popularStops: string[];
  efficiencyMetrics: {
    fuelEfficiency: number;
    timeEfficiency: number;
    passengerEfficiency: number;
  };
  performanceHistory: {
    date: string;
    trips: number;
    distance: number;
    earnings: number;
  }[];
}

export interface SystemAnalytics {
  totalDrivers: number;
  totalRoutes: number;
  totalTrips: number;
  totalDistance: number;
  totalEarnings: number;
  averageEfficiency: number;
  systemHealth: {
    status: string;
    issues: string[];
    recommendations: string[];
  };
  trends: {
    daily: {
      date: string;
      trips: number;
      earnings: number;
    }[];
    weekly: {
      week: string;
      trips: number;
      earnings: number;
    }[];
    monthly: {
      month: string;
      trips: number;
      earnings: number;
    }[];
  };
  alerts: {
    critical: number;
    warning: number;
    info: number;
  };
} 