import api from './api';

export interface Report {
  id: number;
  title: string;
  type: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  data?: any;
}

class ReportService {
  async getAll(): Promise<Report[]> {
    try {
      const response = await api.get('/reports/');
      return response.data;
    } catch (error) {
      console.error('Error fetching reports:', error);
      return [];
    }
  }

  async getById(id: number): Promise<Report | null> {
    try {
      const response = await api.get(`/reports/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching report:', error);
      return null;
    }
  }

  async create(data: Partial<Report>): Promise<Report | null> {
    try {
      const response = await api.post('/reports/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating report:', error);
      return null;
    }
  }

  async download(id: number): Promise<Blob | null> {
    try {
      const response = await api.get(`/reports/${id}/download/`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error downloading report:', error);
      return null;
    }
  }
}

export const reportService = new ReportService(); 