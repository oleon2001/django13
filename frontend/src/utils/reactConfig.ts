// Configuración para React 18 - Optimizaciones para prevenir errores de suspensión

// Configuración para timeouts y delays
export const REACT_CONFIG = {
  // Delays para prevenir suspensión sincrónica
  TRANSITION_DELAY: 50,
  POLLING_INITIAL_DELAY: 200,
  ERROR_RETRY_DELAY: 1000,
  
  // Configuración de polling
  POLLING_INTERVAL: 10000, // 10 segundos
  POLLING_MAX_BACKOFF: 30000, // 30 segundos máximo
  
  // Configuración de Suspense
  SUSPENSE_TIMEOUT: 5000,
  LAZY_LOAD_DELAY: 100,
  
  // Configuración de navegación
  NAVIGATION_DELAY: 100,
  
  // Configuración de API
  API_TIMEOUT: 30000,
  API_RETRY_ATTEMPTS: 3,
} as const;

// Utilidad para crear delays no bloqueantes
export const createSafeDelay = (ms: number): Promise<void> => {
  return new Promise(resolve => {
    setTimeout(resolve, ms);
  });
};

// Utilidad para ejecutar callbacks con delay seguro
export const executeSafely = async <T>(
  callback: () => T | Promise<T>,
  delay: number = REACT_CONFIG.TRANSITION_DELAY
): Promise<T> => {
  await createSafeDelay(delay);
  return callback();
};

// Debounce function para evitar actualizaciones excesivas
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// Throttle function para limitar la frecuencia de ejecución
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Configuración de errores
export const ERROR_MESSAGES = {
  SUSPENSE_ERROR: 'Error de suspensión detectado. La aplicación se está recuperando...',
  NETWORK_ERROR: 'Error de conexión. Reintentando...',
  AUTH_ERROR: 'Error de autenticación. Redirigiendo al login...',
  GENERIC_ERROR: 'Ha ocurrido un error inesperado.',
} as const; 