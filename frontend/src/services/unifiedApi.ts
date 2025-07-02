import api from './api';
import {
  GPSDevice,
  Vehicle,
  Driver,
  GeoFence,
  Location,
  DeviceEvent,
  NetworkEvent,
  Alert,
  Route,
  DeviceStatus,
  GPRSSession,
  UDPSession,
  CarPark,
  CarLane,
  CarSlot,
  Report,
  Statistics,
  CellTower,
  ServerSMS,
  TicketDetail,
  User,
  AuthTokens,
  LoginCredentials,
  RegisterData,
  ApiResponse,
  PaginatedResponse,
  DeviceStats,
  DeviceFilters,
  VehicleFilters,
  DriverFilters,
  GeofenceFilters,
  DateRange,
  RealTimePosition,
  DeviceTrail,
  DeviceCommand,
  GeofenceEvent,
  Position,
  Point
} from '../types/unified';

// ============================================================================
// AUTHENTICATION SERVICE
// ============================================================================

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response = await api.post('/auth/login/', credentials);
    return response.data;
  },

  register: async (data: RegisterData): Promise<User> => {
    const response = await api.post('/auth/register/', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout/');
  },

  refreshToken: async (): Promise<AuthTokens> => {
    const response = await api.post('/auth/refresh/');
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/gps/users/me/');
    return response.data;
  },

  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await api.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword
    });
  },

  resetPassword: async (email: string): Promise<void> => {
    await api.post('/auth/reset-password/', { email });
  }
};

// ============================================================================
// GPS DEVICES SERVICE
// ============================================================================

export const deviceService = {
  // Get all devices with filters
  getDevices: async (filters?: DeviceFilters): Promise<GPSDevice[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.get(`/gps/devices/?${params.toString()}`);
    return response.data;
  },

  // Get single device
  getDevice: async (imei: number): Promise<GPSDevice> => {
    const response = await api.get(`/gps/devices/${imei}/`);
    return response.data;
  },

  // Create new device
  createDevice: async (deviceData: Partial<GPSDevice>): Promise<GPSDevice> => {
    const response = await api.post('/gps/devices/', deviceData);
    return response.data;
  },

  // Update device
  updateDevice: async (imei: number, deviceData: Partial<GPSDevice>): Promise<GPSDevice> => {
    const response = await api.patch(`/gps/devices/${imei}/`, deviceData);
    return response.data;
  },

  // Delete device
  deleteDevice: async (imei: number): Promise<void> => {
    await api.delete(`/gps/devices/${imei}/`);
  },

  // Test device connection
  testConnection: async (imei: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.get(`/gps/devices/${imei}/test-connection/`);
    return response.data;
  },

  // Get device history
  getDeviceHistory: async (imei: number, startDate?: string, endDate?: string): Promise<Location[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const response = await api.get(`/gps/devices/${imei}/history/?${params.toString()}`);
    return response.data;
  },

  // Get device events
  getDeviceEvents: async (imei: number, eventType?: string, startDate?: string, endDate?: string): Promise<DeviceEvent[]> => {
    const params = new URLSearchParams();
    if (eventType) params.append('type', eventType);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const response = await api.get(`/gps/devices/${imei}/events/?${params.toString()}`);
    return response.data;
  },

  // Get device trail
  getDeviceTrail: async (imei: number, startDate?: string, endDate?: string): Promise<DeviceTrail> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const response = await api.get(`/gps/devices/${imei}/trail/?${params.toString()}`);
    return response.data;
  },

  // Get device connection history
  getConnectionHistory: async (imei: number, startTime?: string, endTime?: string): Promise<NetworkEvent[]> => {
    const params = new URLSearchParams();
    if (startTime) params.append('start_time', startTime);
    if (endTime) params.append('end_time', endTime);
    const response = await api.get(`/gps/devices/${imei}/connections/?${params.toString()}`);
    return response.data.history;
  },

  // Get device connection stats
  getConnectionStats: async (imei: number): Promise<any> => {
    const response = await api.get(`/gps/devices/${imei}/connection-stats/`);
    return response.data;
  },

  // Get device current status
  getCurrentStatus: async (imei: number): Promise<DeviceStatus> => {
    const response = await api.get(`/gps/devices/${imei}/status/`);
    return response.data;
  },

  // Send command to device
  sendCommand: async (imei: number, command: DeviceCommand): Promise<DeviceCommand> => {
    const response = await api.post(`/gps/devices/${imei}/command/`, command);
    return response.data;
  },

  // Get device statistics
  getDeviceStats: async (imei: number, dateRange: DateRange): Promise<Statistics> => {
    const response = await api.get(`/gps/devices/${imei}/stats/`, {
      params: dateRange
    });
    return response.data;
  }
};

// ============================================================================
// VEHICLES SERVICE
// ============================================================================

export const vehicleService = {
  // Get all vehicles with filters
  getVehicles: async (filters?: VehicleFilters): Promise<Vehicle[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.get(`/gps/vehicles/?${params.toString()}`);
    return response.data;
  },

  // Get single vehicle
  getVehicle: async (id: number): Promise<Vehicle> => {
    const response = await api.get(`/gps/vehicles/${id}/`);
    return response.data;
  },

  // Create new vehicle
  createVehicle: async (vehicleData: Partial<Vehicle>): Promise<Vehicle> => {
    const response = await api.post('/gps/vehicles/', vehicleData);
    return response.data;
  },

  // Update vehicle
  updateVehicle: async (id: number, vehicleData: Partial<Vehicle>): Promise<Vehicle> => {
    const response = await api.put(`/gps/vehicles/${id}/`, vehicleData);
    return response.data;
  },

  // Delete vehicle
  deleteVehicle: async (id: number): Promise<void> => {
    await api.delete(`/gps/vehicles/${id}/`);
  },

  // Assign GPS device to vehicle
  assignDevice: async (vehicleId: number, deviceId: number): Promise<Vehicle> => {
    const response = await api.post(`/gps/vehicles/${vehicleId}/assign-device/`, {
      device_id: deviceId
    });
    return response.data;
  },

  // Assign driver to vehicle
  assignDriver: async (vehicleId: number, driverId: number): Promise<Vehicle> => {
    const response = await api.post(`/gps/vehicles/${vehicleId}/assign-driver/`, {
      driver_id: driverId
    });
    return response.data;
  },

  // Get available GPS devices
  getAvailableDevices: async (): Promise<GPSDevice[]> => {
    const response = await api.get('/gps/vehicles/available-devices/');
    return response.data;
  },

  // Get available drivers
  getAvailableDrivers: async (): Promise<Driver[]> => {
    const response = await api.get('/gps/vehicles/available-drivers/');
    return response.data;
  }
};

// ============================================================================
// DRIVERS SERVICE
// ============================================================================

export const driverService = {
  // Get all drivers with filters
  getDrivers: async (filters?: DriverFilters): Promise<Driver[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.get(`/gps/drivers/?${params.toString()}`);
    return response.data;
  },

  // Get single driver
  getDriver: async (id: number): Promise<Driver> => {
    const response = await api.get(`/gps/drivers/${id}/`);
    return response.data;
  },

  // Create new driver
  createDriver: async (driverData: Partial<Driver>): Promise<Driver> => {
    const response = await api.post('/gps/drivers/', driverData);
    return response.data;
  },

  // Update driver
  updateDriver: async (id: number, driverData: Partial<Driver>): Promise<Driver> => {
    const response = await api.put(`/gps/drivers/${id}/`, driverData);
    return response.data;
  },

  // Delete driver
  deleteDriver: async (id: number): Promise<void> => {
    await api.delete(`/gps/drivers/${id}/`);
  },

  // Assign vehicle to driver
  assignVehicle: async (driverId: number, vehicleId: number): Promise<Driver> => {
    const response = await api.post(`/gps/drivers/${driverId}/assign-vehicle/`, {
      vehicle_id: vehicleId
    });
    return response.data;
  },

  // Get available vehicles
  getAvailableVehicles: async (): Promise<Vehicle[]> => {
    const response = await api.get('/gps/drivers/available-vehicles/');
    return response.data;
  }
};

// ============================================================================
// GEOFENCING SERVICE
// ============================================================================

export const geofenceService = {
  // Get all geofences with filters
  getGeofences: async (filters?: GeofenceFilters): Promise<GeoFence[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    const response = await api.get(`/geofencing/geofences/?${params.toString()}`);
    return response.data;
  },

  // Get single geofence
  getGeofence: async (id: number): Promise<GeoFence> => {
    const response = await api.get(`/geofencing/geofences/${id}/`);
    return response.data;
  },

  // Create new geofence
  createGeofence: async (geofenceData: Partial<GeoFence>): Promise<GeoFence> => {
    const response = await api.post('/geofencing/geofences/', geofenceData);
    return response.data;
  },

  // Update geofence
  updateGeofence: async (id: number, geofenceData: Partial<GeoFence>): Promise<GeoFence> => {
    const response = await api.put(`/geofencing/geofences/${id}/`, geofenceData);
    return response.data;
  },

  // Delete geofence
  deleteGeofence: async (id: number): Promise<void> => {
    await api.delete(`/geofencing/geofences/${id}/`);
  },

  // Get geofence events
  getGeofenceEvents: async (id: number, startDate?: string, endDate?: string): Promise<GeofenceEvent[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const response = await api.get(`/geofencing/geofences/${id}/events/?${params.toString()}`);
    return response.data;
  },

  // Get geofence statistics
  getGeofenceStats: async (id: number, startDate?: string, endDate?: string): Promise<any> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const response = await api.get(`/geofencing/geofences/${id}/statistics/?${params.toString()}`);
    return response.data;
  },

  // Monitor all geofences
  monitorGeofences: async (): Promise<any> => {
    const response = await api.get('/geofencing/geofences/monitor/');
    return response.data;
  }
};

// ============================================================================
// TRACKING & MONITORING SERVICE
// ============================================================================

export const trackingService = {
  // Get real-time positions
  getRealTimePositions: async (): Promise<RealTimePosition[]> => {
    const response = await api.get('/gps/positions/real-time/');
    return response.data;
  },

  // Get active sessions
  getActiveSessions: async (): Promise<GPRSSession[]> => {
    const response = await api.get('/gps/sessions/active/');
    return response.data.sessions;
  },

  // Get device alerts
  getAlerts: async (deviceId?: number, acknowledged?: boolean): Promise<Alert[]> => {
    const params = new URLSearchParams();
    if (deviceId) params.append('device_id', deviceId.toString());
    if (acknowledged !== undefined) params.append('acknowledged', acknowledged.toString());
    const response = await api.get(`/tracking/alerts/?${params.toString()}`);
    return response.data;
  },

  // Acknowledge alert
  acknowledgeAlert: async (alertId: number): Promise<Alert> => {
    const response = await api.post(`/tracking/alerts/${alertId}/acknowledge/`);
    return response.data;
  },

  // Get device routes
  getDeviceRoutes: async (deviceId: number, completed?: boolean): Promise<Route[]> => {
    const params = new URLSearchParams();
    if (completed !== undefined) params.append('completed', completed.toString());
    const response = await api.get(`/tracking/routes/?device_id=${deviceId}&${params.toString()}`);
    return response.data;
  },

  // Get device status
  getDeviceStatus: async (deviceId: number): Promise<DeviceStatus> => {
    const response = await api.get(`/monitoring/device-status/${deviceId}/`);
    return response.data;
  },

  // Check all devices status
  checkAllDevicesStatus: async (): Promise<DeviceStats> => {
    const response = await api.get('/gps/devices/check-status/');
    return response.data;
  },

  // Get devices activity status
  getDevicesActivityStatus: async (): Promise<any> => {
    const response = await api.get('/gps/devices/activity-status/');
    return response.data;
  }
};

// ============================================================================
// REPORTS SERVICE
// ============================================================================

export const reportService = {
  // Get all reports
  getReports: async (): Promise<Report[]> => {
    const response = await api.get('/reports/reports/');
    return response.data;
  },

  // Get single report
  getReport: async (id: number): Promise<Report> => {
    const response = await api.get(`/reports/reports/${id}/`);
    return response.data;
  },

  // Create new report
  createReport: async (reportData: Partial<Report>): Promise<Report> => {
    const response = await api.post('/reports/reports/', reportData);
    return response.data;
  },

  // Generate route report
  generateRouteReport: async (routeId: number, dateRange: DateRange): Promise<any> => {
    const response = await api.post('/reports/route-report/', {
      route_id: routeId,
      ...dateRange
    });
    return response.data;
  },

  // Generate driver report
  generateDriverReport: async (driverId: number, dateRange: DateRange): Promise<any> => {
    const response = await api.post('/reports/driver-report/', {
      driver_id: driverId,
      ...dateRange
    });
    return response.data;
  },

  // Generate device report
  generateDeviceReport: async (deviceId: number, dateRange: DateRange): Promise<any> => {
    const response = await api.post('/reports/device-report/', {
      device_id: deviceId,
      ...dateRange
    });
    return response.data;
  },

  // Calculate daily statistics
  calculateDailyStats: async (date: string): Promise<any> => {
    const response = await api.post('/reports/statistics/calculate-daily/', {
      date
    });
    return response.data;
  }
};

// ============================================================================
// PARKING SERVICE
// ============================================================================

export const parkingService = {
  // Get all car parks
  getCarParks: async (): Promise<CarPark[]> => {
    const response = await api.get('/gps/car-parks/');
    return response.data;
  },

  // Get car park with lanes and slots
  getCarPark: async (id: number): Promise<CarPark & { lanes: CarLane[] }> => {
    const response = await api.get(`/gps/car-parks/${id}/`);
    return response.data;
  },

  // Get car lanes
  getCarLanes: async (parkId: number): Promise<CarLane[]> => {
    const response = await api.get(`/gps/car-lanes/?park_id=${parkId}`);
    return response.data;
  },

  // Get car slots
  getCarSlots: async (laneId: number): Promise<CarSlot[]> => {
    const response = await api.get(`/gps/car-slots/?lane_id=${laneId}`);
    return response.data;
  },

  // Assign car to slot
  assignCarToSlot: async (slotId: number, carSerial: string): Promise<CarSlot> => {
    const response = await api.post(`/gps/car-slots/${slotId}/assign/`, {
      car_serial: carSerial
    });
    return response.data;
  },

  // Remove car from slot
  removeCarFromSlot: async (slotId: number): Promise<CarSlot> => {
    const response = await api.post(`/gps/car-slots/${slotId}/remove/`);
    return response.data;
  }
};

// ============================================================================
// COMMUNICATION SERVICE
// ============================================================================

export const communicationService = {
  // Get cell towers
  getCellTowers: async (): Promise<CellTower[]> => {
    const response = await api.get('/gps/cell-towers/');
    return response.data;
  },

  // Send SMS to device
  sendSMS: async (deviceId: number, message: string): Promise<ServerSMS> => {
    const response = await api.post('/gps/sms/', {
      device_id: deviceId,
      message
    });
    return response.data;
  },

  // Get SMS history
  getSMSHistory: async (deviceId?: number): Promise<ServerSMS[]> => {
    const params = deviceId ? `?device_id=${deviceId}` : '';
    const response = await api.get(`/gps/sms/${params}`);
    return response.data;
  }
};

// ============================================================================
// TICKETS SERVICE
// ============================================================================

export const ticketService = {
  // Get ticket details
  getTicketDetails: async (deviceId?: number): Promise<TicketDetail[]> => {
    const params = deviceId ? `?device_id=${deviceId}` : '';
    const response = await api.get(`/gps/ticket-details/${params}`);
    return response.data;
  },

  // Create ticket detail
  createTicketDetail: async (ticketData: Partial<TicketDetail>): Promise<TicketDetail> => {
    const response = await api.post('/gps/ticket-details/', ticketData);
    return response.data;
  }
};

// ============================================================================
// COORDINATES SERVICE
// ============================================================================

export const coordinateService = {
  // Get coordinates
  getCoordinates: async (deviceId?: string): Promise<any[]> => {
    const params = deviceId ? `?device_id=${deviceId}` : '';
    const response = await api.get(`/coordinates/coordinates/${params}`);
    return response.data;
  },

  // Get latest coordinates
  getLatestCoordinates: async (deviceId?: string): Promise<any> => {
    const params = deviceId ? `?device_id=${deviceId}` : '';
    const response = await api.get(`/coordinates/coordinates/get_latest/${params}`);
    return response.data;
  },

  // Generate test data
  generateTestData: async (deviceId: string, points: number = 10): Promise<any[]> => {
    const response = await api.get(`/coordinates/coordinates/generate_test_data/?device_id=${deviceId}&points=${points}`);
    return response.data;
  }
};

// ============================================================================
// EXPORT ALL SERVICES
// ============================================================================

export default {
  auth: authService,
  devices: deviceService,
  vehicles: vehicleService,
  drivers: driverService,
  geofences: geofenceService,
  tracking: trackingService,
  reports: reportService,
  parking: parkingService,
  communication: communicationService,
  tickets: ticketService,
  coordinates: coordinateService
}; 