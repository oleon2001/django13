// Core utilities migrated from Django backend
// Based on skyguard/apps/core/utils.py

import { Point } from '../interfaces';

/**
 * Generate device token for authentication
 */
export function generateDeviceToken(imei: number, secret?: string): string {
  const payload = {
    imei,
    timestamp: Date.now(),
    nonce: Math.random().toString(36).substring(2)
  };
  
  const token = btoa(JSON.stringify(payload));
  return secret ? `${token}.${secret}` : token;
}

/**
 * Verify device token
 */
export function verifyDeviceToken(token: string, imei: number, secret?: string): boolean {
  try {
    const parts = token.split('.');
    const payload = JSON.parse(atob(parts[0]));
    
    // Check if token is expired (24 hours)
    const now = Date.now();
    const tokenAge = now - payload.timestamp;
    if (tokenAge > 24 * 60 * 60 * 1000) {
      return false;
    }
    
    // Check IMEI
    if (payload.imei !== imei) {
      return false;
    }
    
    // Check secret if provided
    if (secret && parts[1] !== secret) {
      return false;
    }
    
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Calculate distance between two points using Haversine formula
 */
export function calculateDistance(point1: Point, point2: Point): number {
  const R = 6371; // Earth's radius in kilometers
  const dLat = toRadians(point2.y - point1.y);
  const dLon = toRadians(point2.x - point1.x);
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(point1.y)) * Math.cos(toRadians(point2.y)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Convert degrees to radians
 */
function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}

/**
 * Validate coordinates
 */
export function validateCoordinates(latitude: number, longitude: number): boolean {
  return latitude >= -90 && latitude <= 90 && 
         longitude >= -180 && longitude <= 180;
}

/**
 * Format coordinates with specified precision
 */
export function formatCoordinates(latitude: number, longitude: number, precision: number = 6): string {
  if (!validateCoordinates(latitude, longitude)) {
    throw new Error('Invalid coordinates');
  }
  
  const latStr = latitude.toFixed(precision);
  const lonStr = longitude.toFixed(precision);
  
  return `${latStr}, ${lonStr}`;
}

/**
 * Parse coordinates from string
 */
export function parseCoordinates(coordString: string): Point | null {
  try {
    const coords = coordString.split(',').map(s => parseFloat(s.trim()));
    if (coords.length !== 2 || coords.some(isNaN)) {
      return null;
    }
    
    const [latitude, longitude] = coords;
    if (!validateCoordinates(latitude, longitude)) {
      return null;
    }
    
    return { x: longitude, y: latitude };
  } catch (error) {
    return null;
  }
}

/**
 * Cache device data in localStorage
 */
export function cacheDeviceData(imei: number, data: Record<string, any>, timeout: number = 300): void {
  const cacheKey = `device_${imei}`;
  const cacheData = {
    data,
    timestamp: Date.now(),
    timeout: timeout * 1000
  };
  
  localStorage.setItem(cacheKey, JSON.stringify(cacheData));
}

/**
 * Get cached device data
 */
export function getCachedDeviceData(imei: number): Record<string, any> | null {
  const cacheKey = `device_${imei}`;
  const cached = localStorage.getItem(cacheKey);
  
  if (!cached) return null;
  
  try {
    const cacheData = JSON.parse(cached);
    const now = Date.now();
    
    if (now - cacheData.timestamp > cacheData.timeout) {
      localStorage.removeItem(cacheKey);
      return null;
    }
    
    return cacheData.data;
  } catch (error) {
    localStorage.removeItem(cacheKey);
    return null;
  }
}

/**
 * Clear device cache
 */
export function clearDeviceCache(imei: number): void {
  const cacheKey = `device_${imei}`;
  localStorage.removeItem(cacheKey);
}

/**
 * Format speed in km/h
 */
export function formatSpeed(speedKmh: number): string {
  if (speedKmh < 1) {
    return `${(speedKmh * 1000).toFixed(0)} m/h`;
  }
  return `${speedKmh.toFixed(1)} km/h`;
}

/**
 * Format duration in seconds to human readable format
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
 * Calculate bearing between two points
 */
export function calculateBearing(point1: Point, point2: Point): number {
  const dLon = toRadians(point2.x - point1.x);
  const lat1 = toRadians(point1.y);
  const lat2 = toRadians(point2.y);
  
  const y = Math.sin(dLon) * Math.cos(lat2);
  const x = Math.cos(lat1) * Math.sin(lat2) - 
            Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
  
  let bearing = Math.atan2(y, x);
  bearing = toDegrees(bearing);
  bearing = (bearing + 360) % 360;
  
  return bearing;
}

/**
 * Convert radians to degrees
 */
function toDegrees(radians: number): number {
  return radians * (180 / Math.PI);
}

/**
 * Check if point is inside polygon
 */
export function isPointInPolygon(point: Point, polygon: Point[]): boolean {
  if (polygon.length < 3) return false;
  
  let inside = false;
  const x = point.x;
  const y = point.y;
  
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].x;
    const yi = polygon[i].y;
    const xj = polygon[j].x;
    const yj = polygon[j].y;
    
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }
  
  return inside;
}

/**
 * Generate device report data
 */
export function generateDeviceReport(
  deviceData: Record<string, any>,
  locations: Record<string, any>[],
  events: Record<string, any>[]
): Record<string, any> {
  const totalDistance = locations.reduce((total, loc, index) => {
    if (index === 0) return 0;
    const prev = locations[index - 1];
    return total + calculateDistance(
      { x: prev.longitude, y: prev.latitude },
      { x: loc.longitude, y: loc.latitude }
    );
  }, 0);
  
  const avgSpeed = locations.length > 0 
    ? locations.reduce((sum, loc) => sum + (loc.speed || 0), 0) / locations.length
    : 0;
  
  const maxSpeed = locations.length > 0
    ? Math.max(...locations.map(loc => loc.speed || 0))
    : 0;
  
  const alarmEvents = events.filter(event => event.type === 'ALARM');
  const criticalEvents = events.filter(event => event.priority === 'CRITICAL');
  
  return {
    device: deviceData,
    summary: {
      totalLocations: locations.length,
      totalEvents: events.length,
      totalDistance: totalDistance.toFixed(2),
      averageSpeed: formatSpeed(avgSpeed),
      maxSpeed: formatSpeed(maxSpeed),
      alarmCount: alarmEvents.length,
      criticalCount: criticalEvents.length,
      uptimePercentage: calculateUptimePercentage(events)
    },
    locations: locations.slice(-100), // Last 100 locations
    events: events.slice(-50), // Last 50 events
    generatedAt: new Date().toISOString()
  };
}

/**
 * Calculate uptime percentage based on events
 */
function calculateUptimePercentage(events: Record<string, any>[]): number {
  if (events.length === 0) return 0;
  
  const onlineEvents = events.filter(event => 
    event.type === 'GPS_OK' || event.type === 'CURRENT_FIX'
  );
  
  const offlineEvents = events.filter(event => 
    event.type === 'GPS_LOST' || event.type === 'DISCONNECT'
  );
  
  const totalEvents = onlineEvents.length + offlineEvents.length;
  if (totalEvents === 0) return 100;
  
  return Math.round((onlineEvents.length / totalEvents) * 100);
}

/**
 * Sanitize device name
 */
export function sanitizeDeviceName(name: string): string {
  return name
    .replace(/[<>:"/\\|?*]/g, '') // Remove invalid characters
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim()
    .substring(0, 50); // Limit length
}

/**
 * Validate IMEI format
 */
export function validateIMEI(imei: string): boolean {
  // IMEI should be 15 digits
  if (!/^\d{15}$/.test(imei)) {
    return false;
  }
  
  // Luhn algorithm check
  let sum = 0;
  const digits = imei.split('').map(Number);
  
  for (let i = 0; i < 14; i++) {
    let digit = digits[i];
    if (i % 2 === 1) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    sum += digit;
  }
  
  const checkDigit = (10 - (sum % 10)) % 10;
  return checkDigit === digits[14];
}

/**
 * Format IMEI with proper spacing
 */
export function formatIMEI(imei: number): string {
  const imeiStr = imei.toString();
  if (imeiStr.length !== 15) {
    return imeiStr;
  }
  
  return `${imeiStr.slice(0, 2)} ${imeiStr.slice(2, 8)} ${imeiStr.slice(8, 15)}`;
}

/**
 * Generate unique ID
 */
export function generateUniqueId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substring(2);
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Throttle function
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
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Deep clone object
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T;
  }
  
  if (Array.isArray(obj)) {
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
 * Check if object is empty
 */
export function isEmpty(obj: any): boolean {
  if (obj == null) return true;
  if (Array.isArray(obj) || typeof obj === 'string') return obj.length === 0;
  if (obj instanceof Map || obj instanceof Set) return obj.size === 0;
  if (typeof obj === 'object') return Object.keys(obj).length === 0;
  return false;
}

/**
 * Sleep utility
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry function with exponential backoff
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxAttempts: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxAttempts) {
        throw lastError;
      }
      
      const delay = baseDelay * Math.pow(2, attempt - 1);
      await sleep(delay);
    }
  }
  
  throw lastError!;
} 