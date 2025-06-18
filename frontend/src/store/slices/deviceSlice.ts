import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Device } from '../../types';
import { deviceService } from '../../services/deviceService';

interface DeviceState {
    devices: Device[];
    selectedDevice: Device | null;
    loading: boolean;
    error: string | null;
}

const initialState: DeviceState = {
    devices: [
        {
            id: 1,
            name: 'Bus 101',
            imei: 123456789012345,
            serial: 'SN101',
            connection_status: 'ONLINE',
            updated_at: new Date().toISOString(),
            speed: 45,
            course: 180,
            protocol: 'GT06',
            last_heartbeat: new Date().toISOString(),
            position: {
                latitude: 19.4326,
                longitude: -99.1332
            }
        },
        {
            id: 2,
            name: 'Bus 102',
            imei: 987654321098765,
            serial: 'SN102',
            connection_status: 'OFFLINE',
            updated_at: new Date().toISOString(),
            speed: 0,
            course: 0,
            protocol: 'GT06',
            last_heartbeat: new Date().toISOString(),
            position: {
                latitude: 19.4284,
                longitude: -99.1276
            }
        }
    ],
    selectedDevice: null,
    loading: false,
    error: null,
};

export const fetchDevices = createAsyncThunk(
    'devices/fetchAll',
    async () => {
        return await deviceService.getAll();
    }
);

export const fetchDevice = createAsyncThunk(
    'devices/fetchOne',
    async (id: string) => {
        return await deviceService.getById(Number(id));
    }
);

export const updateDevice = createAsyncThunk(
    'devices/update',
    async ({ id, data }: { id: string; data: Partial<Device> }) => {
        const updatedDevice = await deviceService.getById(Number(id));
        return { ...updatedDevice, ...data };
    }
);

const deviceSlice = createSlice({
    name: 'devices',
    initialState,
    reducers: {
        selectDevice: (state, action) => {
            state.selectedDevice = action.payload;
        },
        clearSelectedDevice: (state) => {
            state.selectedDevice = null;
        },
        clearError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchDevices.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchDevices.fulfilled, (state, action) => {
                state.loading = false;
                state.devices = action.payload;
            })
            .addCase(fetchDevices.rejected, (state, action) => {
                state.loading = false;
                state.error = action.error.message || 'Error al cargar los dispositivos';
            })
            .addCase(fetchDevice.fulfilled, (state, action) => {
                state.selectedDevice = action.payload;
            })
            .addCase(updateDevice.fulfilled, (state, action) => {
                const index = state.devices.findIndex(d => d.id === action.payload.id);
                if (index !== -1) {
                    state.devices[index] = action.payload;
                }
                if (state.selectedDevice?.id === action.payload.id) {
                    state.selectedDevice = action.payload;
                }
            });
    },
});

export const { selectDevice, clearSelectedDevice, clearError } = deviceSlice.actions;
export default deviceSlice.reducer; 