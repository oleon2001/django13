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

// Métricas comprehensivas de geocercas
export interface GeofenceMetrics {
  total_geofences: number;
  active_geofences: number;
  entry_events_24h: number;
  exit_events_24h: number;
  violation_rate: number;
  performance_score: number;
  average_dwell_time: number;
  most_active_devices: Array<{
    device_imei: string;
    device_name: string;
    event_count: number;
  }>;
  time_window_hours: number;
}

// Analytics detallados por geocerca
export interface GeofenceAnalytics {
  total_events: number;
  entry_events: number;
  exit_events: number;
  unique_devices: number;
  average_dwell_time: number;
  hourly_distribution: Record<string, number>;
  device_activity: Array<{
    device_imei: string;
    device_name: string;
    event_count: number;
  }>;
  dwell_time_analysis: {
    min_dwell_time: number;
    max_dwell_time: number;
    average_dwell_time: number;
    total_dwell_sessions: number;
  };
  entry_exit_patterns: Record<string, number>;
}

// Verificación manual de geocercas
export interface ManualGeofenceCheck {
  geofence_id: number;
  geofence_name: string;
  devices_checked: number;
  results: Array<{
    device_imei: string;
    device_name: string;
    events_generated: number;
    events: GeofenceEvent[];
  }>;
}

// Análisis comportamental ML
export interface BehaviorAnalysis {
  device_imei: string;
  device_name: string;
  analysis_period_days: number;
  analysis: {
    behavior_score: number;
    anomalies_detected: Array<{
      timestamp: string;
      anomaly_type: string;
      confidence_score: number;
      description: string;
      location: [number, number];
    }>;
    patterns: {
      peak_hours: number[];
      frequent_routes: Array<{
        route_id: string;
        frequency: number;
        coordinates: [number, number][];
      }>;
      typical_dwell_time: number;
      average_speed_patterns: Record<string, number>;
    };
    compliance_metrics: {
      geofence_adherence_rate: number;
      speed_compliance_rate: number;
      route_efficiency_score: number;
    };
  };
}

// Verificación de geocercas para dispositivo
export interface DeviceGeofenceCheck {
  device_imei: string;
  device_name: string;
  position: [number, number] | null;
  events_generated: number;
  events: GeofenceEvent[];
  timestamp: string;
}

// Filtros para eventos de geocerca
export interface GeofenceEventFilters {
  device?: string;
  type?: 'ENTRY' | 'EXIT';
  from_date?: string;
  to_date?: string;
  days?: number;
  page?: number;
  page_size?: number;
}

// Resultado de eventos de geocerca con paginación
export interface GeofenceEventsResult {
  count: number;
  next: string | null;
  previous: string | null;
  results: GeofenceEvent[];
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
