import React, { memo, forwardRef, useMemo } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardActions,
  Typography,
  IconButton,
  Chip,
  Box,
  Skeleton,
  alpha,
  Fade,
  Grow,
  Tooltip,
  Avatar,
} from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import {
  MoreVert as MoreVertIcon,
  Favorite as FavoriteIcon,
  Share as ShareIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon,
} from '@mui/icons-material';

// Enhanced animations
const cardAnimations = {
  hover: keyframes`
    0% { transform: translateY(0) scale(1); }
    100% { transform: translateY(-4px) scale(1.02); }
  `,
  
  pulse: keyframes`
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
  `,
  
  shimmer: keyframes`
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  `,
  
  slideUp: keyframes`
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  `,
};

// Enhanced Card Container
const StyledCard = styled(Card, {
  shouldForwardProp: (prop) => 
    !['cardVariant', 'interactive', 'elevated', 'glowing'].includes(prop as string),
})<{
  cardVariant?: 'default' | 'outlined' | 'elevated' | 'glass';
  interactive?: boolean;
  elevated?: boolean;
  glowing?: boolean;
}>(({ theme, cardVariant = 'default', interactive = false, elevated = false, glowing = false }) => ({
  position: 'relative',
  borderRadius: theme.spacing(2),
  overflow: 'hidden',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  border: cardVariant === 'outlined' ? `1px solid ${theme.palette.divider}` : 'none',
  
  // Base styles by variant
  ...(cardVariant === 'glass' && {
    background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.8)} 0%, ${alpha(theme.palette.background.paper, 0.6)} 100%)`,
    backdropFilter: 'blur(20px)',
    border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
  }),
  
  ...(cardVariant === 'elevated' && {
    boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.12)}`,
  }),
  
  // Interactive states
  ...(interactive && {
    cursor: 'pointer',
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: `0 12px 40px ${alpha(theme.palette.common.black, 0.15)}`,
      
      '& .card-overlay': {
        opacity: 1,
      },
      
      '& .card-actions': {
        transform: 'translateY(0)',
        opacity: 1,
      },
    },
    
    '&:active': {
      transform: 'translateY(-2px)',
    },
  }),
  
  // Elevated state
  ...(elevated && {
    boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.1)}`,
  }),
  
  // Glowing effect
  ...(glowing && {
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, transparent 50%, ${alpha(theme.palette.secondary.main, 0.1)} 100%)`,
      opacity: 0,
      transition: 'opacity 0.3s ease',
      pointerEvents: 'none',
    },
    
    '&:hover::before': {
      opacity: 1,
    },
  }),
}));

// Card Overlay for interactive effects
const CardOverlay = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
  opacity: 0,
  transition: 'opacity 0.3s ease',
  pointerEvents: 'none',
  zIndex: 1,
}));

// Enhanced Card Header
const StyledCardHeader = styled(CardHeader)(({ theme }) => ({
  paddingBottom: theme.spacing(1),
  
  '& .MuiCardHeader-title': {
    fontSize: '1.125rem',
    fontWeight: 600,
    color: theme.palette.text.primary,
  },
  
  '& .MuiCardHeader-subheader': {
    fontSize: '0.875rem',
    color: theme.palette.text.secondary,
    marginTop: theme.spacing(0.5),
  },
  
  '& .MuiCardHeader-avatar': {
    marginRight: theme.spacing(2),
  },
}));

// Enhanced Card Content
const StyledCardContent = styled(CardContent)(({ theme }) => ({
  padding: theme.spacing(2),
  position: 'relative',
  zIndex: 2,
  
  '&:last-child': {
    paddingBottom: theme.spacing(2),
  },
}));

// Floating Card Actions
const FloatingCardActions = styled(CardActions)(({ theme }) => ({
  position: 'absolute',
  bottom: theme.spacing(1),
  right: theme.spacing(1),
  padding: theme.spacing(0.5),
  background: alpha(theme.palette.background.paper, 0.9),
  backdropFilter: 'blur(10px)',
  borderRadius: theme.spacing(1),
  transform: 'translateY(10px)',
  opacity: 0,
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  zIndex: 3,
  
  '& .MuiIconButton-root': {
    padding: theme.spacing(0.5),
    
    '&:hover': {
      backgroundColor: alpha(theme.palette.primary.main, 0.1),
    },
  },
}));

// Status Indicator
const StatusIndicator = styled(Box)<{ status: 'success' | 'warning' | 'error' | 'info' }>(
  ({ theme, status }) => ({
    position: 'absolute',
    top: theme.spacing(1),
    right: theme.spacing(1),
    width: 12,
    height: 12,
    borderRadius: '50%',
    backgroundColor: theme.palette[status].main,
    boxShadow: `0 0 0 2px ${theme.palette.background.paper}`,
    zIndex: 3,
    
    ...(status === 'success' && {
      animation: `${cardAnimations.pulse} 2s ease-in-out infinite`,
    }),
  })
);

// Metric Display Component
const MetricDisplay = memo<{
  value: string | number;
  label: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactNode;
}>(({ value, label, trend, trendValue, icon }) => {
  
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon sx={{ color: 'success.main', fontSize: '1rem' }} />;
      case 'down':
        return <TrendingDownIcon sx={{ color: 'error.main', fontSize: '1rem' }} />;
      default:
        return <RemoveIcon sx={{ color: 'text.secondary', fontSize: '1rem' }} />;
    }
  };
  
  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'success.main';
      case 'down':
        return 'error.main';
      default:
        return 'text.secondary';
    }
  };
  
  return (
    <Box sx={{ textAlign: 'center' }}>
      {icon && (
        <Box sx={{ mb: 1, color: 'primary.main' }}>
          {icon}
        </Box>
      )}
      
      <Typography variant="h4" component="div" sx={{ fontWeight: 700, mb: 0.5 }}>
        {value}
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        {label}
      </Typography>
      
      {trend && trendValue && (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
          {getTrendIcon()}
          <Typography variant="caption" sx={{ color: getTrendColor(), fontWeight: 600 }}>
            {trendValue}
          </Typography>
        </Box>
      )}
    </Box>
  );
});

MetricDisplay.displayName = 'MetricDisplay';

// Loading Skeleton for Cards
const CardSkeleton = memo<{ variant?: 'default' | 'metric' | 'media' }>(({ variant = 'default' }) => (
  <StyledCard>
    <StyledCardHeader
      avatar={<Skeleton variant="circular" width={40} height={40} />}
      title={<Skeleton variant="text" width="60%" />}
      subheader={<Skeleton variant="text" width="40%" />}
    />
    
    <StyledCardContent>
      {variant === 'metric' ? (
        <Box sx={{ textAlign: 'center' }}>
          <Skeleton variant="text" width="80%" height={60} sx={{ mb: 1 }} />
          <Skeleton variant="text" width="60%" />
        </Box>
      ) : variant === 'media' ? (
        <>
          <Skeleton variant="rectangular" height={200} sx={{ mb: 2 }} />
          <Skeleton variant="text" width="100%" />
          <Skeleton variant="text" width="80%" />
        </>
      ) : (
        <>
          <Skeleton variant="text" width="100%" />
          <Skeleton variant="text" width="90%" />
          <Skeleton variant="text" width="70%" />
        </>
      )}
    </StyledCardContent>
  </StyledCard>
));

CardSkeleton.displayName = 'CardSkeleton';

// Main Enhanced Card Component
export interface EnhancedCardProps {
  title?: string;
  subtitle?: string;
  children?: React.ReactNode;
  avatar?: React.ReactNode;
  actions?: React.ReactNode;
  floatingActions?: React.ReactNode;
  status?: 'success' | 'warning' | 'error' | 'info';
  variant?: 'default' | 'outlined' | 'elevated' | 'glass';
  interactive?: boolean;
  elevated?: boolean;
  glowing?: boolean;
  loading?: boolean;
  loadingVariant?: 'default' | 'metric' | 'media';
  chips?: Array<{ label: string; color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info' }>;
  onClick?: () => void;
  className?: string;
  sx?: object;
  animationDelay?: number;
}

const EnhancedCard = memo(forwardRef<HTMLDivElement, EnhancedCardProps>(({
  title,
  subtitle,
  children,
  avatar,
  actions,
  floatingActions,
  status,
  variant = 'default',
  interactive = false,
  elevated = false,
  glowing = false,
  loading = false,
  loadingVariant = 'default',
  chips,
  onClick,
  className,
  sx,
  animationDelay = 0,
}, ref) => {
  
  // Memoize the card content to prevent unnecessary re-renders
  const cardContent = useMemo(() => {
    if (loading) {
      return <CardSkeleton variant={loadingVariant} />;
    }
    
    return (
      <StyledCard
        ref={ref}
        cardVariant={variant}
        interactive={interactive}
        elevated={elevated}
        glowing={glowing}
        onClick={onClick}
        className={className}
        sx={sx}
      >
        {/* Status Indicator */}
        {status && <StatusIndicator status={status} />}
        
        {/* Card Overlay */}
        {interactive && <CardOverlay className="card-overlay" />}
        
        {/* Header */}
        {(title || subtitle || avatar) && (
          <StyledCardHeader
            avatar={avatar}
            title={title}
            subheader={subtitle}
            action={
              <IconButton size="small">
                <MoreVertIcon />
              </IconButton>
            }
          />
        )}
        
        {/* Chips */}
        {chips && chips.length > 0 && (
          <Box sx={{ px: 2, pb: 1 }}>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {chips.map((chip, index) => (
                <Chip
                  key={index}
                  label={chip.label}
                  size="small"
                  color={chip.color || 'primary'}
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}
        
        {/* Content */}
        {children && (
          <StyledCardContent>
            {children}
          </StyledCardContent>
        )}
        
        {/* Standard Actions */}
        {actions && (
          <CardActions>
            {actions}
          </CardActions>
        )}
        
        {/* Floating Actions */}
        {floatingActions && (
          <FloatingCardActions className="card-actions">
            {floatingActions}
          </FloatingCardActions>
        )}
      </StyledCard>
    );
  }, [
    loading,
    loadingVariant,
    variant,
    interactive,
    elevated,
    glowing,
    onClick,
    className,
    sx,
    status,
    avatar,
    title,
    subtitle,
    chips,
    children,
    actions,
    floatingActions,
    ref,
  ]);
  
  // Apply entrance animation
  if (animationDelay > 0) {
    return (
      <Grow
        in
        timeout={600}
        style={{ transitionDelay: `${animationDelay}ms` }}
      >
        <div>{cardContent}</div>
      </Grow>
    );
  }
  
  return (
    <Fade in timeout={400}>
      <div>{cardContent}</div>
    </Fade>
  );
}));

EnhancedCard.displayName = 'EnhancedCard';

// Specialized Card Components
export const MetricCard = memo<{
  title: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
} & Omit<EnhancedCardProps, 'children'>>(({
  title,
  value,
  trend,
  trendValue,
  icon,
  color = 'primary',
  ...props
}) => (
  <EnhancedCard variant="elevated" {...props}>
    <MetricDisplay
      value={value}
      label={title}
      trend={trend}
      trendValue={trendValue}
      icon={icon}
    />
  </EnhancedCard>
));

MetricCard.displayName = 'MetricCard';

export const ActionCard = memo<{
  title: string;
  description?: string;
  icon?: React.ReactNode;
  primaryAction?: { label: string; onClick: () => void };
  secondaryAction?: { label: string; onClick: () => void };
} & Omit<EnhancedCardProps, 'children' | 'actions'>>(({
  title,
  description,
  icon,
  primaryAction,
  secondaryAction,
  ...props
}) => (
  <EnhancedCard
    title={title}
    subtitle={description}
    avatar={icon && <Avatar sx={{ bgcolor: 'primary.main' }}>{icon}</Avatar>}
    actions={
      <Box sx={{ display: 'flex', gap: 1, ml: 'auto' }}>
        {secondaryAction && (
          <Tooltip title={secondaryAction.label}>
            <IconButton onClick={secondaryAction.onClick}>
              <ShareIcon />
            </IconButton>
          </Tooltip>
        )}
        {primaryAction && (
          <Tooltip title={primaryAction.label}>
            <IconButton onClick={primaryAction.onClick} color="primary">
              <FavoriteIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>
    }
    interactive
    {...props}
  />
));

ActionCard.displayName = 'ActionCard';

export { EnhancedCard as default, CardSkeleton }; 