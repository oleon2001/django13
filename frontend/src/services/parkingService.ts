import api from './api';
import { CarPark, CarLane, CarSlot } from '../types';

export const parkingService = {
  // Car Park operations
  getCarParks: async (): Promise<CarPark[]> => {
    const response = await api.get('/gps/car-parks/');
    return response.data;
  },

  getCarPark: async (id: number): Promise<CarPark> => {
    const response = await api.get(`/gps/car-parks/${id}/`);
    return response.data;
  },

  createCarPark: async (park: Partial<CarPark>): Promise<CarPark> => {
    const response = await api.post('/gps/car-parks/', park);
    return response.data;
  },

  updateCarPark: async (id: number, park: Partial<CarPark>): Promise<CarPark> => {
    const response = await api.patch(`/gps/car-parks/${id}/`, park);
    return response.data;
  },

  deleteCarPark: async (id: number): Promise<void> => {
    await api.delete(`/gps/car-parks/${id}/`);
  },

  // Car Lane operations
  getCarLanes: async (parkId?: number): Promise<CarLane[]> => {
    const url = parkId ? `/gps/car-lanes/?park=${parkId}` : '/gps/car-lanes/';
    const response = await api.get(url);
    return response.data;
  },

  createCarLane: async (lane: Partial<CarLane>): Promise<CarLane> => {
    const response = await api.post('/gps/car-lanes/', lane);
    return response.data;
  },

  updateCarLane: async (id: number, lane: Partial<CarLane>): Promise<CarLane> => {
    const response = await api.patch(`/gps/car-lanes/${id}/`, lane);
    return response.data;
  },

  deleteCarLane: async (id: number): Promise<void> => {
    await api.delete(`/gps/car-lanes/${id}/`);
  },

  // Car Slot operations
  getCarSlots: async (laneId?: number): Promise<CarSlot[]> => {
    const url = laneId ? `/gps/car-slots/?lane=${laneId}` : '/gps/car-slots/';
    const response = await api.get(url);
    return response.data;
  },

  updateCarSlot: async (id: number, slot: Partial<CarSlot>): Promise<CarSlot> => {
    const response = await api.patch(`/gps/car-slots/${id}/`, slot);
    return response.data;
  },

  // Occupancy and statistics
  getParkOccupancy: async (parkId: number) => {
    const response = await api.get(`/gps/car-parks/${parkId}/occupancy/`);
    return response.data;
  },

  getLaneOccupancy: async (laneId: number) => {
    const response = await api.get(`/gps/car-lanes/${laneId}/occupancy/`);
    return response.data;
  },

  // Search cars
  searchCarBySerial: async (serial: string): Promise<CarSlot[]> => {
    const response = await api.get(`/gps/car-slots/search/?serial=${serial}`);
    return response.data;
  },

  // Batch operations
  clearLot: async (parkId: number): Promise<{ cleared: number }> => {
    const response = await api.post(`/gps/car-parks/${parkId}/clear/`);
    return response.data;
  },

  // Import/Export
  exportParkData: async (parkId: number): Promise<Blob> => {
    const response = await api.get(`/gps/car-parks/${parkId}/export/`, {
      responseType: 'blob'
    });
    return response.data;
  },

  importParkData: async (parkId: number, file: File): Promise<{ imported: number }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/gps/car-parks/${parkId}/import/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // Gridless cars (cars not in specific slots)
  getGridlessCars: async () => {
    const response = await api.get('/gps/gridless-cars/');
    return response.data;
  },

  createGridlessCar: async (car: any) => {
    const response = await api.post('/gps/gridless-cars/', car);
    return response.data;
  },
}; 