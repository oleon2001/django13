import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { BaseLayout } from './components/Layout/BaseLayout';
import { LoginPage } from './pages/Login/LoginPage';
import TransitionWrapper from './components/TransitionWrapper';
import ErrorBoundary from './components/ErrorBoundary';
import EnhancedLoading from './components/EnhancedLoading';
// Import lazy-loaded components for better performance
import {
  DashboardWithLoading,
  MonitoringWithLoading,
  GPSWithLoading,
  GeofenceWithLoading,
  TrackingWithLoading,
  VehiclesWithLoading,
  DriversWithLoading,
  ParkingWithLoading,
  SensorsWithLoading,
  ReportsWithLoading,
  SettingsWithLoading,
  DeviceManagementWithLoading,
  RoutesPageWithLoading,
  GPSPageWithLoading,
  ComponentPreloader
} from './components/LazyComponents';
import './App.css';

// Componente para rutas protegidas
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <EnhancedLoading 
        message="Verificando autenticación" 
        subMessage="Validando credenciales de usuario"
        variant="detailed"
        module="dashboard"
      />
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <BaseLayout>
      <ErrorBoundary>
        <Suspense fallback={
          <EnhancedLoading 
            message="Cargando página" 
            subMessage="Preparando contenido"
            variant="default"
          />
        }>
          {children}
        </Suspense>
      </ErrorBoundary>
    </BaseLayout>
  );
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <TransitionWrapper>
        <Router>
          <AuthProvider>
            {/* Preload components for better UX */}
            <ComponentPreloader />
            <Suspense fallback={
              <EnhancedLoading 
                message="Inicializando aplicación" 
                subMessage="Configurando entorno de trabajo"
                variant="detailed"
                module="dashboard"
              />
            }>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <DashboardWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <DashboardWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/gps"
                  element={
                    <ProtectedRoute>
                      <GPSWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/geofences"
                  element={
                    <ProtectedRoute>
                      <GeofenceWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/monitoring"
                  element={
                    <ProtectedRoute>
                      <MonitoringWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/tracking"
                  element={
                    <ProtectedRoute>
                      <TrackingWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/vehicles"
                  element={
                    <ProtectedRoute>
                      <VehiclesWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/drivers"
                  element={
                    <ProtectedRoute>
                      <DriversWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/parking"
                  element={
                    <ProtectedRoute>
                      <ParkingWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/sensors"
                  element={
                    <ProtectedRoute>
                      <SensorsWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/reports"
                  element={
                    <ProtectedRoute>
                      <ReportsWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <SettingsWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route path="/gps-page" element={<GPSPageWithLoading />} />
                <Route
                  path="/devices"
                  element={
                    <ProtectedRoute>
                      <DeviceManagementWithLoading />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/routes"
                  element={
                    <ProtectedRoute>
                      <RoutesPageWithLoading />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </Suspense>
          </AuthProvider>
        </Router>
      </TransitionWrapper>
    </ErrorBoundary>
  );
};

export default App;
