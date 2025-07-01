import { useCrudOperations, useApiQuery, useApiMutation, useRealtimeQuery } from './useApi';
import { Report, RouteReport, DriverReport, DeviceStatistics, DailyStatistics } from '../types/unified';
import { reportService } from '../services/reportService';

// ============================================================================
// REPORT HOOKS - Hooks específicos para reportes
// ============================================================================

/**
 * Hook para operaciones CRUD de reportes
 */
export const useReportCrud = () => {
  return useCrudOperations<Report>('reports', {
    getAll: reportService.getAllReports,
    getById: reportService.getReport,
    create: reportService.createReport,
    update: reportService.updateReport,
    delete: reportService.deleteReport,
  });
};

/**
 * Hook para generar reporte de ruta
 */
export const useGenerateRouteReport = () => {
  return useApiMutation(
    reportService.generateRouteReport,
    {
      successMessage: 'Route report generated successfully',
      errorMessage: 'Failed to generate route report',
      invalidateQueries: ['reports'],
    }
  );
};

/**
 * Hook para generar reporte de conductor
 */
export const useGenerateDriverReport = () => {
  return useApiMutation(
    reportService.generateDriverReport,
    {
      successMessage: 'Driver report generated successfully',
      errorMessage: 'Failed to generate driver report',
      invalidateQueries: ['reports'],
    }
  );
};

/**
 * Hook para generar reporte de dispositivo
 */
export const useGenerateDeviceReport = () => {
  return useApiMutation(
    reportService.generateDeviceReport,
    {
      successMessage: 'Device report generated successfully',
      errorMessage: 'Failed to generate device report',
      invalidateQueries: ['reports'],
    }
  );
};

/**
 * Hook para generar reporte de vehículo
 */
export const useGenerateVehicleReport = () => {
  return useApiMutation(
    reportService.generateVehicleReport,
    {
      successMessage: 'Vehicle report generated successfully',
      errorMessage: 'Failed to generate vehicle report',
      invalidateQueries: ['reports'],
    }
  );
};

/**
 * Hook para generar reporte de geofence
 */
export const useGenerateGeofenceReport = () => {
  return useApiMutation(
    reportService.generateGeofenceReport,
    {
      successMessage: 'Geofence report generated successfully',
      errorMessage: 'Failed to generate geofence report',
      invalidateQueries: ['reports'],
    }
  );
};

/**
 * Hook para generar reporte de alarmas
 */
export const useGenerateAlarmReport = () => {
  return useApiMutation(
    reportService.generateAlarmReport,
    {
      successMessage: 'Alarm report generated successfully',
      errorMessage: 'Failed to generate alarm report',
      invalidateQueries: ['reports'],
    }
  );
};

/**
 * Hook para exportar reporte
 */
export const useExportReport = () => {
  return useApiMutation(
    reportService.exportReport,
    {
      successMessage: 'Report exported successfully',
      errorMessage: 'Failed to export report',
    }
  );
};

/**
 * Hook para descargar reporte
 */
export const useDownloadReport = () => {
  return useApiMutation(
    reportService.downloadReport,
    {
      successMessage: 'Report downloaded successfully',
      errorMessage: 'Failed to download report',
    }
  );
};

/**
 * Hook para obtener reportes por tipo
 */
export const useReportsByType = (type: string) => {
  return useApiQuery(
    ['reports', 'type', type],
    () => reportService.getReportsByType(type),
    {
      enabled: !!type,
    }
  );
};

/**
 * Hook para obtener reportes por estado
 */
export const useReportsByStatus = (status: string) => {
  return useApiQuery(
    ['reports', 'status', status],
    () => reportService.getReportsByStatus(status),
    {
      enabled: !!status,
    }
  );
};

/**
 * Hook para obtener reportes por fecha
 */
export const useReportsByDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'date', startDate, endDate],
    () => reportService.getReportsByDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes pendientes
 */
export const usePendingReports = () => {
  return useApiQuery(
    ['reports', 'pending'],
    reportService.getPendingReports,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener reportes procesando
 */
export const useProcessingReports = () => {
  return useApiQuery(
    ['reports', 'processing'],
    reportService.getProcessingReports,
    {
      refetchInterval: 15000, // Actualizar cada 15 segundos
    }
  );
};

/**
 * Hook para obtener reportes completados
 */
export const useCompletedReports = () => {
  return useApiQuery(
    ['reports', 'completed'],
    reportService.getCompletedReports,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener reportes fallidos
 */
export const useFailedReports = () => {
  return useApiQuery(
    ['reports', 'failed'],
    reportService.getFailedReports,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener estadísticas de reportes
 */
export const useReportStatistics = () => {
  return useApiQuery(
    ['reports', 'statistics'],
    reportService.getReportStatistics,
    {
      refetchInterval: 300000, // Actualizar cada 5 minutos
    }
  );
};

/**
 * Hook para obtener reportes recientes
 */
export const useRecentReports = (limit: number = 10) => {
  return useApiQuery(
    ['reports', 'recent', limit.toString()],
    () => reportService.getRecentReports(limit),
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener reportes por usuario
 */
export const useReportsByUser = (userId: number) => {
  return useApiQuery(
    ['reports', 'user', userId.toString()],
    () => reportService.getReportsByUser(userId),
    {
      enabled: !!userId,
    }
  );
};

/**
 * Hook para obtener reportes por ruta
 */
export const useReportsByRoute = (routeId: number) => {
  return useApiQuery(
    ['reports', 'route', routeId.toString()],
    () => reportService.getReportsByRoute(routeId),
    {
      enabled: !!routeId,
    }
  );
};

/**
 * Hook para obtener reportes por conductor
 */
export const useReportsByDriver = (driverId: number) => {
  return useApiQuery(
    ['reports', 'driver', driverId.toString()],
    () => reportService.getReportsByDriver(driverId),
    {
      enabled: !!driverId,
    }
  );
};

/**
 * Hook para obtener reportes por dispositivo
 */
export const useReportsByDevice = (deviceId: number) => {
  return useApiQuery(
    ['reports', 'device', deviceId.toString()],
    () => reportService.getReportsByDevice(deviceId),
    {
      enabled: !!deviceId,
    }
  );
};

/**
 * Hook para obtener reportes por vehículo
 */
export const useReportsByVehicle = (vehicleId: number) => {
  return useApiQuery(
    ['reports', 'vehicle', vehicleId.toString()],
    () => reportService.getReportsByVehicle(vehicleId),
    {
      enabled: !!vehicleId,
    }
  );
};

/**
 * Hook para obtener reportes por geofence
 */
export const useReportsByGeofence = (geofenceId: number) => {
  return useApiQuery(
    ['reports', 'geofence', geofenceId.toString()],
    () => reportService.getReportsByGeofence(geofenceId),
    {
      enabled: !!geofenceId,
    }
  );
};

/**
 * Hook para obtener reportes por formato
 */
export const useReportsByFormat = (format: string) => {
  return useApiQuery(
    ['reports', 'format', format],
    () => reportService.getReportsByFormat(format),
    {
      enabled: !!format,
    }
  );
};

/**
 * Hook para obtener reportes por tamaño de archivo
 */
export const useReportsByFileSize = (minSize: number, maxSize: number) => {
  return useApiQuery(
    ['reports', 'file-size', minSize.toString(), maxSize.toString()],
    () => reportService.getReportsByFileSize(minSize, maxSize),
    {
      enabled: !!(minSize && maxSize),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de creación
 */
export const useReportsByCreatedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'created-date', startDate, endDate],
    () => reportService.getReportsByCreatedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de actualización
 */
export const useReportsByUpdatedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'updated-date', startDate, endDate],
    () => reportService.getReportsByUpdatedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de generación
 */
export const useReportsByGeneratedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'generated-date', startDate, endDate],
    () => reportService.getReportsByGeneratedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de descarga
 */
export const useReportsByDownloadedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'downloaded-date', startDate, endDate],
    () => reportService.getReportsByDownloadedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de expiración
 */
export const useReportsByExpiryDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'expiry-date', startDate, endDate],
    () => reportService.getReportsByExpiryDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de archivo
 */
export const useReportsByArchivedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'archived-date', startDate, endDate],
    () => reportService.getReportsByArchivedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de eliminación
 */
export const useReportsByDeletedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'deleted-date', startDate, endDate],
    () => reportService.getReportsByDeletedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de restauración
 */
export const useReportsByRestoredDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'restored-date', startDate, endDate],
    () => reportService.getReportsByRestoredDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de migración
 */
export const useReportsByMigratedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'migrated-date', startDate, endDate],
    () => reportService.getReportsByMigratedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de backup
 */
export const useReportsByBackupDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'backup-date', startDate, endDate],
    () => reportService.getReportsByBackupDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de restauración de backup
 */
export const useReportsByBackupRestoredDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'backup-restored-date', startDate, endDate],
    () => reportService.getReportsByBackupRestoredDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de sincronización
 */
export const useReportsBySyncDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'sync-date', startDate, endDate],
    () => reportService.getReportsBySyncDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de validación
 */
export const useReportsByValidationDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'validation-date', startDate, endDate],
    () => reportService.getReportsByValidationDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de aprobación
 */
export const useReportsByApprovalDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'approval-date', startDate, endDate],
    () => reportService.getReportsByApprovalDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de rechazo
 */
export const useReportsByRejectionDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'rejection-date', startDate, endDate],
    () => reportService.getReportsByRejectionDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de publicación
 */
export const useReportsByPublishedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'published-date', startDate, endDate],
    () => reportService.getReportsByPublishedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de despublicación
 */
export const useReportsByUnpublishedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'unpublished-date', startDate, endDate],
    () => reportService.getReportsByUnpublishedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de vista
 */
export const useReportsByViewedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'viewed-date', startDate, endDate],
    () => reportService.getReportsByViewedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de impresión
 */
export const useReportsByPrintedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'printed-date', startDate, endDate],
    () => reportService.getReportsByPrintedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de envío
 */
export const useReportsBySentDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'sent-date', startDate, endDate],
    () => reportService.getReportsBySentDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de recepción
 */
export const useReportsByReceivedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'received-date', startDate, endDate],
    () => reportService.getReportsByReceivedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de confirmación
 */
export const useReportsByConfirmedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'confirmed-date', startDate, endDate],
    () => reportService.getReportsByConfirmedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de cancelación
 */
export const useReportsByCancelledDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'cancelled-date', startDate, endDate],
    () => reportService.getReportsByCancelledDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de pausa
 */
export const useReportsByPausedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'paused-date', startDate, endDate],
    () => reportService.getReportsByPausedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de reanudación
 */
export const useReportsByResumedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'resumed-date', startDate, endDate],
    () => reportService.getReportsByResumedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de finalización
 */
export const useReportsByCompletedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'completed-date', startDate, endDate],
    () => reportService.getReportsByCompletedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de fallo
 */
export const useReportsByFailedDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'failed-date', startDate, endDate],
    () => reportService.getReportsByFailedDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de timeout
 */
export const useReportsByTimeoutDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'timeout-date', startDate, endDate],
    () => reportService.getReportsByTimeoutDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de retry
 */
export const useReportsByRetryDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'retry-date', startDate, endDate],
    () => reportService.getReportsByRetryDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de max retries
 */
export const useReportsByMaxRetriesDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'max-retries-date', startDate, endDate],
    () => reportService.getReportsByMaxRetriesDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de error
 */
export const useReportsByErrorDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'error-date', startDate, endDate],
    () => reportService.getReportsByErrorDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de warning
 */
export const useReportsByWarningDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'warning-date', startDate, endDate],
    () => reportService.getReportsByWarningDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de info
 */
export const useReportsByInfoDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'info-date', startDate, endDate],
    () => reportService.getReportsByInfoDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de debug
 */
export const useReportsByDebugDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'debug-date', startDate, endDate],
    () => reportService.getReportsByDebugDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de trace
 */
export const useReportsByTraceDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'trace-date', startDate, endDate],
    () => reportService.getReportsByTraceDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de fatal
 */
export const useReportsByFatalDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'fatal-date', startDate, endDate],
    () => reportService.getReportsByFatalDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de critical
 */
export const useReportsByCriticalDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'critical-date', startDate, endDate],
    () => reportService.getReportsByCriticalDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de emergency
 */
export const useReportsByEmergencyDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'emergency-date', startDate, endDate],
    () => reportService.getReportsByEmergencyDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de alert
 */
export const useReportsByAlertDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'alert-date', startDate, endDate],
    () => reportService.getReportsByAlertDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de notice
 */
export const useReportsByNoticeDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'notice-date', startDate, endDate],
    () => reportService.getReportsByNoticeDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de verbose
 */
export const useReportsByVerboseDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'verbose-date', startDate, endDate],
    () => reportService.getReportsByVerboseDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de silly
 */
export const useReportsBySillyDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'silly-date', startDate, endDate],
    () => reportService.getReportsBySillyDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de input
 */
export const useReportsByInputDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'input-date', startDate, endDate],
    () => reportService.getReportsByInputDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de prompt
 */
export const useReportsByPromptDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'prompt-date', startDate, endDate],
    () => reportService.getReportsByPromptDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de help
 */
export const useReportsByHelpDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'help-date', startDate, endDate],
    () => reportService.getReportsByHelpDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de data
 */
export const useReportsByDataDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'data-date', startDate, endDate],
    () => reportService.getReportsByDataDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de http
 */
export const useReportsByHttpDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'http-date', startDate, endDate],
    () => reportService.getReportsByHttpDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de verbose
 */
export const useReportsByVerboseHttpDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'verbose-http-date', startDate, endDate],
    () => reportService.getReportsByVerboseHttpDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de silly http
 */
export const useReportsBySillyHttpDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'silly-http-date', startDate, endDate],
    () => reportService.getReportsBySillyHttpDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de input http
 */
export const useReportsByInputHttpDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'input-http-date', startDate, endDate],
    () => reportService.getReportsByInputHttpDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de prompt http
 */
export const useReportsByPromptHttpDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'prompt-http-date', startDate, endDate],
    () => reportService.getReportsByPromptHttpDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de help http
 */
export const useReportsByHelpHttpDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'help-http-date', startDate, endDate],
    () => reportService.getReportsByHelpHttpDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de data http
 */
export const useReportsByDataHttpDate = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'data-http-date', startDate, endDate],
    () => reportService.getReportsByDataHttpDate(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de silly http
 */
export const useReportsBySillyHttpDate2 = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'silly-http-date-2', startDate, endDate],
    () => reportService.getReportsBySillyHttpDate2(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de input http
 */
export const useReportsByInputHttpDate2 = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'input-http-date-2', startDate, endDate],
    () => reportService.getReportsByInputHttpDate2(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de prompt http
 */
export const useReportsByPromptHttpDate2 = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'prompt-http-date-2', startDate, endDate],
    () => reportService.getReportsByPromptHttpDate2(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de help http
 */
export const useReportsByHelpHttpDate2 = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'help-http-date-2', startDate, endDate],
    () => reportService.getReportsByHelpHttpDate2(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
};

/**
 * Hook para obtener reportes por fecha de data http
 */
export const useReportsByDataHttpDate2 = (startDate: string, endDate: string) => {
  return useApiQuery(
    ['reports', 'data-http-date-2', startDate, endDate],
    () => reportService.getReportsByDataHttpDate2(startDate, endDate),
    {
      enabled: !!(startDate && endDate),
    }
  );
}; 