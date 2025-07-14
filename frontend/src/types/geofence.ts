import { LatLngExpression } from 'leaflet';

// Tipos de geometría soportados
export type GeofenceType = 'circle' | 'polygon' | 'rectangle';

export interface GeofencePoint {
  lat: number;
  lng: number;
}

export interface GeofenceGeometry {
  type: GeofenceType;
  // Para círculo: [centro, radioEnMetros]
  // Para polígono/rectángulo: array de puntos
  coordinates: LatLngExpression[] | [LatLngExpression, number];
}

export interface Geofence {
  id: number;
  name: string;
  description?: string;
  geometry: GeofenceGeometry;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: number;
  color?: string;
  fill_opacity?: number;
  stroke_width?: number;
  stroke_color?: string;
  // Relaciones
  devices?: number[]; // IDs de dispositivos asociados
  notify_emails?: string[];
  notify_sms?: string[];
  // Configuración de notificaciones
  notify_on_entry: boolean;
  notify_on_exit: boolean;
  // Configuración de alertas
  alert_on_entry: boolean;
  alert_on_exit: boolean;
  // Tiempo mínimo entre notificaciones (en segundos)
  notification_cooldown: number;
}

export interface GeofenceEvent {
  id: number;
  geofence_id: number;
  device_id: number;
  event_type: 'ENTRY' | 'EXIT';
  timestamp: string;
  position: {
    latitude: number;
    longitude: number;
  };
  device_name?: string;
  geofence_name?: string;
}

export interface CreateGeofenceDTO extends Omit<Geofence, 'id' | 'created_at' | 'updated_at'> {}
export interface UpdateGeofenceDTO extends Partial<CreateGeofenceDTO> {}

export interface GeofenceStats {
  total_geofences: number;
  active_geofences: number;
  total_events_today: number;
  recent_events: GeofenceEvent[];
}

export interface GeofenceFilterParams {
  is_active?: boolean;
  device_id?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
}

export interface GeofenceEventFilterParams {
  geofence_id?: number;
  device_id?: number;
  event_type?: 'ENTRY' | 'EXIT';
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}
