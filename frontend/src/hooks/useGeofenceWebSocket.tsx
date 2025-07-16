import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './useAuth';

interface GeofenceEvent {
  id: number;
  device_id: number;
  device_name: string;
  geofence_id: number;
  geofence_name: string;
  event_type: 'ENTRY' | 'EXIT';
  position: [number, number]; // [lat, lng]
  timestamp: string;
  created_at: string;
}

interface GeofenceNotification {
  title: string;
  message: string;
  data: GeofenceEvent;
  timestamp: string;
}

interface GeofenceAlert {
  alert_level: 'info' | 'warning';
  title: string;
  message: string;
  data: GeofenceEvent;
  timestamp: string;
  auto_close: boolean;
  sound: boolean;
}

interface UseGeofenceWebSocketReturn {
  isConnected: boolean;
  lastEvent: GeofenceEvent | null;
  lastNotification: GeofenceNotification | null;
  lastAlert: GeofenceAlert | null;
  events: GeofenceEvent[];
  clearEvents: () => void;
}

export const useGeofenceWebSocket = (): UseGeofenceWebSocketReturn => {
  const { user, isAuthenticated } = useAuth();
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<GeofenceEvent | null>(null);
  const [lastNotification, setLastNotification] = useState<GeofenceNotification | null>(null);
  const [lastAlert, setLastAlert] = useState<GeofenceAlert | null>(null);
  const [events, setEvents] = useState<GeofenceEvent[]>([]);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setLastEvent(null);
    setLastNotification(null);
    setLastAlert(null);
  }, []);

  const connect = useCallback(() => {
    if (!isAuthenticated || !user) {
      console.log('Not authenticated, skipping WebSocket connection');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('No access token found');
        return;
      }

      // Determine WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/ws/geofences/?token=${token}`;

      console.log('Connecting to geofence WebSocket:', wsUrl);

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('Geofence WebSocket connected');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received geofence WebSocket message:', data);

          switch (data.type) {
            case 'geofence_event':
              const geofenceEvent = data.data as GeofenceEvent;
              setLastEvent(geofenceEvent);
              setEvents(prev => [geofenceEvent, ...prev.slice(0, 49)]); // Keep last 50 events
              
              // Show browser notification if supported
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification(`Geocerca: ${geofenceEvent.geofence_name}`, {
                  body: `${geofenceEvent.device_name} ${geofenceEvent.event_type === 'ENTRY' ? 'entró en' : 'salió de'} la geocerca`,
                  icon: '/favicon.ico',
                });
              }
              break;

            case 'geofence_notification':
              const notification = data as GeofenceNotification;
              setLastNotification(notification);
              
              // Show browser notification
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification(notification.title, {
                  body: notification.message,
                  icon: '/favicon.ico',
                });
              }
              break;

            case 'geofence_alert':
              const alert = data as GeofenceAlert;
              setLastAlert(alert);
              
              // Play sound if configured
              if (alert.sound) {
                try {
                  const audio = new Audio('/static/sounds/alert.mp3');
                  audio.play().catch(console.error);
                } catch (error) {
                  console.error('Error playing alert sound:', error);
                }
              }

              // Show browser notification with urgency
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification(alert.title, {
                  body: alert.message,
                  icon: '/favicon.ico',
                  requireInteraction: !alert.auto_close,
                });
              }
              break;

            case 'geofence_created':
            case 'geofence_updated':
              // Trigger re-fetch of geofences if needed
              console.log('Geofence updated:', data.data);
              break;

            default:
              console.log('Unknown geofence message type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('Geofence WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = (event) => {
        console.log('Geofence WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        
        // Attempt to reconnect after 5 seconds if not a normal closure
        if (event.code !== 1000 && isAuthenticated) {
          setTimeout(() => {
            console.log('Attempting to reconnect geofence WebSocket...');
            connect();
          }, 5000);
        }
      };

    } catch (error) {
      console.error('Error connecting to geofence WebSocket:', error);
      setIsConnected(false);
    }
  }, [isAuthenticated, user]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      console.log('Disconnecting geofence WebSocket');
      wsRef.current.close(1000, 'Component unmounting');
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  // Connect when authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      // Request notification permission
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
          console.log('Notification permission:', permission);
        });
      }

      connect();
    } else {
      disconnect();
    }

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [isAuthenticated, user, connect, disconnect]);

  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        console.log('Page hidden, keeping WebSocket connection');
      } else {
        console.log('Page visible, checking WebSocket connection');
        if (!isConnected && isAuthenticated && user) {
          connect();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isConnected, isAuthenticated, user, connect]);

  return {
    isConnected,
    lastEvent,
    lastNotification,
    lastAlert,
    events,
    clearEvents,
  };
}; 