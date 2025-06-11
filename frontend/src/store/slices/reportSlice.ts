import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Report } from '../../types';
import api from '../../services/api';

interface ReportState {
  reports: Report[];
  loading: boolean;
  error: string | null;
}

const initialState: ReportState = {
  reports: [],
  loading: false,
  error: null,
};

export const fetchReports = createAsyncThunk(
  'reports/fetchReports',
  async () => {
    const response = await api.get<Report[]>('/api/reports/');
    return response.data;
  }
);

const reportSlice = createSlice({
  name: 'reports',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchReports.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchReports.fulfilled, (state, action) => {
        state.loading = false;
        state.reports = action.payload;
      })
      .addCase(fetchReports.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Error al cargar los reportes';
      });
  },
});

export default reportSlice.reducer; 