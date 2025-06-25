# Enhanced Component System

Este sistema de componentes optimizados proporciona una biblioteca moderna y reutilizable de componentes React con Material-UI, diseñados para mejorar la experiencia del usuario y el rendimiento de la aplicación.

## 🚀 Características Principales

- **Diseño Moderno**: Componentes con diseño actualizado y animaciones suaves
- **Accesibilidad**: Cumple con estándares WCAG para accesibilidad web
- **Responsive**: Adaptación automática a diferentes tamaños de pantalla
- **Performance**: Optimizados con React.memo y hooks para mejor rendimiento
- **TypeScript**: Completamente tipado para mejor experiencia de desarrollo
- **Tematización**: Integración completa con el sistema de temas de Material-UI

## 📦 Componentes Disponibles

### BaseLayout
Layout principal de la aplicación con navegación mejorada.

```tsx
import { BaseLayout } from '../components';

function App() {
  return (
    <BaseLayout>
      <YourContent />
    </BaseLayout>
  );
}
```

### EnhancedLoading
Componente de carga con múltiples variantes y animaciones.

```tsx
import { EnhancedLoading } from '../components';

// Variantes disponibles: 'default', 'minimal', 'skeleton', 'dots', 'circular'
<EnhancedLoading 
  variant="skeleton"
  module="users"
  message="Cargando usuarios..."
  size="large"
/>
```

### EnhancedCard
Sistema de tarjetas mejorado con múltiples variantes.

```tsx
import { EnhancedCard, MetricCard, ActionCard } from '../components';

// Tarjeta básica
<EnhancedCard
  title="Título"
  subtitle="Subtítulo"
  variant="elevated"
  status="success"
>
  Contenido de la tarjeta
</EnhancedCard>

// Tarjeta de métricas
<MetricCard
  title="Usuarios Activos"
  value={1234}
  trend={5.2}
  icon={<UsersIcon />}
/>

// Tarjeta de acciones
<ActionCard
  title="Configuración"
  description="Gestionar configuración del sistema"
  actions={[
    { label: 'Editar', onClick: handleEdit },
    { label: 'Eliminar', onClick: handleDelete }
  ]}
/>
```

### EnhancedForm
Sistema de formularios con validación integrada.

```tsx
import { EnhancedForm, FieldConfig } from '../components';

const fields: FieldConfig[] = [
  {
    name: 'email',
    type: 'email',
    label: 'Email',
    required: true,
    validation: (value) => {
      if (!value.includes('@')) return 'Email inválido';
      return null;
    }
  },
  {
    name: 'password',
    type: 'password',
    label: 'Contraseña',
    required: true
  },
  {
    name: 'role',
    type: 'select',
    label: 'Rol',
    options: [
      { value: 'admin', label: 'Administrador' },
      { value: 'user', label: 'Usuario' }
    ]
  }
];

<EnhancedForm
  fields={fields}
  title="Crear Usuario"
  onSubmit={handleSubmit}
  showProgress
/>
```

### EnhancedTable
Tabla avanzada con filtrado, ordenamiento y paginación.

```tsx
import { EnhancedTable, ColumnDef } from '../components';

const columns: ColumnDef[] = [
  {
    id: 'name',
    label: 'Nombre',
    accessor: 'name',
    sortable: true
  },
  {
    id: 'email',
    label: 'Email',
    accessor: 'email',
    sortable: true
  },
  {
    id: 'actions',
    label: 'Acciones',
    accessor: (row) => row.id,
    render: (value, row) => (
      <Button onClick={() => handleEdit(row)}>
        Editar
      </Button>
    )
  }
];

<EnhancedTable
  data={users}
  columns={columns}
  searchable
  selectable
  pagination
  actions={[
    {
      label: 'Exportar',
      icon: <ExportIcon />,
      onClick: handleExport
    }
  ]}
/>
```

### EnhancedModal
Sistema de modales con múltiples variantes.

```tsx
import { 
  EnhancedModal, 
  ConfirmationModal, 
  AlertModal, 
  FormModal 
} from '../components';

// Modal básico
<EnhancedModal
  open={open}
  onClose={handleClose}
  title="Título del Modal"
  variant="centered"
  transition="slide-up"
  actions={[
    { label: 'Cancelar', onClick: handleClose },
    { label: 'Confirmar', onClick: handleConfirm, variant: 'contained' }
  ]}
>
  Contenido del modal
</EnhancedModal>

// Modal de confirmación
<ConfirmationModal
  open={confirmOpen}
  onClose={() => setConfirmOpen(false)}
  onConfirm={handleDelete}
  title="Eliminar Usuario"
  message="¿Estás seguro de que deseas eliminar este usuario?"
  severity="error"
/>

// Modal de alerta
<AlertModal
  open={alertOpen}
  onClose={() => setAlertOpen(false)}
  title="Éxito"
  message="Usuario creado correctamente"
  severity="success"
/>

// Modal de formulario
<FormModal
  open={formOpen}
  onClose={() => setFormOpen(false)}
  title="Editar Usuario"
  onSubmit={handleSubmit}
  maxWidth="md"
>
  <YourFormContent />
</FormModal>
```

## 🎨 Personalización de Tema

Los componentes utilizan el sistema de tokens de diseño definido en `theme.ts`:

```tsx
// Acceso a tokens de diseño
import { useTheme } from '@mui/material/styles';

const theme = useTheme();
// theme.palette.primary.main
// theme.spacing(2)
// theme.shadows[4]
```

## 🔧 Optimizaciones de Rendimiento

### Memoización
Todos los componentes utilizan `React.memo` para evitar re-renderizados innecesarios:

```tsx
const MyComponent = memo(() => {
  // Componente memoizado
});
```

### Callbacks Memoizados
Los event handlers están memoizados con `useCallback`:

```tsx
const handleClick = useCallback(() => {
  // Handler memoizado
}, [dependencies]);
```

### Valores Computados
Los valores derivados usan `useMemo`:

```tsx
const computedValue = useMemo(() => {
  return expensiveComputation(data);
}, [data]);
```

## 📱 Responsive Design

Los componentes se adaptan automáticamente:

- **Mobile**: Diseño optimizado para pantallas pequeñas
- **Tablet**: Layout intermedio con navegación adaptada
- **Desktop**: Experiencia completa con todas las funcionalidades

## ♿ Accesibilidad

Características de accesibilidad incluidas:

- **ARIA Labels**: Etiquetas descriptivas para lectores de pantalla
- **Navegación por Teclado**: Soporte completo para navegación con teclado
- **Contraste**: Colores que cumplen estándares de contraste
- **Focus Management**: Gestión adecuada del foco en modales y formularios

## 🚀 Mejores Prácticas

### Importación
```tsx
// ✅ Importación nombrada para mejor tree-shaking
import { EnhancedTable, EnhancedForm } from '../components';

// ❌ Evitar importación por defecto cuando sea posible
import EnhancedTable from '../components/Tables/EnhancedTable';
```

### Tipado
```tsx
// ✅ Usar tipos exportados
import { ColumnDef, EnhancedTableProps } from '../components';

const columns: ColumnDef[] = [
  // definición de columnas
];
```

### Performance
```tsx
// ✅ Memoizar props complejas
const memoizedColumns = useMemo(() => columns, [data]);
const memoizedActions = useMemo(() => actions, [permissions]);

<EnhancedTable
  columns={memoizedColumns}
  actions={memoizedActions}
  data={data}
/>
```

## 🔄 Migración desde Componentes Antiguos

Para migrar componentes existentes:

1. **Reemplazar imports**:
   ```tsx
   // Antes
   import { Card } from '@mui/material';
   
   // Después
   import { EnhancedCard } from '../components';
   ```

2. **Actualizar props**:
   ```tsx
   // Antes
   <Card>
     <CardContent>Contenido</CardContent>
   </Card>
   
   // Después
   <EnhancedCard title="Título">
     Contenido
   </EnhancedCard>
   ```

3. **Aprovechar nuevas características**:
   ```tsx
   <EnhancedCard
     variant="elevated"
     status="success"
     loading={false}
   >
     Contenido
   </EnhancedCard>
   ```

## 📚 Recursos Adicionales

- [Material-UI Documentation](https://mui.com/)
- [React Performance Best Practices](https://react.dev/learn/render-and-commit)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Nota**: Este sistema de componentes está en constante evolución. Para sugerencias o reportar problemas, contacta al equipo de desarrollo. 