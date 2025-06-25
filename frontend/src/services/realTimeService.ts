import { Device } from '../types';
import { deviceService } from './deviceService';
import { REACT_CONFIG } from '../utils/reactConfig';

type Subscriber = {
  id: string;
  callback: (devices: Device[]) => void;
  lastUpdate?: Date;
};

class RealTimeService {
  private subscribers: Map<string, Subscriber> = new Map();
  private currentDevices: Device[] = [];
  private pollingTimeout: NodeJS.Timeout | null = null;
  private isPolling: boolean = false;
  private errorCount: number = 0;
  private maxErrors: number = 3;

  // Singleton pattern
  private static instance: RealTimeService;
  public static getInstance(): RealTimeService {
    if (!RealTimeService.instance) {
      RealTimeService.instance = new RealTimeService();
    }
    return RealTimeService.instance;
  }

  private constructor() {
    // Private constructor for singleton
  }

  // Subscribe to real-time updates
  subscribe(id: string, callback: (devices: Device[]) => void): () => void {
    console.log(`📡 RealTimeService: Subscribing ${id}`);
    
    this.subscribers.set(id, {
      id,
      callback,
      lastUpdate: new Date()
    });

    // Send current data immediately if available
    if (this.currentDevices.length > 0) {
      setTimeout(() => callback(this.currentDevices), 100);
    }

    // Start polling if this is the first subscriber
    if (this.subscribers.size === 1 && !this.isPolling) {
      this.startPolling();
    }

    // Return unsubscribe function
    return () => this.unsubscribe(id);
  }

  // Unsubscribe from real-time updates
  unsubscribe(id: string): void {
    console.log(`🔌 RealTimeService: Unsubscribing ${id}`);
    this.subscribers.delete(id);

    // Stop polling if no subscribers
    if (this.subscribers.size === 0) {
      this.stopPolling();
    }
  }

  // Start the centralized polling
  private startPolling(): void {
    if (this.isPolling) return;

    console.log('🚀 RealTimeService: Starting centralized polling');
    this.isPolling = true;
    this.errorCount = 0;
    this.poll();
  }

  // Stop the centralized polling
  private stopPolling(): void {
    console.log('⏹️ RealTimeService: Stopping centralized polling');
    
    if (this.pollingTimeout) {
      clearTimeout(this.pollingTimeout);
      this.pollingTimeout = null;
    }
    
    this.isPolling = false;
    this.errorCount = 0;
  }

  // Main polling function
  private async poll(): Promise<void> {
    if (!this.isPolling) return;

    try {
      console.log('🔄 RealTimeService: Fetching device data...');
      const devices = await deviceService.getAll();
      
      // Update current devices
      this.currentDevices = devices;
      this.errorCount = 0; // Reset error count on success

      // Notify all subscribers with a small delay to prevent suspense
      this.notifySubscribers(devices);

      // Schedule next poll
      this.scheduleNextPoll(REACT_CONFIG.POLLING_INTERVAL);

    } catch (error) {
      console.error('❌ RealTimeService: Polling error:', error);
      this.errorCount++;

      // Use exponential backoff on errors
      const backoffDelay = Math.min(
        REACT_CONFIG.ERROR_RETRY_DELAY * Math.pow(2, this.errorCount),
        REACT_CONFIG.POLLING_MAX_BACKOFF
      );

      // Stop polling if too many errors
      if (this.errorCount >= this.maxErrors) {
        console.error('🚫 RealTimeService: Too many errors, stopping polling');
        this.stopPolling();
        return;
      }

      this.scheduleNextPoll(backoffDelay);
    }
  }

  // Schedule next polling iteration
  private scheduleNextPoll(delay: number): void {
    if (!this.isPolling) return;

    this.pollingTimeout = setTimeout(() => {
      if (this.isPolling) {
        this.poll();
      }
    }, delay);
  }

  // Notify all subscribers
  private notifySubscribers(devices: Device[]): void {
    const subscriberCount = this.subscribers.size;
    console.log(`📢 RealTimeService: Notifying ${subscriberCount} subscribers`);

    this.subscribers.forEach((subscriber, id) => {
      try {
        // Use setTimeout to prevent synchronous updates that cause suspense
        setTimeout(() => {
          subscriber.callback(devices);
          subscriber.lastUpdate = new Date();
        }, REACT_CONFIG.TRANSITION_DELAY);
      } catch (error) {
        console.error(`❌ RealTimeService: Error notifying subscriber ${id}:`, error);
      }
    });
  }

  // Get current device data
  getCurrentDevices(): Device[] {
    return [...this.currentDevices];
  }

  // Force refresh
  async forceRefresh(): Promise<void> {
    if (!this.isPolling) {
      this.startPolling();
      return;
    }

    // Cancel current timeout and poll immediately
    if (this.pollingTimeout) {
      clearTimeout(this.pollingTimeout);
      this.pollingTimeout = null;
    }

    await this.poll();
  }

  // Get subscriber info for debugging
  getDebugInfo() {
    return {
      subscriberCount: this.subscribers.size,
      subscribers: Array.from(this.subscribers.keys()),
      isPolling: this.isPolling,
      errorCount: this.errorCount,
      deviceCount: this.currentDevices.length,
      lastDeviceUpdate: this.currentDevices.length > 0 ? 
        Math.max(...this.currentDevices.map(d => 
          d.updated_at ? new Date(d.updated_at).getTime() : 0
        )) : null
    };
  }
}

// Export singleton instance
export const realTimeService = RealTimeService.getInstance();
export default realTimeService; 