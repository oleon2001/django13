import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { BaseLayout } from './components/Layout/BaseLayout';
import { LoginPage } from './pages/Login/LoginPage';
// Import lazy-loaded components for better performance
import {
  LazyDashboard,
  LazyGPS,
  LazyMonitoring,
  LazyTracking,
  LazyVehicles,
  LazyReports,
  LazySettings,
  LazyDrivers,
  LazyParking,
  LazySensors,
  LazyGPSPage,
  LazyDeviceManagement,
  LazyRoutesPage,
  ComponentPreloader
} from './components/LazyComponents';
import './App.css';

// Componente para rutas protegidas
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%)',
        color: '#e01a22',
        fontSize: '1.2rem'
      }}>
        Cargando...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <BaseLayout>{children}</BaseLayout>;
};

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        {/* Preload components for better UX */}
        <ComponentPreloader />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <LazyDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <LazyDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/gps"
            element={
              <ProtectedRoute>
                <LazyGPS />
              </ProtectedRoute>
            }
          />
          <Route
            path="/monitoring"
            element={
              <ProtectedRoute>
                <LazyMonitoring />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tracking"
            element={
              <ProtectedRoute>
                <LazyTracking />
              </ProtectedRoute>
            }
          />
          <Route
            path="/vehicles"
            element={
              <ProtectedRoute>
                <LazyVehicles />
              </ProtectedRoute>
            }
          />
          <Route
            path="/drivers"
            element={
              <ProtectedRoute>
                <LazyDrivers />
              </ProtectedRoute>
            }
          />
          <Route
            path="/parking"
            element={
              <ProtectedRoute>
                <LazyParking />
              </ProtectedRoute>
            }
          />
          <Route
            path="/sensors"
            element={
              <ProtectedRoute>
                <LazySensors />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <LazyReports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <LazySettings />
              </ProtectedRoute>
            }
          />
          <Route path="/gps-page" element={<LazyGPSPage />} />
          <Route
            path="/devices"
            element={
              <ProtectedRoute>
                <LazyDeviceManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/routes"
            element={
              <ProtectedRoute>
                <LazyRoutesPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
};

export default App;
