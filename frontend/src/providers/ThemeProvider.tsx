import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// ============================================================================
// THEME TYPES - Tipos para el tema
// ============================================================================

export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeContextType {
  mode: ThemeMode;
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (mode: ThemeMode) => void;
}

// ============================================================================
// THEME CONTEXT - Contexto para el tema
// ============================================================================

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// ============================================================================
// THEME PROVIDER - Provider para el tema
// ============================================================================

interface ThemeProviderProps {
  children: ReactNode;
  defaultMode?: ThemeMode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ 
  children, 
  defaultMode = 'system' 
}) => {
  const [mode, setMode] = useState<ThemeMode>(defaultMode);
  const [isDark, setIsDark] = useState(false);

  // Aplicar tema al documento
  const applyTheme = (themeMode: ThemeMode) => {
    const root = document.documentElement;
    const isDarkMode = themeMode === 'dark' || 
      (themeMode === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    
    setIsDark(isDarkMode);
    
    if (isDarkMode) {
      root.classList.add('dark');
      root.setAttribute('data-theme', 'dark');
    } else {
      root.classList.remove('dark');
      root.setAttribute('data-theme', 'light');
    }
  };

  // Detectar preferencia del sistema
  const detectSystemTheme = () => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    return mediaQuery.matches ? 'dark' : 'light';
  };

  // Inicializar tema
  useEffect(() => {
    // Cargar tema guardado
    const savedMode = localStorage.getItem('theme-mode') as ThemeMode;
    if (savedMode) {
      setMode(savedMode);
    }
    
    // Aplicar tema inicial
    applyTheme(mode);
  }, []);

  // Escuchar cambios en el tema del sistema
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = () => {
      if (mode === 'system') {
        applyTheme('system');
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, [mode]);

  // Aplicar tema cuando cambie el modo
  useEffect(() => {
    applyTheme(mode);
    localStorage.setItem('theme-mode', mode);
  }, [mode]);

  const toggleTheme = () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setMode(newMode);
  };

  const setTheme = (newMode: ThemeMode) => {
    setMode(newMode);
  };

  const value: ThemeContextType = {
    mode,
    isDark,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

// ============================================================================
// THEME HOOK - Hook para usar el contexto del tema
// ============================================================================

export const useTheme = () => {
  const context = useContext(ThemeContext);
  
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  
  return context;
};

// ============================================================================
// THEME UTILITIES - Utilidades para el tema
// ============================================================================

export const getThemeColors = (isDark: boolean) => {
  return {
    // Colores principales
    primary: isDark ? '#3B82F6' : '#2563EB',
    secondary: isDark ? '#6B7280' : '#4B5563',
    accent: isDark ? '#10B981' : '#059669',
    
    // Colores de fondo
    background: isDark ? '#111827' : '#FFFFFF',
    surface: isDark ? '#1F2937' : '#F9FAFB',
    card: isDark ? '#374151' : '#FFFFFF',
    
    // Colores de texto
    text: isDark ? '#F9FAFB' : '#111827',
    textSecondary: isDark ? '#9CA3AF' : '#6B7280',
    textMuted: isDark ? '#6B7280' : '#9CA3AF',
    
    // Colores de borde
    border: isDark ? '#374151' : '#E5E7EB',
    borderLight: isDark ? '#4B5563' : '#F3F4F6',
    
    // Colores de estado
    success: isDark ? '#10B981' : '#059669',
    warning: isDark ? '#F59E0B' : '#D97706',
    error: isDark ? '#EF4444' : '#DC2626',
    info: isDark ? '#3B82F6' : '#2563EB',
    
    // Colores de hover
    hover: isDark ? '#374151' : '#F3F4F6',
    hoverPrimary: isDark ? '#2563EB' : '#1D4ED8',
    
    // Sombras
    shadow: isDark ? '0 4px 6px -1px rgba(0, 0, 0, 0.3)' : '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    shadowLg: isDark ? '0 10px 15px -3px rgba(0, 0, 0, 0.4)' : '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  };
};

export const getThemeStyles = (isDark: boolean) => {
  const colors = getThemeColors(isDark);
  
  return {
    // Estilos de componentes
    button: {
      primary: {
        backgroundColor: colors.primary,
        color: '#FFFFFF',
        border: `1px solid ${colors.primary}`,
        '&:hover': {
          backgroundColor: colors.hoverPrimary,
          borderColor: colors.hoverPrimary,
        },
      },
      secondary: {
        backgroundColor: 'transparent',
        color: colors.primary,
        border: `1px solid ${colors.primary}`,
        '&:hover': {
          backgroundColor: colors.hover,
        },
      },
      danger: {
        backgroundColor: colors.error,
        color: '#FFFFFF',
        border: `1px solid ${colors.error}`,
        '&:hover': {
          backgroundColor: '#B91C1C',
          borderColor: '#B91C1C',
        },
      },
    },
    
    card: {
      backgroundColor: colors.card,
      border: `1px solid ${colors.border}`,
      borderRadius: '8px',
      boxShadow: colors.shadow,
    },
    
    input: {
      backgroundColor: colors.surface,
      border: `1px solid ${colors.border}`,
      color: colors.text,
      '&:focus': {
        borderColor: colors.primary,
        boxShadow: `0 0 0 3px ${colors.primary}20`,
      },
    },
    
    table: {
      backgroundColor: colors.surface,
      border: `1px solid ${colors.border}`,
      '& th': {
        backgroundColor: colors.hover,
        color: colors.text,
        borderBottom: `1px solid ${colors.border}`,
      },
      '& td': {
        color: colors.text,
        borderBottom: `1px solid ${colors.borderLight}`,
      },
      '& tr:hover': {
        backgroundColor: colors.hover,
      },
    },
  };
}; 