import React from 'react';
import { QueryProvider } from './QueryProvider';
import { NotificationProvider } from './NotificationProvider';
import { AuthProvider } from './AuthProvider';
import { ThemeProvider } from './ThemeProvider';
import { LanguageProvider } from './LanguageProvider';
import { PermissionProvider } from './PermissionProvider';
import { ConfigProvider } from './ConfigProvider';
import { GlobalStateProvider } from './GlobalStateProvider';
import { ErrorProvider } from './ErrorProvider';
import { WebSocketProvider } from './WebSocketProvider';
import { AnalyticsProvider } from './AnalyticsProvider';
import { CacheProvider } from './CacheProvider';
import { LogProvider } from './LogProvider';
import { RouterProvider } from './RouterProvider';
import { FormProvider } from './FormProvider';
import { ModalProvider } from './ModalProvider';

// ============================================================================
// APP PROVIDER - Provider principal que combina todos los providers
// ============================================================================

interface AppProviderProps {
  children: React.ReactNode;
  routes?: any[]; // Rutas para el RouterProvider
  initialFormValues?: Record<string, any>; // Valores iniciales para formularios
}

export const AppProvider: React.FC<AppProviderProps> = ({ 
  children, 
  routes = [],
  initialFormValues = {}
}) => {
  return (
    <ErrorProvider>
      <ConfigProvider>
        <LanguageProvider>
          <ThemeProvider>
            <NotificationProvider>
              <QueryProvider>
                <AuthProvider>
                  <PermissionProvider>
                    <GlobalStateProvider>
                      <WebSocketProvider>
                        <AnalyticsProvider>
                          <CacheProvider>
                            <LogProvider>
                              <RouterProvider routes={routes}>
                                <FormProvider initialValues={initialFormValues}>
                                  <ModalProvider>
                                    {children}
                                  </ModalProvider>
                                </FormProvider>
                              </RouterProvider>
                            </LogProvider>
                          </CacheProvider>
                        </AnalyticsProvider>
                      </WebSocketProvider>
                    </GlobalStateProvider>
                  </PermissionProvider>
                </AuthProvider>
              </QueryProvider>
            </NotificationProvider>
          </ThemeProvider>
        </LanguageProvider>
      </ConfigProvider>
    </ErrorProvider>
  );
}; 