import React, { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';
import { useAuth } from './AuthProvider';
import { useConfig } from './ConfigProvider';

// ============================================================================
// WEBSOCKET TYPES - Tipos para websockets
// ============================================================================

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error' | 'reconnecting';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  id?: string;
}

export interface WebSocketEvent {
  type: 'message' | 'open' | 'close' | 'error' | 'reconnect';
  data?: any;
  timestamp: string;
}

export interface WebSocketContextType {
  status: WebSocketStatus;
  isConnected: boolean;
  isConnecting: boolean;
  isReconnecting: boolean;
  lastMessage: WebSocketMessage | null;
  messageHistory: WebSocketMessage[];
  connectionCount: number;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
  reconnectInterval: number;
  
  // Métodos de conexión
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;
  
  // Métodos de mensajes
  sendMessage: (type: string, data: any) => void;
  sendCommand: (command: string, params?: any) => void;
  
  // Métodos de suscripción
  subscribe: (channel: string, callback: (message: WebSocketMessage) => void) => () => void;
  unsubscribe: (channel: string) => void;
  
  // Métodos de utilidad
  clearMessageHistory: () => void;
  getMessageHistory: (type?: string, limit?: number) => WebSocketMessage[];
  getConnectionStats: () => {
    uptime: number;
    messagesSent: number;
    messagesReceived: number;
    errors: number;
  };
}

// ============================================================================
// WEBSOCKET CONTEXT - Contexto para websockets
// ============================================================================

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

// ============================================================================
// WEBSOCKET PROVIDER - Provider para websockets
// ============================================================================

interface WebSocketProviderProps {
  children: ReactNode;
  url?: string;
  autoConnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  maxMessageHistory?: number;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
  url,
  autoConnect = true,
  maxReconnectAttempts = 5,
  reconnectInterval = 5000,
  maxMessageHistory = 100,
}) => {
  const { user } = useAuth();
  const { config } = useConfig();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [messageHistory, setMessageHistory] = useState<WebSocketMessage[]>([]);
  const [connectionCount, setConnectionCount] = useState(0);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [subscribers, setSubscribers] = useState<Map<string, Set<(message: WebSocketMessage) => void>>>(new Map());
  
  // Estadísticas de conexión
  const statsRef = useRef({
    uptime: 0,
    messagesSent: 0,
    messagesReceived: 0,
    errors: 0,
    connectedAt: 0,
  });

  // Construir URL del websocket
  const getWebSocketUrl = (): string => {
    if (url) return url;
    
    const apiUrl = config.apiBaseUrl;
    const wsUrl = apiUrl.replace(/^http/, 'ws');
    return `${wsUrl}/ws/`;
  };

  // Conectar al websocket
  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      setStatus('connecting');
      const wsUrl = getWebSocketUrl();
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = handleOpen;
      ws.onmessage = handleMessage;
      ws.onclose = handleClose;
      ws.onerror = handleError;
      
      wsRef.current = ws;
    } catch (error) {
      console.error('WebSocket connection error:', error);
      setStatus('error');
      statsRef.current.errors++;
    }
  };

  // Desconectar del websocket
  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setStatus('disconnected');
    setReconnectAttempts(0);
  };

  // Reconectar al websocket
  const reconnect = () => {
    if (reconnectAttempts >= maxReconnectAttempts) {
      setStatus('error');
      return;
    }

    setStatus('reconnecting');
    setReconnectAttempts(prev => prev + 1);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, reconnectInterval);
  };

  // Manejar apertura de conexión
  const handleOpen = () => {
    setStatus('connected');
    setConnectionCount(prev => prev + 1);
    setReconnectAttempts(0);
    statsRef.current.connectedAt = Date.now();
    
    // Enviar autenticación si el usuario está autenticado
    if (user) {
      sendMessage('auth', {
        token: localStorage.getItem('authToken'),
        userId: user.id,
      });
    }
    
    // Iniciar heartbeat
    startHeartbeat();
  };

  // Manejar mensajes recibidos
  const handleMessage = (event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      message.timestamp = new Date().toISOString();
      
      setLastMessage(message);
      setMessageHistory(prev => {
        const updated = [message, ...prev];
        return updated.slice(0, maxMessageHistory);
      });
      
      statsRef.current.messagesReceived++;
      
      // Notificar a los suscriptores
      if (message.type && subscribers.has(message.type)) {
        subscribers.get(message.type)?.forEach(callback => {
          try {
            callback(message);
          } catch (error) {
            console.error('Error in WebSocket subscriber callback:', error);
          }
        });
      }
      
      // Notificar a todos los suscriptores
      if (subscribers.has('*')) {
        subscribers.get('*')?.forEach(callback => {
          try {
            callback(message);
          } catch (error) {
            console.error('Error in WebSocket subscriber callback:', error);
          }
        });
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
      statsRef.current.errors++;
    }
  };

  // Manejar cierre de conexión
  const handleClose = (event: CloseEvent) => {
    setStatus('disconnected');
    
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
    
    // Intentar reconectar si no fue un cierre intencional
    if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
      reconnect();
    }
  };

  // Manejar errores de conexión
  const handleError = (event: Event) => {
    console.error('WebSocket error:', event);
    setStatus('error');
    statsRef.current.errors++;
  };

  // Iniciar heartbeat
  const startHeartbeat = () => {
    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        sendMessage('ping', { timestamp: Date.now() });
      }
    }, 30000); // Ping cada 30 segundos
  };

  // Enviar mensaje
  const sendMessage = (type: string, data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type,
        data,
        timestamp: new Date().toISOString(),
        id: Math.random().toString(36).substr(2, 9),
      };
      
      wsRef.current.send(JSON.stringify(message));
      statsRef.current.messagesSent++;
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', type);
    }
  };

  // Enviar comando
  const sendCommand = (command: string, params?: any) => {
    sendMessage('command', { command, params });
  };

  // Suscribirse a un canal
  const subscribe = (channel: string, callback: (message: WebSocketMessage) => void) => {
    setSubscribers(prev => {
      const newSubscribers = new Map(prev);
      if (!newSubscribers.has(channel)) {
        newSubscribers.set(channel, new Set());
      }
      newSubscribers.get(channel)!.add(callback);
      return newSubscribers;
    });
    
    // Retornar función para desuscribirse
    return () => {
      setSubscribers(prev => {
        const newSubscribers = new Map(prev);
        const channelSubscribers = newSubscribers.get(channel);
        if (channelSubscribers) {
          channelSubscribers.delete(callback);
          if (channelSubscribers.size === 0) {
            newSubscribers.delete(channel);
          }
        }
        return newSubscribers;
      });
    };
  };

  // Desuscribirse de un canal
  const unsubscribe = (channel: string) => {
    setSubscribers(prev => {
      const newSubscribers = new Map(prev);
      newSubscribers.delete(channel);
      return newSubscribers;
    });
  };

  // Limpiar historial de mensajes
  const clearMessageHistory = () => {
    setMessageHistory([]);
  };

  // Obtener historial de mensajes
  const getMessageHistory = (type?: string, limit?: number): WebSocketMessage[] => {
    let filtered = messageHistory;
    
    if (type) {
      filtered = filtered.filter(msg => msg.type === type);
    }
    
    if (limit) {
      filtered = filtered.slice(0, limit);
    }
    
    return filtered;
  };

  // Obtener estadísticas de conexión
  const getConnectionStats = () => {
    const now = Date.now();
    const uptime = statsRef.current.connectedAt > 0 ? now - statsRef.current.connectedAt : 0;
    
    return {
      uptime,
      messagesSent: statsRef.current.messagesSent,
      messagesReceived: statsRef.current.messagesReceived,
      errors: statsRef.current.errors,
    };
  };

  // Conectar automáticamente cuando el usuario se autentica
  useEffect(() => {
    if (autoConnect && user) {
      connect();
    }
  }, [user, autoConnect]);

  // Limpiar al desmontar
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  const value: WebSocketContextType = {
    status,
    isConnected: status === 'connected',
    isConnecting: status === 'connecting',
    isReconnecting: status === 'reconnecting',
    lastMessage,
    messageHistory,
    connectionCount,
    reconnectAttempts,
    maxReconnectAttempts,
    reconnectInterval,
    connect,
    disconnect,
    reconnect,
    sendMessage,
    sendCommand,
    subscribe,
    unsubscribe,
    clearMessageHistory,
    getMessageHistory,
    getConnectionStats,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

// ============================================================================
// WEBSOCKET HOOK - Hook para usar el contexto de websockets
// ============================================================================

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  
  return context;
};

// ============================================================================
// WEBSOCKET HOOKS ESPECÍFICOS - Hooks para casos de uso específicos
// ============================================================================

export const useWebSocketSubscription = (channel: string, callback: (message: WebSocketMessage) => void) => {
  const { subscribe } = useWebSocket();
  
  useEffect(() => {
    const unsubscribe = subscribe(channel, callback);
    return unsubscribe;
  }, [channel, callback, subscribe]);
};

export const useWebSocketMessage = (type: string) => {
  const { messageHistory } = useWebSocket();
  return messageHistory.filter(msg => msg.type === type);
};

export const useWebSocketStatus = () => {
  const { status, isConnected, isConnecting, isReconnecting } = useWebSocket();
  return { status, isConnected, isConnecting, isReconnecting };
};

export const useWebSocketStats = () => {
  const { getConnectionStats } = useWebSocket();
  const [stats, setStats] = useState(getConnectionStats());
  
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(getConnectionStats());
    }, 1000);
    
    return () => clearInterval(interval);
  }, [getConnectionStats]);
  
  return stats;
}; 