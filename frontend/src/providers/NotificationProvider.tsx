import React from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// ============================================================================
// NOTIFICATION PROVIDER - Provider para notificaciones
// ============================================================================

interface NotificationProviderProps {
  children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  return (
    <>
      {children}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
        limit={5}
      />
    </>
  );
};

// ============================================================================
// NOTIFICATION UTILITIES - Utilidades para notificaciones
// ============================================================================

/**
 * Función para mostrar notificación de éxito
 */
export const showSuccess = (message: string, options?: any) => {
  return toast.success(message, {
    position: "top-right",
    autoClose: 5000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    ...options,
  });
};

/**
 * Función para mostrar notificación de error
 */
export const showError = (message: string, options?: any) => {
  return toast.error(message, {
    position: "top-right",
    autoClose: 7000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    ...options,
  });
};

/**
 * Función para mostrar notificación de advertencia
 */
export const showWarning = (message: string, options?: any) => {
  return toast.warning(message, {
    position: "top-right",
    autoClose: 6000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    ...options,
  });
};

/**
 * Función para mostrar notificación de información
 */
export const showInfo = (message: string, options?: any) => {
  return toast.info(message, {
    position: "top-right",
    autoClose: 4000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    ...options,
  });
};

/**
 * Función para mostrar notificación de carga
 */
export const showLoading = (message: string, options?: any) => {
  return toast.loading(message, {
    position: "top-right",
    autoClose: false,
    hideProgressBar: true,
    closeOnClick: false,
    pauseOnHover: true,
    draggable: false,
    ...options,
  });
};

/**
 * Función para actualizar una notificación
 */
export const updateNotification = (toastId: string | number, message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
  toast.update(toastId, {
    render: message,
    type: type,
    isLoading: false,
    autoClose: 5000,
  });
};

/**
 * Función para cerrar una notificación
 */
export const closeNotification = (toastId: string | number) => {
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
  const toastId = toast.info(
    <div>
      <p>{message}</p>
      <div style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
        <button
          onClick={() => {
            onConfirm();
            toast.dismiss(toastId);
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
            toast.dismiss(toastId);
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
    </div>,
    {
      position: "top-center",
      autoClose: false,
      hideProgressBar: true,
      closeOnClick: false,
      pauseOnHover: true,
      draggable: false,
    }
  );
};

/**
 * Función para mostrar notificación de progreso
 */
export const showProgress = (message: string, progress: number) => {
  return toast.info(
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
              transition: 'width 0.3s ease',
            }}
          />
        </div>
        <span style={{ fontSize: '12px', color: '#666' }}>{progress}%</span>
      </div>
    </div>,
    {
      position: "top-right",
      autoClose: false,
      hideProgressBar: true,
      closeOnClick: false,
      pauseOnHover: true,
      draggable: false,
    }
  );
}; 