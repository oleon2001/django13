import React from 'react';
import { 
  Box, 
  Typography, 
  CircularProgress, 
  Fade, 
  Backdrop,
  Dialog,
  DialogContent,
  LinearProgress,
  keyframes 
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Save as SaveIcon,
  CloudUpload as UploadIcon,
  Sync as SyncIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
} from '@mui/icons-material';

// Animaciones personalizadas
const spin = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const bounce = keyframes`
  0%, 20%, 53%, 80%, 100% {
    transform: translate3d(0, 0, 0);
  }
  40%, 43% {
    transform: translate3d(0, -8px, 0);
  }
  70% {
    transform: translate3d(0, -4px, 0);
  }
  90% {
    transform: translate3d(0, -2px, 0);
  }
`;

const fadeInScale = keyframes`
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
`;

// Componentes estilizados
const LoadingContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  minHeight: '200px',
  background: `linear-gradient(135deg, 
    ${theme.palette.background.paper} 0%, 
    ${theme.palette.background.default} 100%)`,
  borderRadius: theme.shape.borderRadius,
}));

const AnimatedIcon = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  '& .spin': {
    animation: `${spin} 1s linear infinite`,
    color: theme.palette.primary.main,
  },
  '& .bounce': {
    animation: `${bounce} 2s infinite`,
    color: theme.palette.success.main,
  },
  '& .fade-scale': {
    animation: `${fadeInScale} 0.5s ease-out`,
    color: theme.palette.primary.main,
  },
}));

const StyledBackdrop = styled(Backdrop)(({ theme }) => ({
  zIndex: theme.zIndex.drawer + 1,
  backgroundColor: 'rgba(0, 0, 0, 0.7)',
  backdropFilter: 'blur(4px)',
}));

const InlineProgress = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  padding: theme.spacing(1, 2),
  backgroundColor: theme.palette.background.paper,
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[1],
}));

// Mapeo de iconos por acción
const actionIcons = {
  save: SaveIcon,
  upload: UploadIcon,
  sync: SyncIcon,
  delete: DeleteIcon,
  edit: EditIcon,
  success: CheckIcon,
  error: ErrorIcon,
};

interface FormLoadingProps {
  open: boolean;
  action?: keyof typeof actionIcons;
  message?: string;
  progress?: number;
  variant?: 'backdrop' | 'dialog' | 'inline' | 'button';
  showProgress?: boolean;
  onClose?: () => void;
  size?: 'small' | 'medium' | 'large';
}

const FormLoading: React.FC<FormLoadingProps> = ({
  open,
  action = 'save',
  message = 'Procesando...',
  progress,
  variant = 'backdrop',
  showProgress = false,
  onClose,
  size = 'medium'
}) => {
  const IconComponent = actionIcons[action] || SaveIcon;
  
  const getIconSize = () => {
    switch (size) {
      case 'small': return '2rem';
      case 'large': return '4rem';
      default: return '3rem';
    }
  };

  const getProgressSize = () => {
    switch (size) {
      case 'small': return 32;
      case 'large': return 64;
      default: return 48;
    }
  };

  const renderLoadingContent = () => (
    <LoadingContainer>
      <AnimatedIcon>
        {action === 'success' ? (
          <IconComponent 
            className="bounce" 
            sx={{ fontSize: getIconSize() }}
          />
        ) : action === 'error' ? (
          <IconComponent 
            className="fade-scale" 
            sx={{ fontSize: getIconSize(), color: 'error.main' }}
          />
        ) : (
          <IconComponent 
            className="spin" 
            sx={{ fontSize: getIconSize() }}
          />
        )}
      </AnimatedIcon>

      <Typography 
        variant={size === 'large' ? 'h5' : 'h6'} 
        color="text.primary" 
        gutterBottom
        sx={{ fontWeight: 500 }}
      >
        {message}
      </Typography>

      {showProgress && typeof progress === 'number' && (
        <Box sx={{ width: '100%', maxWidth: 300, mt: 2 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ 
              height: 6, 
              borderRadius: 3,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                backgroundColor: 'primary.main',
                borderRadius: 3,
              }
            }}
          />
          <Typography 
            variant="body2" 
            color="text.secondary" 
            align="center" 
            sx={{ mt: 1 }}
          >
            {Math.round(progress)}%
          </Typography>
        </Box>
      )}

      {showProgress && typeof progress === 'undefined' && (
        <Box sx={{ mt: 2 }}>
          <CircularProgress 
            size={getProgressSize()} 
            thickness={4}
            sx={{ color: 'primary.main' }}
          />
        </Box>
      )}
    </LoadingContainer>
  );

  if (variant === 'backdrop') {
    return (
      <StyledBackdrop open={open} onClick={onClose}>
        <Fade in={open}>
          <Box>
            {renderLoadingContent()}
          </Box>
        </Fade>
      </StyledBackdrop>
    );
  }

  if (variant === 'dialog') {
    return (
      <Dialog
        open={open}
        onClose={onClose}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: 24,
          }
        }}
      >
        <DialogContent sx={{ p: 0 }}>
          {renderLoadingContent()}
        </DialogContent>
      </Dialog>
    );
  }

  if (variant === 'inline') {
    return (
      <Fade in={open}>
        <InlineProgress>
          <CircularProgress 
            size={24} 
            thickness={4}
            sx={{ color: 'primary.main' }}
          />
          <Typography variant="body2" color="text.primary">
            {message}
          </Typography>
          {showProgress && typeof progress === 'number' && (
            <Typography variant="body2" color="text.secondary">
              {Math.round(progress)}%
            </Typography>
          )}
        </InlineProgress>
      </Fade>
    );
  }

  if (variant === 'button') {
    return (
      <Fade in={open}>
        <Box 
          display="flex" 
          alignItems="center" 
          gap={1}
          sx={{ 
            opacity: open ? 1 : 0,
            transition: 'opacity 0.3s ease'
          }}
        >
          <CircularProgress 
            size={16} 
            thickness={4}
            sx={{ color: 'primary.main' }}
          />
          <Typography variant="body2" color="text.primary">
            {message}
          </Typography>
        </Box>
      </Fade>
    );
  }

  return null;
};

export default FormLoading; 