# Proyecto Falkun - Sistema de GPS Tracking

Este proyecto es un sistema de GPS tracking basado en Django 1.3.1 con PostgreSQL y PostGIS para el manejo de datos geoespaciales.

## 🚀 Configuración Rápida

### Prerrequisitos

- Docker y Docker Compose
- Python 3.x
- Git

### Instalación Automática

1. **Configurar todo el entorno automáticamente:**
   ```bash
   ./manage_falkun.sh setup
   ```

2. **Crear superusuario:**
   ```bash
   ./manage_falkun.sh superuser
   ```

3. **Ejecutar el servidor:**
   ```bash
   ./manage_falkun.sh runserver
   ```

El proyecto estará disponible en: http://localhost:8000

## 📋 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `./manage_falkun.sh setup` | Configurar todo el entorno (DB + venv + deps) |
| `./manage_falkun.sh start-db` | Levantar solo la base de datos |
| `./manage_falkun.sh stop-db` | Detener la base de datos |
| `./manage_falkun.sh runserver` | Ejecutar servidor de desarrollo |
| `./manage_falkun.sh migrate` | Ejecutar migraciones |
| `./manage_falkun.sh superuser` | Crear superusuario |
| `./manage_falkun.sh status` | Mostrar estado del proyecto |
| `./manage_falkun.sh help` | Mostrar ayuda |

## 🗄️ Base de Datos

### Configuración
- **Base de datos:** `falkun`
- **Usuario:** `falkun_user`
- **Contraseña:** `falkun_password`
- **Puerto:** `5433`
- **Motor:** PostgreSQL con PostGIS

### Acceso a pgAdmin
- **URL:** http://localhost:8080
- **Email:** admin@falkun.com
- **Contraseña:** admin123

## 🔧 Configuración Manual

### 1. Levantar Base de Datos
```bash
docker-compose up -d db
```

### 2. Crear Entorno Virtual
```bash
python3 -m venv venv_falkun
source venv_falkun/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Django
El proyecto usa el archivo `skyguard/sites/www/settings_docker.py` que está configurado para trabajar con la base de datos Docker.

### 5. Ejecutar Migraciones
```bash
cd skyguard
export DJANGO_SETTINGS_MODULE=sites.www.settings_docker
python manage.py migrate
```

### 6. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 7. Ejecutar Servidor
```bash
python manage.py runserver 0.0.0.0:8000
```

## 📁 Estructura del Proyecto

```
django14/
├── docker-compose.yml          # Configuración de Docker
├── init-db.sql                 # Script de inicialización de BD
├── manage_falkun.sh            # Script de manejo del proyecto
├── requirements.txt            # Dependencias de Python
├── skyguard/                   # Proyecto Django principal
│   ├── sites/
│   │   └── www/
│   │       ├── settings.py     # Configuración original
│   │       └── settings_docker.py # Configuración para Docker
│   ├── gps/                    # Aplicaciones GPS
│   ├── templates/              # Plantillas
│   └── static/                 # Archivos estáticos
└── README_FALKUN.md           # Este archivo
```

## 🐛 Solución de Problemas

### Error de conexión a la base de datos
1. Verificar que Docker esté ejecutándose
2. Verificar que el contenedor esté activo: `docker ps`
3. Verificar logs: `docker-compose logs db`

### Error de dependencias
1. Asegurar que el entorno virtual esté activado
2. Reinstalar dependencias: `pip install -r requirements.txt`

### Error de migraciones
1. Verificar que la base de datos esté ejecutándose
2. Verificar la configuración en `settings_docker.py`
3. Ejecutar: `python manage.py makemigrations` antes de `migrate`

## 🔒 Seguridad

- Cambiar las contraseñas por defecto en producción
- Configurar variables de entorno para credenciales sensibles
- Habilitar HTTPS en producción
- Configurar firewall apropiadamente

## 📝 Notas de Desarrollo

- El proyecto usa Django 1.3.1 (versión antigua)
- Requiere PostGIS para funcionalidad geoespacial
- Compatible con Python 3.x
- Usa uWSGI para producción

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto es privado y confidencial. 