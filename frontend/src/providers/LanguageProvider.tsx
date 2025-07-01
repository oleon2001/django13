import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// ============================================================================
// LANGUAGE TYPES - Tipos para el idioma
// ============================================================================

export type Language = 'es' | 'en' | 'fr' | 'pt';

export interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, params?: Record<string, any>) => string;
  formatDate: (date: Date | string, options?: Intl.DateTimeFormatOptions) => string;
  formatNumber: (number: number, options?: Intl.NumberFormatOptions) => string;
  formatCurrency: (amount: number, currency?: string) => string;
}

// ============================================================================
// TRANSLATIONS - Traducciones disponibles
// ============================================================================

const translations: Record<Language, Record<string, string>> = {
  es: {
    // Navegación
    'nav.dashboard': 'Panel de Control',
    'nav.devices': 'Dispositivos',
    'nav.vehicles': 'Vehículos',
    'nav.drivers': 'Conductores',
    'nav.routes': 'Rutas',
    'nav.geofences': 'Geocercas',
    'nav.reports': 'Reportes',
    'nav.settings': 'Configuración',
    'nav.profile': 'Perfil',
    'nav.logout': 'Cerrar Sesión',
    
    // Dashboard
    'dashboard.title': 'Panel de Control',
    'dashboard.total_devices': 'Total de Dispositivos',
    'dashboard.active_devices': 'Dispositivos Activos',
    'dashboard.offline_devices': 'Dispositivos Offline',
    'dashboard.total_vehicles': 'Total de Vehículos',
    'dashboard.active_vehicles': 'Vehículos Activos',
    'dashboard.total_drivers': 'Total de Conductores',
    'dashboard.active_drivers': 'Conductores Activos',
    'dashboard.total_routes': 'Total de Rutas',
    'dashboard.active_routes': 'Rutas Activas',
    'dashboard.total_geofences': 'Total de Geocercas',
    'dashboard.active_geofences': 'Geocercas Activas',
    
    // Dispositivos
    'devices.title': 'Dispositivos',
    'devices.add': 'Agregar Dispositivo',
    'devices.edit': 'Editar Dispositivo',
    'devices.delete': 'Eliminar Dispositivo',
    'devices.name': 'Nombre',
    'devices.type': 'Tipo',
    'devices.status': 'Estado',
    'devices.location': 'Ubicación',
    'devices.battery': 'Batería',
    'devices.signal': 'Señal',
    'devices.last_seen': 'Última Vez',
    'devices.actions': 'Acciones',
    
    // Vehículos
    'vehicles.title': 'Vehículos',
    'vehicles.add': 'Agregar Vehículo',
    'vehicles.edit': 'Editar Vehículo',
    'vehicles.delete': 'Eliminar Vehículo',
    'vehicles.plate': 'Placa',
    'vehicles.brand': 'Marca',
    'vehicles.model': 'Modelo',
    'vehicles.year': 'Año',
    'vehicles.driver': 'Conductor',
    'vehicles.device': 'Dispositivo',
    
    // Conductores
    'drivers.title': 'Conductores',
    'drivers.add': 'Agregar Conductor',
    'drivers.edit': 'Editar Conductor',
    'drivers.delete': 'Eliminar Conductor',
    'drivers.name': 'Nombre',
    'drivers.license': 'Licencia',
    'drivers.phone': 'Teléfono',
    'drivers.email': 'Email',
    'drivers.status': 'Estado',
    
    // Rutas
    'routes.title': 'Rutas',
    'routes.add': 'Agregar Ruta',
    'routes.edit': 'Editar Ruta',
    'routes.delete': 'Eliminar Ruta',
    'routes.name': 'Nombre',
    'routes.description': 'Descripción',
    'routes.start_point': 'Punto de Inicio',
    'routes.end_point': 'Punto Final',
    'routes.distance': 'Distancia',
    'routes.duration': 'Duración',
    
    // Geocercas
    'geofences.title': 'Geocercas',
    'geofences.add': 'Agregar Geocerca',
    'geofences.edit': 'Editar Geocerca',
    'geofences.delete': 'Eliminar Geocerca',
    'geofences.name': 'Nombre',
    'geofences.type': 'Tipo',
    'geofences.radius': 'Radio',
    'geofences.center': 'Centro',
    'geofences.status': 'Estado',
    
    // Reportes
    'reports.title': 'Reportes',
    'reports.generate': 'Generar Reporte',
    'reports.download': 'Descargar',
    'reports.export': 'Exportar',
    'reports.type': 'Tipo de Reporte',
    'reports.date_range': 'Rango de Fechas',
    'reports.filters': 'Filtros',
    
    // Estados
    'status.active': 'Activo',
    'status.inactive': 'Inactivo',
    'status.online': 'En Línea',
    'status.offline': 'Offline',
    'status.warning': 'Advertencia',
    'status.error': 'Error',
    'status.success': 'Éxito',
    
    // Acciones
    'actions.view': 'Ver',
    'actions.edit': 'Editar',
    'actions.delete': 'Eliminar',
    'actions.save': 'Guardar',
    'actions.cancel': 'Cancelar',
    'actions.confirm': 'Confirmar',
    'actions.close': 'Cerrar',
    'actions.refresh': 'Actualizar',
    'actions.search': 'Buscar',
    'actions.filter': 'Filtrar',
    'actions.export': 'Exportar',
    'actions.import': 'Importar',
    
    // Mensajes
    'message.success': 'Operación exitosa',
    'message.error': 'Error en la operación',
    'message.warning': 'Advertencia',
    'message.info': 'Información',
    'message.confirm_delete': '¿Está seguro de que desea eliminar este elemento?',
    'message.loading': 'Cargando...',
    'message.no_data': 'No hay datos disponibles',
    'message.no_results': 'No se encontraron resultados',
    
    // Formularios
    'form.required': 'Este campo es requerido',
    'form.invalid_email': 'Email inválido',
    'form.invalid_phone': 'Teléfono inválido',
    'form.password_mismatch': 'Las contraseñas no coinciden',
    'form.min_length': 'Mínimo {min} caracteres',
    'form.max_length': 'Máximo {max} caracteres',
    
    // Fechas
    'date.today': 'Hoy',
    'date.yesterday': 'Ayer',
    'date.this_week': 'Esta Semana',
    'date.last_week': 'Semana Pasada',
    'date.this_month': 'Este Mes',
    'date.last_month': 'Mes Pasado',
    'date.this_year': 'Este Año',
    'date.last_year': 'Año Pasado',
    
    // Tiempo
    'time.seconds': 'segundos',
    'time.minutes': 'minutos',
    'time.hours': 'horas',
    'time.days': 'días',
    'time.weeks': 'semanas',
    'time.months': 'meses',
    'time.years': 'años',
    
    // Unidades
    'unit.km': 'km',
    'unit.miles': 'millas',
    'unit.meters': 'metros',
    'unit.feet': 'pies',
    'unit.kmh': 'km/h',
    'unit.mph': 'mph',
    'unit.liters': 'litros',
    'unit.gallons': 'galones',
    'unit.percent': '%',
    'unit.degrees': '°',
  },
  
  en: {
    // Navigation
    'nav.dashboard': 'Dashboard',
    'nav.devices': 'Devices',
    'nav.vehicles': 'Vehicles',
    'nav.drivers': 'Drivers',
    'nav.routes': 'Routes',
    'nav.geofences': 'Geofences',
    'nav.reports': 'Reports',
    'nav.settings': 'Settings',
    'nav.profile': 'Profile',
    'nav.logout': 'Logout',
    
    // Dashboard
    'dashboard.title': 'Dashboard',
    'dashboard.total_devices': 'Total Devices',
    'dashboard.active_devices': 'Active Devices',
    'dashboard.offline_devices': 'Offline Devices',
    'dashboard.total_vehicles': 'Total Vehicles',
    'dashboard.active_vehicles': 'Active Vehicles',
    'dashboard.total_drivers': 'Total Drivers',
    'dashboard.active_drivers': 'Active Drivers',
    'dashboard.total_routes': 'Total Routes',
    'dashboard.active_routes': 'Active Routes',
    'dashboard.total_geofences': 'Total Geofences',
    'dashboard.active_geofences': 'Active Geofences',
    
    // Devices
    'devices.title': 'Devices',
    'devices.add': 'Add Device',
    'devices.edit': 'Edit Device',
    'devices.delete': 'Delete Device',
    'devices.name': 'Name',
    'devices.type': 'Type',
    'devices.status': 'Status',
    'devices.location': 'Location',
    'devices.battery': 'Battery',
    'devices.signal': 'Signal',
    'devices.last_seen': 'Last Seen',
    'devices.actions': 'Actions',
    
    // Vehicles
    'vehicles.title': 'Vehicles',
    'vehicles.add': 'Add Vehicle',
    'vehicles.edit': 'Edit Vehicle',
    'vehicles.delete': 'Delete Vehicle',
    'vehicles.plate': 'Plate',
    'vehicles.brand': 'Brand',
    'vehicles.model': 'Model',
    'vehicles.year': 'Year',
    'vehicles.driver': 'Driver',
    'vehicles.device': 'Device',
    
    // Drivers
    'drivers.title': 'Drivers',
    'drivers.add': 'Add Driver',
    'drivers.edit': 'Edit Driver',
    'drivers.delete': 'Delete Driver',
    'drivers.name': 'Name',
    'drivers.license': 'License',
    'drivers.phone': 'Phone',
    'drivers.email': 'Email',
    'drivers.status': 'Status',
    
    // Routes
    'routes.title': 'Routes',
    'routes.add': 'Add Route',
    'routes.edit': 'Edit Route',
    'routes.delete': 'Delete Route',
    'routes.name': 'Name',
    'routes.description': 'Description',
    'routes.start_point': 'Start Point',
    'routes.end_point': 'End Point',
    'routes.distance': 'Distance',
    'routes.duration': 'Duration',
    
    // Geofences
    'geofences.title': 'Geofences',
    'geofences.add': 'Add Geofence',
    'geofences.edit': 'Edit Geofence',
    'geofences.delete': 'Delete Geofence',
    'geofences.name': 'Name',
    'geofences.type': 'Type',
    'geofences.radius': 'Radius',
    'geofences.center': 'Center',
    'geofences.status': 'Status',
    
    // Reports
    'reports.title': 'Reports',
    'reports.generate': 'Generate Report',
    'reports.download': 'Download',
    'reports.export': 'Export',
    'reports.type': 'Report Type',
    'reports.date_range': 'Date Range',
    'reports.filters': 'Filters',
    
    // Status
    'status.active': 'Active',
    'status.inactive': 'Inactive',
    'status.online': 'Online',
    'status.offline': 'Offline',
    'status.warning': 'Warning',
    'status.error': 'Error',
    'status.success': 'Success',
    
    // Actions
    'actions.view': 'View',
    'actions.edit': 'Edit',
    'actions.delete': 'Delete',
    'actions.save': 'Save',
    'actions.cancel': 'Cancel',
    'actions.confirm': 'Confirm',
    'actions.close': 'Close',
    'actions.refresh': 'Refresh',
    'actions.search': 'Search',
    'actions.filter': 'Filter',
    'actions.export': 'Export',
    'actions.import': 'Import',
    
    // Messages
    'message.success': 'Operation successful',
    'message.error': 'Operation failed',
    'message.warning': 'Warning',
    'message.info': 'Information',
    'message.confirm_delete': 'Are you sure you want to delete this item?',
    'message.loading': 'Loading...',
    'message.no_data': 'No data available',
    'message.no_results': 'No results found',
    
    // Forms
    'form.required': 'This field is required',
    'form.invalid_email': 'Invalid email',
    'form.invalid_phone': 'Invalid phone number',
    'form.password_mismatch': 'Passwords do not match',
    'form.min_length': 'Minimum {min} characters',
    'form.max_length': 'Maximum {max} characters',
    
    // Dates
    'date.today': 'Today',
    'date.yesterday': 'Yesterday',
    'date.this_week': 'This Week',
    'date.last_week': 'Last Week',
    'date.this_month': 'This Month',
    'date.last_month': 'Last Month',
    'date.this_year': 'This Year',
    'date.last_year': 'Last Year',
    
    // Time
    'time.seconds': 'seconds',
    'time.minutes': 'minutes',
    'time.hours': 'hours',
    'time.days': 'days',
    'time.weeks': 'weeks',
    'time.months': 'months',
    'time.years': 'years',
    
    // Units
    'unit.km': 'km',
    'unit.miles': 'miles',
    'unit.meters': 'meters',
    'unit.feet': 'feet',
    'unit.kmh': 'km/h',
    'unit.mph': 'mph',
    'unit.liters': 'liters',
    'unit.gallons': 'gallons',
    'unit.percent': '%',
    'unit.degrees': '°',
  },
  
  fr: {
    // Navigation
    'nav.dashboard': 'Tableau de Bord',
    'nav.devices': 'Appareils',
    'nav.vehicles': 'Véhicules',
    'nav.drivers': 'Conducteurs',
    'nav.routes': 'Itinéraires',
    'nav.geofences': 'Géofences',
    'nav.reports': 'Rapports',
    'nav.settings': 'Paramètres',
    'nav.profile': 'Profil',
    'nav.logout': 'Déconnexion',
    
    // Dashboard
    'dashboard.title': 'Tableau de Bord',
    'dashboard.total_devices': 'Total des Appareils',
    'dashboard.active_devices': 'Appareils Actifs',
    'dashboard.offline_devices': 'Appareils Hors Ligne',
    'dashboard.total_vehicles': 'Total des Véhicules',
    'dashboard.active_vehicles': 'Véhicules Actifs',
    'dashboard.total_drivers': 'Total des Conducteurs',
    'dashboard.active_drivers': 'Conducteurs Actifs',
    'dashboard.total_routes': 'Total des Itinéraires',
    'dashboard.active_routes': 'Itinéraires Actifs',
    'dashboard.total_geofences': 'Total des Géofences',
    'dashboard.active_geofences': 'Géofences Actives',
    
    // Estados
    'status.active': 'Actif',
    'status.inactive': 'Inactif',
    'status.online': 'En Ligne',
    'status.offline': 'Hors Ligne',
    'status.warning': 'Avertissement',
    'status.error': 'Erreur',
    'status.success': 'Succès',
    
    // Acciones
    'actions.view': 'Voir',
    'actions.edit': 'Modifier',
    'actions.delete': 'Supprimer',
    'actions.save': 'Enregistrer',
    'actions.cancel': 'Annuler',
    'actions.confirm': 'Confirmer',
    'actions.close': 'Fermer',
    'actions.refresh': 'Actualiser',
    'actions.search': 'Rechercher',
    'actions.filter': 'Filtrer',
    'actions.export': 'Exporter',
    'actions.import': 'Importer',
    
    // Mensajes
    'message.success': 'Opération réussie',
    'message.error': 'Échec de l\'opération',
    'message.warning': 'Avertissement',
    'message.info': 'Information',
    'message.confirm_delete': 'Êtes-vous sûr de vouloir supprimer cet élément?',
    'message.loading': 'Chargement...',
    'message.no_data': 'Aucune donnée disponible',
    'message.no_results': 'Aucun résultat trouvé',
  },
  
  pt: {
    // Navegação
    'nav.dashboard': 'Painel de Controle',
    'nav.devices': 'Dispositivos',
    'nav.vehicles': 'Veículos',
    'nav.drivers': 'Motoristas',
    'nav.routes': 'Rotas',
    'nav.geofences': 'Geocercas',
    'nav.reports': 'Relatórios',
    'nav.settings': 'Configurações',
    'nav.profile': 'Perfil',
    'nav.logout': 'Sair',
    
    // Dashboard
    'dashboard.title': 'Painel de Controle',
    'dashboard.total_devices': 'Total de Dispositivos',
    'dashboard.active_devices': 'Dispositivos Ativos',
    'dashboard.offline_devices': 'Dispositivos Offline',
    'dashboard.total_vehicles': 'Total de Veículos',
    'dashboard.active_vehicles': 'Veículos Ativos',
    'dashboard.total_drivers': 'Total de Motoristas',
    'dashboard.active_drivers': 'Motoristas Ativos',
    'dashboard.total_routes': 'Total de Rotas',
    'dashboard.active_routes': 'Rotas Ativas',
    'dashboard.total_geofences': 'Total de Geocercas',
    'dashboard.active_geofences': 'Geocercas Ativas',
    
    // Estados
    'status.active': 'Ativo',
    'status.inactive': 'Inativo',
    'status.online': 'Online',
    'status.offline': 'Offline',
    'status.warning': 'Aviso',
    'status.error': 'Erro',
    'status.success': 'Sucesso',
    
    // Ações
    'actions.view': 'Ver',
    'actions.edit': 'Editar',
    'actions.delete': 'Excluir',
    'actions.save': 'Salvar',
    'actions.cancel': 'Cancelar',
    'actions.confirm': 'Confirmar',
    'actions.close': 'Fechar',
    'actions.refresh': 'Atualizar',
    'actions.search': 'Buscar',
    'actions.filter': 'Filtrar',
    'actions.export': 'Exportar',
    'actions.import': 'Importar',
    
    // Mensagens
    'message.success': 'Operação bem-sucedida',
    'message.error': 'Falha na operação',
    'message.warning': 'Aviso',
    'message.info': 'Informação',
    'message.confirm_delete': 'Tem certeza de que deseja excluir este item?',
    'message.loading': 'Carregando...',
    'message.no_data': 'Nenhum dado disponível',
    'message.no_results': 'Nenhum resultado encontrado',
  },
};

// ============================================================================
// LANGUAGE CONTEXT - Contexto para el idioma
// ============================================================================

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// ============================================================================
// LANGUAGE PROVIDER - Provider para el idioma
// ============================================================================

interface LanguageProviderProps {
  children: ReactNode;
  defaultLanguage?: Language;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ 
  children, 
  defaultLanguage = 'es' 
}) => {
  const [language, setLanguage] = useState<Language>(defaultLanguage);

  // Cargar idioma guardado
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language') as Language;
    if (savedLanguage && translations[savedLanguage]) {
      setLanguage(savedLanguage);
    }
  }, []);

  // Guardar idioma cuando cambie
  useEffect(() => {
    localStorage.setItem('language', language);
    document.documentElement.setAttribute('lang', language);
  }, [language]);

  // Función de traducción
  const t = (key: string, params?: Record<string, any>): string => {
    const translation = translations[language]?.[key] || key;
    
    if (params) {
      return translation.replace(/\{(\w+)\}/g, (match, param) => {
        return params[param] !== undefined ? String(params[param]) : match;
      });
    }
    
    return translation;
  };

  // Formatear fecha
  const formatDate = (date: Date | string, options?: Intl.DateTimeFormatOptions): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const locale = language === 'es' ? 'es-ES' : 
                   language === 'en' ? 'en-US' : 
                   language === 'fr' ? 'fr-FR' : 'pt-BR';
    
    return dateObj.toLocaleDateString(locale, options);
  };

  // Formatear número
  const formatNumber = (number: number, options?: Intl.NumberFormatOptions): string => {
    const locale = language === 'es' ? 'es-ES' : 
                   language === 'en' ? 'en-US' : 
                   language === 'fr' ? 'fr-FR' : 'pt-BR';
    
    return number.toLocaleString(locale, options);
  };

  // Formatear moneda
  const formatCurrency = (amount: number, currency = 'USD'): string => {
    const locale = language === 'es' ? 'es-ES' : 
                   language === 'en' ? 'en-US' : 
                   language === 'fr' ? 'fr-FR' : 'pt-BR';
    
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
    }).format(amount);
  };

  const value: LanguageContextType = {
    language,
    setLanguage,
    t,
    formatDate,
    formatNumber,
    formatCurrency,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

// ============================================================================
// LANGUAGE HOOK - Hook para usar el contexto del idioma
// ============================================================================

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  
  return context;
}; 