// Subsidies interfaces migrated from Django backend
// Based on skyguard/apps/subsidies/models.py

import { User } from '../../core/interfaces';

// Driver Models
export interface Driver {
  id: number;
  name: string;
  middle: string;
  last: string;
  birth: string;
  cstatus: 'SOL' | 'CAS' | 'VIU' | 'DIV';
  payroll: string;
  socials: string;
  taxid: string;
  license?: string;
  lic_exp?: string;
  address: string;
  phone: string;
  phone1?: string;
  phone2?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

// Daily Log Models
export interface DailyLog {
  id: number;
  driver: Driver;
  route?: number;
  start: string;
  stop: string;
  regular: number;
  preferent: number;
  total: number;
  due: number;
  payed: number;
  difference: number;
  created_at: string;
  updated_at: string;
}

// Cash Receipt Models
export interface CashReceipt {
  id: number;
  driver: Driver;
  ticket1: number;
  ticket2?: number;
  payed1?: number;
  payed2?: number;
  payed3?: number;
  payed4?: number;
  payed5?: number;
  created_at: string;
  updated_at: string;
}

// Time Sheet Models
export interface TimeSheetCapture {
  id: number;
  date: string;
  name: string;
  times: [string, string][]; // [start_time, end_time]
  driver?: string;
  route?: string;
  created_at: string;
  updated_at: string;
}

// Subsidy Route Models
export interface SubsidyRoute {
  id: number;
  name: string;
  route_code: string;
  company: string;
  branch?: string;
  flag: string;
  units: string[];
  km: number;
  frequency: number;
  time_minutes: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Subsidy Report Models
export interface SubsidyReport {
  id: number;
  route: SubsidyRoute;
  report_type: 'daily' | 'weekly' | 'monthly' | 'timesheet' | 'cash';
  start_date: string;
  end_date: string;
  generated_by: User;
  file_path?: string;
  report_data: Record<string, any>;
  created_at: string;
}

// Economic Mapping Models
export interface EconomicMapping {
  id: number;
  unit_name: string;
  economic_number: string;
  route?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Enums
export enum CivilStatus {
  SOLTERO = 'SOL',
  CASADO = 'CAS',
  VIUDO = 'VIU',
  DIVORCIADO = 'DIV'
}

export enum RouteCode {
  A6 = 'A6',
  RUTA_155 = '155',
  RUTA_202 = '202',
  RUTA_31 = '31',
  RUTA_207E = '207E',
  RUTA_207P = '207P',
  RUTA_400S1 = '400S1',
  RUTA_400S2 = '400S2',
  RUTA_400S4H = '400S4H',
  RUTA_400S4J = '400S4J'
}

export enum ReportType {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  TIMESHEET = 'timesheet',
  CASH = 'cash'
}

// Service Interfaces
export interface ISubsidyService {
  // Driver management
  getDrivers(): Promise<Driver[]>;
  getDriver(id: number): Promise<Driver | null>;
  createDriver(driver: Partial<Driver>): Promise<Driver>;
  updateDriver(id: number, driver: Partial<Driver>): Promise<Driver>;
  deleteDriver(id: number): Promise<void>;
  
  // Daily log management
  getDailyLogs(driverId?: number, startDate?: string, endDate?: string): Promise<DailyLog[]>;
  getDailyLog(id: number): Promise<DailyLog | null>;
  createDailyLog(log: Partial<DailyLog>): Promise<DailyLog>;
  updateDailyLog(id: number, log: Partial<DailyLog>): Promise<DailyLog>;
  deleteDailyLog(id: number): Promise<void>;
  
  // Cash receipt management
  getCashReceipts(driverId?: number): Promise<CashReceipt[]>;
  getCashReceipt(id: number): Promise<CashReceipt | null>;
  createCashReceipt(receipt: Partial<CashReceipt>): Promise<CashReceipt>;
  updateCashReceipt(id: number, receipt: Partial<CashReceipt>): Promise<CashReceipt>;
  deleteCashReceipt(id: number): Promise<void>;
  
  // Time sheet management
  getTimeSheets(startDate?: string, endDate?: string): Promise<TimeSheetCapture[]>;
  getTimeSheet(id: number): Promise<TimeSheetCapture | null>;
  createTimeSheet(timesheet: Partial<TimeSheetCapture>): Promise<TimeSheetCapture>;
  updateTimeSheet(id: number, timesheet: Partial<TimeSheetCapture>): Promise<TimeSheetCapture>;
  deleteTimeSheet(id: number): Promise<void>;
  
  // Route management
  getRoutes(): Promise<SubsidyRoute[]>;
  getRoute(id: number): Promise<SubsidyRoute | null>;
  createRoute(route: Partial<SubsidyRoute>): Promise<SubsidyRoute>;
  updateRoute(id: number, route: Partial<SubsidyRoute>): Promise<SubsidyRoute>;
  deleteRoute(id: number): Promise<void>;
  
  // Report management
  getReports(routeId?: number, reportType?: ReportType): Promise<SubsidyReport[]>;
  getReport(id: number): Promise<SubsidyReport | null>;
  generateReport(reportType: ReportType, routeId: number, startDate: string, endDate: string): Promise<SubsidyReport>;
  downloadReport(id: number): Promise<Blob>;
  
  // Economic mapping management
  getEconomicMappings(): Promise<EconomicMapping[]>;
  getEconomicMapping(id: number): Promise<EconomicMapping | null>;
  createEconomicMapping(mapping: Partial<EconomicMapping>): Promise<EconomicMapping>;
  updateEconomicMapping(id: number, mapping: Partial<EconomicMapping>): Promise<EconomicMapping>;
  deleteEconomicMapping(id: number): Promise<void>;
  
  // Analytics
  getDriverAnalytics(driverId: number, startDate: string, endDate: string): Promise<Record<string, any>>;
  getRouteAnalytics(routeId: number, startDate: string, endDate: string): Promise<Record<string, any>>;
  getSystemAnalytics(startDate: string, endDate: string): Promise<Record<string, any>>;
}

// Utility Interfaces
export interface DriverAnalytics {
  driver: Driver;
  totalDays: number;
  totalHours: number;
  totalPassengers: number;
  totalRevenue: number;
  averagePassengersPerDay: number;
  averageRevenuePerDay: number;
  mostActiveDays: string[];
  peakHours: number[];
}

export interface RouteAnalytics {
  route: SubsidyRoute;
  totalDrivers: number;
  totalDays: number;
  totalPassengers: number;
  totalRevenue: number;
  averagePassengersPerDay: number;
  averageRevenuePerDay: number;
  driverPerformance: DriverAnalytics[];
  peakDays: string[];
  peakHours: number[];
}

export interface SystemAnalytics {
  totalDrivers: number;
  totalRoutes: number;
  totalPassengers: number;
  totalRevenue: number;
  activeDrivers: number;
  activeRoutes: number;
  topPerformingDrivers: DriverAnalytics[];
  topPerformingRoutes: RouteAnalytics[];
  revenueTrend: Record<string, number>;
  passengerTrend: Record<string, number>;
}

// Form Interfaces
export interface DriverFormData {
  name: string;
  middle: string;
  last: string;
  birth: string;
  cstatus: CivilStatus;
  payroll: string;
  socials: string;
  taxid: string;
  license?: string;
  lic_exp?: string;
  address: string;
  phone: string;
  phone1?: string;
  phone2?: string;
  active: boolean;
}

export interface DailyLogFormData {
  driver_id: number;
  route?: number;
  start: string;
  stop: string;
  regular: number;
  preferent: number;
  total: number;
  due: number;
  payed: number;
}

export interface CashReceiptFormData {
  driver_id: number;
  ticket1: number;
  ticket2?: number;
  payed1?: number;
  payed2?: number;
  payed3?: number;
  payed4?: number;
  payed5?: number;
}

export interface TimeSheetFormData {
  date: string;
  name: string;
  times: [string, string][];
  driver?: string;
  route?: string;
}

export interface RouteFormData {
  name: string;
  route_code: RouteCode;
  company: string;
  branch?: string;
  flag: string;
  units: string[];
  km: number;
  frequency: number;
  time_minutes: number;
  is_active: boolean;
}

export interface EconomicMappingFormData {
  unit_name: string;
  economic_number: string;
  route?: string;
  is_active: boolean;
}

// Filter Interfaces
export interface DriverFilter {
  active?: boolean;
  route?: number;
  search?: string;
}

export interface DailyLogFilter {
  driver_id?: number;
  route?: number;
  start_date?: string;
  end_date?: string;
}

export interface CashReceiptFilter {
  driver_id?: number;
  start_date?: string;
  end_date?: string;
}

export interface TimeSheetFilter {
  start_date?: string;
  end_date?: string;
  driver?: string;
  route?: string;
}

export interface RouteFilter {
  is_active?: boolean;
  company?: string;
  search?: string;
}

export interface ReportFilter {
  route_id?: number;
  report_type?: ReportType;
  start_date?: string;
  end_date?: string;
  generated_by?: number;
} 