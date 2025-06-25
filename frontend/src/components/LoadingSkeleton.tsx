import React from 'react';
import { Box, Skeleton, Card, CardContent, Grid, keyframes, Fade } from '@mui/material';
import { styled } from '@mui/material/styles';

// Animaciones personalizadas
const wave = keyframes`
  0% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(100%);
  }
  100% {
    transform: translateX(100%);
  }
`;

const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const pulse = keyframes`
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
`;

// Componentes estilizados
const AnimatedCard = styled(Card)(({ theme }) => ({
  animation: `${fadeInUp} 0.6s ease-out`,
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: `linear-gradient(90deg, 
      transparent 0%, 
      ${theme.palette.primary.main}08 50%, 
      transparent 100%)`,
    transform: 'translateX(-100%)',
    animation: `${wave} 2s infinite`,
    zIndex: 1,
  },
}));

const EnhancedSkeleton = styled(Skeleton)(({ theme }) => ({
  backgroundColor: theme.palette.grey[100],
  '&::after': {
    background: `linear-gradient(90deg, 
      transparent 0%, 
      ${theme.palette.primary.main}15 50%, 
      transparent 100%)`,
  },
}));

const PulsingSkeleton = styled(Skeleton)(({ theme }) => ({
  animation: `${pulse} 1.5s ease-in-out infinite`,
  backgroundColor: theme.palette.grey[100],
}));

const LoadingContainer = styled(Box)(({ theme }) => ({
  background: `linear-gradient(135deg, 
    ${theme.palette.background.default} 0%, 
    ${theme.palette.background.paper} 100%)`,
  minHeight: '100vh',
  padding: theme.spacing(2),
}));

interface LoadingSkeletonProps {
  variant?: 'dashboard' | 'list' | 'map' | 'table' | 'card';
  count?: number;
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  variant = 'dashboard', 
  count = 1 
}) => {
  const renderDashboardSkeleton = () => (
    <LoadingContainer>
      <Fade in timeout={300}>
        <Box sx={{ p: 3 }}>
          {/* Header skeleton */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <EnhancedSkeleton 
              variant="text" 
              width={250} 
              height={50} 
              sx={{ animationDelay: '0.1s' }}
            />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <EnhancedSkeleton 
                variant="rectangular" 
                width={140} 
                height={40} 
                sx={{ borderRadius: 1, animationDelay: '0.2s' }}
              />
              <PulsingSkeleton 
                variant="circular" 
                width={40} 
                height={40} 
                sx={{ animationDelay: '0.3s' }}
              />
            </Box>
          </Box>

          {/* Stats cards skeleton */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            {[1, 2, 3, 4].map((item) => (
              <Grid item xs={12} sm={6} md={3} key={item}>
                <AnimatedCard sx={{ animationDelay: `${item * 0.1}s` }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <PulsingSkeleton 
                        variant="circular" 
                        width={48} 
                        height={48} 
                        sx={{ mr: 2, animationDelay: `${item * 0.15}s` }}
                      />
                      <Box sx={{ flexGrow: 1 }}>
                        <EnhancedSkeleton 
                          variant="text" 
                          width="70%" 
                          sx={{ animationDelay: `${item * 0.2}s` }}
                        />
                        <EnhancedSkeleton 
                          variant="text" 
                          width="50%" 
                          sx={{ animationDelay: `${item * 0.25}s` }}
                        />
                      </Box>
                    </Box>
                    <EnhancedSkeleton 
                      variant="text" 
                      width="90%" 
                      height={40} 
                      sx={{ animationDelay: `${item * 0.3}s` }}
                    />
                  </CardContent>
                </AnimatedCard>
              </Grid>
            ))}
          </Grid>

          {/* Main content skeleton */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <AnimatedCard sx={{ animationDelay: '0.5s' }}>
                <CardContent>
                  <Box sx={{ mb: 2 }}>
                    <EnhancedSkeleton 
                      variant="text" 
                      width="40%" 
                      height={30} 
                      sx={{ animationDelay: '0.6s' }}
                    />
                  </Box>
                  <EnhancedSkeleton 
                    variant="rectangular" 
                    width="100%" 
                    height={450} 
                    sx={{ borderRadius: 2, animationDelay: '0.7s' }}
                  />
                </CardContent>
              </AnimatedCard>
            </Grid>
            <Grid item xs={12} md={4}>
              <AnimatedCard sx={{ animationDelay: '0.6s' }}>
                <CardContent>
                  <EnhancedSkeleton 
                    variant="text" 
                    width="70%" 
                    height={30} 
                    sx={{ mb: 3, animationDelay: '0.7s' }}
                  />
                  {[1, 2, 3, 4, 5].map((item) => (
                    <Box key={item} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <PulsingSkeleton 
                        variant="circular" 
                        width={40} 
                        height={40} 
                        sx={{ mr: 2, animationDelay: `${0.8 + item * 0.1}s` }}
                      />
                      <Box sx={{ flexGrow: 1 }}>
                        <EnhancedSkeleton 
                          variant="text" 
                          width="80%" 
                          sx={{ animationDelay: `${0.85 + item * 0.1}s` }}
                        />
                        <EnhancedSkeleton 
                          variant="text" 
                          width="60%" 
                          sx={{ animationDelay: `${0.9 + item * 0.1}s` }}
                        />
                      </Box>
                      <EnhancedSkeleton 
                        variant="rectangular" 
                        width={70} 
                        height={24} 
                        sx={{ borderRadius: 1, animationDelay: `${0.95 + item * 0.1}s` }}
                      />
                    </Box>
                  ))}
                </CardContent>
              </AnimatedCard>
            </Grid>
          </Grid>
        </Box>
      </Fade>
    </LoadingContainer>
  );

  const renderListSkeleton = () => (
    <Fade in timeout={300}>
      <Box sx={{ p: 2 }}>
        {Array.from({ length: count }).map((_, index) => (
          <AnimatedCard key={index} sx={{ mb: 2, animationDelay: `${index * 0.1}s` }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PulsingSkeleton 
                  variant="circular" 
                  width={56} 
                  height={56} 
                  sx={{ mr: 2, animationDelay: `${index * 0.15}s` }}
                />
                <Box sx={{ flexGrow: 1 }}>
                  <EnhancedSkeleton 
                    variant="text" 
                    width="70%" 
                    height={28} 
                    sx={{ animationDelay: `${index * 0.2}s` }}
                  />
                  <EnhancedSkeleton 
                    variant="text" 
                    width="50%" 
                    height={20} 
                    sx={{ animationDelay: `${index * 0.25}s` }}
                  />
                  <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                    <EnhancedSkeleton 
                      variant="rectangular" 
                      width={80} 
                      height={18} 
                      sx={{ borderRadius: 1, animationDelay: `${index * 0.3}s` }}
                    />
                    <EnhancedSkeleton 
                      variant="rectangular" 
                      width={80} 
                      height={18} 
                      sx={{ borderRadius: 1, animationDelay: `${index * 0.35}s` }}
                    />
                    <EnhancedSkeleton 
                      variant="rectangular" 
                      width={80} 
                      height={18} 
                      sx={{ borderRadius: 1, animationDelay: `${index * 0.4}s` }}
                    />
                  </Box>
                </Box>
                <EnhancedSkeleton 
                  variant="rectangular" 
                  width={90} 
                  height={32} 
                  sx={{ borderRadius: 1, animationDelay: `${index * 0.45}s` }}
                />
              </Box>
            </CardContent>
          </AnimatedCard>
        ))}
      </Box>
    </Fade>
  );

  const renderMapSkeleton = () => (
    <Fade in timeout={400}>
      <Box sx={{ position: 'relative', width: '100%', height: 400 }}>
        <EnhancedSkeleton 
          variant="rectangular" 
          width="100%" 
          height="100%" 
          sx={{ borderRadius: 2 }}
        />
        {/* Map controls skeleton */}
        <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
          <PulsingSkeleton 
            variant="rectangular" 
            width={48} 
            height={48} 
            sx={{ mb: 1, borderRadius: 1, animationDelay: '0.2s' }}
          />
          <PulsingSkeleton 
            variant="rectangular" 
            width={48} 
            height={48} 
            sx={{ mb: 1, borderRadius: 1, animationDelay: '0.4s' }}
          />
          <PulsingSkeleton 
            variant="rectangular" 
            width={48} 
            height={48} 
            sx={{ borderRadius: 1, animationDelay: '0.6s' }}
          />
        </Box>
        {/* Map markers skeleton */}
        {[1, 2, 3, 4, 5].map((item) => (
          <PulsingSkeleton
            key={item}
            variant="circular"
            width={28}
            height={28}
            sx={{
              position: 'absolute',
              top: `${15 + item * 12}%`,
              left: `${25 + item * 15}%`,
              animationDelay: `${0.8 + item * 0.2}s`,
            }}
          />
        ))}
      </Box>
    </Fade>
  );

  const renderTableSkeleton = () => (
    <Fade in timeout={300}>
      <AnimatedCard>
        <CardContent>
          {/* Table header */}
          <Box sx={{ display: 'flex', mb: 3 }}>
            {[1, 2, 3, 4, 5].map((col) => (
              <Box key={col} sx={{ flex: 1, px: 1 }}>
                <EnhancedSkeleton 
                  variant="text" 
                  width="85%" 
                  height={28} 
                  sx={{ animationDelay: `${col * 0.1}s` }}
                />
              </Box>
            ))}
          </Box>
          
          {/* Table rows */}
          {Array.from({ length: count }).map((_, index) => (
            <Box key={index} sx={{ display: 'flex', mb: 2 }}>
              {[1, 2, 3, 4, 5].map((col) => (
                <Box key={col} sx={{ flex: 1, px: 1 }}>
                  <EnhancedSkeleton 
                    variant="text" 
                    width="95%" 
                    height={22} 
                    sx={{ animationDelay: `${(index * 5 + col) * 0.05}s` }}
                  />
                </Box>
              ))}
            </Box>
          ))}
        </CardContent>
      </AnimatedCard>
    </Fade>
  );

  const renderCardSkeleton = () => (
    <Fade in timeout={300}>
      <Grid container spacing={2}>
        {Array.from({ length: count }).map((_, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <AnimatedCard sx={{ animationDelay: `${index * 0.1}s` }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PulsingSkeleton 
                    variant="circular" 
                    width={48} 
                    height={48} 
                    sx={{ mr: 2, animationDelay: `${index * 0.15}s` }}
                  />
                  <Box sx={{ flexGrow: 1 }}>
                    <EnhancedSkeleton 
                      variant="text" 
                      width="80%" 
                      sx={{ animationDelay: `${index * 0.2}s` }}
                    />
                    <EnhancedSkeleton 
                      variant="text" 
                      width="60%" 
                      sx={{ animationDelay: `${index * 0.25}s` }}
                    />
                  </Box>
                </Box>
                <EnhancedSkeleton 
                  variant="rectangular" 
                  width="100%" 
                  height={140} 
                  sx={{ mb: 2, borderRadius: 1, animationDelay: `${index * 0.3}s` }}
                />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <EnhancedSkeleton 
                    variant="text" 
                    width="45%" 
                    sx={{ animationDelay: `${index * 0.35}s` }}
                  />
                  <EnhancedSkeleton 
                    variant="rectangular" 
                    width={90} 
                    height={28} 
                    sx={{ borderRadius: 1, animationDelay: `${index * 0.4}s` }}
                  />
                </Box>
              </CardContent>
            </AnimatedCard>
          </Grid>
        ))}
      </Grid>
    </Fade>
  );

  switch (variant) {
    case 'dashboard':
      return renderDashboardSkeleton();
    case 'list':
      return renderListSkeleton();
    case 'map':
      return renderMapSkeleton();
    case 'table':
      return renderTableSkeleton();
    case 'card':
      return renderCardSkeleton();
    default:
      return renderDashboardSkeleton();
  }
};

export default LoadingSkeleton; 