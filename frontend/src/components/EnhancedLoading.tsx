import React from 'react';
import { Box, Typography, LinearProgress, Fade, Zoom, keyframes } from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Dashboard as DashboardIcon,
  MonitorHeart as MonitorIcon,
  GpsFixed as GpsIcon,
  DirectionsCar as VehicleIcon,
  Person as DriverIcon,
  LocalParking as ParkingIcon,
  Sensors as SensorIcon,
  Assessment as ReportIcon,
  Settings as SettingsIcon,
  DevicesOther as DeviceIcon,
  Route as RouteIcon,
  Timeline as TrackingIcon,
} from '@mui/icons-material';

// Animaciones personalizadas
const pulse = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;

const float = keyframes`
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
`;

const shimmer = keyframes`
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
`;

const rotate = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

// Componentes estilizados
const LoadingContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '60vh',
  padding: theme.spacing(4),
  background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
}));

const IconContainer = styled(Box)(({ theme }) => ({
  position: 'relative',
  marginBottom: theme.spacing(3),
  '& .main-icon': {
    fontSize: '4rem',
    color: theme.palette.primary.main,
    animation: `${pulse} 2s ease-in-out infinite`,
  },
  '& .orbit-icon': {
    position: 'absolute',
    fontSize: '1.5rem',
    color: theme.palette.primary.light,
    animation: `${rotate} 3s linear infinite`,
  },
}));

const LoadingText = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.primary,
  fontWeight: 500,
  marginBottom: theme.spacing(2),
  animation: `${slideIn} 0.8s ease-out`,
}));

const SubText = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: '0.875rem',
  animation: `${slideIn} 1s ease-out`,
}));

const StyledLinearProgress = styled(LinearProgress)(({ theme }) => ({
  width: '200px',
  height: '4px',
  borderRadius: '2px',
  marginTop: theme.spacing(2),
  backgroundColor: theme.palette.grey[200],
  '& .MuiLinearProgress-bar': {
    backgroundColor: theme.palette.primary.main,
    borderRadius: '2px',
  },
}));

const FloatingDots = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  marginTop: theme.spacing(2),
  '& .dot': {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: theme.palette.primary.main,
    animation: `${float} 1.5s ease-in-out infinite`,
    '&:nth-of-type(2)': {
      animationDelay: '0.2s',
    },
    '&:nth-of-type(3)': {
      animationDelay: '0.4s',
    },
  },
}));

const ShimmerBox = styled(Box)(({ theme }) => ({
  background: `linear-gradient(90deg, 
    ${theme.palette.grey[100]} 0%, 
    ${theme.palette.grey[200]} 50%, 
    ${theme.palette.grey[100]} 100%)`,
  backgroundSize: '200px 100%',
  animation: `${shimmer} 1.5s ease-in-out infinite`,
  borderRadius: theme.shape.borderRadius,
}));

// Mapeo de iconos por módulo
const moduleIcons = {
  dashboard: DashboardIcon,
  monitoring: MonitorIcon,
  gps: GpsIcon,
  vehicles: VehicleIcon,
  drivers: DriverIcon,
  parking: ParkingIcon,
  sensors: SensorIcon,
  reports: ReportIcon,
  settings: SettingsIcon,
  devices: DeviceIcon,
  routes: RouteIcon,
  tracking: TrackingIcon,
};

interface EnhancedLoadingProps {
  module?: keyof typeof moduleIcons;
  message?: string;
  subMessage?: string;
  showProgress?: boolean;
  variant?: 'default' | 'minimal' | 'detailed';
}

const EnhancedLoading: React.FC<EnhancedLoadingProps> = ({
  module = 'dashboard',
  message = 'Cargando...',
  subMessage = 'Por favor espere mientras se carga el contenido',
  showProgress = true,
  variant = 'default'
}) => {
  const IconComponent = moduleIcons[module] || DashboardIcon;

  if (variant === 'minimal') {
    return (
      <Fade in timeout={300}>
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          minHeight="200px"
          gap={2}
        >
          <IconComponent sx={{ 
            fontSize: '2rem', 
            color: 'primary.main',
            animation: `${pulse} 1.5s ease-in-out infinite`
          }} />
          <Typography variant="h6" color="text.secondary">
            {message}
          </Typography>
        </Box>
      </Fade>
    );
  }

  if (variant === 'detailed') {
    return (
      <Fade in timeout={500}>
        <LoadingContainer>
          <Zoom in timeout={600}>
            <IconContainer>
              <IconComponent className="main-icon" />
              <Box
                className="orbit-icon"
                sx={{
                  top: '-10px',
                  right: '-10px',
                  transformOrigin: '20px 35px',
                }}
              >
                <GpsIcon sx={{ fontSize: '1rem' }} />
              </Box>
            </IconContainer>
          </Zoom>

          <LoadingText variant="h5">{message}</LoadingText>
          <SubText>{subMessage}</SubText>

          {showProgress && (
            <Fade in timeout={800}>
              <StyledLinearProgress />
            </Fade>
          )}

          <FloatingDots>
            <Box className="dot" />
            <Box className="dot" />
            <Box className="dot" />
          </FloatingDots>

          {/* Elementos decorativos */}
          <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
            {[1, 2, 3, 4].map((item) => (
              <ShimmerBox
                key={item}
                sx={{
                  width: 40,
                  height: 6,
                  animationDelay: `${item * 0.2}s`,
                }}
              />
            ))}
          </Box>
        </LoadingContainer>
      </Fade>
    );
  }

  // Variant default
  return (
    <Fade in timeout={400}>
      <LoadingContainer>
        <Zoom in timeout={500}>
          <IconContainer>
            <IconComponent className="main-icon" />
          </IconContainer>
        </Zoom>

        <LoadingText variant="h6">{message}</LoadingText>
        
        {showProgress && (
          <Fade in timeout={600}>
            <StyledLinearProgress />
          </Fade>
        )}

        <FloatingDots>
          <Box className="dot" />
          <Box className="dot" />
          <Box className="dot" />
        </FloatingDots>
      </LoadingContainer>
    </Fade>
  );
};

export default EnhancedLoading; 