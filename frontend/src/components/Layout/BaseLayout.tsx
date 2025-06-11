import React, { useState } from 'react';
import { Link } from 'react-router-dom';
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
  Button,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircle from '@mui/icons-material/AccountCircle';
import DashboardIcon from '@mui/icons-material/Dashboard';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import BarChartIcon from '@mui/icons-material/BarChart';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '../../hooks/useAuth'; // Import useAuth hook
import logo from '../../assets/img/logofalkon.png';

interface BaseLayoutProps {
  children: React.ReactNode;
}

const drawerWidth = 240;

export const BaseLayout: React.FC<BaseLayoutProps> = ({ children }) => {
  const { user, logout } = useAuth(); // Get user and logout from useAuth
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const navItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'GPS', icon: <LocationOnIcon />, path: '/gps' },
    { text: 'Monitoreo', icon: <MonitorHeartIcon />, path: '/monitoring' },
    { text: 'Rastreo', icon: <TrackChangesIcon />, path: '/tracking' },
    { text: 'Vehículos', icon: <DirectionsCarIcon />, path: '/vehicles' },
    { text: 'Reportes', icon: <BarChartIcon />, path: '/reports' },
    { text: 'Configuración', icon: <SettingsIcon />, path: '/settings' },
  ];

  const drawer = (
    <div>
      <Toolbar>
        <img src={logo} alt="Skyguard Logo" style={{ height: 40, margin: '10px auto' }} />
      </Toolbar>
      <List>
        {navItems.map((item) => (
          <ListItemButton
            key={item.text}
            component={Link}
            to={item.path}
            onClick={handleDrawerToggle}
            sx={{
              margin: '4px 8px', // Apply margin as defined in theme for ListItemButton
              borderRadius: '4px', // Apply border radius as defined in theme for ListItemButton
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItemButton>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            SkyGuard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {user && (
              <Typography variant="subtitle1" sx={{ mr: 1 }}>
                Hola, {user.username}
              </Typography>
            )}
            <IconButton color="inherit">
              <AccountCircle />
            </IconButton>
            <Button color="inherit" onClick={logout} startIcon={<LogoutIcon />}>
              Cerrar Sesión
            </Button>
          </Box>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` }, overflowY: 'auto' }}
      >
        <Toolbar /> {/* Add a toolbar to offset content below the AppBar */}
        {children}
      </Box>
    </Box>
  );
}; 