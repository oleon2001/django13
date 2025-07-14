/**
 * Core utilities for the GPS tracking system.
 * Migrated from backend Django utilities to TypeScript.
 */

/**
 * Validate GPS coordinates.
 */
export function validateCoordinates(latitude: number, longitude: number): boolean {
  return (
    latitude >= -90 && latitude <= 90 &&
    longitude >= -180 && longitude <= 180
  );
}

/**
 * Calculate distance between two points using Haversine formula.
 */
export function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth's radius in kilometers
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Format speed for display.
 */
export function formatSpeed(speedKmh: number): string {
  if (speedKmh < 1) {
    return `${(speedKmh * 1000).toFixed(0)} m/h`;
  }
  return `${speedKmh.toFixed(1)} km/h`;
}

/**
 * Format duration in seconds to human readable format.
 */
export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}

/**
 * Generate a unique ID.
 */
export function generateUniqueId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Format coordinates for display.
 */
export function formatCoordinates(latitude: number, longitude: number, precision: number = 6): string {
  return `${latitude.toFixed(precision)}, ${longitude.toFixed(precision)}`;
}

/**
 * Parse coordinates from string.
 */
export function parseCoordinates(coordString: string): { latitude: number; longitude: number } | null {
  const match = coordString.match(/^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$/);
  if (!match) {
    return null;
  }

  const latitude = parseFloat(match[1]);
  const longitude = parseFloat(match[2]);

  if (!validateCoordinates(latitude, longitude)) {
    return null;
  }

  return { latitude, longitude };
}

/**
 * Calculate bearing between two points.
 */
export function calculateBearing(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const lat1Rad = lat1 * Math.PI / 180;
  const lat2Rad = lat2 * Math.PI / 180;

  const y = Math.sin(dLon) * Math.cos(lat2Rad);
  const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) - 
            Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLon);

  let bearing = Math.atan2(y, x) * 180 / Math.PI;
  bearing = (bearing + 360) % 360;

  return bearing;
}

/**
 * Check if a point is inside a polygon.
 */
export function isPointInPolygon(point: { latitude: number; longitude: number }, polygon: Array<{ latitude: number; longitude: number }>): boolean {
  let inside = false;
  const { latitude, longitude } = point;

  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].longitude;
    const yi = polygon[i].latitude;
    const xj = polygon[j].longitude;
    const yj = polygon[j].latitude;

    if (((yi > latitude) !== (yj > latitude)) && (longitude < (xj - xi) * (latitude - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }

  return inside;
}

/**
 * Sanitize device name.
 */
export function sanitizeDeviceName(name: string): string {
  return name.replace(/[^a-zA-Z0-9\s\-_]/g, '').trim();
}

/**
 * Validate IMEI format.
 */
export function validateIMEI(imei: string): boolean {
  // Basic IMEI validation (15 digits)
  if (!/^\d{15}$/.test(imei)) {
    return false;
  }

  // Luhn algorithm check
  let sum = 0;
  const length = imei.length;
  for (let i = length - 1; i >= 0; i--) {
    let d = parseInt(imei.charAt(i));
    if (i % 2 === 0) {
      d *= 2;
      if (d > 9) {
        d -= 9;
      }
    }
    sum += d;
  }

  return sum % 10 === 0;
}

/**
 * Format IMEI for display.
 */
export function formatIMEI(imei: string): string {
  return imei.replace(/(\d{4})(?=\d)/g, '$1-');
}

/**
 * Debounce function.
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Throttle function.
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Deep clone an object.
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T;
  }

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }

  if (typeof obj === 'object') {
    const cloned = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }

  return obj;
}

/**
 * Generate a random string.
 */
export function generateRandomString(length: number = 8): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Convert bytes to human readable format.
 */
export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Sleep function for async operations.
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
} 