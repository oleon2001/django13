import { useState, useEffect, useRef, startTransition } from 'react';
import { Device } from '../types';
import { realTimeService } from '../services/realTimeService';

interface UseRealTimeDevicesOptions {
  enabled?: boolean;
  componentId?: string;
  onError?: (error: Error) => void;
}

interface UseRealTimeDevicesReturn {
  devices: Device[];
  loading: boolean;
  error: string | null;
  lastUpdate: Date | null;
  forceRefresh: () => Promise<void>;
  debugInfo: any;
}

export const useRealTimeDevices = (
  options: UseRealTimeDevicesOptions = {}
): UseRealTimeDevicesReturn => {
  const {
    enabled = true,
    componentId = 'unknown-component',
    onError
  } = options;

  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const unsubscribeRef = useRef<(() => void) | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (!enabled) {
      // Cleanup if disabled
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }
      return;
    }

    console.log(`🔗 useRealTimeDevices: Connecting ${componentId}`);

    // Subscribe to real-time updates
    const unsubscribe = realTimeService.subscribe(
      componentId,
      (updatedDevices: Device[]) => {
        if (!mountedRef.current) return;

        // Use startTransition to prevent suspense errors
        startTransition(() => {
          setDevices(updatedDevices);
          setLastUpdate(new Date());
          setError(null);
          setLoading(false);
        });
      }
    );

    unsubscribeRef.current = unsubscribe;

    // Get current devices immediately if available
    const currentDevices = realTimeService.getCurrentDevices();
    if (currentDevices.length > 0) {
      startTransition(() => {
        setDevices(currentDevices);
        setLoading(false);
      });
    }

    // Cleanup function
    return () => {
      console.log(`🔌 useRealTimeDevices: Disconnecting ${componentId}`);
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }
    };
  }, [enabled, componentId]);

  // Force refresh function
  const forceRefresh = async (): Promise<void> => {
    try {
      startTransition(() => {
        setError(null);
      });
      
      await realTimeService.forceRefresh();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      
      startTransition(() => {
        setError(errorMessage);
      });
      
      if (onError) {
        onError(err instanceof Error ? err : new Error(errorMessage));
      }
    }
  };

  // Get debug info
  const debugInfo = realTimeService.getDebugInfo();

  return {
    devices,
    loading,
    error,
    lastUpdate,
    forceRefresh,
    debugInfo
  };
}; 