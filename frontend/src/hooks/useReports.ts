import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reportService } from '../services/reportService';

// ============================================================================
// REPORT HOOKS - Hooks específicos para reportes
// ============================================================================

/**
 * Hook para obtener todos los reportes
 */
export const useGetAllReports = () => {
  return useQuery({
    queryKey: ['reports', 'all'],
    queryFn: reportService.getAll,
    refetchInterval: 60000, // Actualizar cada minuto
  });
};

/**
 * Hook para obtener un reporte por ID
 */
export const useGetReportById = (reportId: number) => {
  return useQuery({
    queryKey: ['reports', 'detail', reportId.toString()],
    queryFn: () => reportService.getById(reportId),
    enabled: !!reportId,
  });
};

/**
 * Hook para crear un reporte
 */
export const useCreateReport = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: any) => reportService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });
};

/**
 * Hook para descargar un reporte
 */
export const useDownloadReport = () => {
  return useMutation({
    mutationFn: (id: number) => reportService.download(id),
  });
};

/**
 * Hook para obtener reporte de ruta
 */
export const useGetRouteReport = (routeId: number, date: string) => {
  return useQuery({
    queryKey: ['reports', 'route', routeId.toString(), date],
    queryFn: () => reportService.getRouteReport(routeId, date),
    enabled: !!(routeId && date),
  });
};

/**
 * Hook para exportar CSV de ruta
 */
export const useExportRouteCSV = () => {
  return useMutation({
    mutationFn: ({ routeId, date }: { routeId: number; date: string }) => 
      reportService.exportRouteCSV(routeId, date),
  });
};

/**
 * Hook para obtener reporte de conductor
 */
export const useGetDriverReport = (driverId: number, startDate: string, endDate: string) => {
  return useQuery({
    queryKey: ['reports', 'driver', driverId.toString(), startDate, endDate],
    queryFn: () => reportService.getDriverReport(driverId, startDate, endDate),
    enabled: !!(driverId && startDate && endDate),
  });
};

/**
 * Hook para obtener estadísticas de dispositivo
 */
export const useGetDeviceStatistics = (deviceId: number, startDate: string, endDate: string) => {
  return useQuery({
    queryKey: ['reports', 'device-stats', deviceId.toString(), startDate, endDate],
    queryFn: () => reportService.getDeviceStatistics(deviceId, startDate, endDate),
    enabled: !!(deviceId && startDate && endDate),
  });
};

/**
 * Hook para calcular estadísticas diarias
 */
export const useCalculateDailyStatistics = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (date: string) => reportService.calculateDailyStatistics(date),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports', 'daily-stats'] });
    },
  });
};

/**
 * Hook para obtener estadísticas diarias
 */
export const useGetDailyStatistics = (date?: string) => {
  return useQuery({
    queryKey: ['reports', 'daily-stats', date],
    queryFn: () => reportService.getDailyStatistics(date),
    refetchInterval: 300000, // Actualizar cada 5 minutos
  });
};

/**
 * Hook para exportar reporte
 */
export const useExportReport = () => {
  return useMutation({
    mutationFn: ({ reportType, params, format }: { 
      reportType: 'route' | 'driver' | 'device' | 'daily'; 
      params: any; 
      format?: 'csv' | 'json' | 'pdf' 
    }) => reportService.exportReport(reportType, params, format),
  });
};

/**
 * Hook para obtener reporte resumen
 */
export const useGetSummaryReport = (filters?: {
  date_from?: string;
  date_to?: string;
  route_code?: number;
  driver_id?: number;
}) => {
  return useQuery({
    queryKey: ['reports', 'summary', filters],
    queryFn: () => reportService.getSummaryReport(filters),
    enabled: !!filters,
  });
}; 