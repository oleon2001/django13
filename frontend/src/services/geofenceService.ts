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
}

export const geofenceService = new GeofenceService();
export default geofenceService;
