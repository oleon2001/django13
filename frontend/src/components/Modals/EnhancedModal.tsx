import React, { memo, useCallback, useEffect, useMemo } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  IconButton,
  Button,
  Typography,
  Box,
  Slide,
  Fade,
  Grow,
  Zoom,
  useTheme,
  useMediaQuery,
  alpha,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { TransitionProps } from '@mui/material/transitions';
import {
  Close as CloseIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as SuccessIcon,
  Help as QuestionIcon,
} from '@mui/icons-material';

// Enhanced Dialog Container
const StyledDialog = styled(Dialog, {
  shouldForwardProp: (prop) => !['modalVariant'].includes(prop as string),
})<{ modalVariant?: 'default' | 'fullscreen' | 'drawer' | 'centered' }>(
  ({ theme, modalVariant = 'default' }) => ({
    '& .MuiDialog-paper': {
      borderRadius: modalVariant === 'fullscreen' ? 0 : theme.spacing(2),
      boxShadow: `0 24px 48px ${alpha(theme.palette.common.black, 0.15)}`,
      backdropFilter: 'blur(20px)',
      background: `linear-gradient(145deg, ${alpha(theme.palette.background.paper, 0.95)} 0%, ${alpha(theme.palette.background.paper, 0.9)} 100%)`,
      border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
      
      ...(modalVariant === 'drawer' && {
        position: 'fixed',
        right: 0,
        top: 0,
        height: '100vh',
        maxHeight: '100vh',
        borderRadius: `${theme.spacing(2)} 0 0 ${theme.spacing(2)}`,
        margin: 0,
      }),
      
      ...(modalVariant === 'centered' && {
        minWidth: 400,
        maxWidth: 600,
      }),
    },
    
    '& .MuiBackdrop-root': {
      backgroundColor: alpha(theme.palette.common.black, 0.6),
      backdropFilter: 'blur(8px)',
    },
  })
);

// Enhanced Dialog Title
const StyledDialogTitle = styled(DialogTitle, {
  shouldForwardProp: (prop) => !['severity'].includes(prop as string),
})<{ severity?: 'success' | 'warning' | 'error' | 'info' | 'question' }>(
  ({ theme, severity }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(2),
    padding: theme.spacing(3),
    borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    background: severity && severity !== 'question'
      ? `linear-gradient(135deg, ${alpha(theme.palette[severity].main, 0.08)} 0%, ${alpha(theme.palette[severity].main, 0.04)} 100%)`
      : 'transparent',
    
    '& .MuiTypography-root': {
      fontWeight: 700,
      fontSize: '1.25rem',
      color: severity && severity !== 'question' 
        ? theme.palette[severity].main 
        : severity === 'question' 
        ? theme.palette.primary.main 
        : theme.palette.text.primary,
      flex: 1,
    },
  })
);

// Enhanced Dialog Content
const StyledDialogContent = styled(DialogContent)(({ theme }) => ({
  padding: theme.spacing(3),
  
  '&.MuiDialogContent-dividers': {
    borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  },
}));

// Enhanced Dialog Actions
const StyledDialogActions = styled(DialogActions)(({ theme }) => ({
  padding: theme.spacing(2, 3, 3),
  gap: theme.spacing(1),
  
  '& .MuiButton-root': {
    borderRadius: theme.spacing(1),
    fontWeight: 600,
    textTransform: 'none',
    minHeight: 40,
    paddingX: theme.spacing(3),
  },
}));

// Icon Container
const IconContainer = styled(Box, {
  shouldForwardProp: (prop) => !['severity'].includes(prop as string),
})<{ severity?: 'success' | 'warning' | 'error' | 'info' | 'question' }>(
  ({ theme, severity }) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: 48,
    height: 48,
    borderRadius: '50%',
    backgroundColor: severity ? alpha(theme.palette[severity === 'question' ? 'primary' : severity].main, 0.1) : 'transparent',
    
    '& .MuiSvgIcon-root': {
      fontSize: '2rem',
      color: severity 
        ? theme.palette[severity === 'question' ? 'primary' : severity].main 
        : theme.palette.text.secondary,
    },
  })
);

// Close Button
const CloseButton = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  right: theme.spacing(1),
  top: theme.spacing(1),
  color: theme.palette.text.secondary,
  
  '&:hover': {
    backgroundColor: alpha(theme.palette.text.secondary, 0.1),
  },
}));

// Transition Components
const SlideUpTransition = React.forwardRef<unknown, TransitionProps & { children: React.ReactElement }>(
  (props, ref) => <Slide direction="up" ref={ref} {...props} />
);
SlideUpTransition.displayName = 'SlideUpTransition';

const SlideDownTransition = React.forwardRef<unknown, TransitionProps & { children: React.ReactElement }>(
  (props, ref) => <Slide direction="down" ref={ref} {...props} />
);
SlideDownTransition.displayName = 'SlideDownTransition';

const SlideRightTransition = React.forwardRef<unknown, TransitionProps & { children: React.ReactElement }>(
  (props, ref) => <Slide direction="left" ref={ref} {...props} />
);
SlideRightTransition.displayName = 'SlideRightTransition';

// Modal Types
export type ModalVariant = 'default' | 'fullscreen' | 'drawer' | 'centered';
export type ModalTransition = 'fade' | 'slide-up' | 'slide-down' | 'slide-right' | 'grow' | 'zoom';
export type ModalSeverity = 'success' | 'warning' | 'error' | 'info' | 'question';

// Action Button Interface
export interface ModalAction {
  label: string;
  onClick: () => void | Promise<void>;
  variant?: 'text' | 'outlined' | 'contained';
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  disabled?: boolean;
  loading?: boolean;
  autoFocus?: boolean;
}

// Enhanced Modal Props
export interface EnhancedModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children?: React.ReactNode;
  content?: string;
  severity?: ModalSeverity;
  variant?: ModalVariant;
  transition?: ModalTransition;
  actions?: ModalAction[];
  showCloseButton?: boolean;
  closeOnBackdropClick?: boolean;
  closeOnEscapeKey?: boolean;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
  fullWidth?: boolean;
  dividers?: boolean;
  className?: string;
  sx?: object;
}

// Severity Icons Mapping
const severityIcons = {
  success: SuccessIcon,
  warning: WarningIcon,
  error: ErrorIcon,
  info: InfoIcon,
  question: QuestionIcon,
};

// Transition Components Mapping
const transitionComponents = {
  fade: Fade,
  'slide-up': SlideUpTransition,
  'slide-down': SlideDownTransition,
  'slide-right': SlideRightTransition,
  grow: Grow,
  zoom: Zoom,
};

// Enhanced Modal Component
const EnhancedModal = memo<EnhancedModalProps>(({
  open,
  onClose,
  title,
  children,
  content,
  severity,
  variant = 'default',
  transition = 'fade',
  actions = [],
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEscapeKey = true,
  maxWidth = 'sm',
  fullWidth = false,
  dividers = false,
  className,
  sx,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Auto-adjust variant for mobile
  const effectiveVariant = useMemo(() => {
    if (isMobile && variant === 'default') {
      return 'fullscreen';
    }
    return variant;
  }, [variant, isMobile]);
  
  // Handle close with custom logic
  const handleClose = useCallback((_: {}, reason: 'backdropClick' | 'escapeKeyDown') => {
    if (reason === 'backdropClick' && !closeOnBackdropClick) return;
    if (reason === 'escapeKeyDown' && !closeOnEscapeKey) return;
    onClose();
  }, [onClose, closeOnBackdropClick, closeOnEscapeKey]);
  
  // Handle action click with loading state
  const handleActionClick = useCallback(async (action: ModalAction) => {
    if (action.disabled || action.loading) return;
    
    try {
      await action.onClick();
    } catch (error) {
      console.error('Modal action error:', error);
    }
  }, []);
  
  // Get transition component
  const TransitionComponent = transitionComponents[transition];
  
  // Get severity icon
  const SeverityIcon = severity ? severityIcons[severity] : null;
  
  // Handle keyboard navigation
  useEffect(() => {
    if (!open) return;
    
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        // Handle tab navigation within modal
        const focusableElements = document.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
        
        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open]);
  
  return (
    <StyledDialog
      open={open}
      onClose={handleClose}
      modalVariant={effectiveVariant}
      maxWidth={effectiveVariant === 'fullscreen' ? false : maxWidth}
      fullWidth={fullWidth}
      fullScreen={effectiveVariant === 'fullscreen'}
      TransitionComponent={TransitionComponent}
      className={className}
      sx={sx}
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
      keepMounted={false}
    >
      {/* Title */}
      {title && (
        <StyledDialogTitle
          id="modal-title"
          severity={severity}
        >
          {SeverityIcon && (
            <IconContainer severity={severity}>
              <SeverityIcon />
            </IconContainer>
          )}
          
          <Typography variant="h6" component="h2">
            {title}
          </Typography>
          
          {showCloseButton && (
            <CloseButton onClick={onClose} size="small">
              <CloseIcon />
            </CloseButton>
          )}
        </StyledDialogTitle>
      )}
      
      {/* Content */}
      {(children || content) && (
        <StyledDialogContent dividers={dividers} id="modal-description">
          {content && (
            <DialogContentText
              sx={{
                color: theme.palette.text.primary,
                fontSize: '1rem',
                lineHeight: 1.6,
              }}
            >
              {content}
            </DialogContentText>
          )}
          {children}
        </StyledDialogContent>
      )}
      
      {/* Actions */}
      {actions.length > 0 && (
        <StyledDialogActions>
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant || 'text'}
              color={action.color || 'primary'}
              disabled={action.disabled || action.loading}
              autoFocus={action.autoFocus}
              onClick={() => handleActionClick(action)}
              sx={{
                ...(action.loading && {
                  '&.Mui-disabled': {
                    color: theme.palette.text.secondary,
                  },
                }),
              }}
            >
              {action.loading ? 'Cargando...' : action.label}
            </Button>
          ))}
        </StyledDialogActions>
      )}
    </StyledDialog>
  );
});

EnhancedModal.displayName = 'EnhancedModal';

// Specialized Modal Components
export const ConfirmationModal = memo<{
  open: boolean;
  onClose: () => void;
  onConfirm: () => void | Promise<void>;
  title?: string;
  message?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  severity?: ModalSeverity;
  loading?: boolean;
}>(({
  open,
  onClose,
  onConfirm,
  title = 'Confirmar acción',
  message = '¿Estás seguro de que deseas continuar?',
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  severity = 'question',
  loading = false,
}) => (
  <EnhancedModal
    open={open}
    onClose={onClose}
    title={title}
    content={message}
    severity={severity}
    actions={[
      {
        label: cancelLabel,
        onClick: onClose,
        variant: 'outlined',
      },
      {
        label: confirmLabel,
        onClick: onConfirm,
        variant: 'contained',
        color: severity === 'error' ? 'error' : 'primary',
        loading,
        autoFocus: true,
      },
    ]}
  />
));

ConfirmationModal.displayName = 'ConfirmationModal';

export const AlertModal = memo<{
  open: boolean;
  onClose: () => void;
  title?: string;
  message: string;
  severity?: ModalSeverity;
  buttonLabel?: string;
}>(({
  open,
  onClose,
  title,
  message,
  severity = 'info',
  buttonLabel = 'Entendido',
}) => (
  <EnhancedModal
    open={open}
    onClose={onClose}
    title={title}
    content={message}
    severity={severity}
    actions={[
      {
        label: buttonLabel,
        onClick: onClose,
        variant: 'contained',
        autoFocus: true,
      },
    ]}
  />
));

AlertModal.displayName = 'AlertModal';

export const FormModal = memo<{
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  onSubmit?: () => void | Promise<void>;
  submitLabel?: string;
  cancelLabel?: string;
  loading?: boolean;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
}>(({
  open,
  onClose,
  title,
  children,
  onSubmit,
  submitLabel = 'Guardar',
  cancelLabel = 'Cancelar',
  loading = false,
  maxWidth = 'md',
}) => (
  <EnhancedModal
    open={open}
    onClose={onClose}
    title={title}
    maxWidth={maxWidth}
    fullWidth
    dividers
    actions={[
      {
        label: cancelLabel,
        onClick: onClose,
        variant: 'outlined',
      },
      ...(onSubmit ? [{
        label: submitLabel,
        onClick: onSubmit,
        variant: 'contained' as const,
        loading,
        autoFocus: true,
      }] : []),
    ]}
  >
    {children}
  </EnhancedModal>
));

FormModal.displayName = 'FormModal';

export default EnhancedModal; 