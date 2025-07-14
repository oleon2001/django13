import React, { useState, useCallback, useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Chip,
  Badge,
  useMediaQuery,
  useTheme,
  Fade,
  Collapse,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  LocationOn as LocationOnIcon,
  MonitorHeart as MonitorHeartIcon,
  DirectionsCar as DirectionsCarIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  LocalParking as LocalParkingIcon,
  Sensors as SensorsIcon,
  Route as RouteIcon,
  Devices as DevicesIcon,
  Notifications as NotificationsIcon,
  ExpandMore,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../hooks/useAuth';
import { designTokens } from '../../theme';
import logo from '../../assets/img/logofalkon.png';

interface BaseLayoutProps {
  children: React.ReactNode;
}

interface NavItem {
  text: string;
  icon: React.ReactNode;
  path: string;
  badge?: number;
  subItems?: NavItem[];
}

const drawerWidth = 280;

export const BaseLayout: React.FC<BaseLayoutProps> = ({ children }) => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const theme = useTheme();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [notificationAnchor, setNotificationAnchor] = useState<null | HTMLElement>(null);
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  // Memoized navigation items for better performance
  const navItems: NavItem[] = useMemo(() => [
    { 
      text: t('navigation.dashboard'), 
      icon: <DashboardIcon />, 
      path: '/dashboard',
      badge: 3
    },
    // { 
    //   text: t('navigation.gps'), 
    //   icon: <LocationOnIcon />, 
    //   path: '/gps' 
    // },
    { 
      text: t('navigation.deviceManagement'), 
      icon: <DevicesIcon />, 
      path: '/devices',
      badge: 2
    },
    { 
      text: t('navigation.geofences'), 
      icon: <LocationOnIcon />, 
      path: '/geofences' 
    },
    { 
      text: t('navigation.monitoring'), 
      icon: <MonitorHeartIcon />, 
      path: '/monitoring' 
    },
    { 
      text: t('navigation.fleet'), 
      icon: <DirectionsCarIcon />, 
      path: '/fleet',
      subItems: [
        { text: t('navigation.vehicles'), icon: <DirectionsCarIcon />, path: '/vehicles' },
        { text: t('navigation.drivers'), icon: <PersonIcon />, path: '/drivers' },
        { text: t('navigation.parking'), icon: <LocalParkingIcon />, path: '/parking' },
      ]
    },
    { 
      text: t('navigation.sensors'), 
      icon: <SensorsIcon />, 
      path: '/sensors' 
    },
    { 
      text: t('navigation.routes'), 
      icon: <RouteIcon />, 
      path: '/routes' 
    },
    { 
      text: t('navigation.reports'), 
      icon: <BarChartIcon />, 
      path: '/reports' 
    },
    { 
      text: t('navigation.configuration'), 
      icon: <SettingsIcon />, 
      path: '/settings' 
    },
  ], [t]);

  const handleDrawerToggle = useCallback(() => {
    setMobileOpen(!mobileOpen);
  }, [mobileOpen]);

  const handleUserMenuOpen = useCallback((event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  }, []);

  const handleUserMenuClose = useCallback(() => {
    setUserMenuAnchor(null);
  }, []);

  const handleNotificationOpen = useCallback((event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchor(event.currentTarget);
  }, []);

  const handleNotificationClose = useCallback(() => {
    setNotificationAnchor(null);
  }, []);

  const handleItemExpand = useCallback((itemPath: string) => {
    setExpandedItems(prev => 
      prev.includes(itemPath) 
        ? prev.filter(path => path !== itemPath)
        : [...prev, itemPath]
    );
  }, []);

  const handleLogout = useCallback(async () => {
    handleUserMenuClose();
    await logout();
  }, [logout, handleUserMenuClose]);

  const isActive = useCallback((path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  }, [location.pathname]);

  // Enhanced Navigation Item Component
  const NavItemComponent = React.memo<{ 
    item: NavItem; 
    level?: number;
    onItemClick?: () => void;
  }>(({ item, level = 0, onItemClick }) => {
    const isItemActive = isActive(item.path);
    const hasSubItems = item.subItems && item.subItems.length > 0;
    const isExpanded = expandedItems.includes(item.path);

    const handleClick = () => {
      if (hasSubItems) {
        handleItemExpand(item.path);
      } else {
        onItemClick?.();
      }
    };

    return (
      <>
        <ListItemButton
          component={hasSubItems ? 'div' : Link}
          to={hasSubItems ? undefined : item.path}
          onClick={handleClick}
          selected={isItemActive}
          sx={{
            pl: 2 + level * 2,
            borderRadius: 2,
            mx: 1,
            mb: 0.5,
            minHeight: 48,
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: 4,
              backgroundColor: 'primary.main',
              transform: isItemActive ? 'scaleY(1)' : 'scaleY(0)',
              transformOrigin: 'center',
              transition: 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            },
            '&:hover': {
              backgroundColor: 'rgba(224, 26, 34, 0.08)',
              transform: 'translateX(4px)',
              '& .MuiListItemIcon-root': {
                color: 'primary.main',
              },
            },
            '&.Mui-selected': {
              backgroundColor: 'rgba(224, 26, 34, 0.12)',
              '& .MuiListItemIcon-root': {
                color: 'primary.main',
              },
              '& .MuiListItemText-primary': {
                fontWeight: 600,
                color: 'primary.main',
              },
            },
          }}
        >
          <ListItemIcon
            sx={{
              minWidth: 40,
              color: isItemActive ? 'primary.main' : 'text.secondary',
              transition: 'color 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
          >
            {item.icon}
          </ListItemIcon>
          
          <ListItemText 
            primary={item.text}
            primaryTypographyProps={{
              fontSize: '0.875rem',
              fontWeight: isItemActive ? 600 : 500,
              color: isItemActive ? 'primary.main' : 'text.primary',
            }}
          />
          
          {item.badge && (
            <Chip
              label={item.badge}
              size="small"
              color="primary"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                fontWeight: 600,
                mr: hasSubItems ? 1 : 0,
              }}
            />
          )}
          
          {hasSubItems && (
            <IconButton
              size="small"
              sx={{ 
                color: 'text.secondary',
                transition: 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
              }}
            >
              <ExpandMore fontSize="small" />
            </IconButton>
          )}
        </ListItemButton>

        {hasSubItems && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.subItems?.map((subItem) => (
                <NavItemComponent
                  key={subItem.path}
                  item={subItem}
                  level={level + 1}
                  onItemClick={onItemClick}
                />
              ))}
            </List>
          </Collapse>
        )}
      </>
    );
  });

  // Enhanced Drawer Content
  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo Section */}
      <Box
        sx={{
          p: 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: 1,
          borderColor: 'divider',
          background: 'linear-gradient(135deg, rgba(224, 26, 34, 0.02) 0%, rgba(224, 26, 34, 0.08) 100%)',
        }}
      >
        <Box
          component="img"
          src={logo}
          alt="SkyGuard Logo"
          sx={{
            height: 40,
            width: 'auto',
            transition: 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              transform: 'scale(1.05)',
            },
          }}
        />
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, overflowY: 'auto', py: 2 }}>
        <List>
          {navItems.map((item) => (
            <NavItemComponent
              key={item.path}
              item={item}
              onItemClick={isMobile ? handleDrawerToggle : undefined}
            />
          ))}
        </List>
      </Box>

      {/* User Info Section */}
      <Box
        sx={{
          p: 2,
          borderTop: 1,
          borderColor: 'divider',
          background: 'linear-gradient(135deg, rgba(224, 26, 34, 0.02) 0%, rgba(224, 26, 34, 0.08) 100%)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar
            sx={{
              bgcolor: 'primary.main',
              width: 36,
              height: 36,
              fontSize: '0.875rem',
              fontWeight: 600,
            }}
          >
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="subtitle2" noWrap>
              {user?.username || 'Usuario'}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user?.email || 'usuario@skyguard.com'}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: 'background.default' }}>
      {/* Enhanced AppBar */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          bgcolor: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ minHeight: 64 }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ 
              mr: 2, 
              display: { md: 'none' },
              color: 'text.primary',
            }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ 
              flexGrow: 1,
              color: 'text.primary',
              fontWeight: 600,
              fontSize: '1.125rem',
            }}
          >
            {t('app.name')}
          </Typography>

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Notifications */}
            <Tooltip title="Notificaciones">
              <IconButton
                color="inherit"
                onClick={handleNotificationOpen}
                sx={{ color: 'text.primary' }}
              >
                <Badge badgeContent={4} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* User Menu */}
            <Tooltip title="Perfil de usuario">
              <IconButton
                onClick={handleUserMenuOpen}
                sx={{ 
                  p: 0.5,
                  ml: 1,
                  transition: 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'scale(1.05)',
                  },
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: 'primary.main',
                    width: 36,
                    height: 36,
                    fontSize: '0.875rem',
                    fontWeight: 600,
                  }}
                >
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </Avatar>
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* User Menu */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 200,
            borderRadius: 2,
            boxShadow: designTokens.shadows.lg,
          },
        }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="subtitle1" fontWeight={600}>
            {user?.username || 'Usuario'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {user?.email || 'usuario@skyguard.com'}
          </Typography>
        </Box>
        
        <MenuItem onClick={handleUserMenuClose}>
          <PersonIcon sx={{ mr: 2 }} />
          Mi Perfil
        </MenuItem>
        
        <MenuItem onClick={handleUserMenuClose}>
          <SettingsIcon sx={{ mr: 2 }} />
          Configuración
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
          <LogoutIcon sx={{ mr: 2 }} />
          Cerrar Sesión
        </MenuItem>
      </Menu>

      {/* Notification Menu */}
      <Menu
        anchorEl={notificationAnchor}
        open={Boolean(notificationAnchor)}
        onClose={handleNotificationClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 320,
            maxWidth: 400,
            borderRadius: 2,
            boxShadow: designTokens.shadows.lg,
          },
        }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" fontWeight={600}>
            Notificaciones
          </Typography>
        </Box>
        
        <Box sx={{ maxHeight: 300, overflowY: 'auto' }}>
          {/* Sample notifications */}
          <MenuItem onClick={handleNotificationClose}>
            <Box>
              <Typography variant="subtitle2">
                Dispositivo GPS desconectado
              </Typography>
              <Typography variant="body2" color="text.secondary">
                El dispositivo 12345 se desconectó hace 5 minutos
              </Typography>
            </Box>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleNotificationClose}>
            <Box>
              <Typography variant="subtitle2">
                Nuevo vehículo registrado
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Se registró el vehículo ABC-123 exitosamente
              </Typography>
            </Box>
          </MenuItem>
        </Box>
      </Menu>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile Drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              borderRight: 'none',
              boxShadow: designTokens.shadows.xl,
            },
          }}
        >
          {drawerContent}
        </Drawer>
        
        {/* Desktop Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              borderRight: 1,
              borderColor: 'divider',
              boxShadow: 'none',
            },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Toolbar sx={{ minHeight: 64 }} />
        
        <Box
          sx={{
            flex: 1,
            p: { xs: 2, sm: 3 },
            overflowY: 'auto',
            bgcolor: 'background.default',
          }}
        >
          <Fade in timeout={300}>
            <Box>
              {children}
            </Box>
          </Fade>
        </Box>
      </Box>
    </Box>
  );
}; 