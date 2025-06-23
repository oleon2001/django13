import React from 'react';
import { Box, Skeleton, Card, CardContent, Grid } from '@mui/material';

interface LoadingSkeletonProps {
  variant?: 'dashboard' | 'list' | 'map' | 'table' | 'card';
  count?: number;
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  variant = 'dashboard', 
  count = 1 
}) => {
  const renderDashboardSkeleton = () => (
    <Box sx={{ p: 3 }}>
      {/* Header skeleton */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Skeleton variant="text" width={200} height={40} />
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Skeleton variant="rectangular" width={120} height={32} />
          <Skeleton variant="circular" width={40} height={40} />
        </Box>
      </Box>

      {/* Stats cards skeleton */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[1, 2, 3, 4].map((item) => (
          <Grid item xs={12} sm={6} md={3} key={item}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
                  <Box sx={{ flexGrow: 1 }}>
                    <Skeleton variant="text" width="60%" />
                    <Skeleton variant="text" width="40%" />
                  </Box>
                </Box>
                <Skeleton variant="text" width="80%" height={32} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main content skeleton */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Skeleton variant="rectangular" width="100%" height={400} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Skeleton variant="text" width="60%" height={24} sx={{ mb: 2 }} />
              {[1, 2, 3, 4, 5].map((item) => (
                <Box key={item} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Skeleton variant="circular" width={32} height={32} sx={{ mr: 2 }} />
                  <Box sx={{ flexGrow: 1 }}>
                    <Skeleton variant="text" width="70%" />
                    <Skeleton variant="text" width="50%" />
                  </Box>
                  <Skeleton variant="rectangular" width={60} height={20} />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderListSkeleton = () => (
    <Box sx={{ p: 2 }}>
      {Array.from({ length: count }).map((_, index) => (
        <Card key={index} sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Skeleton variant="circular" width={48} height={48} sx={{ mr: 2 }} />
              <Box sx={{ flexGrow: 1 }}>
                <Skeleton variant="text" width="60%" height={24} />
                <Skeleton variant="text" width="40%" height={20} />
                <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                  <Skeleton variant="text" width={80} height={16} />
                  <Skeleton variant="text" width={80} height={16} />
                  <Skeleton variant="text" width={80} height={16} />
                </Box>
              </Box>
              <Skeleton variant="rectangular" width={80} height={24} />
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );

  const renderMapSkeleton = () => (
    <Box sx={{ position: 'relative', width: '100%', height: 400 }}>
      <Skeleton 
        variant="rectangular" 
        width="100%" 
        height="100%" 
        sx={{ borderRadius: 1 }}
      />
      {/* Map controls skeleton */}
      <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
        <Skeleton variant="rectangular" width={40} height={40} sx={{ mb: 1 }} />
        <Skeleton variant="rectangular" width={40} height={40} sx={{ mb: 1 }} />
        <Skeleton variant="rectangular" width={40} height={40} />
      </Box>
      {/* Map markers skeleton */}
      {[1, 2, 3].map((item) => (
        <Skeleton
          key={item}
          variant="circular"
          width={24}
          height={24}
          sx={{
            position: 'absolute',
            top: `${20 + item * 15}%`,
            left: `${30 + item * 20}%`,
          }}
        />
      ))}
    </Box>
  );

  const renderTableSkeleton = () => (
    <Card>
      <CardContent>
        {/* Table header */}
        <Box sx={{ display: 'flex', mb: 2 }}>
          {[1, 2, 3, 4, 5].map((col) => (
            <Box key={col} sx={{ flex: 1, px: 1 }}>
              <Skeleton variant="text" width="80%" height={24} />
            </Box>
          ))}
        </Box>
        
        {/* Table rows */}
        {Array.from({ length: count }).map((_, index) => (
          <Box key={index} sx={{ display: 'flex', mb: 1 }}>
            {[1, 2, 3, 4, 5].map((col) => (
              <Box key={col} sx={{ flex: 1, px: 1 }}>
                <Skeleton variant="text" width="90%" height={20} />
              </Box>
            ))}
          </Box>
        ))}
      </CardContent>
    </Card>
  );

  const renderCardSkeleton = () => (
    <Grid container spacing={2}>
      {Array.from({ length: count }).map((_, index) => (
        <Grid item xs={12} sm={6} md={4} key={index}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
                <Box sx={{ flexGrow: 1 }}>
                  <Skeleton variant="text" width="70%" />
                  <Skeleton variant="text" width="50%" />
                </Box>
              </Box>
              <Skeleton variant="rectangular" width="100%" height={120} sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Skeleton variant="text" width="40%" />
                <Skeleton variant="rectangular" width={80} height={24} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
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