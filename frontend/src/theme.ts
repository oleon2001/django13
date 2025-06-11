import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        primary: {
            light: '#ff4d4d',
            main: '#e01a22',
            dark: '#c0151c',
            contrastText: '#fff',
        },
        secondary: {
            light: '#ff5c8d',
            main: '#dc004e',
            dark: '#a00037',
            contrastText: '#fff',
        },
        error: {
            main: '#f44336',
        },
        warning: {
            main: '#ff9800',
        },
        info: {
            main: '#2196f3',
        },
        success: {
            main: '#4caf50',
        },
        background: {
            default: '#f5f5f5',
            paper: '#ffffff',
        },
    },
    typography: {
        fontFamily: [
            '-apple-system',
            'BlinkMacSystemFont',
            '"Segoe UI"',
            'Roboto',
            '"Helvetica Neue"',
            'Arial',
            'sans-serif',
        ].join(','),
        h1: { fontSize: '2.5rem', fontWeight: 500, },
        h2: { fontSize: '2rem', fontWeight: 500, },
        h3: { fontSize: '1.75rem', fontWeight: 500, },
        h4: { fontSize: '1.5rem', fontWeight: 500, },
        body1: { fontSize: '1rem', },
        body2: { fontSize: '0.875rem', },
    },
    spacing: 8,
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    borderRadius: '4px',
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    boxShadow: 'none',
                },
            },
        },
        MuiDrawer: {
            styleOverrides: {
                paper: {
                    boxShadow: '2px 0px 5px rgba(0,0,0,0.1)',
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    borderRadius: '8px',
                    boxShadow: '0px 2px 4px rgba(0,0,0,0.05)',
                },
            },
        },
        MuiTextField: {
            defaultProps: {
                variant: 'outlined',
                size: 'small',
            },
        },
        MuiTab: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                },
            },
        },
        MuiListItemButton: {
            styleOverrides: {
                root: {
                    borderRadius: '4px',
                    margin: '4px 0',
                }
            }
        }
    },
});

export default theme; 