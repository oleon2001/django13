# SkyGuard GPS Tracking System

Sistema de seguimiento GPS con soporte para múltiples protocolos de dispositivos.

## Requisitos

- Python 3.8 o superior
- PostgreSQL 12 o superior con PostGIS
- Redis 6 o superior
- GDAL 3.4 o superior

## Configuración del Entorno de Desarrollo

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd skyguard
```

2. Crear y activar entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Configurar la base de datos:
```bash
# Crear base de datos PostgreSQL con PostGIS
createdb skyguard
psql skyguard -c "CREATE EXTENSION postgis;"

# Aplicar migraciones
python manage.py migrate
```

6. Crear superusuario:
```bash
python manage.py createsuperuser
```

7. Iniciar servidor de desarrollo:
```bash
python manage.py runserver
```

## Estructura del Proyecto

```
skyguard/
├── apps/                    # Aplicaciones Django
│   ├── gps/                # Aplicación GPS
│   ├── monitoring/         # Aplicación de monitoreo
│   └── tracking/           # Aplicación de seguimiento
├── core/                   # Módulo core
├── settings/              # Configuraciones Django
├── static/                # Archivos estáticos
├── templates/             # Plantillas
└── media/                 # Archivos multimedia
```

## Protocolos Soportados

- Concox
- Meiligao
- Manchester
- CatM1
- CYACD
- Bluetooth

## Desarrollo

### Ejecutar Tests
```bash
pytest
```

### Formatear Código
```bash
black .
```

### Verificar Tipos
```bash
mypy .
```

### Linting
```bash
flake8
```

## Despliegue

1. Configurar variables de entorno de producción
2. Recolectar archivos estáticos:
```bash
python manage.py collectstatic
```
3. Configurar servidor web (Nginx/Apache)
4. Configurar servidor WSGI (Gunicorn/uWSGI)

## Licencia

[Incluir información de licencia] 