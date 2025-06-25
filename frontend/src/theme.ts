import { createTheme, ThemeOptions } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';

// Design Tokens - Centralized design system
const designTokens = {
  // Color Palette - Enhanced Arsenal-inspired colors
  colors: {
    primary: {
      50: '#ffebee',
      100: '#ffcdd2',
      200: '#ef9a9a',
      300: '#e57373',
      400: '#ef5350',
      500: '#e01a22', // Arsenal Red - Main
      600: '#d32f2f',
      700: '#c62828',
      800: '#b71c1c',
      900: '#8d0000',
    },
    secondary: {
      50: '#fce4ec',
      100: '#f8bbd9',
      200: '#f48fb1',
      300: '#f06292',
      400: '#ec407a',
      500: '#dc004e', // Deep Pink
      600: '#c2185b',
      700: '#ad1457',
      800: '#880e4f',
      900: '#560027',
    },
    neutral: {
      0: '#ffffff',
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#eeeeee',
      300: '#e0e0e0',
      400: '#bdbdbd',
      500: '#9e9e9e',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
      950: '#0a0a0a',
    },
    success: {
      50: '#e8f5e8',
      100: '#c8e6c9',
      200: '#a5d6a7',
      300: '#81c784',
      400: '#66bb6a',
      500: '#4caf50',
      600: '#43a047',
      700: '#388e3c',
      800: '#2e7d32',
      900: '#1b5e20',
    },
    warning: {
      50: '#fff8e1',
      100: '#ffecb3',
      200: '#ffe082',
      300: '#ffd54f',
      400: '#ffca28',
      500: '#ffc107',
      600: '#ffb300',
      700: '#ffa000',
      800: '#ff8f00',
      900: '#ff6f00',
    },
    error: {
      50: '#ffebee',
      100: '#ffcdd2',
      200: '#ef9a9a',
      300: '#e57373',
      400: '#ef5350',
      500: '#f44336',
      600: '#e53935',
      700: '#d32f2f',
      800: '#c62828',
      900: '#b71c1c',
    },
    info: {
      50: '#e3f2fd',
      100: '#bbdefb',
      200: '#90caf9',
      300: '#64b5f6',
      400: '#42a5f5',
      500: '#2196f3',
      600: '#1e88e5',
      700: '#1976d2',
      800: '#1565c0',
      900: '#0d47a1',
    },
  },
  
  // Typography Scale
  typography: {
    fontFamily: {
      primary: [
        'Inter',
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Helvetica Neue"',
        'Arial',
        'sans-serif',
      ].join(','),
      mono: [
        'SF Mono',
        'Monaco',
        'Inconsolata',
        '"Roboto Mono"',
        'Consolas',
        '"Courier New"',
        'monospace',
      ].join(','),
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
      '5xl': '3rem',    // 48px
      '6xl': '3.75rem', // 60px
    },
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
    lineHeight: {
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2,
    },
  },
  
  // Spacing Scale (8px base)
  spacing: {
    0: '0',
    1: '0.25rem',  // 4px
    2: '0.5rem',   // 8px
    3: '0.75rem',  // 12px
    4: '1rem',     // 16px
    5: '1.25rem',  // 20px
    6: '1.5rem',   // 24px
    8: '2rem',     // 32px
    10: '2.5rem',  // 40px
    12: '3rem',    // 48px
    16: '4rem',    // 64px
    20: '5rem',    // 80px
    24: '6rem',    // 96px
  },
  
  // Border Radius
  borderRadius: {
    none: '0',
    sm: '0.125rem',   // 2px
    base: '0.25rem',  // 4px
    md: '0.375rem',   // 6px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    '3xl': '1.5rem',  // 24px
    full: '9999px',
  },
  
  // Shadows
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  },
  
  // Z-Index Scale
  zIndex: {
    hide: -1,
    auto: 'auto',
    base: 0,
    docked: 10,
    dropdown: 1000,
    sticky: 1100,
    banner: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    skipLink: 1600,
    toast: 1700,
    tooltip: 1800,
  },
};

// Enhanced Theme Configuration
const themeOptions: ThemeOptions = {
  palette: {
    mode: 'light',
    primary: {
      light: designTokens.colors.primary[400],
      main: designTokens.colors.primary[500],
      dark: designTokens.colors.primary[700],
      contrastText: designTokens.colors.neutral[0],
    },
    secondary: {
      light: designTokens.colors.secondary[400],
      main: designTokens.colors.secondary[500],
      dark: designTokens.colors.secondary[700],
      contrastText: designTokens.colors.neutral[0],
    },
    error: {
      light: designTokens.colors.error[400],
      main: designTokens.colors.error[500],
      dark: designTokens.colors.error[700],
      contrastText: designTokens.colors.neutral[0],
    },
    warning: {
      light: designTokens.colors.warning[400],
      main: designTokens.colors.warning[500],
      dark: designTokens.colors.warning[700],
      contrastText: designTokens.colors.neutral[900],
    },
    info: {
      light: designTokens.colors.info[400],
      main: designTokens.colors.info[500],
      dark: designTokens.colors.info[700],
      contrastText: designTokens.colors.neutral[0],
    },
    success: {
      light: designTokens.colors.success[400],
      main: designTokens.colors.success[500],
      dark: designTokens.colors.success[700],
      contrastText: designTokens.colors.neutral[0],
    },
    grey: {
      50: designTokens.colors.neutral[50],
      100: designTokens.colors.neutral[100],
      200: designTokens.colors.neutral[200],
      300: designTokens.colors.neutral[300],
      400: designTokens.colors.neutral[400],
      500: designTokens.colors.neutral[500],
      600: designTokens.colors.neutral[600],
      700: designTokens.colors.neutral[700],
      800: designTokens.colors.neutral[800],
      900: designTokens.colors.neutral[900],
    },
    background: {
      default: designTokens.colors.neutral[50],
      paper: designTokens.colors.neutral[0],
    },
    text: {
      primary: designTokens.colors.neutral[900],
      secondary: designTokens.colors.neutral[600],
      disabled: designTokens.colors.neutral[400],
    },
    divider: alpha(designTokens.colors.neutral[900], 0.12),
  },
  
  typography: {
    fontFamily: designTokens.typography.fontFamily.primary,
    fontSize: 16,
    fontWeightLight: designTokens.typography.fontWeight.light,
    fontWeightRegular: designTokens.typography.fontWeight.normal,
    fontWeightMedium: designTokens.typography.fontWeight.medium,
    fontWeightBold: designTokens.typography.fontWeight.bold,
    
    h1: {
      fontSize: designTokens.typography.fontSize['5xl'],
      fontWeight: designTokens.typography.fontWeight.bold,
      lineHeight: designTokens.typography.lineHeight.tight,
      letterSpacing: '-0.025em',
    },
    h2: {
      fontSize: designTokens.typography.fontSize['4xl'],
      fontWeight: designTokens.typography.fontWeight.bold,
      lineHeight: designTokens.typography.lineHeight.tight,
      letterSpacing: '-0.025em',
    },
    h3: {
      fontSize: designTokens.typography.fontSize['3xl'],
      fontWeight: designTokens.typography.fontWeight.semibold,
      lineHeight: designTokens.typography.lineHeight.snug,
    },
    h4: {
      fontSize: designTokens.typography.fontSize['2xl'],
      fontWeight: designTokens.typography.fontWeight.semibold,
      lineHeight: designTokens.typography.lineHeight.snug,
    },
    h5: {
      fontSize: designTokens.typography.fontSize.xl,
      fontWeight: designTokens.typography.fontWeight.semibold,
      lineHeight: designTokens.typography.lineHeight.snug,
    },
    h6: {
      fontSize: designTokens.typography.fontSize.lg,
      fontWeight: designTokens.typography.fontWeight.semibold,
      lineHeight: designTokens.typography.lineHeight.snug,
    },
    subtitle1: {
      fontSize: designTokens.typography.fontSize.base,
      fontWeight: designTokens.typography.fontWeight.medium,
      lineHeight: designTokens.typography.lineHeight.normal,
    },
    subtitle2: {
      fontSize: designTokens.typography.fontSize.sm,
      fontWeight: designTokens.typography.fontWeight.medium,
      lineHeight: designTokens.typography.lineHeight.normal,
    },
    body1: {
      fontSize: designTokens.typography.fontSize.base,
      fontWeight: designTokens.typography.fontWeight.normal,
      lineHeight: designTokens.typography.lineHeight.relaxed,
    },
    body2: {
      fontSize: designTokens.typography.fontSize.sm,
      fontWeight: designTokens.typography.fontWeight.normal,
      lineHeight: designTokens.typography.lineHeight.normal,
    },
    button: {
      fontSize: designTokens.typography.fontSize.sm,
      fontWeight: designTokens.typography.fontWeight.medium,
      textTransform: 'none',
      letterSpacing: '0.025em',
    },
    caption: {
      fontSize: designTokens.typography.fontSize.xs,
      fontWeight: designTokens.typography.fontWeight.normal,
      lineHeight: designTokens.typography.lineHeight.normal,
    },
    overline: {
      fontSize: designTokens.typography.fontSize.xs,
      fontWeight: designTokens.typography.fontWeight.medium,
      textTransform: 'uppercase',
      letterSpacing: '0.1em',
    },
  },
  
  spacing: 8, // Base spacing unit
  
  shape: {
    borderRadius: 8, // Default border radius
  },
  
  breakpoints: {
    values: {
      xs: 0,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
    },
  },
  
  shadows: [
    'none',
    designTokens.shadows.sm,
    designTokens.shadows.base,
    designTokens.shadows.md,
    designTokens.shadows.lg,
    designTokens.shadows.xl,
    designTokens.shadows['2xl'],
    '0 32px 64px -12px rgba(0, 0, 0, 0.25)',
    '0 48px 96px -12px rgba(0, 0, 0, 0.25)',
    '0 64px 128px -12px rgba(0, 0, 0, 0.25)',
    '0 80px 160px -12px rgba(0, 0, 0, 0.25)',
    '0 96px 192px -12px rgba(0, 0, 0, 0.25)',
    '0 112px 224px -12px rgba(0, 0, 0, 0.25)',
    '0 128px 256px -12px rgba(0, 0, 0, 0.25)',
    '0 144px 288px -12px rgba(0, 0, 0, 0.25)',
    '0 160px 320px -12px rgba(0, 0, 0, 0.25)',
    '0 176px 352px -12px rgba(0, 0, 0, 0.25)',
    '0 192px 384px -12px rgba(0, 0, 0, 0.25)',
    '0 208px 416px -12px rgba(0, 0, 0, 0.25)',
    '0 224px 448px -12px rgba(0, 0, 0, 0.25)',
    '0 240px 480px -12px rgba(0, 0, 0, 0.25)',
    '0 256px 512px -12px rgba(0, 0, 0, 0.25)',
    '0 272px 544px -12px rgba(0, 0, 0, 0.25)',
    '0 288px 576px -12px rgba(0, 0, 0, 0.25)',
    '0 304px 608px -12px rgba(0, 0, 0, 0.25)',
  ],
  
  components: {
    // Enhanced Button Component
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: designTokens.typography.fontWeight.medium,
          borderRadius: designTokens.borderRadius.lg,
          padding: '10px 20px',
          fontSize: designTokens.typography.fontSize.sm,
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: designTokens.shadows.md,
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          boxShadow: designTokens.shadows.sm,
          '&:hover': {
            boxShadow: designTokens.shadows.lg,
          },
        },
        outlined: {
          borderWidth: '1.5px',
          '&:hover': {
            borderWidth: '1.5px',
          },
        },
        sizeSmall: {
          padding: '6px 16px',
          fontSize: designTokens.typography.fontSize.xs,
        },
        sizeLarge: {
          padding: '12px 24px',
          fontSize: designTokens.typography.fontSize.base,
        },
      },
    },
    
    // Enhanced Card Component
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: designTokens.borderRadius.xl,
          boxShadow: designTokens.shadows.base,
          border: `1px solid ${alpha(designTokens.colors.neutral[900], 0.08)}`,
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: designTokens.shadows.lg,
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    
    // Enhanced AppBar
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          borderBottom: `1px solid ${alpha(designTokens.colors.neutral[900], 0.08)}`,
          backgroundColor: alpha(designTokens.colors.neutral[0], 0.8),
          backdropFilter: 'blur(20px)',
          color: designTokens.colors.neutral[900],
        },
      },
    },
    
    // Enhanced Drawer
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: `1px solid ${alpha(designTokens.colors.neutral[900], 0.08)}`,
          boxShadow: 'none',
          backgroundColor: designTokens.colors.neutral[0],
        },
      },
    },
    
    // Enhanced TextField
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        size: 'small',
      },
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: designTokens.borderRadius.lg,
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: designTokens.colors.primary[300],
              },
            },
            '&.Mui-focused': {
              '& .MuiOutlinedInput-notchedOutline': {
                borderWidth: '2px',
                borderColor: designTokens.colors.primary[500],
              },
            },
          },
        },
      },
    },
    
    // Enhanced Chip
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: designTokens.borderRadius.full,
          fontWeight: designTokens.typography.fontWeight.medium,
          fontSize: designTokens.typography.fontSize.xs,
        },
        filled: {
          '&.MuiChip-colorPrimary': {
            backgroundColor: alpha(designTokens.colors.primary[500], 0.1),
            color: designTokens.colors.primary[700],
          },
          '&.MuiChip-colorSecondary': {
            backgroundColor: alpha(designTokens.colors.secondary[500], 0.1),
            color: designTokens.colors.secondary[700],
          },
        },
      },
    },
    
    // Enhanced List Items
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: designTokens.borderRadius.lg,
          margin: '2px 8px',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            backgroundColor: alpha(designTokens.colors.primary[500], 0.08),
            transform: 'translateX(4px)',
          },
          '&.Mui-selected': {
            backgroundColor: alpha(designTokens.colors.primary[500], 0.12),
            '&:hover': {
              backgroundColor: alpha(designTokens.colors.primary[500], 0.16),
            },
          },
        },
      },
    },
    
    // Enhanced Paper
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: designTokens.borderRadius.xl,
          border: `1px solid ${alpha(designTokens.colors.neutral[900], 0.08)}`,
        },
        elevation1: {
          boxShadow: designTokens.shadows.sm,
        },
        elevation2: {
          boxShadow: designTokens.shadows.base,
        },
        elevation3: {
          boxShadow: designTokens.shadows.md,
        },
        elevation4: {
          boxShadow: designTokens.shadows.lg,
        },
      },
    },
    
    // Enhanced Tab
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: designTokens.typography.fontWeight.medium,
          fontSize: designTokens.typography.fontSize.sm,
          minHeight: 48,
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            color: designTokens.colors.primary[600],
          },
        },
      },
    },
    
    // Enhanced Alert
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: designTokens.borderRadius.lg,
          border: 'none',
        },
        standardSuccess: {
          backgroundColor: alpha(designTokens.colors.success[500], 0.1),
          color: designTokens.colors.success[800],
        },
        standardError: {
          backgroundColor: alpha(designTokens.colors.error[500], 0.1),
          color: designTokens.colors.error[800],
        },
        standardWarning: {
          backgroundColor: alpha(designTokens.colors.warning[500], 0.1),
          color: designTokens.colors.warning[800],
        },
        standardInfo: {
          backgroundColor: alpha(designTokens.colors.info[500], 0.1),
          color: designTokens.colors.info[800],
        },
      },
    },
    
    // Enhanced Tooltip
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: designTokens.colors.neutral[800],
          fontSize: designTokens.typography.fontSize.xs,
          borderRadius: designTokens.borderRadius.md,
          padding: '8px 12px',
        },
        arrow: {
          color: designTokens.colors.neutral[800],
        },
      },
    },
    
    // Enhanced LinearProgress
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          height: 6,
          borderRadius: designTokens.borderRadius.full,
          backgroundColor: alpha(designTokens.colors.neutral[900], 0.08),
        },
        bar: {
          borderRadius: designTokens.borderRadius.full,
        },
      },
    },
  },
};

// Create the theme
const theme = createTheme(themeOptions);

// Export design tokens for use in components
export { designTokens };
export default theme; 