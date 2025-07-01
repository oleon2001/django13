import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';

// ============================================================================
// HOTKEY TYPES - Tipos para hotkeys
// ============================================================================

export interface Hotkey {
  id: string;
  keys: string[];
  description: string;
  category: string;
  action: () => void;
  enabled: boolean;
  global: boolean;
  preventDefault: boolean;
  stopPropagation: boolean;
  priority: number;
  context?: string;
}

export interface HotkeyContext {
  id: string;
  name: string;
  description: string;
  active: boolean;
  hotkeys: Hotkey[];
}

export interface HotkeyState {
  activeContext: string | null;
  contexts: Map<string, HotkeyContext>;
  globalHotkeys: Hotkey[];
  pressedKeys: Set<string>;
  isRecording: boolean;
  recordingHotkey: string | null;
}

export interface HotkeyContextType {
  // Estado
  state: HotkeyState;
  
  // Métodos de registro
  registerHotkey: (hotkey: Omit<Hotkey, 'id'>) => string;
  unregisterHotkey: (id: string) => void;
  updateHotkey: (id: string, updates: Partial<Hotkey>) => void;
  
  // Métodos de contexto
  registerContext: (context: Omit<HotkeyContext, 'id'>) => string;
  unregisterContext: (id: string) => void;
  activateContext: (id: string) => void;
  deactivateContext: (id: string) => void;
  getActiveContext: () => string | null;
  
  // Métodos de grabación
  startRecording: (hotkeyId: string) => void;
  stopRecording: () => void;
  isRecordingHotkey: (hotkeyId: string) => boolean;
  
  // Métodos de utilidad
  getHotkey: (id: string) => Hotkey | null;
  getHotkeysByCategory: (category: string) => Hotkey[];
  getHotkeysByContext: (contextId: string) => Hotkey[];
  getGlobalHotkeys: () => Hotkey[];
  
  // Métodos de validación
  isValidKeyCombination: (keys: string[]) => boolean;
  parseKeyCombination: (combination: string) => string[];
  formatKeyCombination: (keys: string[]) => string;
  
  // Métodos de configuración
  enableHotkey: (id: string) => void;
  disableHotkey: (id: string) => void;
  enableAllHotkeys: () => void;
  disableAllHotkeys: () => void;
  
  // Métodos de exportación
  exportHotkeys: () => Record<string, any>;
  importHotkeys: (data: Record<string, any>) => void;
}

// ============================================================================
// HOTKEY CONTEXT - Contexto para hotkeys
// ============================================================================

const HotkeyContext = createContext<HotkeyContextType | undefined>(undefined);

// ============================================================================
// HOTKEY PROVIDER - Provider para hotkeys
// ============================================================================

interface HotkeyProviderProps {
  children: ReactNode;
  enableGlobalHotkeys?: boolean;
  enableContextHotkeys?: boolean;
  enableRecording?: boolean;
  preventDefault?: boolean;
  stopPropagation?: boolean;
  debugMode?: boolean;
}

export const HotkeyProvider: React.FC<HotkeyProviderProps> = ({
  children,
  enableGlobalHotkeys = true,
  enableContextHotkeys = true,
  enableRecording = true,
  preventDefault = true,
  stopPropagation = true,
  debugMode = false,
}) => {
  const [state, setState] = useState<HotkeyState>({
    activeContext: null,
    contexts: new Map(),
    globalHotkeys: [],
    pressedKeys: new Set(),
    isRecording: false,
    recordingHotkey: null,
  });

  const hotkeysRef = useRef<Map<string, Hotkey>>(new Map());
  const nextIdRef = useRef(1);

  // Generar ID único
  const generateId = (): string => {
    return `hotkey_${nextIdRef.current++}`;
  };

  // Normalizar teclas
  const normalizeKey = (key: string): string => {
    return key.toLowerCase().replace(/\s+/g, '');
  };

  // Parsear combinación de teclas
  const parseKeyCombination = (combination: string): string[] => {
    return combination
      .split('+')
      .map(key => normalizeKey(key.trim()))
      .filter(Boolean);
  };

  // Formatear combinación de teclas
  const formatKeyCombination = (keys: string[]): string => {
    return keys
      .map(key => key.charAt(0).toUpperCase() + key.slice(1))
      .join(' + ');
  };

  // Verificar si es una combinación válida
  const isValidKeyCombination = (keys: string[]): boolean => {
    if (keys.length === 0) return false;
    
    const validKeys = new Set([
      'ctrl', 'cmd', 'alt', 'shift', 'meta',
      'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
      'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
      '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
      'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
      'enter', 'escape', 'tab', 'space', 'backspace', 'delete',
      'arrowup', 'arrowdown', 'arrowleft', 'arrowright',
      'home', 'end', 'pageup', 'pagedown',
    ]);

    return keys.every(key => validKeys.has(key));
  };

  // Verificar si las teclas coinciden
  const keysMatch = (pressed: Set<string>, required: string[]): boolean => {
    if (pressed.size !== required.length) return false;
    
    return required.every(key => pressed.has(key));
  };

  // Manejar evento de tecla
  const handleKeyEvent = (event: KeyboardEvent, isKeyDown: boolean): void => {
    const key = normalizeKey(event.key);
    const pressedKeys = new Set(state.pressedKeys);

    if (isKeyDown) {
      pressedKeys.add(key);
    } else {
      pressedKeys.delete(key);
    }

    setState(prev => ({
      ...prev,
      pressedKeys,
    }));

    // Si está grabando, actualizar las teclas presionadas
    if (state.isRecording && isKeyDown) {
      const recordingKeys = Array.from(pressedKeys);
      if (isValidKeyCombination(recordingKeys)) {
        const hotkey = hotkeysRef.current.get(state.recordingHotkey!);
        if (hotkey) {
          updateHotkey(state.recordingHotkey!, { keys: recordingKeys });
        }
        stopRecording();
      }
    }

    // Verificar hotkeys globales
    if (enableGlobalHotkeys && isKeyDown) {
      for (const hotkey of state.globalHotkeys) {
        if (hotkey.enabled && keysMatch(pressedKeys, hotkey.keys)) {
          if (hotkey.preventDefault) {
            event.preventDefault();
          }
          if (hotkey.stopPropagation) {
            event.stopPropagation();
          }
          
          if (debugMode) {
            console.log(`Global hotkey triggered: ${formatKeyCombination(hotkey.keys)}`);
          }
          
          hotkey.action();
          break;
        }
      }
    }

    // Verificar hotkeys de contexto
    if (enableContextHotkeys && isKeyDown && state.activeContext) {
      const context = state.contexts.get(state.activeContext);
      if (context) {
        for (const hotkey of context.hotkeys) {
          if (hotkey.enabled && keysMatch(pressedKeys, hotkey.keys)) {
            if (hotkey.preventDefault) {
              event.preventDefault();
            }
            if (hotkey.stopPropagation) {
              event.stopPropagation();
            }
            
            if (debugMode) {
              console.log(`Context hotkey triggered: ${formatKeyCombination(hotkey.keys)}`);
            }
            
            hotkey.action();
            break;
          }
        }
      }
    }
  };

  // Registrar hotkey
  const registerHotkey = (hotkey: Omit<Hotkey, 'id'>): string => {
    const id = generateId();
    const newHotkey: Hotkey = {
      ...hotkey,
      id,
      keys: hotkey.keys.map(normalizeKey),
      preventDefault: hotkey.preventDefault ?? preventDefault,
      stopPropagation: hotkey.stopPropagation ?? stopPropagation,
    };

    hotkeysRef.current.set(id, newHotkey);

    if (newHotkey.global) {
      setState(prev => ({
        ...prev,
        globalHotkeys: [...prev.globalHotkeys, newHotkey],
      }));
    } else if (newHotkey.context) {
      const context = state.contexts.get(newHotkey.context);
      if (context) {
        setState(prev => {
          const newContexts = new Map(prev.contexts);
          newContexts.set(newHotkey.context!, {
            ...context,
            hotkeys: [...context.hotkeys, newHotkey],
          });
          return { ...prev, contexts: newContexts };
        });
      }
    }

    return id;
  };

  // Desregistrar hotkey
  const unregisterHotkey = (id: string): void => {
    const hotkey = hotkeysRef.current.get(id);
    if (!hotkey) return;

    hotkeysRef.current.delete(id);

    if (hotkey.global) {
      setState(prev => ({
        ...prev,
        globalHotkeys: prev.globalHotkeys.filter(h => h.id !== id),
      }));
    } else if (hotkey.context) {
      const context = state.contexts.get(hotkey.context);
      if (context) {
        setState(prev => {
          const newContexts = new Map(prev.contexts);
          newContexts.set(hotkey.context!, {
            ...context,
            hotkeys: context.hotkeys.filter(h => h.id !== id),
          });
          return { ...prev, contexts: newContexts };
        });
      }
    }
  };

  // Actualizar hotkey
  const updateHotkey = (id: string, updates: Partial<Hotkey>): void => {
    const hotkey = hotkeysRef.current.get(id);
    if (!hotkey) return;

    const updatedHotkey = { ...hotkey, ...updates };
    hotkeysRef.current.set(id, updatedHotkey);

    // Actualizar en el estado correspondiente
    if (updatedHotkey.global) {
      setState(prev => ({
        ...prev,
        globalHotkeys: prev.globalHotkeys.map(h => h.id === id ? updatedHotkey : h),
      }));
    } else if (updatedHotkey.context) {
      const context = state.contexts.get(updatedHotkey.context);
      if (context) {
        setState(prev => {
          const newContexts = new Map(prev.contexts);
          newContexts.set(updatedHotkey.context!, {
            ...context,
            hotkeys: context.hotkeys.map(h => h.id === id ? updatedHotkey : h),
          });
          return { ...prev, contexts: newContexts };
        });
      }
    }
  };

  // Registrar contexto
  const registerContext = (context: Omit<HotkeyContext, 'id'>): string => {
    const id = generateId();
    const newContext: HotkeyContext = {
      ...context,
      id,
      hotkeys: [],
    };

    setState(prev => {
      const newContexts = new Map(prev.contexts);
      newContexts.set(id, newContext);
      return { ...prev, contexts: newContexts };
    });

    return id;
  };

  // Desregistrar contexto
  const unregisterContext = (id: string): void => {
    setState(prev => {
      const newContexts = new Map(prev.contexts);
      newContexts.delete(id);
      return { ...prev, contexts: newContexts };
    });
  };

  // Activar contexto
  const activateContext = (id: string): void => {
    const context = state.contexts.get(id);
    if (context) {
      setState(prev => ({
        ...prev,
        activeContext: id,
      }));
    }
  };

  // Desactivar contexto
  const deactivateContext = (id: string): void => {
    if (state.activeContext === id) {
      setState(prev => ({
        ...prev,
        activeContext: null,
      }));
    }
  };

  // Obtener contexto activo
  const getActiveContext = (): string | null => {
    return state.activeContext;
  };

  // Iniciar grabación
  const startRecording = (hotkeyId: string): void => {
    if (!enableRecording) return;

    setState(prev => ({
      ...prev,
      isRecording: true,
      recordingHotkey: hotkeyId,
    }));
  };

  // Detener grabación
  const stopRecording = (): void => {
    setState(prev => ({
      ...prev,
      isRecording: false,
      recordingHotkey: null,
    }));
  };

  // Verificar si está grabando un hotkey
  const isRecordingHotkey = (hotkeyId: string): boolean => {
    return state.isRecording && state.recordingHotkey === hotkeyId;
  };

  // Obtener hotkey
  const getHotkey = (id: string): Hotkey | null => {
    return hotkeysRef.current.get(id) || null;
  };

  // Obtener hotkeys por categoría
  const getHotkeysByCategory = (category: string): Hotkey[] => {
    return Array.from(hotkeysRef.current.values()).filter(h => h.category === category);
  };

  // Obtener hotkeys por contexto
  const getHotkeysByContext = (contextId: string): Hotkey[] => {
    const context = state.contexts.get(contextId);
    return context ? context.hotkeys : [];
  };

  // Obtener hotkeys globales
  const getGlobalHotkeys = (): Hotkey[] => {
    return state.globalHotkeys;
  };

  // Habilitar hotkey
  const enableHotkey = (id: string): void => {
    updateHotkey(id, { enabled: true });
  };

  // Deshabilitar hotkey
  const disableHotkey = (id: string): void => {
    updateHotkey(id, { enabled: false });
  };

  // Habilitar todos los hotkeys
  const enableAllHotkeys = (): void => {
    Array.from(hotkeysRef.current.keys()).forEach(enableHotkey);
  };

  // Deshabilitar todos los hotkeys
  const disableAllHotkeys = (): void => {
    Array.from(hotkeysRef.current.keys()).forEach(disableHotkey);
  };

  // Exportar hotkeys
  const exportHotkeys = (): Record<string, any> => {
    return {
      hotkeys: Array.from(hotkeysRef.current.values()),
      contexts: Array.from(state.contexts.values()),
      activeContext: state.activeContext,
    };
  };

  // Importar hotkeys
  const importHotkeys = (data: Record<string, any>): void => {
    // Limpiar hotkeys existentes
    hotkeysRef.current.clear();
    setState(prev => ({
      ...prev,
      globalHotkeys: [],
      contexts: new Map(),
    }));

    // Importar contextos
    if (data.contexts) {
      data.contexts.forEach((context: any) => {
        registerContext(context);
      });
    }

    // Importar hotkeys
    if (data.hotkeys) {
      data.hotkeys.forEach((hotkey: any) => {
        registerHotkey(hotkey);
      });
    }

    // Establecer contexto activo
    if (data.activeContext) {
      activateContext(data.activeContext);
    }
  };

  // Configurar event listeners
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => handleKeyEvent(event, true);
    const handleKeyUp = (event: KeyboardEvent) => handleKeyEvent(event, false);

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    };
  }, [state.pressedKeys, state.isRecording, state.recordingHotkey, state.globalHotkeys, state.activeContext, state.contexts]);

  const value: HotkeyContextType = {
    state,
    registerHotkey,
    unregisterHotkey,
    updateHotkey,
    registerContext,
    unregisterContext,
    activateContext,
    deactivateContext,
    getActiveContext,
    startRecording,
    stopRecording,
    isRecordingHotkey,
    getHotkey,
    getHotkeysByCategory,
    getHotkeysByContext,
    getGlobalHotkeys,
    isValidKeyCombination,
    parseKeyCombination,
    formatKeyCombination,
    enableHotkey,
    disableHotkey,
    enableAllHotkeys,
    disableAllHotkeys,
    exportHotkeys,
    importHotkeys,
  };

  return (
    <HotkeyContext.Provider value={value}>
      {children}
    </HotkeyContext.Provider>
  );
};

// ============================================================================
// HOTKEY HOOK - Hook para usar el contexto de hotkeys
// ============================================================================

export const useHotkey = () => {
  const context = useContext(HotkeyContext);
  
  if (context === undefined) {
    throw new Error('useHotkey must be used within a HotkeyProvider');
  }
  
  return context;
};

// ============================================================================
// HOTKEY HOOKS ESPECÍFICOS - Hooks para casos de uso específicos
// ============================================================================

export const useHotkeyRegistration = () => {
  const { registerHotkey, unregisterHotkey, updateHotkey } = useHotkey();
  return { registerHotkey, unregisterHotkey, updateHotkey };
};

export const useHotkeyContext = () => {
  const { registerContext, activateContext, deactivateContext, getActiveContext } = useHotkey();
  return { registerContext, activateContext, deactivateContext, getActiveContext };
};

export const useHotkeyRecording = () => {
  const { startRecording, stopRecording, isRecordingHotkey } = useHotkey();
  return { startRecording, stopRecording, isRecordingHotkey };
}; 