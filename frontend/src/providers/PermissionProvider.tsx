import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from './AuthProvider';

// ============================================================================
// PERMISSION TYPES - Tipos para permisos
// ============================================================================

export type Permission = 
  // Dispositivos
  | 'devices.view'
  | 'devices.create'
  | 'devices.edit'
  | 'devices.delete'
  | 'devices.export'
  | 'devices.import'
  
  // Vehículos
  | 'vehicles.view'
  | 'vehicles.create'
  | 'vehicles.edit'
  | 'vehicles.delete'
  | 'vehicles.export'
  | 'vehicles.import'
  
  // Conductores
  | 'drivers.view'
  | 'drivers.create'
  | 'drivers.edit'
  | 'drivers.delete'
  | 'drivers.export'
  | 'drivers.import'
  
  // Rutas
  | 'routes.view'
  | 'routes.create'
  | 'routes.edit'
  | 'routes.delete'
  | 'routes.export'
  | 'routes.import'
  
  // Geocercas
  | 'geofences.view'
  | 'geofences.create'
  | 'geofences.edit'
  | 'geofences.delete'
  | 'geofences.export'
  | 'geofences.import'
  
  // Reportes
  | 'reports.view'
  | 'reports.create'
  | 'reports.edit'
  | 'reports.delete'
  | 'reports.export'
  | 'reports.schedule'
  
  // Usuarios
  | 'users.view'
  | 'users.create'
  | 'users.edit'
  | 'users.delete'
  | 'users.export'
  | 'users.import'
  
  // Configuración
  | 'settings.view'
  | 'settings.edit'
  | 'settings.system'
  | 'settings.security'
  
  // Sistema
  | 'system.admin'
  | 'system.superuser'
  | 'system.monitor'
  | 'system.logs'
  | 'system.backup'
  | 'system.restore';

export type Role = 'admin' | 'manager' | 'operator' | 'viewer' | 'driver';

export interface PermissionContextType {
  permissions: Permission[];
  roles: Role[];
  hasPermission: (permission: Permission) => boolean;
  hasAnyPermission: (permissions: Permission[]) => boolean;
  hasAllPermissions: (permissions: Permission[]) => boolean;
  hasRole: (role: Role) => boolean;
  hasAnyRole: (roles: Role[]) => boolean;
  hasAllRoles: (roles: Role[]) => boolean;
  isAdmin: () => boolean;
  isSuperUser: () => boolean;
  canView: (resource: string) => boolean;
  canCreate: (resource: string) => boolean;
  canEdit: (resource: string) => boolean;
  canDelete: (resource: string) => boolean;
  canExport: (resource: string) => boolean;
  canImport: (resource: string) => boolean;
}

// ============================================================================
// PERMISSION MAPPINGS - Mapeo de roles a permisos
// ============================================================================

const rolePermissions: Record<Role, Permission[]> = {
  admin: [
    // Dispositivos
    'devices.view', 'devices.create', 'devices.edit', 'devices.delete', 'devices.export', 'devices.import',
    // Vehículos
    'vehicles.view', 'vehicles.create', 'vehicles.edit', 'vehicles.delete', 'vehicles.export', 'vehicles.import',
    // Conductores
    'drivers.view', 'drivers.create', 'drivers.edit', 'drivers.delete', 'drivers.export', 'drivers.import',
    // Rutas
    'routes.view', 'routes.create', 'routes.edit', 'routes.delete', 'routes.export', 'routes.import',
    // Geocercas
    'geofences.view', 'geofences.create', 'geofences.edit', 'geofences.delete', 'geofences.export', 'geofences.import',
    // Reportes
    'reports.view', 'reports.create', 'reports.edit', 'reports.delete', 'reports.export', 'reports.schedule',
    // Usuarios
    'users.view', 'users.create', 'users.edit', 'users.delete', 'users.export', 'users.import',
    // Configuración
    'settings.view', 'settings.edit', 'settings.system', 'settings.security',
    // Sistema
    'system.admin', 'system.superuser', 'system.monitor', 'system.logs', 'system.backup', 'system.restore',
  ],
  
  manager: [
    // Dispositivos
    'devices.view', 'devices.create', 'devices.edit', 'devices.export',
    // Vehículos
    'vehicles.view', 'vehicles.create', 'vehicles.edit', 'vehicles.export',
    // Conductores
    'drivers.view', 'drivers.create', 'drivers.edit', 'drivers.export',
    // Rutas
    'routes.view', 'routes.create', 'routes.edit', 'routes.export',
    // Geocercas
    'geofences.view', 'geofences.create', 'geofences.edit', 'geofences.export',
    // Reportes
    'reports.view', 'reports.create', 'reports.edit', 'reports.export', 'reports.schedule',
    // Usuarios
    'users.view', 'users.create', 'users.edit', 'users.export',
    // Configuración
    'settings.view', 'settings.edit',
    // Sistema
    'system.monitor', 'system.logs',
  ],
  
  operator: [
    // Dispositivos
    'devices.view', 'devices.edit', 'devices.export',
    // Vehículos
    'vehicles.view', 'vehicles.edit', 'vehicles.export',
    // Conductores
    'drivers.view', 'drivers.edit', 'drivers.export',
    // Rutas
    'routes.view', 'routes.edit', 'routes.export',
    // Geocercas
    'geofences.view', 'geofences.edit', 'geofences.export',
    // Reportes
    'reports.view', 'reports.create', 'reports.export',
    // Usuarios
    'users.view',
    // Configuración
    'settings.view',
  ],
  
  viewer: [
    // Dispositivos
    'devices.view', 'devices.export',
    // Vehículos
    'vehicles.view', 'vehicles.export',
    // Conductores
    'drivers.view', 'drivers.export',
    // Rutas
    'routes.view', 'routes.export',
    // Geocercas
    'geofences.view', 'geofences.export',
    // Reportes
    'reports.view', 'reports.export',
    // Usuarios
    'users.view',
    // Configuración
    'settings.view',
  ],
  
  driver: [
    // Dispositivos
    'devices.view',
    // Vehículos
    'vehicles.view',
    // Rutas
    'routes.view',
    // Geocercas
    'geofences.view',
    // Reportes
    'reports.view',
  ],
};

// ============================================================================
// PERMISSION CONTEXT - Contexto para permisos
// ============================================================================

const PermissionContext = createContext<PermissionContextType | undefined>(undefined);

// ============================================================================
// PERMISSION PROVIDER - Provider para permisos
// ============================================================================

interface PermissionProviderProps {
  children: ReactNode;
}

export const PermissionProvider: React.FC<PermissionProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);

  // Calcular permisos basados en el usuario
  useEffect(() => {
    if (user) {
      const userRoles: Role[] = [];
      const userPermissions: Permission[] = [];

      // Determinar roles del usuario
      if (user.is_superuser) {
        userRoles.push('admin');
      } else if (user.is_staff) {
        userRoles.push('manager');
      } else if (user.groups.includes('operator')) {
        userRoles.push('operator');
      } else if (user.groups.includes('viewer')) {
        userRoles.push('viewer');
      } else if (user.groups.includes('driver')) {
        userRoles.push('driver');
      } else {
        userRoles.push('viewer'); // Rol por defecto
      }

      // Obtener permisos de los roles
      userRoles.forEach(role => {
        const rolePerms = rolePermissions[role] || [];
        userPermissions.push(...rolePerms);
      });

      // Agregar permisos específicos del usuario
      if (user.permissions) {
        userPermissions.push(...user.permissions as Permission[]);
      }

      // Eliminar duplicados
      const uniquePermissions = [...new Set(userPermissions)];
      
      setRoles(userRoles);
      setPermissions(uniquePermissions);
    } else {
      setRoles([]);
      setPermissions([]);
    }
  }, [user]);

  // Verificar si tiene un permiso específico
  const hasPermission = (permission: Permission): boolean => {
    return permissions.includes(permission);
  };

  // Verificar si tiene al menos uno de los permisos
  const hasAnyPermission = (permissionsToCheck: Permission[]): boolean => {
    return permissionsToCheck.some(permission => permissions.includes(permission));
  };

  // Verificar si tiene todos los permisos
  const hasAllPermissions = (permissionsToCheck: Permission[]): boolean => {
    return permissionsToCheck.every(permission => permissions.includes(permission));
  };

  // Verificar si tiene un rol específico
  const hasRole = (role: Role): boolean => {
    return roles.includes(role);
  };

  // Verificar si tiene al menos uno de los roles
  const hasAnyRole = (rolesToCheck: Role[]): boolean => {
    return rolesToCheck.some(role => roles.includes(role));
  };

  // Verificar si tiene todos los roles
  const hasAllRoles = (rolesToCheck: Role[]): boolean => {
    return rolesToCheck.every(role => roles.includes(role));
  };

  // Verificar si es administrador
  const isAdmin = (): boolean => {
    return hasRole('admin') || hasPermission('system.admin');
  };

  // Verificar si es superusuario
  const isSuperUser = (): boolean => {
    return hasPermission('system.superuser');
  };

  // Verificar permisos por recurso
  const canView = (resource: string): boolean => {
    return hasPermission(`${resource}.view` as Permission);
  };

  const canCreate = (resource: string): boolean => {
    return hasPermission(`${resource}.create` as Permission);
  };

  const canEdit = (resource: string): boolean => {
    return hasPermission(`${resource}.edit` as Permission);
  };

  const canDelete = (resource: string): boolean => {
    return hasPermission(`${resource}.delete` as Permission);
  };

  const canExport = (resource: string): boolean => {
    return hasPermission(`${resource}.export` as Permission);
  };

  const canImport = (resource: string): boolean => {
    return hasPermission(`${resource}.import` as Permission);
  };

  const value: PermissionContextType = {
    permissions,
    roles,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    hasAllRoles,
    isAdmin,
    isSuperUser,
    canView,
    canCreate,
    canEdit,
    canDelete,
    canExport,
    canImport,
  };

  return (
    <PermissionContext.Provider value={value}>
      {children}
    </PermissionContext.Provider>
  );
};

// ============================================================================
// PERMISSION HOOK - Hook para usar el contexto de permisos
// ============================================================================

export const usePermission = () => {
  const context = useContext(PermissionContext);
  
  if (context === undefined) {
    throw new Error('usePermission must be used within a PermissionProvider');
  }
  
  return context;
};

// ============================================================================
// PERMISSION COMPONENTS - Componentes para control de acceso
// ============================================================================

interface RequirePermissionProps {
  permission: Permission;
  children: ReactNode;
  fallback?: ReactNode;
}

export const RequirePermission: React.FC<RequirePermissionProps> = ({ 
  permission, 
  children, 
  fallback = null 
}) => {
  const { hasPermission } = usePermission();
  
  return hasPermission(permission) ? <>{children}</> : <>{fallback}</>;
};

interface RequireRoleProps {
  role: Role;
  children: ReactNode;
  fallback?: ReactNode;
}

export const RequireRole: React.FC<RequireRoleProps> = ({ 
  role, 
  children, 
  fallback = null 
}) => {
  const { hasRole } = usePermission();
  
  return hasRole(role) ? <>{children}</> : <>{fallback}</>;
};

interface RequireAnyPermissionProps {
  permissions: Permission[];
  children: ReactNode;
  fallback?: ReactNode;
}

export const RequireAnyPermission: React.FC<RequireAnyPermissionProps> = ({ 
  permissions, 
  children, 
  fallback = null 
}) => {
  const { hasAnyPermission } = usePermission();
  
  return hasAnyPermission(permissions) ? <>{children}</> : <>{fallback}</>;
};

interface RequireAllPermissionsProps {
  permissions: Permission[];
  children: ReactNode;
  fallback?: ReactNode;
}

export const RequireAllPermissions: React.FC<RequireAllPermissionsProps> = ({ 
  permissions, 
  children, 
  fallback = null 
}) => {
  const { hasAllPermissions } = usePermission();
  
  return hasAllPermissions(permissions) ? <>{children}</> : <>{fallback}</>;
}; 