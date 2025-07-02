import React from 'react';
import { Toaster, toast } from 'react-hot-toast';

// ============================================================================
// NOTIFICATION TYPES - Tipos para notificaciones
// ============================================================================

export interface NotificationOptions {
  duration?: number;
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
  style?: React.CSSProperties;
  icon?: string | React.ReactElement;
  id?: string;
}

export interface NotificationContextType {
  success: (message: string, options?: NotificationOptions) => string;
  error: (message: string, options?: NotificationOptions) => string;
  warning: (message: string, options?: NotificationOptions) => string;
  info: (message: string, options?: NotificationOptions) => string;
  dismiss: (toastId?: string) => void;
  dismissAll: () => void;
}

// ============================================================================
// NOTIFICATION CONTEXT - Contexto para notificaciones
// ============================================================================

const NotificationContext = React.createContext<NotificationContextType | undefined>(undefined);

// ============================================================================
// NOTIFICATION PROVIDER - Proveedor de notificaciones
// ============================================================================

interface NotificationProviderProps {
  children: React.ReactNode;
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
  duration?: number;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({
  children,
  position = 'top-right',
  duration = 4000,
}) => {
  const success = (message: string, options?: NotificationOptions): string => {
    return toast.success(message, {
      duration: options?.duration || duration,
      position: options?.position || position,
      style: options?.style,
      icon: options?.icon,
      id: options?.id,
    });
  };

  const error = (message: string, options?: NotificationOptions): string => {
    return toast.error(message, {
      duration: options?.duration || duration,
      position: options?.position || position,
      style: options?.style,
      icon: options?.icon,
      id: options?.id,
    });
  };

  const warning = (message: string, options?: NotificationOptions): string => {
    return toast(message, {
      duration: options?.duration || duration,
      position: options?.position || position,
      style: {
        ...options?.style,
        background: '#fbbf24',
        color: '#1f2937',
      },
      icon: options?.icon || '⚠️',
      id: options?.id,
    });
  };

  const info = (message: string, options?: NotificationOptions): string => {
    return toast(message, {
      duration: options?.duration || duration,
      position: options?.position || position,
      style: {
        ...options?.style,
        background: '#3b82f6',
        color: '#ffffff',
      },
      icon: options?.icon || 'ℹ️',
      id: options?.id,
    });
  };

  const dismiss = (toastId?: string): void => {
    if (toastId) {
      toast.dismiss(toastId);
    } else {
      toast.dismiss();
    }
  };

  const dismissAll = (): void => {
    toast.dismiss();
  };

  const value: NotificationContextType = {
    success,
    error,
    warning,
    info,
    dismiss,
    dismissAll,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <Toaster
        position={position}
        toastOptions={{
          duration: duration,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: duration,
            style: {
              background: '#10b981',
              color: '#ffffff',
            },
          },
          error: {
            duration: duration,
            style: {
              background: '#ef4444',
              color: '#ffffff',
            },
          },
        }}
      />
    </NotificationContext.Provider>
  );
};

// ============================================================================
// NOTIFICATION HOOK - Hook para usar notificaciones
// ============================================================================

export const useNotification = (): NotificationContextType => {
  const context = React.useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

// ============================================================================
// NOTIFICATION UTILITIES - Utilidades para notificaciones
// ============================================================================

/**
 * Función para mostrar notificación de éxito
 */
export const showSuccess = (message: string, options?: any) => {
  return toast.success(message, {
    duration: 5000,
    ...options,
  });
};

/**
 * Función para mostrar notificación de error
 */
export const showError = (message: string, options?: any) => {
  return toast.error(message, {
    duration: 7000,
    ...options,
  });
};

/**
 * Función para mostrar notificación de advertencia
 */
export const showWarning = (message: string, options?: any) => {
  return toast(message, {
    duration: 6000,
    icon: '⚠️',
    style: {
      background: '#ff9800',
    },
    ...options,
  });
};

/**
 * Función para mostrar notificación de información
 */
export const showInfo = (message: string, options?: any) => {
  return toast(message, {
    duration: 4000,
    icon: 'ℹ️',
    style: {
      background: '#2196f3',
    },
    ...options,
  });
};

/**
 * Función para mostrar notificación de carga
 */
export const showLoading = (message: string, options?: any) => {
  return toast.loading(message, {
    duration: Infinity,
    ...options,
  });
};

/**
 * Función para actualizar una notificación
 */
export const updateNotification = (toastId: string, message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
  toast.dismiss(toastId);
  
  switch (type) {
    case 'success':
      return toast.success(message, { duration: 5000 });
    case 'error':
      return toast.error(message, { duration: 5000 });
    case 'warning':
      return toast(message, { 
        duration: 5000,
        icon: '⚠️',
        style: { background: '#ff9800' }
      });
    default:
      return toast(message, { 
        duration: 5000,
        icon: 'ℹ️',
        style: { background: '#2196f3' }
      });
  }
};

/**
 * Función para cerrar una notificación
 */
export const closeNotification = (toastId: string) => {
  toast.dismiss(toastId);
};

/**
 * Función para cerrar todas las notificaciones
 */
export const closeAllNotifications = () => {
  toast.dismiss();
};

/**
 * Función para mostrar notificación de confirmación
 */
export const showConfirm = (message: string, onConfirm: () => void, onCancel?: () => void) => {
  const toastId = toast(
    (t) => (
      <div>
        <p>{message}</p>
        <div style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
          <button
            onClick={() => {
              onConfirm();
              toast.dismiss(t.id);
            }}
            style={{
              padding: '5px 10px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '3px',
              cursor: 'pointer',
            }}
          >
            Confirmar
          </button>
          <button
            onClick={() => {
              onCancel?.();
              toast.dismiss(t.id);
            }}
            style={{
              padding: '5px 10px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '3px',
              cursor: 'pointer',
            }}
          >
            Cancelar
          </button>
        </div>
      </div>
    ),
    {
      duration: Infinity,
      style: {
        background: '#363636',
        color: '#fff',
      },
    }
  );
  
  return toastId;
};

/**
 * Función para mostrar notificación de progreso
 */
export const showProgress = (message: string, progress: number) => {
  return toast(
    <div>
      <p>{message}</p>
      <div style={{ marginTop: '10px' }}>
        <div style={{ width: '100%', backgroundColor: '#f0f0f0', borderRadius: '3px' }}>
          <div 
            style={{ 
              width: `${progress}%`, 
              height: '20px', 
              backgroundColor: '#007bff', 
              borderRadius: '3px',
              transition: 'width 0.3s ease'
            }} 
          />
        </div>
        <span style={{ fontSize: '12px', color: '#666' }}>{progress}%</span>
      </div>
    </div>,
    {
      duration: Infinity,
      style: {
        background: '#363636',
        color: '#fff',
      },
    }
  );
}; 