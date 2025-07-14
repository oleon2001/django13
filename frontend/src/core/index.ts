// Core module index - exports all core functionality
// This module provides the foundation for the entire application

// Interfaces
export * from './interfaces';

// Exceptions
export * from './exceptions';

// Utilities
export * from './utils';

// Configuration
export * from './config';

// Factory
export * from './factory';

// Initialize core module
import { ServiceFactory } from './factory';
import { validateConfig } from './config';

/**
 * Initialize the core module
 */
export function initializeCore(): void {
  try {
    // Validate configuration
    if (!validateConfig()) {
      throw new Error('Core configuration validation failed');
    }

    // Initialize service factory
    ServiceFactory.initialize();

    console.log('Core module initialized successfully');
  } catch (error) {
    console.error('Failed to initialize core module:', error);
    throw error;
  }
}

/**
 * Check if core module is ready
 */
export function isCoreReady(): boolean {
  try {
    return ServiceFactory.getRegisteredServices().length > 0;
  } catch {
    return false;
  }
}

// Auto-initialize when module is imported
if (typeof window !== 'undefined') {
  // Only initialize in browser environment
  initializeCore();
} 