import React, { memo, useMemo } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Skeleton,
  CircularProgress,
  useTheme,
  alpha,
} from '@mui/material';
import { keyframes, styled } from '@mui/material/styles';
import {
  Dashboard as DashboardIcon,
  LocationOn as LocationOnIcon,
  MonitorHeart as MonitorHeartIcon,
  TrackChanges as TrackChangesIcon,
  DirectionsCar as DirectionsCarIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon,
  Person as PersonIcon,
  LocalParking as LocalParkingIcon,
  Sensors as SensorsIcon,
  Route as RouteIcon,
  Devices as DevicesIcon,
  CloudSync as CloudSyncIcon,
} from '@mui/icons-material';

// Enhanced animations with better performance
const animations = {
  pulse: keyframes`
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
  `,
  
  float: keyframes`
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  `,
  
  shimmer: keyframes`
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  `,
  
  rotate: keyframes`
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  `,
  
  slideIn: keyframes`
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  `,
  
  breathe: keyframes`
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
  `,
  
  wave: keyframes`
    0%, 60%, 100% { transform: initial; }
    30% { transform: translateY(-15px); }
  `,
};

// Optimized styled components with better performance
const LoadingContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '200px',
  padding: theme.spacing(4),
  position: 'relative',
  background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.02)} 0%, ${alpha(theme.palette.primary.main, 0.08)} 100%)`,
  borderRadius: theme.shape.borderRadius * 2,
  backdropFilter: 'blur(10px)',
  border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
  overflow: 'hidden',
  
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: '-100%',
    width: '100%',
    height: '100%',
    background: `linear-gradient(90deg, transparent, ${alpha(theme.palette.primary.main, 0.1)}, transparent)`,
    animation: `${animations.shimmer} 2s infinite`,
  },
}));

const IconContainer = styled(Box)(({ theme }) => ({
  position: 'relative',
  marginBottom: theme.spacing(3),
  animation: `${animations.float} 3s ease-in-out infinite`,
  
  '& .MuiSvgIcon-root': {
    fontSize: '3rem',
    color: theme.palette.primary.main,
    filter: `drop-shadow(0 4px 8px ${alpha(theme.palette.primary.main, 0.3)})`,
  },
}));

const LoadingText = styled(Typography)(({ theme }) => ({
  marginBottom: theme.spacing(1),
  fontWeight: 600,
  color: theme.palette.text.primary,
  textAlign: 'center',
  animation: `${animations.slideIn} 0.6s ease-out`,
}));

const SubText = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  textAlign: 'center',
  marginBottom: theme.spacing(3),
  animation: `${animations.slideIn} 0.8s ease-out`,
}));

const StyledLinearProgress = styled(LinearProgress)(({ theme }) => ({
  width: '100%',
  maxWidth: 300,
  height: 6,
  borderRadius: 3,
  backgroundColor: alpha(theme.palette.primary.main, 0.1),
  
  '& .MuiLinearProgress-bar': {
    borderRadius: 3,
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
  },
}));

const FloatingDots = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  marginTop: theme.spacing(2),
  
  '& .dot': {
    width: 8,
    height: 8,
    borderRadius: '50%',
    backgroundColor: theme.palette.primary.main,
    animation: `${animations.wave} 1.4s ease-in-out infinite`,
    
    '&:nth-of-type(1)': { animationDelay: '0s' },
    '&:nth-of-type(2)': { animationDelay: '0.1s' },
    '&:nth-of-type(3)': { animationDelay: '0.2s' },
  },
}));

const SkeletonContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  maxWidth: 400,
  padding: theme.spacing(2),
  
  '& .MuiSkeleton-root': {
    borderRadius: theme.shape.borderRadius,
    backgroundColor: alpha(theme.palette.primary.main, 0.1),
  },
}));

// Module icons mapping with better organization
const moduleIcons = {
  dashboard: DashboardIcon,
  gps: LocationOnIcon,
  monitoring: MonitorHeartIcon,
  tracking: TrackChangesIcon,
  vehicles: DirectionsCarIcon,
  reports: BarChartIcon,
  settings: SettingsIcon,
  users: PersonIcon,
  parking: LocalParkingIcon,
  sensors: SensorsIcon,
  routes: RouteIcon,
  devices: DevicesIcon,
  sync: CloudSyncIcon,
  default: DashboardIcon,
} as const;

// Enhanced loading variants
export type LoadingVariant = 'default' | 'minimal' | 'skeleton' | 'dots' | 'circular' | 'detailed';
export type ModuleType = keyof typeof moduleIcons;

export interface EnhancedLoadingProps {
  module?: ModuleType;
  message?: string;
  subMessage?: string;
  showProgress?: boolean;
  progress?: number;
  variant?: LoadingVariant;
  size?: 'small' | 'medium' | 'large';
  fullScreen?: boolean;
  className?: string;
}

const EnhancedLoading: React.FC<EnhancedLoadingProps> = memo(({
  module = 'default',
  message = 'Cargando...',
  subMessage = 'Por favor espere mientras procesamos su solicitud',
  showProgress = false,
  progress,
  variant = 'default',
  size = 'medium',
  fullScreen = false,
  className,
}) => {
  const theme = useTheme();
  
  // Memoize icon component for better performance
  const IconComponent = useMemo(() => moduleIcons[module] || moduleIcons.default, [module]);
  
  // Memoize size configurations
  const sizeConfig = useMemo(() => ({
    small: { minHeight: '120px', iconSize: '2rem', padding: 2 },
    medium: { minHeight: '200px', iconSize: '3rem', padding: 4 },
    large: { minHeight: '300px', iconSize: '4rem', padding: 6 },
  }), []);
  
  const currentSize = sizeConfig[size];
  
  // Render different variants
  const renderContent = () => {
    switch (variant) {
      case 'minimal':
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
            <CircularProgress size={24} thickness={4} />
            <Typography variant="body2" color="text.secondary">
              {message}
            </Typography>
          </Box>
        );
        
      case 'skeleton':
        return (
          <SkeletonContainer>
            <Skeleton variant="rectangular" height={60} sx={{ mb: 2 }} />
            <Skeleton variant="text" width="80%" sx={{ mb: 1 }} />
            <Skeleton variant="text" width="60%" sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" height={40} />
          </SkeletonContainer>
        );
        
      case 'dots':
        return (
          <Box sx={{ textAlign: 'center', p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              {message}
            </Typography>
            <FloatingDots>
              <Box className="dot" />
              <Box className="dot" />
              <Box className="dot" />
            </FloatingDots>
          </Box>
        );
        
      case 'circular':
        return (
          <Box sx={{ textAlign: 'center', p: 4 }}>
            <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
              <CircularProgress
                size={60}
                thickness={4}
                variant={progress !== undefined ? 'determinate' : 'indeterminate'}
                value={progress}
                sx={{
                  color: theme.palette.primary.main,
                  '& .MuiCircularProgress-circle': {
                    strokeLinecap: 'round',
                  },
                }}
              />
              {progress !== undefined && (
                <Box
                  sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: 'absolute',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography variant="caption" component="div" color="text.secondary">
                    {`${Math.round(progress)}%`}
                  </Typography>
                </Box>
              )}
            </Box>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              {message}
            </Typography>
            {subMessage && (
              <Typography variant="body2" color="text.secondary">
                {subMessage}
              </Typography>
            )}
          </Box>
        );
        
      case 'detailed':
      default:
        return (
          <>
            <IconContainer>
              <IconComponent sx={{ fontSize: currentSize.iconSize }} />
            </IconContainer>
            
            <LoadingText variant="h6">
              {message}
            </LoadingText>
            
            {subMessage && (
              <SubText variant="body2">
                {subMessage}
              </SubText>
            )}
            
            {showProgress && (
              <Box sx={{ width: '100%', maxWidth: 300, mb: 2 }}>
                <StyledLinearProgress
                  variant={progress !== undefined ? 'determinate' : 'indeterminate'}
                  value={progress}
                />
                {progress !== undefined && (
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', textAlign: 'center' }}>
                    {Math.round(progress)}% completado
                  </Typography>
                )}
              </Box>
            )}
            
            <FloatingDots>
              <Box className="dot" />
              <Box className="dot" />
              <Box className="dot" />
            </FloatingDots>
          </>
        );
    }
  };
  
  const containerProps = {
    className,
    sx: {
      minHeight: currentSize.minHeight,
      padding: currentSize.padding,
      ...(fullScreen && {
        position: 'fixed' as const,
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: theme.zIndex.modal,
        backgroundColor: alpha(theme.palette.background.default, 0.9),
        backdropFilter: 'blur(8px)',
      }),
    },
  };
  
  if (variant === 'minimal' || variant === 'skeleton' || variant === 'dots' || variant === 'circular') {
    return (
      <Box {...containerProps}>
        {renderContent()}
      </Box>
    );
  }
  
  return (
    <LoadingContainer {...containerProps}>
      {renderContent()}
    </LoadingContainer>
  );
});

EnhancedLoading.displayName = 'EnhancedLoading';

export default EnhancedLoading; 