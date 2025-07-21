import api from './api';
import {
  Geofence,
  GeofenceEvent,
  CreateGeofenceDTO,
  UpdateGeofenceDTO,
  GeofenceStats,
  GeofenceFilterParams,
  GeofenceEventFilterParams,
  GeofenceType,
  GeofenceGeometry,
  GeofenceMetrics,
  GeofenceAnalytics,
  ManualGeofenceCheck,
  BehaviorAnalysis,
  DeviceGeofenceCheck,
  GeofenceEventsResult,
  GeofenceEventFilters,
} from '../types/geofence';

// Re-exportar tipos para compatibilidad
export type {
  Geofence,
  GeofenceEvent,
  CreateGeofenceDTO,
  UpdateGeofenceDTO,
  GeofenceStats,
  GeofenceFilterParams,
  GeofenceEventFilterParams,
  GeofenceType,
  GeofenceGeometry,
  GeofenceMetrics,
  GeofenceAnalytics,
  ManualGeofenceCheck,
  BehaviorAnalysis,
  DeviceGeofenceCheck,
  GeofenceEventsResult,
  GeofenceEventFilters,
};

/**
 * Servicio para la gestión de geocercas
 */
class GeofenceService {
  // Endpoints base
  private baseUrl = '/api/gps/geofences';
  private eventsUrl = `${this.baseUrl}/events`;

  /**
   * Obtiene todas las geocercas con filtros opcionales
   */
  async getAll(filters?: GeofenceFilterParams): Promise<Geofence[]> {
    try {
      const response = await api.get<Geofence[]>(this.baseUrl, { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error al obtener geocercas:', error);
      throw error;
    }
  }

  /**
   * Obtiene una geocerca por su ID
   */
  async getById(id: number): Promise<Geofence> {
    try {
      const response = await api.get<Geofence>(`${this.baseUrl}/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener la geocerca ${id}:`, error);
      throw error;
    }
  }

  /**
   * Crea una nueva geocerca
   */
  async create(geofence: CreateGeofenceDTO): Promise<Geofence> {
    try {
      const response = await api.post<Geofence>(this.baseUrl, geofence);
      return response.data;
    } catch (error) {
      console.error('Error al crear la geocerca:', error);
      throw error;
    }
  }

  /**
   * Actualiza una geocerca existente
   */
  async update(id: number, updates: UpdateGeofenceDTO): Promise<Geofence> {
    try {
      const response = await api.patch<Geofence>(`${this.baseUrl}/${id}/`, updates);
      return response.data;
    } catch (error) {
      console.error(`Error al actualizar la geocerca ${id}:`, error);
      throw error;
    }
  }

  /**
   * Elimina una geocerca
   */
  async delete(id: number): Promise<void> {
    try {
      await api.delete(`${this.baseUrl}/${id}/`);
    } catch (error) {
      console.error(`Error al eliminar la geocerca ${id}:`, error);
      throw error;
    }
  }

  /**
   * Obtiene eventos de geocercas con filtros
   */
  async getEvents(params?: GeofenceEventFilterParams): Promise<GeofenceEvent[]> {
    try {
      const response = await api.get<GeofenceEvent[]>(this.eventsUrl, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener eventos de geocercas:', error);
      throw error;
    }
  }

  /**
   * Obtiene estadísticas de geocercas
   */
  async getStats(): Promise<GeofenceStats> {
    try {
      const response = await api.get<GeofenceStats>(`${this.baseUrl}/stats/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas de geocercas:', error);
      throw error;
    }
  }

  /**
   * Asigna dispositivos a una geocerca
   */
  async assignDevices(geofenceId: number, deviceIds: number[]): Promise<void> {
    try {
      await api.post(`${this.baseUrl}/${geofenceId}/assign-devices/`, { device_ids: deviceIds });
    } catch (error) {
      console.error(`Error al asignar dispositivos a la geocerca ${geofenceId}:`, error);
      throw error;
    }
  }

  /**
   * Obtiene los dispositivos asociados a una geocerca
   */
  async getAssignedDevices(geofenceId: number): Promise<number[]> {
    try {
      const response = await api.get<number[]>(`${this.baseUrl}/${geofenceId}/devices/`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener dispositivos de la geocerca ${geofenceId}:`, error);
      throw error;
    }
  }

  /**
   * Verifica si una coordenada está dentro de una geocerca
   */
  async checkPointInGeofence(
    geofenceId: number,
    lat: number,
    lng: number
  ): Promise<{ inside: boolean }> {
    try {
      const response = await api.get<{ inside: boolean }>(
        `${this.baseUrl}/${geofenceId}/check-point/`,
        { params: { lat, lng } }
      );
      return response.data;
    } catch (error) {
      console.error(`Error al verificar punto en geocerca ${geofenceId}:`, error);
      throw error;
    }
  }

  /**
   * Obtiene métricas comprehensivas de geocercas
   */
  async getMetrics(hours: number = 24): Promise<GeofenceMetrics> {
    try {
      const response = await api.get<GeofenceMetrics>(`${this.baseUrl}/metrics/`, { 
        params: { hours } 
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener métricas de geocercas:', error);
      throw error;
    }
  }

  /**
   * Obtiene analytics detallados para una geocerca específica
   */
  async getGeofenceAnalytics(id: number, days: number = 7): Promise<GeofenceAnalytics> {
    try {
      const response = await api.get<GeofenceAnalytics>(
        `${this.baseUrl}/${id}/analytics/`, 
        { params: { days } }
      );
      return response.data;
    } catch (error) {
      console.error(`Error al obtener analytics para geocerca ${id}:`, error);
      throw error;
    }
  }

  /**
   * Verifica manualmente todas las geocercas para una geocerca específica
   */
  async checkGeofenceDevices(id: number): Promise<ManualGeofenceCheck> {
    try {
      const response = await api.post<ManualGeofenceCheck>(
        `${this.baseUrl}/${id}/check_devices/`
      );
      return response.data;
    } catch (error) {
      console.error(`Error al verificar dispositivos para geocerca ${id}:`, error);
      throw error;
    }
  }

  /**
   * Obtiene análisis comportamental ML para un dispositivo específico
   */
  async getDeviceBehaviorAnalysis(deviceId: string, days: number = 7): Promise<BehaviorAnalysis> {
    try {
      const response = await api.get<BehaviorAnalysis>(
        `/api/device-analytics/${deviceId}/behavior_analysis/`, 
        { params: { days } }
      );
      return response.data;
    } catch (error) {
      console.error(`Error al obtener análisis comportamental para dispositivo ${deviceId}:`, error);
      throw error;
    }
  }

  /**
   * Verifica geocercas manualmente para un dispositivo específico
   */
  async checkDeviceGeofences(deviceId: string): Promise<DeviceGeofenceCheck> {
    try {
      const response = await api.post<DeviceGeofenceCheck>(
        `/api/device-analytics/${deviceId}/check_geofences/`
      );
      return response.data;
    } catch (error) {
      console.error(`Error al verificar geocercas para dispositivo ${deviceId}:`, error);
      throw error;
    }
  }

  /**
   * Obtiene eventos de geocerca con filtros avanzados
   */
  async getGeofenceEvents(id: number, filters?: GeofenceEventFilters): Promise<GeofenceEventsResult> {
    try {
      const response = await api.get<GeofenceEventsResult>(
        `${this.baseUrl}/${id}/events/`, 
        { params: filters }
      );
      return response.data;
    } catch (error) {
      console.error(`Error al obtener eventos para geocerca ${id}:`, error);
      throw error;
    }
  }
}

export const geofenceService = new GeofenceService();
export default geofenceService;
