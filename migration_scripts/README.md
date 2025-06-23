# 🔄 Scripts de Migración - Backend Legacy a Nuevo

Este directorio contiene todos los scripts necesarios para migrar datos del backend legacy de SkyGuard al nuevo sistema modular.

## 📋 Índice

- [Scripts Disponibles](#scripts-disponibles)
- [Proceso de Migración](#proceso-de-migración)
- [Uso Rápido](#uso-rápido)
- [Uso Avanzado](#uso-avanzado)
- [Solución de Problemas](#solución-de-problemas)
- [Logs y Reportes](#logs-y-reportes)

## 📁 Scripts Disponibles

### 1. `run_migration.py` - **Script Maestro**
Orquesta todo el proceso de migración ejecutando los demás scripts en el orden correcto.

**Características:**
- ✅ Coordina todo el proceso
- ✅ Manejo de errores robusto
- ✅ Reportes detallados
- ✅ Modo dry-run por defecto

### 2. `data_analysis.py` - **Análisis Pre-Migración**
Analiza los datos existentes en el sistema legacy para identificar problemas potenciales.

**Qué analiza:**
- 📊 Conteos de registros
- 🔍 Integridad de datos
- ⚠️ Problemas potenciales
- 📈 Estimaciones de tiempo

### 3. `migrate_core_data.py` - **Migración Principal**
Migra los datos principales del sistema (dispositivos, SIM cards, geocercas, etc.).

**Migra:**
- 📱 Tarjetas SIM
- 🔧 Configuraciones Harness
- 📡 Dispositivos GPS
- 🗺️ Geocercas
- 🎯 Overlays

### 4. `migrate_historical_logs.py` - **Migración Histórica**
Migra logs históricos (aceleración, alarmas, estadísticas) en lotes para manejar grandes volúmenes.

**Migra:**
- 📈 Logs de aceleración
- 🚨 Logs de alarmas
- 📊 Estadísticas de dispositivos

### 5. `validate_migration.py` - **Validación Post-Migración**
Valida que la migración se completó correctamente comparando datos legacy vs nuevos.

**Valida:**
- ✅ Conteos de registros
- 🔍 Integridad referencial
- 📊 Muestreo de datos
- 📝 Reporte de cobertura

## 🚀 Proceso de Migración

### Flujo Completo

```
1. ANÁLISIS        → Analiza datos existentes
2. MIGRACIÓN CORE  → Migra datos principales
3. MIGRACIÓN HIST  → Migra logs históricos
4. VALIDACIÓN      → Verifica integridad
```

### Estados de Ejecución

- **DRY RUN**: Simula la migración sin modificar datos (por defecto)
- **EXECUTE**: Ejecuta la migración real modificando la base de datos

## ⚡ Uso Rápido

### Análisis Inicial (Recomendado)
```bash
# Analizar datos existentes
python run_migration.py

# Solo análisis, sin migración
python data_analysis.py
```

### Migración Completa (Dry Run)
```bash
# Proceso completo en modo prueba
python run_migration.py
```

### Migración Real (PRODUCCIÓN)
```bash
# ⚠️ PELIGROSO: Modifica la base de datos
python run_migration.py --execute
```

## 🔧 Uso Avanzado

### Opciones del Script Maestro

```bash
# Migración completa (dry run)
python run_migration.py

# Migración real
python run_migration.py --execute

# Saltar análisis inicial
python run_migration.py --skip-analysis

# Solo datos principales (sin históricos)
python run_migration.py --skip-historical

# Migración rápida
python run_migration.py --skip-analysis --skip-historical
```

### Scripts Individuales

#### Análisis de Datos
```bash
python data_analysis.py
```

#### Migración Principal
```bash
# Dry run
python migrate_core_data.py --dry-run

# Ejecución real
python migrate_core_data.py --execute
```

#### Migración Histórica
```bash
# Últimos 30 días
python migrate_historical_logs.py --days 30 --execute

# Todos los registros
python migrate_historical_logs.py --execute

# Lotes más pequeños
python migrate_historical_logs.py --batch-size 1000 --execute
```

#### Validación
```bash
python validate_migration.py
```

## 🔍 Solución de Problemas

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
```
Error: django.db.utils.OperationalError
```
**Solución:**
- Verificar configuración en `settings.py`
- Verificar que la base de datos esté ejecutándose
- Verificar credenciales

#### 2. Memoria Insuficiente
```
Error: MemoryError durante migración histórica
```
**Solución:**
```bash
# Reducir tamaño de lote
python migrate_historical_logs.py --batch-size 1000

# Migrar por períodos
python migrate_historical_logs.py --days 30
```

#### 3. Dispositivos Faltantes
```
Warning: Dispositivo XXXXX no encontrado
```
**Solución:**
- Ejecutar primero `migrate_core_data.py`
- Verificar que los dispositivos existen en legacy

#### 4. Duplicados
```
Error: IntegrityError - UNIQUE constraint failed
```
**Solución:**
- Los scripts manejan duplicados automáticamente
- Verificar logs para detalles específicos

### Logs de Debug

```bash
# Ver logs en tiempo real
tail -f migration.log

# Buscar errores específicos
grep "ERROR" migration.log

# Ver progreso
grep "%" migration.log
```

## 📊 Logs y Reportes

### Archivos Generados

| Archivo | Propósito |
|---------|-----------|
| `master_migration.log` | Log del proceso maestro |
| `migration.log` | Log de migración principal |
| `historical_migration.log` | Log de migración histórica |
| `migration_validation.log` | Log de validación |
| `migration_analysis_report.txt` | Reporte de análisis |

### Interpretación de Logs

#### Estados de Migración
- ✅ `PASS` - Completado sin errores
- ⚠️ `WARN` - Completado con advertencias
- ❌ `FAIL` - Falló con errores
- 🔥 `ERROR` - Error crítico

#### Progreso
```
SIM Cards: 150/150 (100.0%)
GPS Devices: 75/100 (75.0%)
```

#### Resumen Final
```
TOTAL: 1,250 registros migrados, 5 errores, 23 saltados
```

## ⚠️ Consideraciones Importantes

### Antes de Ejecutar en Producción

1. **BACKUP OBLIGATORIO**
   ```bash
   # PostgreSQL
   pg_dump skyguard_db > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # MySQL
   mysqldump skyguard_db > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Prueba en Ambiente de Desarrollo**
   ```bash
   # Siempre probar primero
   python run_migration.py
   ```

3. **Verificar Espacio en Disco**
   - La migración puede duplicar temporalmente el uso de espacio
   - Logs históricos requieren espacio adicional

4. **Tiempo de Ejecución**
   - Datos principales: 5-30 minutos
   - Logs históricos: 1-8 horas (dependiendo del volumen)
   - Validación: 10-60 minutos

### Durante la Migración

- ✅ No interrumpir el proceso
- ✅ Monitorear logs en tiempo real
- ✅ Verificar uso de memoria y CPU
- ❌ No ejecutar otras operaciones pesadas

### Después de la Migración

1. **Verificar Resultados**
   ```bash
   python validate_migration.py
   ```

2. **Probar Funcionalidad**
   - Verificar que el nuevo sistema funciona
   - Probar operaciones críticas
   - Verificar reportes y consultas

3. **Monitoreo**
   - Rendimiento de consultas
   - Uso de memoria
   - Logs de aplicación

## 🆘 Contacto y Soporte

Si encuentras problemas durante la migración:

1. **Revisar logs detalladamente**
2. **Ejecutar validación para identificar problemas**
3. **Documentar el error específico**
4. **Preparar información del entorno**

---

**⚠️ RECORDATORIO: Siempre hacer backup antes de ejecutar en producción** 