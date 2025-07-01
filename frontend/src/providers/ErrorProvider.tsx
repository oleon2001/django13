import React, { createContext, useContext, useState, ReactNode } from 'react';

// ============================================================================
// ERROR TYPES - Tipos para errores
// ============================================================================

export interface AppError {
  id: string;
  type: 'error' | 'warning' | 'info';
  title: string;
  message: string;
  details?: string;
  timestamp: string;
  source: string;
  stack?: string;
  userAgent?: string;
  url?: string;
  userId?: string;
  sessionId?: string;
  resolved: boolean;
  retryCount: number;
  maxRetries: number;
  retryable: boolean;
  action?: {
    label: string;
    handler: () => void;
  };
}

export interface ErrorContextType {
  errors: AppError[];
  addError: (error: Omit<AppError, 'id' | 'timestamp' | 'resolved' | 'retryCount'>) => void;
  removeError: (id: string) => void;
  resolveError: (id: string) => void;
  retryError: (id: string) => void;
  clearErrors: () => void;
  clearResolvedErrors: () => void;
  getUnresolvedErrors: () => AppError[];
  getErrorsByType: (type: AppError['type']) => AppError[];
  getErrorsBySource: (source: string) => AppError[];
  hasErrors: () => boolean;
  hasUnresolvedErrors: () => boolean;
  getErrorCount: () => number;
  getUnresolvedErrorCount: () => number;
}

// ============================================================================
// ERROR CONTEXT - Contexto para errores
// ============================================================================

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

// ============================================================================
// ERROR PROVIDER - Provider para errores
// ============================================================================

interface ErrorProviderProps {
  children: ReactNode;
  maxErrors?: number;
  autoResolveAfter?: number; // en milisegundos
}

export const ErrorProvider: React.FC<ErrorProviderProps> = ({ 
  children, 
  maxErrors = 100,
  autoResolveAfter = 30000 // 30 segundos
}) => {
  const [errors, setErrors] = useState<AppError[]>([]);

  // Generar ID único para errores
  const generateErrorId = (): string => {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Agregar error
  const addError = (errorData: Omit<AppError, 'id' | 'timestamp' | 'resolved' | 'retryCount'>) => {
    const newError: AppError = {
      ...errorData,
      id: generateErrorId(),
      timestamp: new Date().toISOString(),
      resolved: false,
      retryCount: 0,
    };

    setErrors(prevErrors => {
      const updatedErrors = [newError, ...prevErrors];
      
      // Limitar el número máximo de errores
      if (updatedErrors.length > maxErrors) {
        return updatedErrors.slice(0, maxErrors);
      }
      
      return updatedErrors;
    });

    // Auto-resolver errores después de un tiempo (solo para warnings e info)
    if (errorData.type !== 'error' && autoResolveAfter > 0) {
      setTimeout(() => {
        resolveError(newError.id);
      }, autoResolveAfter);
    }
  };

  // Remover error
  const removeError = (id: string) => {
    setErrors(prevErrors => prevErrors.filter(error => error.id !== id));
  };

  // Resolver error
  const resolveError = (id: string) => {
    setErrors(prevErrors =>
      prevErrors.map(error =>
        error.id === id ? { ...error, resolved: true } : error
      )
    );
  };

  // Reintentar error
  const retryError = (id: string) => {
    setErrors(prevErrors =>
      prevErrors.map(error => {
        if (error.id === id && error.retryable && error.retryCount < error.maxRetries) {
          return {
            ...error,
            retryCount: error.retryCount + 1,
            resolved: false,
          };
        }
        return error;
      })
    );
  };

  // Limpiar todos los errores
  const clearErrors = () => {
    setErrors([]);
  };

  // Limpiar errores resueltos
  const clearResolvedErrors = () => {
    setErrors(prevErrors => prevErrors.filter(error => !error.resolved));
  };

  // Obtener errores no resueltos
  const getUnresolvedErrors = (): AppError[] => {
    return errors.filter(error => !error.resolved);
  };

  // Obtener errores por tipo
  const getErrorsByType = (type: AppError['type']): AppError[] => {
    return errors.filter(error => error.type === type);
  };

  // Obtener errores por fuente
  const getErrorsBySource = (source: string): AppError[] => {
    return errors.filter(error => error.source === source);
  };

  // Verificar si hay errores
  const hasErrors = (): boolean => {
    return errors.length > 0;
  };

  // Verificar si hay errores no resueltos
  const hasUnresolvedErrors = (): boolean => {
    return errors.some(error => !error.resolved);
  };

  // Obtener conteo de errores
  const getErrorCount = (): number => {
    return errors.length;
  };

  // Obtener conteo de errores no resueltos
  const getUnresolvedErrorCount = (): number => {
    return errors.filter(error => !error.resolved).length;
  };

  const value: ErrorContextType = {
    errors,
    addError,
    removeError,
    resolveError,
    retryError,
    clearErrors,
    clearResolvedErrors,
    getUnresolvedErrors,
    getErrorsByType,
    getErrorsBySource,
    hasErrors,
    hasUnresolvedErrors,
    getErrorCount,
    getUnresolvedErrorCount,
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
    </ErrorContext.Provider>
  );
};

// ============================================================================
// ERROR HOOK - Hook para usar el contexto de errores
// ============================================================================

export const useError = () => {
  const context = useContext(ErrorContext);
  
  if (context === undefined) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  
  return context;
};

// ============================================================================
// ERROR UTILITIES - Utilidades para manejo de errores
// ============================================================================

export const createError = (
  type: AppError['type'],
  title: string,
  message: string,
  source: string,
  options: Partial<Omit<AppError, 'id' | 'timestamp' | 'resolved' | 'retryCount' | 'type' | 'title' | 'message' | 'source'>> = {}
): Omit<AppError, 'id' | 'timestamp' | 'resolved' | 'retryCount'> => {
  return {
    type,
    title,
    message,
    source,
    details: options.details,
    stack: options.stack,
    userAgent: options.userAgent || navigator.userAgent,
    url: options.url || window.location.href,
    userId: options.userId,
    sessionId: options.sessionId,
    maxRetries: options.maxRetries || 3,
    retryable: options.retryable !== undefined ? options.retryable : type !== 'error',
    action: options.action,
  };
};

export const createApiError = (
  error: any,
  source: string,
  options: Partial<Omit<AppError, 'id' | 'timestamp' | 'resolved' | 'retryCount' | 'type' | 'title' | 'message' | 'source'>> = {}
): Omit<AppError, 'id' | 'timestamp' | 'resolved' | 'retryCount'> => {
  const isNetworkError = !error.response;
  const isServerError = error.response?.status >= 500;
  const isClientError = error.response?.status >= 400 && error.response?.status < 500;
  
  let type: AppError['type'] = 'error';
  let title = 'Error';
  let message = 'An unexpected error occurred';
  
  if (isNetworkError) {
    type = 'warning';
    title = 'Connection Error';
    message = 'Unable to connect to the server. Please check your internet connection.';
  } else if (isServerError) {
    type = 'error';
    title = 'Server Error';
    message = 'The server encountered an error. Please try again later.';
  } else if (isClientError) {
    type = 'warning';
    title = 'Request Error';
    message = error.response?.data?.message || 'The request could not be completed.';
  }
  
  return createError(type, title, message, source, {
    ...options,
    details: error.response?.data?.detail || error.message,
    retryable: isNetworkError || isServerError,
  });
};

export const createValidationError = (
  field: string,
  message: string,
  source: string
): Omit<AppError, 'id' | 'timestamp' | 'resolved' | 'retryCount'> => {
  return createError('warning', 'Validation Error', `${field}: ${message}`, source, {
    retryable: false,
  });
};

export const createPermissionError = (
  action: string,
  resource: string,
  source: string
): Omit<AppError, 'id' | 'timestamp' | 'resolved' | 'retryCount'> => {
  return createError('warning', 'Permission Denied', `You don't have permission to ${action} ${resource}`, source, {
    retryable: false,
  });
};

// ============================================================================
// ERROR BOUNDARY - Componente para capturar errores de React
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode | ((error: Error, errorInfo: React.ErrorInfo) => ReactNode);
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ error, errorInfo });
    
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
    
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      if (typeof this.props.fallback === 'function') {
        return this.props.fallback(this.state.error!, this.state.errorInfo!);
      }
      
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      // Default fallback UI
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>An error occurred while rendering this component.</p>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details>
              <summary>Error Details</summary>
              <pre>{this.state.error.toString()}</pre>
              {this.state.errorInfo && (
                <pre>{this.state.errorInfo.componentStack}</pre>
              )}
            </details>
          )}
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
} 