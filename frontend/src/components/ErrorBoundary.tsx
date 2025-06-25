import { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Alert } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { ERROR_MESSAGES } from '../utils/reactConfig';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  isSuspenseError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  private retryTimeoutId: NodeJS.Timeout | null = null;

  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    isSuspenseError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Detectar si es un error de suspensión
    const isSuspenseError = Boolean(
      error.message.includes('suspended while responding to synchronous input') ||
      error.message.includes('startTransition') ||
      error.stack?.includes('throwException')
    );

    return {
      hasError: true,
      error,
      errorInfo: null,
      isSuspenseError,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error capturado por ErrorBoundary:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Si es un error de suspensión, intentar recuperación automática
    if (this.state.isSuspenseError) {
      this.scheduleRetry();
    }
  }

  private scheduleRetry = () => {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
    }

    this.retryTimeoutId = setTimeout(() => {
      this.handleRetry();
    }, 2000); // Retry after 2 seconds
  };

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      isSuspenseError: false,
    });
  };

  private handleReload = () => {
    window.location.reload();
  };

  public componentWillUnmount() {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
    }
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3,
            bgcolor: 'background.default',
          }}
        >
          <Alert 
            severity={this.state.isSuspenseError ? "warning" : "error"} 
            sx={{ mb: 3, maxWidth: 600 }}
          >
            <Typography variant="h6" gutterBottom>
              {this.state.isSuspenseError ? 'Error de Carga' : 'Error de Aplicación'}
            </Typography>
            <Typography variant="body2">
              {this.state.isSuspenseError 
                ? ERROR_MESSAGES.SUSPENSE_ERROR
                : ERROR_MESSAGES.GENERIC_ERROR
              }
            </Typography>
          </Alert>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={this.handleRetry}
              sx={{ minWidth: 120 }}
            >
              Reintentar
            </Button>
            <Button
              variant="outlined"
              onClick={this.handleReload}
              sx={{ minWidth: 120 }}
            >
              Recargar Página
            </Button>
          </Box>

          {process.env.NODE_ENV === 'development' && this.state.error && (
            <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.100', borderRadius: 1, maxWidth: 800, overflow: 'auto' }}>
              <Typography variant="subtitle2" gutterBottom>
                Detalles del Error (Solo en Desarrollo):
              </Typography>
              <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', whiteSpace: 'pre-wrap' }}>
                {this.state.error.toString()}
                {this.state.errorInfo?.componentStack}
              </Typography>
            </Box>
          )}
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 