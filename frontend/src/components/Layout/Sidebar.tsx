import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

interface MenuItem {
  path: string;
  label: string;
  icon?: string;
}

const menuItems: MenuItem[] = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/vehicles', label: 'Vehículos' },
  { path: '/geofences', label: 'Geocercas' },
  { path: '/reports', label: 'Reportes' },
  { path: '/settings', label: 'Configuración' },
];

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'active' : ''}`
            }
          >
            {item.icon && <span className="sidebar-icon">{item.icon}</span>}
            <span className="sidebar-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar; 