import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import { useAuth } from './AuthProvider';
import { usePermission } from './PermissionProvider';
import { useLanguage } from './LanguageProvider';

// ============================================================================
// ROUTER TYPES - Tipos para el router
// ============================================================================

export interface Route {
  path: string;
  name: string;
  component: React.ComponentType<any>;
  exact?: boolean;
  strict?: boolean;
  sensitive?: boolean;
  meta?: {
    title?: string;
    description?: string;
    icon?: string;
    breadcrumb?: string;
    requiresAuth?: boolean;
    permissions?: string[];
    roles?: string[];
    layout?: string;
    sidebar?: boolean;
    menu?: boolean;
    order?: number;
    badge?: string | number;
    badgeColor?: string;
    hidden?: boolean;
    cache?: boolean;
    keepAlive?: boolean;
  };
  children?: Route[];
}

export interface RouteMatch {
  path: string;
  url: string;
  isExact: boolean;
  params: Record<string, string>;
  route: Route;
}

export interface RouterState {
  location: {
    pathname: string;
    search: string;
    hash: string;
    state?: any;
  };
  history: Array<{
    pathname: string;
    search: string;
    hash: string;
    timestamp: number;
  }>;
  currentRoute: Route | null;
  matchedRoutes: RouteMatch[];
  isLoading: boolean;
  error: Error | null;
}

export interface RouterContextType {
  // Estado
  state: RouterState;
  
  // Métodos de navegación
  navigate: (to: string, options?: { replace?: boolean; state?: any }) => void;
  goBack: () => void;
  goForward: () => void;
  go: (n: number) => void;
  
  // Métodos de rutas
  getRoute: (path: string) => Route | null;
  getRoutes: () => Route[];
  addRoute: (route: Route) => void;
  removeRoute: (path: string) => void;
  updateRoute: (path: string, updates: Partial<Route>) => void;
  
  // Métodos de utilidad
  isActive: (path: string) => boolean;
  isExact: (path: string) => boolean;
  getBreadcrumbs: () => Array<{ path: string; name: string; active: boolean }>;
  getMenuItems: () => Route[];
  getSidebarItems: () => Route[];
  
  // Métodos de guardias
  canAccess: (route: Route) => boolean;
  requireAuth: (route: Route) => boolean;
  requirePermission: (route: Route, permission: string) => boolean;
  requireRole: (route: Route, role: string) => boolean;
  
  // Métodos de historial
  getHistory: () => RouterState['history'];
  clearHistory: () => void;
  getPreviousRoute: () => string | null;
  getNextRoute: () => string | null;
  
  // Métodos de utilidad
  generatePath: (path: string, params?: Record<string, string>) => string;
  parsePath: (path: string) => { pathname: string; search: string; hash: string };
  resolvePath: (to: string, from?: string) => string;
}

// ============================================================================
// ROUTER CONTEXT - Contexto para el router
// ============================================================================

const RouterContext = createContext<RouterContextType | undefined>(undefined);

// ============================================================================
// ROUTER PROVIDER - Provider para el router
// ============================================================================

interface RouterProviderProps {
  children: ReactNode;
  routes: Route[];
  basename?: string;
  historyLimit?: number;
  enableHistory?: boolean;
  enableGuards?: boolean;
  enableBreadcrumbs?: boolean;
  enableMenu?: boolean;
  enableSidebar?: boolean;
}

export const RouterProvider: React.FC<RouterProviderProps> = ({
  children,
  routes,
  basename = '',
  historyLimit = 50,
  enableHistory = true,
  enableGuards = true,
  enableBreadcrumbs = true,
  enableMenu = true,
  enableSidebar = true,
}) => {
  const { user, isAuthenticated } = useAuth();
  const { hasPermission, hasRole } = usePermission();
  const { t } = useLanguage();
  
  const [state, setState] = useState<RouterState>({
    location: {
      pathname: window.location.pathname,
      search: window.location.search,
      hash: window.location.hash,
    },
    history: [],
    currentRoute: null,
    matchedRoutes: [],
    isLoading: false,
    error: null,
  });

  const routesRef = useRef<Route[]>(routes);
  const historyIndexRef = useRef<number>(-1);

  // Normalizar path
  const normalizePath = (path: string): string => {
    const normalized = path.startsWith('/') ? path : `/${path}`;
    return basename ? `${basename}${normalized}` : normalized;
  };

  // Buscar ruta por path
  const findRoute = (path: string, routes: Route[]): Route | null => {
    for (const route of routes) {
      if (route.path === path) {
        return route;
      }
      if (route.children) {
        const childRoute = findRoute(path, route.children);
        if (childRoute) {
          return childRoute;
        }
      }
    }
    return null;
  };

  // Hacer match de rutas
  const matchRoutes = (pathname: string): RouteMatch[] => {
    const matches: RouteMatch[] = [];
    
    const matchRoute = (route: Route, parentPath = ''): void => {
      const fullPath = parentPath + route.path;
      
      if (route.exact) {
        if (pathname === fullPath) {
          matches.push({
            path: fullPath,
            url: fullPath,
            isExact: true,
            params: {},
            route,
          });
        }
      } else {
        if (pathname.startsWith(fullPath)) {
          matches.push({
            path: fullPath,
            url: fullPath,
            isExact: pathname === fullPath,
            params: {},
            route,
          });
        }
      }
      
      if (route.children) {
        route.children.forEach(child => matchRoute(child, fullPath));
      }
    };
    
    routesRef.current.forEach(route => matchRoute(route));
    return matches;
  };

  // Verificar si puede acceder a una ruta
  const canAccess = (route: Route): boolean => {
    if (!enableGuards) return true;
    
    // Verificar autenticación
    if (route.meta?.requiresAuth && !isAuthenticated) {
      return false;
    }
    
    // Verificar permisos
    if (route.meta?.permissions && route.meta.permissions.length > 0) {
      if (!route.meta.permissions.some(permission => hasPermission(permission as any))) {
        return false;
      }
    }
    
    // Verificar roles
    if (route.meta?.roles && route.meta.roles.length > 0) {
      if (!route.meta.roles.some(role => hasRole(role as any))) {
        return false;
      }
    }
    
    return true;
  };

  // Verificar si requiere autenticación
  const requireAuth = (route: Route): boolean => {
    return route.meta?.requiresAuth || false;
  };

  // Verificar si requiere permiso
  const requirePermission = (route: Route, permission: string): boolean => {
    return route.meta?.permissions?.includes(permission) || false;
  };

  // Verificar si requiere rol
  const requireRole = (route: Route, role: string): boolean => {
    return route.meta?.roles?.includes(role) || false;
  };

  // Navegar a una ruta
  const navigate = (to: string, options: { replace?: boolean; state?: any } = {}) => {
    const { replace = false, state } = options;
    const pathname = normalizePath(to);
    
    // Verificar si la ruta existe
    const route = findRoute(pathname, routesRef.current);
    if (!route) {
      console.warn(`Route not found: ${pathname}`);
      return;
    }
    
    // Verificar acceso
    if (!canAccess(route)) {
      console.warn(`Access denied to route: ${pathname}`);
      return;
    }
    
    // Actualizar historial
    const newLocation = { pathname, search: '', hash: '', state };
    
    if (replace) {
      // Reemplazar entrada actual
      setState(prev => ({
        ...prev,
        location: newLocation,
        currentRoute: route,
        matchedRoutes: matchRoutes(pathname),
        history: prev.history.slice(0, historyIndexRef.current).concat({
          pathname,
          search: '',
          hash: '',
          timestamp: Date.now(),
        }),
      }));
    } else {
      // Agregar nueva entrada
      setState(prev => {
        const newHistory = prev.history.concat({
          pathname,
          search: '',
          hash: '',
          timestamp: Date.now(),
        }).slice(-historyLimit);
        
        historyIndexRef.current = newHistory.length - 1;
        
        return {
          ...prev,
          location: newLocation,
          currentRoute: route,
          matchedRoutes: matchRoutes(pathname),
          history: newHistory,
        };
      });
    }
    
    // Actualizar URL del navegador
    window.history[replace ? 'replaceState' : 'pushState'](state, '', pathname);
    
    // Actualizar título de la página
    if (route.meta?.title) {
      document.title = t(route.meta.title);
    }
  };

  // Ir hacia atrás
  const goBack = () => {
    if (historyIndexRef.current > 0) {
      historyIndexRef.current--;
      const historyEntry = state.history[historyIndexRef.current];
      if (historyEntry) {
        navigate(historyEntry.pathname, { replace: true });
      }
    }
  };

  // Ir hacia adelante
  const goForward = () => {
    if (historyIndexRef.current < state.history.length - 1) {
      historyIndexRef.current++;
      const historyEntry = state.history[historyIndexRef.current];
      if (historyEntry) {
        navigate(historyEntry.pathname, { replace: true });
      }
    }
  };

  // Ir a una posición específica
  const go = (n: number) => {
    const newIndex = historyIndexRef.current + n;
    if (newIndex >= 0 && newIndex < state.history.length) {
      historyIndexRef.current = newIndex;
      const historyEntry = state.history[newIndex];
      if (historyEntry) {
        navigate(historyEntry.pathname, { replace: true });
      }
    }
  };

  // Obtener ruta
  const getRoute = (path: string): Route | null => {
    return findRoute(normalizePath(path), routesRef.current);
  };

  // Obtener todas las rutas
  const getRoutes = (): Route[] => {
    return routesRef.current;
  };

  // Agregar ruta
  const addRoute = (route: Route) => {
    routesRef.current = [...routesRef.current, route];
  };

  // Remover ruta
  const removeRoute = (path: string) => {
    routesRef.current = routesRef.current.filter(route => route.path !== path);
  };

  // Actualizar ruta
  const updateRoute = (path: string, updates: Partial<Route>) => {
    routesRef.current = routesRef.current.map(route => 
      route.path === path ? { ...route, ...updates } : route
    );
  };

  // Verificar si una ruta está activa
  const isActive = (path: string): boolean => {
    return state.location.pathname.startsWith(normalizePath(path));
  };

  // Verificar si una ruta es exacta
  const isExact = (path: string): boolean => {
    return state.location.pathname === normalizePath(path);
  };

  // Obtener breadcrumbs
  const getBreadcrumbs = (): Array<{ path: string; name: string; active: boolean }> => {
    if (!enableBreadcrumbs) return [];
    
    const breadcrumbs: Array<{ path: string; name: string; active: boolean }> = [];
    const currentPath = state.location.pathname;
    
    // Agregar breadcrumb raíz
    breadcrumbs.push({
      path: '/',
      name: t('nav.dashboard'),
      active: currentPath === '/',
    });
    
    // Agregar breadcrumbs de rutas anidadas
    let currentPathParts = currentPath.split('/').filter(Boolean);
    let accumulatedPath = '';
    
    currentPathParts.forEach((part, index) => {
      accumulatedPath += `/${part}`;
      const route = findRoute(accumulatedPath, routesRef.current);
      
      if (route && route.meta?.breadcrumb) {
        breadcrumbs.push({
          path: accumulatedPath,
          name: t(route.meta.breadcrumb),
          active: index === currentPathParts.length - 1,
        });
      }
    });
    
    return breadcrumbs;
  };

  // Obtener elementos del menú
  const getMenuItems = (): Route[] => {
    if (!enableMenu) return [];
    
    return routesRef.current
      .filter(route => route.meta?.menu !== false && !route.meta?.hidden)
      .filter(route => canAccess(route))
      .sort((a, b) => (a.meta?.order || 0) - (b.meta?.order || 0));
  };

  // Obtener elementos de la sidebar
  const getSidebarItems = (): Route[] => {
    if (!enableSidebar) return [];
    
    return routesRef.current
      .filter(route => route.meta?.sidebar !== false && !route.meta?.hidden)
      .filter(route => canAccess(route))
      .sort((a, b) => (a.meta?.order || 0) - (b.meta?.order || 0));
  };

  // Obtener historial
  const getHistory = (): RouterState['history'] => {
    return state.history;
  };

  // Limpiar historial
  const clearHistory = () => {
    setState(prev => ({ ...prev, history: [] }));
    historyIndexRef.current = -1;
  };

  // Obtener ruta anterior
  const getPreviousRoute = (): string | null => {
    if (historyIndexRef.current > 0) {
      return state.history[historyIndexRef.current - 1]?.pathname || null;
    }
    return null;
  };

  // Obtener siguiente ruta
  const getNextRoute = (): string | null => {
    if (historyIndexRef.current < state.history.length - 1) {
      return state.history[historyIndexRef.current + 1]?.pathname || null;
    }
    return null;
  };

  // Generar path con parámetros
  const generatePath = (path: string, params: Record<string, string> = {}): string => {
    let generatedPath = path;
    
    Object.entries(params).forEach(([key, value]) => {
      generatedPath = generatedPath.replace(`:${key}`, value);
    });
    
    return normalizePath(generatedPath);
  };

  // Parsear path
  const parsePath = (path: string): { pathname: string; search: string; hash: string } => {
    const url = new URL(path, window.location.origin);
    return {
      pathname: url.pathname,
      search: url.search,
      hash: url.hash,
    };
  };

  // Resolver path
  const resolvePath = (to: string, from?: string): string => {
    if (to.startsWith('/')) {
      return normalizePath(to);
    }
    
    const basePath = from || state.location.pathname;
    const resolved = new URL(to, `http://localhost${basePath}`).pathname;
    return normalizePath(resolved);
  };

  // Manejar cambios de navegación del navegador
  useEffect(() => {
    const handlePopState = (event: PopStateEvent) => {
      const pathname = window.location.pathname;
      const route = findRoute(pathname, routesRef.current);
      
      if (route && canAccess(route)) {
        setState(prev => ({
          ...prev,
          location: {
            pathname,
            search: window.location.search,
            hash: window.location.hash,
            state: event.state,
          },
          currentRoute: route,
          matchedRoutes: matchRoutes(pathname),
        }));
      }
    };

    window.addEventListener('popstate', handlePopState);
    
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  // Inicializar ruta actual
  useEffect(() => {
    const pathname = window.location.pathname;
    const route = findRoute(pathname, routesRef.current);
    
    if (route && canAccess(route)) {
      setState(prev => ({
        ...prev,
        currentRoute: route,
        matchedRoutes: matchRoutes(pathname),
        history: enableHistory ? [{
          pathname,
          search: window.location.search,
          hash: window.location.hash,
          timestamp: Date.now(),
        }] : [],
      }));
      
      historyIndexRef.current = 0;
    }
  }, []);

  const value: RouterContextType = {
    state,
    navigate,
    goBack,
    goForward,
    go,
    getRoute,
    getRoutes,
    addRoute,
    removeRoute,
    updateRoute,
    isActive,
    isExact,
    getBreadcrumbs,
    getMenuItems,
    getSidebarItems,
    canAccess,
    requireAuth,
    requirePermission,
    requireRole,
    getHistory,
    clearHistory,
    getPreviousRoute,
    getNextRoute,
    generatePath,
    parsePath,
    resolvePath,
  };

  return (
    <RouterContext.Provider value={value}>
      {children}
    </RouterContext.Provider>
  );
};

// ============================================================================
// ROUTER HOOK - Hook para usar el contexto del router
// ============================================================================

export const useRouter = () => {
  const context = useContext(RouterContext);
  
  if (context === undefined) {
    throw new Error('useRouter must be used within a RouterProvider');
  }
  
  return context;
};

// ============================================================================
// ROUTER HOOKS ESPECÍFICOS - Hooks para casos de uso específicos
// ============================================================================

export const useNavigation = () => {
  const { navigate, goBack, goForward, go } = useRouter();
  return { navigate, goBack, goForward, go };
};

export const useRoute = (path: string) => {
  const { getRoute, isActive, isExact } = useRouter();
  const route = getRoute(path);
  
  return {
    route,
    isActive: isActive(path),
    isExact: isExact(path),
  };
};

export const useBreadcrumbs = () => {
  const { getBreadcrumbs } = useRouter();
  return getBreadcrumbs();
};

export const useMenu = () => {
  const { getMenuItems, getSidebarItems } = useRouter();
  return {
    menuItems: getMenuItems(),
    sidebarItems: getSidebarItems(),
  };
};

export const useRouteGuard = () => {
  const { canAccess, requireAuth, requirePermission, requireRole } = useRouter();
  return { canAccess, requireAuth, requirePermission, requireRole };
}; 