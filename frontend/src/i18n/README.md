# Internacionalización (i18n) - SkyGuard

Este documento explica cómo usar el sistema de internacionalización implementado con react-i18next en la aplicación SkyGuard.

## 🌐 Idiomas Soportados

- **Español (es)** - Idioma por defecto
- **Inglés (en)** - English
- **Portugués (pt)** - Português

## 📁 Estructura de Archivos

```
src/i18n/
├── index.ts                    # Configuración principal
├── locales/
│   ├── es/translation.json    # Traducciones en español
│   ├── en/translation.json    # Traducciones en inglés
│   └── pt/translation.json    # Traducciones en portugués
├── hooks/
│   └── useLanguage.tsx        # Hook personalizado
├── components/
│   └── LanguageSelector/      # Selector de idiomas
└── types/
    └── i18n.ts               # Tipos TypeScript
```

## 🚀 Uso Básico

### 1. Importar useTranslation

```tsx
import { useTranslation } from 'react-i18next';

function MiComponente() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('navigation.dashboard')}</h1>
      <p>{t('dashboard.welcome')}</p>
    </div>
  );
}
```

### 2. Hook Personalizado useLanguage

```tsx
import useLanguage from '../hooks/useLanguage';

function MiComponente() {
  const { changeLanguage, currentLanguage, getAvailableLanguages } = useLanguage();
  
  const handleLanguageChange = (lang: string) => {
    changeLanguage(lang);
  };
  
  return (
    <select value={currentLanguage} onChange={(e) => handleLanguageChange(e.target.value)}>
      {getAvailableLanguages().map(lang => (
        <option key={lang.code} value={lang.code}>{lang.name}</option>
      ))}
    </select>
  );
}
```

### 3. Componente LanguageSelector

```tsx
import LanguageSelector from '../components/LanguageSelector';

function ConfiguracionPage() {
  return (
    <div>
      <h1>Configuración</h1>
      <LanguageSelector 
        variant="outlined"
        size="medium"
        fullWidth={true}
        showLabel={true}
      />
    </div>
  );
}
```

## 📋 Traducciones por Módulo

### Dashboard
```tsx
// Títulos y estadísticas
t('dashboard.title')           // "Dashboard GPS"
t('dashboard.totalDevices')    // "Total de Dispositivos"
t('dashboard.onlineDevices')   // "Dispositivos en Línea"
t('dashboard.realTime')        // "En Vivo"
t('dashboard.lastUpdate')      // "Última actualización"
```

### Dispositivos GPS
```tsx
// Gestión de dispositivos
t('devices.title')             // "Dispositivos GPS"
t('devices.addDevice')         // "Agregar Dispositivo"
t('devices.online')            // "En línea"
t('devices.testConnection')    // "Probar Conexión"
t('devices.connectionTest.testing') // "Probando conexión..."
```

### Vehículos
```tsx
// Gestión de vehículos
t('vehicles.title')            // "Vehículos"
t('vehicles.addVehicle')       // "Agregar Vehículo"
t('vehicles.plate')            // "Placa"
t('vehicles.status.active')    // "Activo"
t('vehicles.types.car')        // "Automóvil"
```

### Conductores
```tsx
// Gestión de conductores
t('drivers.title')             // "Conductores"
t('drivers.addDriver')         // "Agregar Conductor"
t('drivers.fullName')          // "Nombre Completo"
t('drivers.licenseNumber')     // "Número de Licencia"
```

### Reportes
```tsx
// Sistema de reportes
t('reports.title')             // "Reportes"
t('reports.generate')          // "Generar Reporte"
t('reports.types.tracking')    // "Seguimiento"
t('reports.status.completed')  // "Completado"
```

### Monitoreo
```tsx
// Monitoreo en tiempo real
t('monitoring.title')          // "Monitoreo"
t('monitoring.liveTracking')   // "Seguimiento en Vivo"
t('monitoring.alertTypes.speed') // "Velocidad"
```

### Configuración
```tsx
// Configuración de la aplicación
t('configuration.title')       // "Configuración"
t('configuration.language')    // "Idioma"
t('configuration.themes.light') // "Claro"
t('configuration.languages.es') // "Español"
```

## 🔧 Funciones Comunes

### Mensajes Comunes
```tsx
t('common.save')              // "Guardar"
t('common.cancel')            // "Cancelar"
t('common.loading')           // "Cargando..."
t('common.error')             // "Error"
t('common.success')           // "Éxito"
```

### Validaciones
```tsx
t('validation.required')      // "Este campo es obligatorio"
t('validation.email')         // "Debe ser un email válido"
```

### Errores
```tsx
t('errors.network')           // "Error de conexión de red"
t('errors.unauthorized')      // "No autorizado"
```

## 💡 Interpolación

Usa variables en las traducciones:

```tsx
// En translation.json
{
  "validation": {
    "minLength": "Debe tener al menos {{min}} caracteres"
  }
}

// En el componente
t('validation.minLength', { min: 6 })
// Resultado: "Debe tener al menos 6 caracteres"
```

## 🎯 Mejores Prácticas

### 1. Estructura Jerárquica
Organiza las traducciones por módulo y funcionalidad:
```json
{
  "devices": {
    "management": {
      "title": "Gestión de Dispositivos",
      "actions": {
        "add": "Agregar",
        "edit": "Editar"
      }
    }
  }
}
```

### 2. Valores por Defecto
Siempre proporciona un valor por defecto:
```tsx
t('devices.title', 'Dispositivos GPS')
```

### 3. Consistencia
Usa los mismos términos en todos los módulos:
- "Agregar" para crear nuevos elementos
- "Editar" para modificar existentes
- "Eliminar" para borrar

### 4. Pluralización
Para textos que cambian según cantidad:
```json
{
  "devices": {
    "count_one": "{{count}} dispositivo",
    "count_other": "{{count}} dispositivos"
  }
}
```

## 🔄 Cambio de Idioma

El cambio de idioma es automático y persistente:

1. **Automático**: Detecta el idioma del navegador
2. **Persistente**: Se guarda en localStorage
3. **Inmediato**: Los cambios se aplican instantáneamente

## 🧪 Agregar Nuevas Traducciones

### 1. Agregar a los archivos JSON
```json
// es/translation.json
{
  "newModule": {
    "title": "Nuevo Módulo",
    "description": "Descripción del nuevo módulo"
  }
}
```

### 2. Usar en el componente
```tsx
function NuevoModulo() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('newModule.title')}</h1>
      <p>{t('newModule.description')}</p>
    </div>
  );
}
```

## 🌍 Extensión a Otros Idiomas

Para agregar un nuevo idioma:

1. Crear archivo `src/i18n/locales/[código]/translation.json`
2. Agregar al array de recursos en `src/i18n/index.ts`
3. Actualizar el componente `LanguageSelector`
4. Agregar las traducciones correspondientes

---

¡Con este sistema de internacionalización, SkyGuard puede ser usado por usuarios de todo el mundo! 🌍 