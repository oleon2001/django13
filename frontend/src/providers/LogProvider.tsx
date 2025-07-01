import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import { useAuth } from './AuthProvider';
import { useConfig } from './ConfigProvider';

// ============================================================================
// LOG TYPES - Tipos para logs
// ============================================================================

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal';

export interface LogEntry {
  id: string;
  level: LogLevel;
  message: string;
  timestamp: string;
  category: string;
  userId?: string;
  sessionId: string;
  userAgent: string;
  url: string;
  stack?: string;
  data?: any;
  tags: string[];
  source: string;
  duration?: number;
  memory?: {
    used: number;
    total: number;
    free: number;
  };
}

export interface LogFilter {
  level?: LogLevel[];
  category?: string[];
  userId?: string;
  sessionId?: string;
  tags?: string[];
  source?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  search?: string;
}

export interface LogStats {
  total: number;
  byLevel: Record<LogLevel, number>;
  byCategory: Record<string, number>;
  bySource: Record<string, number>;
  errors: number;
  warnings: number;
  oldestEntry: string | null;
  newestEntry: string | null;
  averagePerMinute: number;
}

export interface LogContextType {
  // Estado
  logs: LogEntry[];
  isEnabled: boolean;
  currentLevel: LogLevel;
  
  // Métodos de logging
  debug: (message: string, data?: any, tags?: string[]) => void;
  info: (message: string, data?: any, tags?: string[]) => void;
  warn: (message: string, data?: any, tags?: string[]) => void;
  error: (message: string, error?: Error, data?: any, tags?: string[]) => void;
  fatal: (message: string, error?: Error, data?: any, tags?: string[]) => void;
  
  // Métodos de logging con categoría
  log: (level: LogLevel, category: string, message: string, data?: any, tags?: string[]) => void;
  
  // Métodos de logging de rendimiento
  time: (label: string) => void;
  timeEnd: (label: string) => void;
  
  // Métodos de filtrado
  getLogs: (filter?: LogFilter) => LogEntry[];
  getLogsByLevel: (level: LogLevel) => LogEntry[];
  getLogsByCategory: (category: string) => LogEntry[];
  getLogsByTag: (tag: string) => LogEntry[];
  getLogsBySource: (source: string) => LogEntry[];
  
  // Métodos de estadísticas
  getStats: () => LogStats;
  getErrorRate: () => number;
  getWarningRate: () => number;
  
  // Métodos de utilidad
  clear: () => void;
  clearByLevel: (level: LogLevel) => void;
  clearByCategory: (category: string) => void;
  clearByTag: (tag: string) => void;
  
  // Métodos de configuración
  setLevel: (level: LogLevel) => void;
  enable: () => void;
  disable: () => void;
  
  // Métodos de exportación
  export: (format: 'json' | 'csv' | 'txt', filter?: LogFilter) => void;
  download: (filename?: string) => void;
  
  // Métodos de búsqueda
  search: (query: string) => LogEntry[];
  searchAdvanced: (filter: LogFilter) => LogEntry[];
}

// ============================================================================
// LOG CONTEXT - Contexto para logs
// ============================================================================

const LogContext = createContext<LogContextType | undefined>(undefined);

// ============================================================================
// LOG PROVIDER - Provider para logs
// ============================================================================

interface LogProviderProps {
  children: ReactNode;
  enabled?: boolean;
  level?: LogLevel;
  maxLogs?: number;
  enableConsole?: boolean;
  enableRemote?: boolean;
  remoteEndpoint?: string;
  enablePersistence?: boolean;
  persistenceKey?: string;
  autoCleanup?: boolean;
  cleanupInterval?: number;
}

export const LogProvider: React.FC<LogProviderProps> = ({
  children,
  enabled = true,
  level = 'info',
  maxLogs = 1000,
  enableConsole = true,
  enableRemote = false,
  remoteEndpoint = '/api/logs',
  enablePersistence = true,
  persistenceKey = 'app_logs',
  autoCleanup = true,
  cleanupInterval = 5 * 60 * 1000, // 5 minutos
}) => {
  const { user } = useAuth();
  const { config } = useConfig();
  
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isEnabled, setIsEnabled] = useState(enabled);
  const [currentLevel, setCurrentLevel] = useState<LogLevel>(level);
  
  const sessionIdRef = useRef<string>('');
  const timersRef = useRef<Map<string, number>>(new Map());
  const cleanupIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Niveles de log ordenados por severidad
  const logLevels: LogLevel[] = ['debug', 'info', 'warn', 'error', 'fatal'];
  const levelIndex = logLevels.indexOf(currentLevel);

  // Generar ID único
  const generateId = (): string => {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Generar Session ID
  const generateSessionId = (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Verificar si un nivel debe ser registrado
  const shouldLog = (logLevel: LogLevel): boolean => {
    if (!isEnabled) return false;
    return logLevels.indexOf(logLevel) >= levelIndex;
  };

  // Obtener información del sistema
  const getSystemInfo = () => {
    return {
      userAgent: navigator.userAgent,
      url: window.location.href,
      memory: 'memory' in performance ? {
        used: (performance as any).memory.usedJSHeapSize,
        total: (performance as any).memory.totalJSHeapSize,
        free: (performance as any).memory.totalJSHeapSize - (performance as any).memory.usedJSHeapSize,
      } : undefined,
    };
  };

  // Crear entrada de log
  const createLogEntry = (
    level: LogLevel,
    category: string,
    message: string,
    data?: any,
    tags: string[] = [],
    error?: Error
  ): LogEntry => {
    const systemInfo = getSystemInfo();
    
    return {
      id: generateId(),
      level,
      message,
      timestamp: new Date().toISOString(),
      category,
      userId: user?.id?.toString(),
      sessionId: sessionIdRef.current,
      userAgent: systemInfo.userAgent,
      url: systemInfo.url,
      stack: error?.stack,
      data,
      tags,
      source: 'frontend',
      memory: systemInfo.memory,
    };
  };

  // Agregar log
  const addLog = (entry: LogEntry) => {
    setLogs(prev => {
      const updated = [entry, ...prev];
      return updated.slice(0, maxLogs);
    });

    // Log a consola si está habilitado
    if (enableConsole) {
      const consoleMethod = entry.level === 'debug' ? 'debug' :
                           entry.level === 'info' ? 'info' :
                           entry.level === 'warn' ? 'warn' :
                           entry.level === 'error' ? 'error' : 'error';
      
      console[consoleMethod](
        `[${entry.category}] ${entry.message}`,
        entry.data || '',
        entry.tags.length > 0 ? `Tags: ${entry.tags.join(', ')}` : ''
      );
    }

    // Enviar a servidor remoto si está habilitado
    if (enableRemote && remoteEndpoint) {
      sendToRemote(entry);
    }
  };

  // Enviar log al servidor remoto
  const sendToRemote = async (entry: LogEntry) => {
    try {
      await fetch(remoteEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entry),
      });
    } catch (error) {
      console.error('Error sending log to remote server:', error);
    }
  };

  // Métodos de logging
  const debug = (message: string, data?: any, tags: string[] = []) => {
    if (!shouldLog('debug')) return;
    const entry = createLogEntry('debug', 'general', message, data, tags);
    addLog(entry);
  };

  const info = (message: string, data?: any, tags: string[] = []) => {
    if (!shouldLog('info')) return;
    const entry = createLogEntry('info', 'general', message, data, tags);
    addLog(entry);
  };

  const warn = (message: string, data?: any, tags: string[] = []) => {
    if (!shouldLog('warn')) return;
    const entry = createLogEntry('warn', 'general', message, data, tags);
    addLog(entry);
  };

  const error = (message: string, error?: Error, data?: any, tags: string[] = []) => {
    if (!shouldLog('error')) return;
    const entry = createLogEntry('error', 'general', message, data, tags, error);
    addLog(entry);
  };

  const fatal = (message: string, error?: Error, data?: any, tags: string[] = []) => {
    if (!shouldLog('fatal')) return;
    const entry = createLogEntry('fatal', 'general', message, data, tags, error);
    addLog(entry);
  };

  // Log con categoría
  const log = (level: LogLevel, category: string, message: string, data?: any, tags: string[] = []) => {
    if (!shouldLog(level)) return;
    const entry = createLogEntry(level, category, message, data, tags);
    addLog(entry);
  };

  // Timer para medir rendimiento
  const time = (label: string) => {
    timersRef.current.set(label, performance.now());
  };

  const timeEnd = (label: string) => {
    const startTime = timersRef.current.get(label);
    if (startTime) {
      const duration = performance.now() - startTime;
      timersRef.current.delete(label);
      log('info', 'performance', `${label} took ${duration.toFixed(2)}ms`, { duration }, ['performance']);
    }
  };

  // Obtener logs con filtro
  const getLogs = (filter?: LogFilter): LogEntry[] => {
    let filteredLogs = logs;

    if (filter) {
      if (filter.level && filter.level.length > 0) {
        filteredLogs = filteredLogs.filter(log => filter.level!.includes(log.level));
      }

      if (filter.category && filter.category.length > 0) {
        filteredLogs = filteredLogs.filter(log => filter.category!.includes(log.category));
      }

      if (filter.userId) {
        filteredLogs = filteredLogs.filter(log => log.userId === filter.userId);
      }

      if (filter.sessionId) {
        filteredLogs = filteredLogs.filter(log => log.sessionId === filter.sessionId);
      }

      if (filter.tags && filter.tags.length > 0) {
        filteredLogs = filteredLogs.filter(log => 
          filter.tags!.some(tag => log.tags.includes(tag))
        );
      }

      if (filter.source && filter.source.length > 0) {
        filteredLogs = filteredLogs.filter(log => filter.source!.includes(log.source));
      }

      if (filter.dateRange) {
        filteredLogs = filteredLogs.filter(log => {
          const timestamp = new Date(log.timestamp).getTime();
          const start = new Date(filter.dateRange!.start).getTime();
          const end = new Date(filter.dateRange!.end).getTime();
          return timestamp >= start && timestamp <= end;
        });
      }

      if (filter.search) {
        const searchLower = filter.search.toLowerCase();
        filteredLogs = filteredLogs.filter(log =>
          log.message.toLowerCase().includes(searchLower) ||
          log.category.toLowerCase().includes(searchLower) ||
          log.tags.some(tag => tag.toLowerCase().includes(searchLower))
        );
      }
    }

    return filteredLogs;
  };

  // Obtener logs por nivel
  const getLogsByLevel = (level: LogLevel): LogEntry[] => {
    return logs.filter(log => log.level === level);
  };

  // Obtener logs por categoría
  const getLogsByCategory = (category: string): LogEntry[] => {
    return logs.filter(log => log.category === category);
  };

  // Obtener logs por tag
  const getLogsByTag = (tag: string): LogEntry[] => {
    return logs.filter(log => log.tags.includes(tag));
  };

  // Obtener logs por fuente
  const getLogsBySource = (source: string): LogEntry[] => {
    return logs.filter(log => log.source === source);
  };

  // Obtener estadísticas
  const getStats = (): LogStats => {
    const byLevel: Record<LogLevel, number> = {
      debug: 0,
      info: 0,
      warn: 0,
      error: 0,
      fatal: 0,
    };

    const byCategory: Record<string, number> = {};
    const bySource: Record<string, number> = {};

    let errors = 0;
    let warnings = 0;
    let oldestEntry: string | null = null;
    let newestEntry: string | null = null;

    logs.forEach(log => {
      byLevel[log.level]++;
      
      if (log.level === 'error' || log.level === 'fatal') errors++;
      if (log.level === 'warn') warnings++;

      byCategory[log.category] = (byCategory[log.category] || 0) + 1;
      bySource[log.source] = (bySource[log.source] || 0) + 1;

      if (!oldestEntry || log.timestamp < oldestEntry) {
        oldestEntry = log.timestamp;
      }
      if (!newestEntry || log.timestamp > newestEntry) {
        newestEntry = log.timestamp;
      }
    });

    // Calcular promedio por minuto
    let averagePerMinute = 0;
    if (logs.length > 0 && oldestEntry && newestEntry) {
      const oldest = new Date(oldestEntry).getTime();
      const newest = new Date(newestEntry).getTime();
      const durationMinutes = (newest - oldest) / (1000 * 60);
      averagePerMinute = durationMinutes > 0 ? logs.length / durationMinutes : 0;
    }

    return {
      total: logs.length,
      byLevel,
      byCategory,
      bySource,
      errors,
      warnings,
      oldestEntry,
      newestEntry,
      averagePerMinute,
    };
  };

  // Obtener tasa de errores
  const getErrorRate = (): number => {
    const stats = getStats();
    return stats.total > 0 ? stats.errors / stats.total : 0;
  };

  // Obtener tasa de advertencias
  const getWarningRate = (): number => {
    const stats = getStats();
    return stats.total > 0 ? stats.warnings / stats.total : 0;
  };

  // Limpiar logs
  const clear = (): void => {
    setLogs([]);
  };

  // Limpiar logs por nivel
  const clearByLevel = (level: LogLevel): void => {
    setLogs(prev => prev.filter(log => log.level !== level));
  };

  // Limpiar logs por categoría
  const clearByCategory = (category: string): void => {
    setLogs(prev => prev.filter(log => log.category !== category));
  };

  // Limpiar logs por tag
  const clearByTag = (tag: string): void => {
    setLogs(prev => prev.filter(log => !log.tags.includes(tag)));
  };

  // Establecer nivel de log
  const setLevel = (level: LogLevel): void => {
    setCurrentLevel(level);
  };

  // Habilitar logging
  const enable = (): void => {
    setIsEnabled(true);
  };

  // Deshabilitar logging
  const disable = (): void => {
    setIsEnabled(false);
  };

  // Exportar logs
  const export_ = (format: 'json' | 'csv' | 'txt', filter?: LogFilter): void => {
    const filteredLogs = getLogs(filter);
    let content = '';
    let filename = `logs_${Date.now()}`;

    switch (format) {
      case 'json':
        content = JSON.stringify(filteredLogs, null, 2);
        filename += '.json';
        break;
      
      case 'csv':
        content = 'Timestamp,Level,Category,Message,Tags,Source\n';
        filteredLogs.forEach(log => {
          content += `"${log.timestamp}","${log.level}","${log.category}","${log.message}","${log.tags.join(',')}","${log.source}"\n`;
        });
        filename += '.csv';
        break;
      
      case 'txt':
        filteredLogs.forEach(log => {
          content += `[${log.timestamp}] ${log.level.toUpperCase()} [${log.category}] ${log.message}\n`;
          if (log.tags.length > 0) {
            content += `  Tags: ${log.tags.join(', ')}\n`;
          }
          if (log.data) {
            content += `  Data: ${JSON.stringify(log.data)}\n`;
          }
          content += '\n';
        });
        filename += '.txt';
        break;
    }

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Descargar logs
  const download = (filename?: string): void => {
    const defaultFilename = `logs_${Date.now()}.json`;
    export_('json');
  };

  // Buscar logs
  const search = (query: string): LogEntry[] => {
    return getLogs({ search: query });
  };

  // Búsqueda avanzada
  const searchAdvanced = (filter: LogFilter): LogEntry[] => {
    return getLogs(filter);
  };

  // Limpieza automática
  const autoCleanup = () => {
    if (logs.length > maxLogs * 0.8) {
      const logsToRemove = Math.floor(logs.length * 0.2);
      setLogs(prev => prev.slice(0, prev.length - logsToRemove));
    }
  };

  // Inicializar
  useEffect(() => {
    sessionIdRef.current = generateSessionId();

    if (autoCleanup && cleanupInterval > 0) {
      cleanupIntervalRef.current = setInterval(autoCleanup, cleanupInterval);
    }

    return () => {
      if (cleanupIntervalRef.current) {
        clearInterval(cleanupIntervalRef.current);
      }
    };
  }, [autoCleanup, cleanupInterval]);

  // Cargar logs guardados
  useEffect(() => {
    if (enablePersistence) {
      try {
        const savedLogs = localStorage.getItem(persistenceKey);
        if (savedLogs) {
          const parsed = JSON.parse(savedLogs);
          setLogs(parsed);
        }
      } catch (error) {
        console.error('Error loading saved logs:', error);
      }
    }
  }, [enablePersistence, persistenceKey]);

  // Guardar logs
  useEffect(() => {
    if (enablePersistence) {
      try {
        localStorage.setItem(persistenceKey, JSON.stringify(logs));
      } catch (error) {
        console.error('Error saving logs:', error);
      }
    }
  }, [logs, enablePersistence, persistenceKey]);

  const value: LogContextType = {
    logs,
    isEnabled,
    currentLevel,
    debug,
    info,
    warn,
    error,
    fatal,
    log,
    time,
    timeEnd,
    getLogs,
    getLogsByLevel,
    getLogsByCategory,
    getLogsByTag,
    getLogsBySource,
    getStats,
    getErrorRate,
    getWarningRate,
    clear,
    clearByLevel,
    clearByCategory,
    clearByTag,
    setLevel,
    enable,
    disable,
    export: export_,
    download,
    search,
    searchAdvanced,
  };

  return (
    <LogContext.Provider value={value}>
      {children}
    </LogContext.Provider>
  );
};

// ============================================================================
// LOG HOOK - Hook para usar el contexto de logs
// ============================================================================

export const useLog = () => {
  const context = useContext(LogContext);
  
  if (context === undefined) {
    throw new Error('useLog must be used within a LogProvider');
  }
  
  return context;
};

// ============================================================================
// LOG HOOKS ESPECÍFICOS - Hooks para casos de uso específicos
// ============================================================================

export const useLogger = (category: string) => {
  const { log, debug, info, warn, error, fatal } = useLog();
  
  return {
    debug: (message: string, data?: any, tags?: string[]) => debug(message, data, tags),
    info: (message: string, data?: any, tags?: string[]) => info(message, data, tags),
    warn: (message: string, data?: any, tags?: string[]) => warn(message, data, tags),
    error: (message: string, error?: Error, data?: any, tags?: string[]) => error(message, error, data, tags),
    fatal: (message: string, error?: Error, data?: any, tags?: string[]) => fatal(message, error, data, tags),
    log: (level: LogLevel, message: string, data?: any, tags?: string[]) => log(level, category, message, data, tags),
  };
};

export const useLogStats = () => {
  const { getStats, getErrorRate, getWarningRate } = useLog();
  return {
    stats: getStats(),
    errorRate: getErrorRate(),
    warningRate: getWarningRate(),
  };
};

export const useLogSearch = () => {
  const { search, searchAdvanced, getLogs } = useLog();
  return { search, searchAdvanced, getLogs };
}; 