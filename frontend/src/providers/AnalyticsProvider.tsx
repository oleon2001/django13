import React, { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';
import { useAuth } from './AuthProvider';
import { useConfig } from './ConfigProvider';

// ============================================================================
// ANALYTICS TYPES - Tipos para analytics
// ============================================================================

export interface AnalyticsEvent {
  id: string;
  name: string;
  category: string;
  action: string;
  label?: string;
  value?: number;
  properties?: Record<string, any>;
  timestamp: string;
  userId?: string;
  sessionId: string;
  page?: string;
  userAgent?: string;
  ip?: string;
}

export interface AnalyticsPageView {
  id: string;
  path: string;
  title: string;
  referrer?: string;
  timestamp: string;
  userId?: string;
  sessionId: string;
  duration?: number;
  scrollDepth?: number;
  interactions: number;
}

export interface AnalyticsUser {
  id: string;
  email: string;
  name: string;
  role: string;
  firstSeen: string;
  lastSeen: string;
  totalSessions: number;
  totalEvents: number;
  properties: Record<string, any>;
}

export interface AnalyticsSession {
  id: string;
  userId?: string;
  startTime: string;
  endTime?: string;
  duration?: number;
  pageViews: number;
  events: number;
  referrer?: string;
  userAgent: string;
  ip?: string;
  properties: Record<string, any>;
}

export interface AnalyticsContextType {
  // Estado
  isEnabled: boolean;
  currentSession: AnalyticsSession | null;
  currentUser: AnalyticsUser | null;
  
  // Métodos de eventos
  trackEvent: (name: string, category: string, action: string, label?: string, value?: number, properties?: Record<string, any>) => void;
  trackPageView: (path: string, title: string, referrer?: string) => void;
  trackUserAction: (action: string, properties?: Record<string, any>) => void;
  trackError: (error: Error, context?: Record<string, any>) => void;
  trackPerformance: (metric: string, value: number, properties?: Record<string, any>) => void;
  
  // Métodos de usuario
  identifyUser: (userId: string, properties?: Record<string, any>) => void;
  setUserProperty: (key: string, value: any) => void;
  setUserProperties: (properties: Record<string, any>) => void;
  
  // Métodos de sesión
  startSession: () => void;
  endSession: () => void;
  updateSession: (properties: Record<string, any>) => void;
  
  // Métodos de utilidad
  getSessionId: () => string;
  getUserId: () => string | undefined;
  isTrackingEnabled: () => boolean;
  enableTracking: () => void;
  disableTracking: () => void;
  
  // Métodos de datos
  getEvents: (filters?: Record<string, any>) => AnalyticsEvent[];
  getPageViews: (filters?: Record<string, any>) => AnalyticsPageView[];
  getSessionData: () => AnalyticsSession | null;
  getUserData: () => AnalyticsUser | null;
  
  // Métodos de exportación
  exportData: (format: 'json' | 'csv') => void;
  clearData: () => void;
}

// ============================================================================
// ANALYTICS CONTEXT - Contexto para analytics
// ============================================================================

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

// ============================================================================
// ANALYTICS PROVIDER - Provider para analytics
// ============================================================================

interface AnalyticsProviderProps {
  children: ReactNode;
  enabled?: boolean;
  sessionTimeout?: number; // en milisegundos
  maxEvents?: number;
  autoTrackPageViews?: boolean;
  autoTrackErrors?: boolean;
  autoTrackPerformance?: boolean;
}

export const AnalyticsProvider: React.FC<AnalyticsProviderProps> = ({
  children,
  enabled = true,
  sessionTimeout = 30 * 60 * 1000, // 30 minutos
  maxEvents = 1000,
  autoTrackPageViews = true,
  autoTrackErrors = true,
  autoTrackPerformance = true,
}) => {
  const { user } = useAuth();
  const { config } = useConfig();
  
  const [isEnabled, setIsEnabled] = useState(enabled);
  const [currentSession, setCurrentSession] = useState<AnalyticsSession | null>(null);
  const [currentUser, setCurrentUser] = useState<AnalyticsUser | null>(null);
  const [events, setEvents] = useState<AnalyticsEvent[]>([]);
  const [pageViews, setPageViews] = useState<AnalyticsPageView[]>([]);
  
  const sessionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const sessionStartTimeRef = useRef<number>(0);
  const pageViewStartTimeRef = useRef<number>(0);
  const scrollDepthRef = useRef<number>(0);
  const interactionsRef = useRef<number>(0);

  // Generar ID único
  const generateId = (): string => {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Generar Session ID
  const generateSessionId = (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Obtener Session ID actual
  const getSessionId = (): string => {
    if (!currentSession) {
      return generateSessionId();
    }
    return currentSession.id;
  };

  // Obtener User ID actual
  const getUserId = (): string | undefined => {
    return user?.id?.toString();
  };

  // Verificar si el tracking está habilitado
  const isTrackingEnabled = (): boolean => {
    return isEnabled && !config.features.predictiveAnalytics; // Deshabilitar si no hay analytics predictivo
  };

  // Habilitar tracking
  const enableTracking = () => {
    setIsEnabled(true);
    localStorage.setItem('analytics_enabled', 'true');
  };

  // Deshabilitar tracking
  const disableTracking = () => {
    setIsEnabled(false);
    localStorage.setItem('analytics_enabled', 'false');
  };

  // Iniciar sesión
  const startSession = () => {
    if (!isTrackingEnabled()) return;

    const sessionId = generateSessionId();
    const startTime = new Date().toISOString();
    
    const session: AnalyticsSession = {
      id: sessionId,
      userId: getUserId(),
      startTime,
      userAgent: navigator.userAgent,
      pageViews: 0,
      events: 0,
      properties: {},
    };

    setCurrentSession(session);
    sessionStartTimeRef.current = Date.now();
    
    // Guardar en localStorage
    localStorage.setItem('analytics_session', JSON.stringify(session));
    
    // Configurar timeout de sesión
    sessionTimeoutRef.current = setTimeout(() => {
      endSession();
    }, sessionTimeout);
  };

  // Finalizar sesión
  const endSession = () => {
    if (!currentSession) return;

    const endTime = new Date().toISOString();
    const duration = Date.now() - sessionStartTimeRef.current;
    
    const updatedSession: AnalyticsSession = {
      ...currentSession,
      endTime,
      duration,
    };

    setCurrentSession(null);
    
    if (sessionTimeoutRef.current) {
      clearTimeout(sessionTimeoutRef.current);
      sessionTimeoutRef.current = null;
    }
    
    // Guardar sesión completada
    const completedSessions = JSON.parse(localStorage.getItem('analytics_completed_sessions') || '[]');
    completedSessions.push(updatedSession);
    localStorage.setItem('analytics_completed_sessions', JSON.stringify(completedSessions));
    
    // Limpiar sesión actual
    localStorage.removeItem('analytics_session');
  };

  // Actualizar sesión
  const updateSession = (properties: Record<string, any>) => {
    if (!currentSession) return;

    const updatedSession: AnalyticsSession = {
      ...currentSession,
      properties: { ...currentSession.properties, ...properties },
    };

    setCurrentSession(updatedSession);
    localStorage.setItem('analytics_session', JSON.stringify(updatedSession));
  };

  // Rastrear evento
  const trackEvent = (
    name: string,
    category: string,
    action: string,
    label?: string,
    value?: number,
    properties?: Record<string, any>
  ) => {
    if (!isTrackingEnabled()) return;

    const event: AnalyticsEvent = {
      id: generateId(),
      name,
      category,
      action,
      label,
      value,
      properties: {
        ...properties,
        page: window.location.pathname,
        referrer: document.referrer,
      },
      timestamp: new Date().toISOString(),
      userId: getUserId(),
      sessionId: getSessionId(),
      userAgent: navigator.userAgent,
    };

    setEvents(prev => {
      const updated = [event, ...prev];
      return updated.slice(0, maxEvents);
    });

    // Actualizar contador de eventos de la sesión
    if (currentSession) {
      updateSession({ events: currentSession.events + 1 });
    }

    // Enviar a servidor (simulado)
    sendToServer('event', event);
  };

  // Rastrear vista de página
  const trackPageView = (path: string, title: string, referrer?: string) => {
    if (!isTrackingEnabled()) return;

    const pageView: AnalyticsPageView = {
      id: generateId(),
      path,
      title,
      referrer: referrer || document.referrer,
      timestamp: new Date().toISOString(),
      userId: getUserId(),
      sessionId: getSessionId(),
      duration: pageViewStartTimeRef.current > 0 ? Date.now() - pageViewStartTimeRef.current : undefined,
      scrollDepth: scrollDepthRef.current,
      interactions: interactionsRef.current,
    };

    setPageViews(prev => {
      const updated = [pageView, ...prev];
      return updated.slice(0, maxEvents);
    });

    // Actualizar contador de vistas de página de la sesión
    if (currentSession) {
      updateSession({ pageViews: currentSession.pageViews + 1 });
    }

    // Resetear métricas de página
    pageViewStartTimeRef.current = Date.now();
    scrollDepthRef.current = 0;
    interactionsRef.current = 0;

    // Enviar a servidor (simulado)
    sendToServer('pageview', pageView);
  };

  // Rastrear acción de usuario
  const trackUserAction = (action: string, properties?: Record<string, any>) => {
    trackEvent('user_action', 'user', action, undefined, undefined, properties);
    interactionsRef.current++;
  };

  // Rastrear error
  const trackError = (error: Error, context?: Record<string, any>) => {
    trackEvent('error', 'system', 'error_occurred', error.message, undefined, {
      errorName: error.name,
      errorStack: error.stack,
      ...context,
    });
  };

  // Rastrear rendimiento
  const trackPerformance = (metric: string, value: number, properties?: Record<string, any>) => {
    trackEvent('performance', 'system', metric, undefined, value, properties);
  };

  // Identificar usuario
  const identifyUser = (userId: string, properties?: Record<string, any>) => {
    if (!isTrackingEnabled()) return;

    const userData: AnalyticsUser = {
      id: userId,
      email: user?.email || '',
      name: user?.full_name || '',
      role: user?.groups?.[0] || 'user',
      firstSeen: new Date().toISOString(),
      lastSeen: new Date().toISOString(),
      totalSessions: 1,
      totalEvents: 0,
      properties: properties || {},
    };

    setCurrentUser(userData);
    localStorage.setItem('analytics_user', JSON.stringify(userData));
  };

  // Establecer propiedad de usuario
  const setUserProperty = (key: string, value: any) => {
    if (!currentUser) return;

    const updatedUser: AnalyticsUser = {
      ...currentUser,
      properties: { ...currentUser.properties, [key]: value },
    };

    setCurrentUser(updatedUser);
    localStorage.setItem('analytics_user', JSON.stringify(updatedUser));
  };

  // Establecer propiedades de usuario
  const setUserProperties = (properties: Record<string, any>) => {
    if (!currentUser) return;

    const updatedUser: AnalyticsUser = {
      ...currentUser,
      properties: { ...currentUser.properties, ...properties },
    };

    setCurrentUser(updatedUser);
    localStorage.setItem('analytics_user', JSON.stringify(updatedUser));
  };

  // Obtener eventos
  const getEvents = (filters?: Record<string, any>): AnalyticsEvent[] => {
    let filteredEvents = events;

    if (filters) {
      filteredEvents = filteredEvents.filter(event => {
        return Object.entries(filters).every(([key, value]) => {
          return event.properties?.[key] === value || event[key as keyof AnalyticsEvent] === value;
        });
      });
    }

    return filteredEvents;
  };

  // Obtener vistas de página
  const getPageViews = (filters?: Record<string, any>): AnalyticsPageView[] => {
    let filteredPageViews = pageViews;

    if (filters) {
      filteredPageViews = filteredPageViews.filter(pageView => {
        return Object.entries(filters).every(([key, value]) => {
          return pageView[key as keyof AnalyticsPageView] === value;
        });
      });
    }

    return filteredPageViews;
  };

  // Obtener datos de sesión
  const getSessionData = (): AnalyticsSession | null => {
    return currentSession;
  };

  // Obtener datos de usuario
  const getUserData = (): AnalyticsUser | null => {
    return currentUser;
  };

  // Exportar datos
  const exportData = (format: 'json' | 'csv') => {
    const data = {
      events,
      pageViews,
      currentSession,
      currentUser,
    };

    if (format === 'json') {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } else if (format === 'csv') {
      // Implementar exportación CSV
      console.log('CSV export not implemented yet');
    }
  };

  // Limpiar datos
  const clearData = () => {
    setEvents([]);
    setPageViews([]);
    localStorage.removeItem('analytics_session');
    localStorage.removeItem('analytics_user');
    localStorage.removeItem('analytics_completed_sessions');
  };

  // Enviar datos al servidor (simulado)
  const sendToServer = (type: string, data: any) => {
    // En una implementación real, aquí se enviarían los datos al servidor
    console.log(`Analytics ${type}:`, data);
  };

  // Inicializar analytics
  useEffect(() => {
    // Cargar configuración guardada
    const savedEnabled = localStorage.getItem('analytics_enabled');
    if (savedEnabled !== null) {
      setIsEnabled(savedEnabled === 'true');
    }

    // Cargar sesión guardada
    const savedSession = localStorage.getItem('analytics_session');
    if (savedSession) {
      try {
        const session = JSON.parse(savedSession);
        setCurrentSession(session);
        sessionStartTimeRef.current = new Date(session.startTime).getTime();
      } catch (error) {
        console.error('Error loading saved session:', error);
      }
    }

    // Cargar usuario guardado
    const savedUser = localStorage.getItem('analytics_user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setCurrentUser(userData);
      } catch (error) {
        console.error('Error loading saved user:', error);
      }
    }

    // Iniciar sesión si no hay una activa
    if (!currentSession && isTrackingEnabled()) {
      startSession();
    }

    // Identificar usuario si está autenticado
    if (user && !currentUser) {
      identifyUser(user.id.toString(), {
        email: user.email,
        name: user.full_name,
        role: user.groups?.[0] || 'user',
      });
    }
  }, [user, isTrackingEnabled]);

  // Auto-track page views
  useEffect(() => {
    if (!autoTrackPageViews || !isTrackingEnabled()) return;

    const handlePageView = () => {
      trackPageView(window.location.pathname, document.title);
    };

    // Track initial page view
    handlePageView();

    // Listen for navigation changes
    window.addEventListener('popstate', handlePageView);
    
    return () => {
      window.removeEventListener('popstate', handlePageView);
    };
  }, [autoTrackPageViews, isTrackingEnabled]);

  // Auto-track errors
  useEffect(() => {
    if (!autoTrackErrors || !isTrackingEnabled()) return;

    const handleError = (event: ErrorEvent) => {
      trackError(event.error || new Error(event.message), {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      trackError(new Error(event.reason), {
        type: 'unhandled_rejection',
      });
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [autoTrackErrors, isTrackingEnabled]);

  // Auto-track performance
  useEffect(() => {
    if (!autoTrackPerformance || !isTrackingEnabled()) return;

    const trackPerformanceMetrics = () => {
      if ('performance' in window) {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        
        if (navigation) {
          trackPerformance('dom_content_loaded', navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart);
          trackPerformance('load', navigation.loadEventEnd - navigation.loadEventStart);
          trackPerformance('first_paint', performance.getEntriesByName('first-paint')[0]?.startTime || 0);
          trackPerformance('first_contentful_paint', performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0);
        }
      }
    };

    // Track performance after page load
    if (document.readyState === 'complete') {
      trackPerformanceMetrics();
    } else {
      window.addEventListener('load', trackPerformanceMetrics);
      return () => window.removeEventListener('load', trackPerformanceMetrics);
    }
  }, [autoTrackPerformance, isTrackingEnabled]);

  // Track scroll depth
  useEffect(() => {
    if (!isTrackingEnabled()) return;

    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const depth = Math.round((scrollTop / scrollHeight) * 100);
      
      if (depth > scrollDepthRef.current) {
        scrollDepthRef.current = depth;
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isTrackingEnabled]);

  const value: AnalyticsContextType = {
    isEnabled,
    currentSession,
    currentUser,
    trackEvent,
    trackPageView,
    trackUserAction,
    trackError,
    trackPerformance,
    identifyUser,
    setUserProperty,
    setUserProperties,
    startSession,
    endSession,
    updateSession,
    getSessionId,
    getUserId,
    isTrackingEnabled,
    enableTracking,
    disableTracking,
    getEvents,
    getPageViews,
    getSessionData,
    getUserData,
    exportData,
    clearData,
  };

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
};

// ============================================================================
// ANALYTICS HOOK - Hook para usar el contexto de analytics
// ============================================================================

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  
  if (context === undefined) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  
  return context;
};

// ============================================================================
// ANALYTICS HOOKS ESPECÍFICOS - Hooks para casos de uso específicos
// ============================================================================

export const useTrackEvent = () => {
  const { trackEvent } = useAnalytics();
  return trackEvent;
};

export const useTrackPageView = () => {
  const { trackPageView } = useAnalytics();
  return trackPageView;
};

export const useTrackUserAction = () => {
  const { trackUserAction } = useAnalytics();
  return trackUserAction;
};

export const useTrackError = () => {
  const { trackError } = useAnalytics();
  return trackError;
};

export const useAnalyticsSession = () => {
  const { currentSession, startSession, endSession, updateSession } = useAnalytics();
  return { currentSession, startSession, endSession, updateSession };
};

export const useAnalyticsUser = () => {
  const { currentUser, identifyUser, setUserProperty, setUserProperties } = useAnalytics();
  return { currentUser, identifyUser, setUserProperty, setUserProperties };
}; 