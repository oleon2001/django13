import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { User } from '../../types';
import authService from '../../services/auth';

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
}

const initialState: AuthState = {
    user: null,
    token: null,
    isAuthenticated: false,
    loading: false,
    error: null,
};

// Inicializar el estado desde el localStorage de manera segura
const initializeState = () => {
    try {
        const user = authService.getUser();
        const token = authService.getToken();
        const isAuthenticated = authService.isAuthenticated();

        return {
            user,
            token,
            isAuthenticated,
            loading: false,
            error: null,
        };
    } catch (error) {
        console.error('Error initializing auth state:', error);
        return initialState;
    }
};

export const login = createAsyncThunk(
    'auth/login',
    async (credentials: { username: string; password: string }) => {
        const response = await authService.login(credentials);
        return response;
    }
);

export const logout = createAsyncThunk(
    'auth/logout',
    async () => {
        await authService.logout();
    }
);

export const getCurrentUser = createAsyncThunk(
    'auth/getCurrentUser',
    async () => {
        const user = await authService.getCurrentUser();
        return user;
    }
);

const authSlice = createSlice({
    name: 'auth',
    initialState: initializeState(),
    reducers: {
        clearError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(login.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(login.fulfilled, (state, action) => {
                state.loading = false;
                state.isAuthenticated = true;
                state.token = action.payload.access;
                state.user = action.payload.user;
            })
            .addCase(login.rejected, (state, action) => {
                state.loading = false;
                state.error = action.error.message || 'Error al iniciar sesión';
            })
            .addCase(logout.fulfilled, (state) => {
                state.user = null;
                state.token = null;
                state.isAuthenticated = false;
            })
            .addCase(getCurrentUser.fulfilled, (state, action) => {
                state.user = action.payload;
                state.isAuthenticated = true;
            });
    },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer; 