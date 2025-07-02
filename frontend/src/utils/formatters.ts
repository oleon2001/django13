// Formateo de fechas
export const formatDate = (date: string | Date, options?: Intl.DateTimeFormatOptions): string => {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) return '';
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options,
  };
  
  return new Intl.DateTimeFormat('es-ES', defaultOptions).format(dateObj);
};

export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatTime = (date: string | Date): string => {
  return formatDate(date, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

export const formatRelativeTime = (date: string | Date): string => {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'Hace un momento';
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `Hace ${diffInMinutes} minuto${diffInMinutes > 1 ? 's' : ''}`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `Hace ${diffInHours} hora${diffInHours > 1 ? 's' : ''}`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `Hace ${diffInDays} día${diffInDays > 1 ? 's' : ''}`;
  }
  
  return formatDate(date);
};

// Formateo de números
export const formatNumber = (num: number, options?: Intl.NumberFormatOptions): string => {
  if (num === null || num === undefined || isNaN(num)) return '';
  
  const defaultOptions: Intl.NumberFormatOptions = {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
    ...options,
  };
  
  return new Intl.NumberFormat('es-ES', defaultOptions).format(num);
};

export const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency,
  }).format(amount);
};

export const formatPercentage = (value: number, decimals = 1): string => {
  return `${formatNumber(value, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}%`;
};

// Formateo de distancias
export const formatDistance = (meters: number): string => {
  if (meters < 1000) {
    return `${Math.round(meters)}m`;
  }
  
  const kilometers = meters / 1000;
  return `${formatNumber(kilometers, { minimumFractionDigits: 1, maximumFractionDigits: 2 })}km`;
};

export const formatSpeed = (metersPerSecond: number): string => {
  const kmPerHour = metersPerSecond * 3.6;
  return `${formatNumber(kmPerHour, { minimumFractionDigits: 0, maximumFractionDigits: 1 })} km/h`;
};

// Formateo de coordenadas
export const formatCoordinates = (lat: number, lng: number, precision = 6): string => {
  const latStr = lat.toFixed(precision);
  const lngStr = lng.toFixed(precision);
  const latDir = lat >= 0 ? 'N' : 'S';
  const lngDir = lng >= 0 ? 'E' : 'W';
  
  return `${latStr}°${latDir}, ${lngStr}°${lngDir}`;
};

// Formateo de teléfonos
export const formatPhone = (phone: string): string => {
  if (!phone) return '';
  
  // Remover todos los caracteres no numéricos
  const cleaned = phone.replace(/\D/g, '');
  
  // Formatear según la longitud
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  
  if (cleaned.length === 11) {
    return `+${cleaned.slice(0, 1)} (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  
  return phone;
};

// Formateo de IMEI
export const formatIMEI = (imei: string): string => {
  if (!imei) return '';
  
  const cleaned = imei.replace(/\D/g, '');
  
  if (cleaned.length === 15) {
    return `${cleaned.slice(0, 4)} ${cleaned.slice(4, 8)} ${cleaned.slice(8, 12)} ${cleaned.slice(12)}`;
  }
  
  return imei;
};

// Formateo de placas de vehículos
export const formatLicensePlate = (plate: string): string => {
  if (!plate) return '';
  
  return plate.toUpperCase().replace(/\s/g, '');
};

// Formateo de nombres
export const formatName = (firstName: string, lastName: string): string => {
  if (!firstName && !lastName) return '';
  
  const formatPart = (part: string) => {
    if (!part) return '';
    return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
  };
  
  return `${formatPart(firstName)} ${formatPart(lastName)}`.trim();
};

export const formatFullName = (firstName: string, lastName: string, middleName?: string): string => {
  const parts = [firstName, middleName, lastName].filter(Boolean);
  return parts.map(part => part!.charAt(0).toUpperCase() + part!.slice(1).toLowerCase()).join(' ');
};

// Formateo de estados
export const formatStatus = (status: string): string => {
  if (!status) return '';
  
  const statusMap: Record<string, string> = {
    active: 'Activo',
    inactive: 'Inactivo',
    online: 'En línea',
    offline: 'Desconectado',
    moving: 'En movimiento',
    stopped: 'Detenido',
    idle: 'Inactivo',
    busy: 'Ocupado',
    available: 'Disponible',
    unavailable: 'No disponible',
    pending: 'Pendiente',
    completed: 'Completado',
    cancelled: 'Cancelado',
    error: 'Error',
    warning: 'Advertencia',
    info: 'Información',
    success: 'Éxito',
  };
  
  return statusMap[status.toLowerCase()] || status;
};

// Formateo de tipos de eventos
export const formatEventType = (eventType: string): string => {
  if (!eventType) return '';
  
  const eventMap: Record<string, string> = {
    ignition_on: 'Encendido',
    ignition_off: 'Apagado',
    geofence_enter: 'Entrada a geocerca',
    geofence_exit: 'Salida de geocerca',
    speed_limit_exceeded: 'Exceso de velocidad',
    low_battery: 'Batería baja',
    maintenance_due: 'Mantenimiento requerido',
    emergency: 'Emergencia',
    location_update: 'Actualización de ubicación',
    status_change: 'Cambio de estado',
  };
  
  return eventMap[eventType.toLowerCase()] || eventType;
};

// Formateo de duración
export const formatDuration = (seconds: number): string => {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (minutes < 60) {
    return `${minutes}m ${remainingSeconds}s`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (hours < 24) {
    return `${hours}h ${remainingMinutes}m`;
  }
  
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;
  
  return `${days}d ${remainingHours}h`;
};

// Formateo de tamaños de archivo
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

// Formateo de texto
export const truncateText = (text: string, maxLength: number, suffix = '...'): string => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength - suffix.length) + suffix;
};

export const capitalizeFirst = (text: string): string => {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

export const capitalizeWords = (text: string): string => {
  if (!text) return '';
  return text.split(' ').map(word => capitalizeFirst(word)).join(' ');
};

// Formateo de URLs
export const formatUrl = (url: string): string => {
  if (!url) return '';
  
  // Remover protocolo si existe
  let formatted = url.replace(/^https?:\/\//, '');
  
  // Remover www si existe
  formatted = formatted.replace(/^www\./, '');
  
  // Limitar longitud
  if (formatted.length > 50) {
    formatted = formatted.substring(0, 47) + '...';
  }
  
  return formatted;
};

// Formateo de códigos de error
export const formatErrorCode = (code: string | number): string => {
  if (!code) return '';
  
  const codeStr = code.toString();
  
  // Si es un código HTTP
  if (/^\d{3}$/.test(codeStr)) {
    const httpCodes: Record<string, string> = {
      '400': 'Solicitud incorrecta',
      '401': 'No autorizado',
      '403': 'Prohibido',
      '404': 'No encontrado',
      '500': 'Error interno del servidor',
      '502': 'Puerta de enlace incorrecta',
      '503': 'Servicio no disponible',
    };
    
    return httpCodes[codeStr] || `Error ${codeStr}`;
  }
  
  return codeStr;
};

// Formateo de direcciones
export const formatAddress = (address: {
  street?: string;
  city?: string;
  state?: string;
  country?: string;
  postalCode?: string;
}): string => {
  const parts = [
    address.street,
    address.city,
    address.state,
    address.postalCode,
    address.country,
  ].filter(Boolean);
  
  return parts.join(', ');
};

// Formateo de rangos de fechas
export const formatDateRange = (startDate: string | Date, endDate: string | Date): string => {
  const start = formatDate(startDate);
  const end = formatDate(endDate);
  
  if (start === end) {
    return start;
  }
  
  return `${start} - ${end}`;
};

// Formateo de listas
export const formatList = (items: string[], conjunction = 'y'): string => {
  if (!items || items.length === 0) return '';
  if (items.length === 1) return items[0];
  if (items.length === 2) return `${items[0]} ${conjunction} ${items[1]}`;
  
  const last = items.pop();
  return `${items.join(', ')} ${conjunction} ${last}`;
}; 