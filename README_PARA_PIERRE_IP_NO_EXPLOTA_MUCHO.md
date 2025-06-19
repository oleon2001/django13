# Guía de Despliegue - SkyGuard en IP Pública

## Descripción General
Esta guía te ayudará a desplegar la aplicación SkyGuard (Frontend React + Backend Django) en un servidor con IP pública para acceso desde internet.

## Arquitectura de Despliegue
```
Internet
    ↓
Nginx (Puerto 80/443) → Proxy Reverso
    ├── Frontend React (Puerto 3000) → /
    └── Backend Django (Puerto 8000) → /api/
```

## Prerrequisitos del Sistema

### 1. Servidor con IP Pública
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Mínimo 2GB RAM, 2 CPU cores
- 20GB de espacio en disco
- Acceso root o sudo

### 2. Software Base Requerido
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas del sistema
sudo apt install -y curl wget git vim nano htop tree
sudo apt install -y build-essential software-properties-common apt-transport-https
sudo apt install -y ca-certificates gnupg lsb-release

# Instalar servidor web y base de datos
sudo apt install -y nginx postgresql postgresql-contrib postgresql-client
sudo apt install -y redis-server

# Instalar Python y herramientas de desarrollo
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y libpq-dev python3-psycopg2 

# Instalar dependencias para compilación de paquetes Python
sudo apt install -y gcc g++ make libssl-dev libffi-dev
sudo apt install -y libjpeg-dev libpng-dev libwebp-dev
sudo apt install -y gdal-bin libgdal-dev libproj-dev libgeos-dev

# Instalar herramientas de sistema
sudo apt install -y ufw fail2ban logrotate
sudo apt install -y certbot python3-certbot-nginx

# Verificar versiones instaladas
echo "=== Versiones Instaladas ==="
python3 --version
pip3 --version
nginx -v
psql --version
redis-server --version
node --version 2>/dev/null || echo "Node.js no instalado aún"
```

### 2.1 Configurar Seguridad Básica del Sistema
```bash
# Configurar fail2ban para proteger SSH
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Configuración básica de `jail.local`:
```ini
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 3
backend = systemd

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 1h
```

```bash
# Iniciar fail2ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

# Configurar límites del sistema
sudo nano /etc/security/limits.conf
```

Agregar al final de `limits.conf`:
```
# Límites para aplicación web
www-data soft nofile 65536
www-data hard nofile 65536
www-data soft nproc 4096
www-data hard nproc 4096
```

```bash
# Configurar kernel parameters
sudo nano /etc/sysctl.conf
```

Agregar configuraciones de red:
```
# Configuración de red para aplicación web
net.core.somaxconn = 1024
net.core.netdev_max_backlog = 5000
net.core.rmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_default = 262144
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 120
net.ipv4.tcp_max_syn_backlog = 4096
```

```bash
# Aplicar configuraciones
sudo sysctl -p

# Verificar configuraciones aplicadas
sudo sysctl net.core.somaxconn
```

## Paso 1: Configuración del Servidor

### 1.1 Configurar Firewall
```bash
# Instalar ufw si no está instalado
sudo apt install ufw

# Configurar reglas básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # Temporal para pruebas
sudo ufw allow 3000/tcp  # Temporal para pruebas

# Activar firewall
sudo ufw enable
```

### 1.2 Configurar PostgreSQL
```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear base de datos y usuario (usa la contraseña que generaste antes)
CREATE DATABASE skyguard;
CREATE USER skyguard_user WITH ENCRYPTED PASSWORD 'TU_PASSWORD_GENERADO_AQUI';
GRANT ALL PRIVILEGES ON DATABASE skyguard TO skyguard_user;
ALTER USER skyguard_user CREATEDB;

# Configurar permisos adicionales necesarios para Django
GRANT CREATE ON SCHEMA public TO skyguard_user;
GRANT USAGE ON SCHEMA public TO skyguard_user;

# Salir de PostgreSQL
\q

# Instalar PostGIS (necesario para funciones geoespaciales)
sudo apt install postgresql-12-postgis-3 postgresql-12-postgis-3-scripts

# Habilitar PostGIS en la base de datos
sudo -u postgres psql -d skyguard -c "CREATE EXTENSION IF NOT EXISTS postgis;"
sudo -u postgres psql -d skyguard -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"

# Verificar instalación de PostGIS
sudo -u postgres psql -d skyguard -c "SELECT PostGIS_version();"

# Configurar PostgreSQL para aceptar conexiones locales
sudo nano /etc/postgresql/12/main/pg_hba.conf
```

**Configuración de `pg_hba.conf`** (agregar/modificar estas líneas):
```
# Permitir conexiones locales con contraseña
local   skyguard        skyguard_user                     md5
host    skyguard        skyguard_user   127.0.0.1/32      md5
host    skyguard        skyguard_user   ::1/128           md5
```

```bash
# Configurar parámetros de PostgreSQL para mejor rendimiento
sudo nano /etc/postgresql/12/main/postgresql.conf
```

**Configuraciones recomendadas en `postgresql.conf`:**
```
# Configuración de memoria (ajustar según tu servidor)
shared_buffers = 256MB                  # 25% de RAM disponible
effective_cache_size = 1GB              # 75% de RAM disponible
maintenance_work_mem = 64MB
work_mem = 4MB

# Configuración de conexiones
max_connections = 100
listen_addresses = 'localhost'

# Configuración de logs
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'error'
log_min_duration_statement = 1000
```

```bash
# Reiniciar PostgreSQL para aplicar cambios
sudo systemctl restart postgresql

# Verificar que PostgreSQL esté funcionando
sudo systemctl status postgresql

# Probar conexión con el usuario creado
psql -h localhost -U skyguard_user -d skyguard -c "SELECT version();"
```

### 1.3 Configurar Redis
```bash
# Iniciar y habilitar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar funcionamiento
redis-cli ping
```

## Paso 2: Preparar el Código Fuente

### 2.1 Clonar y Configurar el Proyecto
```bash
# Crear directorio para la aplicación
sudo mkdir -p /var/www/skyguard
sudo chown $USER:$USER /var/www/skyguard

# Clonar el proyecto (ajustar la URL según tu repositorio)
cd /var/www/skyguard
git clone <tu-repositorio-url> .

# O copiar archivos existentes
# cp -r /ruta/a/tu/proyecto/* /var/www/skyguard/
```

### 2.2 Configurar Variables de Entorno
```bash
# Crear archivo de entorno para producción
cp .env.example .env.production

# Editar configuración de producción
nano .env.production
```

**IMPORTANTE**: Antes de editar el archivo, genera las claves y contraseñas necesarias:

```bash
# Generar clave secreta de Django (50 caracteres seguros)
python3 -c "from django.core.management.utils import get_random_secret_key; print('DJANGO_SECRET_KEY=' + get_random_secret_key())"

# O alternativamente, generar con openssl
openssl rand -base64 50

# Generar contraseña segura para base de datos (20 caracteres)
openssl rand -base64 20

# Generar contraseña para usuario de aplicación
openssl rand -base64 16

# Verificar tu IP pública
curl -4 ifconfig.co
# o
curl -4 icanhazip.com
```

Contenido del archivo `.env.production`:
```bash
# Base de datos
DB_NAME=skyguard
DB_USER=skyguard_user
DB_PASSWORD=AQUI_TU_PASSWORD_GENERADO_BASE64_20
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1

# Django
DJANGO_SECRET_KEY=AQUI_TU_CLAVE_SECRETA_GENERADA_50_CHARS
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=tu-dominio.com,TU_IP_PUBLICA_AQUI,localhost,127.0.0.1

# Email (opcional pero recomendado para notificaciones)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-app-gmail
DEFAULT_FROM_EMAIL=tu-email@gmail.com

# Seguridad (HTTPS)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Configuración adicional para producción
DJANGO_SETTINGS_MODULE=skyguard.settings.production
PYTHONPATH=/var/www/skyguard

# Configuración de archivos estáticos
STATIC_ROOT=/var/www/skyguard/static
MEDIA_ROOT=/var/www/skyguard/media

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/django/skyguard.log
```

**Configurar Email de Gmail (Opcional pero Recomendado):**
```bash
# Para usar Gmail, necesitas generar una contraseña de aplicación:
# 1. Ve a https://myaccount.google.com/security
# 2. Activa la verificación en 2 pasos
# 3. Ve a "Contraseñas de aplicaciones"
# 4. Genera una contraseña para "Correo"
# 5. Usa esa contraseña en EMAIL_HOST_PASSWORD
```

## Paso 3: Configurar Backend Django

### 3.1 Instalar Dependencias Python
```bash
cd /var/www/skyguard

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Actualizar pip a la última versión
pip install --upgrade pip setuptools wheel

# Instalar dependencias principales
pip install -r requirements.txt

# Instalar dependencias adicionales para producción
pip install gunicorn
pip install psycopg2-binary  # Driver PostgreSQL
pip install redis            # Cliente Redis
pip install celery          # Para tareas asíncronas (si se usa)
pip install pillow          # Para manejo de imágenes
pip install whitenoise      # Para servir archivos estáticos

# Instalar dependencias de desarrollo/debugging (opcional)
pip install django-debug-toolbar
pip install django-extensions

# Verificar instalación
pip list | grep -E "(Django|gunicorn|psycopg2|redis)"
```

### 3.2 Configurar Django para Producción
```bash
# Cargar variables de entorno
export $(cat .env.production | xargs)

# Verificar configuración de Django
python manage.py check --deploy

# Crear directorios necesarios
mkdir -p /var/www/skyguard/static
mkdir -p /var/www/skyguard/media
mkdir -p /var/www/skyguard/logs

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear datos iniciales (si existen fixtures)
# python manage.py loaddata initial_data.json

# Crear superusuario (interactivo)
python manage.py createsuperuser

# O crear superusuario no interactivo
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@tudominio.com', 'TU_PASSWORD_ADMIN_AQUI')" | python manage.py shell

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Verificar configuración de la base de datos
python manage.py dbshell -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"

# Probar el servidor de desarrollo (temporal)
python manage.py runserver 0.0.0.0:8000 &
sleep 5
curl http://localhost:8000/api/
pkill -f "python manage.py runserver"
```

### 3.3 Configurar Gunicorn
```bash
# Crear archivo de configuración de Gunicorn
nano /var/www/skyguard/gunicorn.conf.py
```

Contenido de `gunicorn.conf.py`:
```python
import multiprocessing
import os

# Configuración de red
bind = "127.0.0.1:8000"
backlog = 2048

# Configuración de workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Configuración de requests
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Configuración de archivos
pidfile = "/var/run/gunicorn/skyguard.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# Configuración de logging
errorlog = "/var/log/gunicorn/skyguard_error.log"
loglevel = "info"
accesslog = "/var/log/gunicorn/skyguard_access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de desarrollo (cambiar a False en producción)
reload = False
spew = False

# Variables de entorno
raw_env = [
    'DJANGO_SETTINGS_MODULE=skyguard.settings.production',
]
```

```bash
# Crear directorios para logs de Gunicorn
sudo mkdir -p /var/log/gunicorn
sudo mkdir -p /var/run/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
sudo chown www-data:www-data /var/run/gunicorn

# Probar configuración de Gunicorn
/var/www/skyguard/venv/bin/gunicorn --config gunicorn.conf.py skyguard.wsgi:application --check-config
```

### 3.4 Crear Servicio Systemd para Django
```bash
sudo nano /etc/systemd/system/skyguard-django.service
```

Contenido del servicio:
```ini
[Unit]
Description=SkyGuard Django Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/skyguard
Environment=PATH=/var/www/skyguard/venv/bin
EnvironmentFile=/var/www/skyguard/.env.production
ExecStart=/var/www/skyguard/venv/bin/gunicorn --config gunicorn.conf.py skyguard.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## Paso 4: Configurar Frontend React

### 4.1 Instalar Node.js y npm (Versión LTS)
```bash
# Instalar Node.js LTS usando NodeSource
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar instalación
node --version
npm --version

# Instalar yarn (alternativa a npm, opcional pero recomendado)
npm install -g yarn

# Verificar yarn
yarn --version
```

### 4.2 Instalar Dependencias del Frontend
```bash
cd /var/www/skyguard/frontend

# Limpiar cache si existe instalación previa
npm cache clean --force
rm -rf node_modules package-lock.json

# Instalar dependencias
npm install

# O usando yarn (más rápido)
# yarn install

# Verificar dependencias críticas
npm list react react-dom axios

# Instalar dependencias adicionales si no están en package.json
npm install --save axios react-router-dom @mui/material @emotion/react @emotion/styled
npm install --save @mui/icons-material leaflet react-leaflet
npm install --save i18next react-i18next i18next-browser-languagedetector

# Dependencias de desarrollo
npm install --save-dev @types/node @types/react @types/react-dom typescript
```

### 4.3 Configurar Variables de Entorno del Frontend
```bash
# Crear archivo de configuración para desarrollo
nano /var/www/skyguard/frontend/.env.development
```

Contenido de `.env.development`:
```bash
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
GENERATE_SOURCEMAP=true
REACT_APP_ENV=development
```

```bash
# Crear archivo de configuración para producción
nano /var/www/skyguard/frontend/.env.production
```

Contenido de `.env.production`:
```bash
REACT_APP_API_URL=https://TU_DOMINIO_O_IP/api
REACT_APP_WS_URL=wss://TU_DOMINIO_O_IP/ws
GENERATE_SOURCEMAP=false
REACT_APP_ENV=production
PUBLIC_URL=/
BUILD_PATH=build
```

### 4.4 Configurar Proxy para Desarrollo (Opcional)
```bash
# El archivo package.json ya tiene configurado el proxy
# Verificar que contenga:
grep -A 1 -B 1 "proxy" /var/www/skyguard/frontend/package.json
```

Si no existe, agregar al `package.json`:
```json
{
  "name": "frontend",
  "version": "0.1.0",
  "proxy": "http://localhost:8000",
  ...
}
```

### 4.5 Construir la Aplicación
```bash
cd /var/www/skyguard/frontend

# Construir para producción
npm run build

# O usando yarn
# yarn build

# Verificar que el build se creó correctamente
ls -la build/
ls -la build/static/

# Probar el build localmente (opcional)
npx serve -s build -p 3001 &
sleep 3
curl http://localhost:3001
pkill -f "serve -s build"

# Verificar tamaño del bundle
du -sh build/
```

### 4.6 Optimizar Build de Producción
```bash
# Instalar herramientas de análisis (opcional)
npm install --save-dev webpack-bundle-analyzer

# Analizar el bundle (opcional)
npx webpack-bundle-analyzer build/static/js/*.js

# Configurar compresión adicional en package.json si no existe
# Agregar script de build optimizado
```

Agregar al `package.json` si no existe:
```json
{
  "scripts": {
    "build": "react-scripts build",
    "build:analyze": "npm run build && npx webpack-bundle-analyzer build/static/js/*.js",
    "build:production": "GENERATE_SOURCEMAP=false react-scripts build"
  }
}
```

## Paso 5: Configurar Nginx

### 5.1 Crear Configuración de Nginx
```bash
sudo nano /etc/nginx/sites-available/skyguard
```

Contenido de la configuración:
```nginx
server {
    listen 80;
    server_name tu-dominio.com tu-ip-publica;
    
    # Redireccionar HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com tu-ip-publica;
    
    # Certificados SSL (configurar después)
    # ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
    
    # Configuración SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Logs
    access_log /var/log/nginx/skyguard_access.log;
    error_log /var/log/nginx/skyguard_error.log;
    
    # Configuración de archivos estáticos
    location /static/ {
        alias /var/www/skyguard/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/skyguard/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API Backend (Django)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Admin Django
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend React
    location / {
        root /var/www/skyguard/frontend/build;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
        
        # Headers de seguridad
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    }
    
    # Configuración para archivos grandes
    client_max_body_size 100M;
    
    # Compresión
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
```

### 5.2 Habilitar el Sitio
```bash
# Habilitar configuración
sudo ln -s /etc/nginx/sites-available/skyguard /etc/nginx/sites-enabled/

# Deshabilitar sitio por defecto
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

## Paso 6: Configurar SSL con Let's Encrypt

### 6.1 Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 6.2 Obtener Certificado SSL
```bash
# Para dominio
sudo certbot --nginx -d tu-dominio.com

# Para IP pública (no recomendado, usar dominio)
# Los certificados SSL no funcionan con IPs, necesitas un dominio
```

### 6.3 Configurar Renovación Automática
```bash
# Verificar renovación automática
sudo certbot renew --dry-run

# El cron job se crea automáticamente
```

## Paso 7: Configurar Permisos y Servicios

### 7.1 Configurar Permisos
```bash
# Cambiar propietario de archivos
sudo chown -R www-data:www-data /var/www/skyguard
sudo chmod -R 755 /var/www/skyguard

# Permisos especiales para logs
sudo mkdir -p /var/log/django
sudo chown www-data:www-data /var/log/django
```

### 7.2 Iniciar Servicios
```bash
# Recargar systemd
sudo systemctl daemon-reload

# Iniciar y habilitar servicios
sudo systemctl start skyguard-django
sudo systemctl enable skyguard-django

# Verificar estado
sudo systemctl status skyguard-django
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server
```

## Paso 8: Configurar Dominio (Recomendado)

### 8.1 Configurar DNS
En tu proveedor de dominio, crea un registro A:
```
Tipo: A
Nombre: @ (o tu subdominio)
Valor: TU_IP_PUBLICA
TTL: 300
```

### 8.2 Actualizar Configuración
```bash
# Actualizar ALLOWED_HOSTS en .env.production
nano /var/www/skyguard/.env.production

# Agregar tu dominio
DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,tu-ip-publica

# Reiniciar servicios
sudo systemctl restart skyguard-django
sudo systemctl restart nginx
```

## Paso 9: Verificación y Pruebas Completas

### 9.1 Verificar Servicios del Sistema
```bash
# Verificar todos los servicios están corriendo
echo "=== Estado de Servicios ==="
sudo systemctl status nginx --no-pager -l
sudo systemctl status postgresql --no-pager -l
sudo systemctl status redis-server --no-pager -l
sudo systemctl status skyguard-django --no-pager -l

# Verificar puertos abiertos
echo "=== Puertos Abiertos ==="
sudo netstat -tlnp | grep -E ':(80|443|8000|5432|6379)'

# Verificar procesos
echo "=== Procesos de la Aplicación ==="
ps aux | grep -E "(nginx|postgres|redis|gunicorn)" | grep -v grep
```

### 9.2 Pruebas de Conectividad de Base de Datos
```bash
# Probar conexión a PostgreSQL
echo "=== Prueba PostgreSQL ==="
psql -h localhost -U skyguard_user -d skyguard -c "SELECT version();"
psql -h localhost -U skyguard_user -d skyguard -c "SELECT PostGIS_version();"

# Verificar tablas de Django
psql -h localhost -U skyguard_user -d skyguard -c "\dt"

# Probar Redis
echo "=== Prueba Redis ==="
redis-cli ping
redis-cli info replication
```

### 9.3 Pruebas de la API Backend
```bash
# Probar endpoints básicos de la API
echo "=== Pruebas de API ==="

# Probar health check (si existe)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health/ || echo "Endpoint health no disponible"

# Probar endpoint de autenticación
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' \
  -s -o /dev/null -w "Status: %{http_code}\n"

# Probar endpoints principales (ajustar según tu API)
curl -s -o /dev/null -w "API Root Status: %{http_code}\n" http://localhost:8000/api/

# Verificar archivos estáticos
curl -s -o /dev/null -w "Static Files Status: %{http_code}\n" http://localhost:8000/static/admin/css/base.css
```

### 9.4 Pruebas del Frontend
```bash
echo "=== Pruebas del Frontend ==="

# Verificar que los archivos del build existen
ls -la /var/www/skyguard/frontend/build/
ls -la /var/www/skyguard/frontend/build/static/

# Probar acceso directo al build
cd /var/www/skyguard/frontend/build
python3 -m http.server 3001 &
HTTP_PID=$!
sleep 2
curl -s -o /dev/null -w "Frontend Build Status: %{http_code}\n" http://localhost:3001/
kill $HTTP_PID
```

### 9.5 Pruebas a través de Nginx
```bash
echo "=== Pruebas a través de Nginx ==="

# Probar HTTP (debería redirigir a HTTPS)
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/

# Probar HTTPS (puede fallar si no hay certificado SSL aún)
curl -k -s -o /dev/null -w "HTTPS Status: %{http_code}\n" https://localhost/ 2>/dev/null || echo "HTTPS no disponible (normal sin certificado SSL)"

# Probar API a través de Nginx
curl -s -o /dev/null -w "API through Nginx Status: %{http_code}\n" http://localhost/api/

# Probar archivos estáticos a través de Nginx
curl -s -o /dev/null -w "Static through Nginx Status: %{http_code}\n" http://localhost/static/admin/css/base.css
```

### 9.6 Verificar Logs
```bash
echo "=== Verificación de Logs ==="

# Logs de Django/Gunicorn
echo "--- Logs de Django ---"
sudo journalctl -u skyguard-django --no-pager -n 10

# Logs de Nginx
echo "--- Logs de Nginx ---"
sudo tail -n 5 /var/log/nginx/skyguard_access.log 2>/dev/null || echo "Log de acceso no existe aún"
sudo tail -n 5 /var/log/nginx/skyguard_error.log 2>/dev/null || echo "Log de errores no existe aún"

# Logs del sistema
echo "--- Logs del Sistema ---"
sudo tail -n 5 /var/log/syslog | grep -E "(nginx|postgres|redis)"
```

### 9.7 Pruebas de Rendimiento Básicas
```bash
echo "=== Pruebas de Rendimiento ==="

# Instalar herramientas de prueba
sudo apt install -y apache2-utils curl

# Prueba de carga básica (10 requests)
ab -n 10 -c 2 http://localhost/api/ 2>/dev/null | grep -E "(Requests per second|Time per request)"

# Prueba de tiempo de respuesta
time curl -s http://localhost/ > /dev/null
```

### 9.8 Verificar Configuración de Seguridad
```bash
echo "=== Verificación de Seguridad ==="

# Verificar firewall
sudo ufw status

# Verificar fail2ban
sudo fail2ban-client status

# Verificar permisos de archivos críticos
ls -la /var/www/skyguard/.env.production
ls -la /var/www/skyguard/

# Verificar que no hay archivos de configuración expuestos
curl -s -o /dev/null -w "Config File Protection: %{http_code}\n" http://localhost/.env
```

### 9.9 Crear Script de Verificación Automática
```bash
# Crear script de monitoreo
sudo nano /usr/local/bin/skyguard-health-check.sh
```

Contenido del script:
```bash
#!/bin/bash
echo "=== SkyGuard Health Check - $(date) ==="

# Verificar servicios
services=("nginx" "postgresql" "redis-server" "skyguard-django")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✓ $service está funcionando"
    else
        echo "✗ $service NO está funcionando"
    fi
done

# Verificar puertos
ports=("80:nginx" "443:nginx-ssl" "8000:django" "5432:postgresql" "6379:redis")
for port_service in "${ports[@]}"; do
    port=${port_service%:*}
    service=${port_service#*:}
    if netstat -tlpn | grep -q ":$port "; then
        echo "✓ Puerto $port ($service) está abierto"
    else
        echo "✗ Puerto $port ($service) NO está abierto"
    fi
done

# Verificar endpoints
endpoints=("http://localhost/" "http://localhost/api/")
for endpoint in "${endpoints[@]}"; do
    if curl -s -f $endpoint > /dev/null 2>&1; then
        echo "✓ $endpoint responde correctamente"
    else
        echo "✗ $endpoint NO responde"
    fi
done

# Verificar espacio en disco
disk_usage=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
if [ $disk_usage -lt 80 ]; then
    echo "✓ Espacio en disco OK ($disk_usage%)"
else
    echo "⚠ Advertencia: Espacio en disco alto ($disk_usage%)"
fi

# Verificar memoria
mem_usage=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')
if [ $mem_usage -lt 80 ]; then
    echo "✓ Uso de memoria OK ($mem_usage%)"
else
    echo "⚠ Advertencia: Uso de memoria alto ($mem_usage%)"
fi

echo "=== Fin del Health Check ==="
```

```bash
# Hacer ejecutable el script
sudo chmod +x /usr/local/bin/skyguard-health-check.sh

# Ejecutar verificación
sudo /usr/local/bin/skyguard-health-check.sh

# Programar verificación cada hora
echo "0 * * * * /usr/local/bin/skyguard-health-check.sh >> /var/log/skyguard-health.log 2>&1" | sudo crontab -
```

## Paso 10: Monitoreo y Mantenimiento

### 10.1 Configurar Logs
```bash
# Configurar rotación de logs
sudo nano /etc/logrotate.d/skyguard
```

Contenido:
```
/var/log/nginx/skyguard_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data adm
    postrotate
        systemctl reload nginx
    endscript
}

/var/log/django/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### 10.2 Backup Automático
```bash
# Crear script de backup
sudo nano /usr/local/bin/skyguard-backup.sh
```

Contenido del script:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/skyguard"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de base de datos
pg_dump -U skyguard_user -h localhost skyguard > $BACKUP_DIR/db_$DATE.sql

# Backup de archivos
tar -czf $BACKUP_DIR/files_$DATE.tar.gz -C /var/www skyguard

# Limpiar backups antiguos (mantener 7 días)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Hacer ejecutable
sudo chmod +x /usr/local/bin/skyguard-backup.sh

# Configurar cron para backup diario
sudo crontab -e
# Agregar línea:
0 2 * * * /usr/local/bin/skyguard-backup.sh
```

## Solución de Problemas Comunes

### Error 502 Bad Gateway
```bash
# Verificar que Django esté corriendo
sudo systemctl status skyguard-django

# Verificar logs
sudo journalctl -u skyguard-django -n 50
```

### Error de Base de Datos
```bash
# Verificar conexión a PostgreSQL
sudo -u postgres psql -d skyguard -c "SELECT version();"

# Verificar configuración en .env.production
```

### Problemas de Permisos
```bash
# Reconfigurar permisos
sudo chown -R www-data:www-data /var/www/skyguard
sudo chmod -R 755 /var/www/skyguard
```

### Frontend no Carga
```bash
# Verificar build del frontend
cd /var/www/skyguard/frontend
npm run build

# Verificar configuración de Nginx
sudo nginx -t
```

### Problemas de Servicios GPS

#### Servidores GPS No Inician
```bash
# Verificar configuración de puertos
sudo netstat -tlnp | grep -E "55300|62000|15557|55301"

# Verificar permisos de usuario
sudo -u skyguard /opt/skyguard/venv/bin/python manage.py gps_servers status

# Verificar logs de inicio
sudo journalctl -u skyguard-gps-servers.service -n 50 --no-pager

# Reiniciar servicios GPS
sudo systemctl restart skyguard-gps-servers.service
sudo systemctl restart skyguard-device-monitor.service

# Verificar dependencias
sudo systemctl status postgresql.service
sudo systemctl status skyguard-django.service
```

#### Dispositivos GPS No Se Conectan
```bash
# Verificar puertos abiertos externamente
sudo ufw status | grep -E "55300|62000|15557|55301"

# Verificar conectividad desde dispositivo
# telnet IP_SERVIDOR 55300

# Verificar logs de conexión
tail -f /opt/skyguard/logs/gps.log | grep -i "connection\|login\|error"

# Verificar configuración de red
sudo iptables -L | grep -E "55300|62000|15557|55301"

# Probar con simulador local
cd /opt/skyguard
python gps_simulator.py
```

#### Dispositivos Marcados Como Offline
```bash
# Verificar configuración de timeout
grep -i "timeout\|heartbeat" /opt/skyguard/.env.production

# Ejecutar verificación manual
python manage.py check_device_status --timeout 120 --verbose

# Verificar últimos heartbeats
python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
from django.utils import timezone
devices = GPSDevice.objects.filter(connection_status='OFFLINE')[:5]
for device in devices:
    if device.last_heartbeat:
        diff = timezone.now() - device.last_heartbeat
        print(f'{device.imei}: {diff.total_seconds():.0f}s ago')
    else:
        print(f'{device.imei}: No heartbeat')
"

# Ajustar timeout del monitor
sudo systemctl edit skyguard-device-monitor.service
# Agregar:
# [Service]
# ExecStart=
# ExecStart=/opt/skyguard/venv/bin/python manage.py start_device_monitor --timeout 5 --interval 60
```

#### Problemas de Protocolo GPS
```bash
# Verificar decodificación de paquetes
tail -f /opt/skyguard/logs/gps.log | grep -i "decode\|packet\|protocol"

# Verificar configuración de protocolo
python manage.py shell -c "
from skyguard.apps.gps.servers.server_manager import server_manager
print(server_manager.server_configs)
"

# Reiniciar servidor específico
python manage.py gps_servers stop --server concox
python manage.py gps_servers start --server concox

# Verificar handshake de dispositivos
python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
devices = GPSDevice.objects.filter(connection_status='ONLINE')
for device in devices:
    print(f'{device.imei}: {device.protocol} - {device.last_heartbeat}')
"
```

#### Performance de GPS Lenta
```bash
# Verificar índices de base de datos
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"\"\"
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'public' AND tablename LIKE '%gps%'
ORDER BY idx_tup_read DESC;
\"\"\")
for row in cursor.fetchall():
    print(row)
"

# Limpiar datos antiguos
python manage.py shell -c "
from skyguard.apps.gps.models import GPSLocation, GPSEvent
from django.utils import timezone
from datetime import timedelta

# Eliminar posiciones más antiguas de 90 días
old_date = timezone.now() - timedelta(days=90)
locations_deleted = GPSLocation.objects.filter(timestamp__lt=old_date).delete()
print(f'Posiciones eliminadas: {locations_deleted[0]}')

# Eliminar eventos más antiguos de 180 días
old_date = timezone.now() - timedelta(days=180)
events_deleted = GPSEvent.objects.filter(timestamp__lt=old_date).delete()
print(f'Eventos eliminados: {events_deleted[0]}')
"

# Optimizar base de datos
sudo -u postgres psql skyguard_db -c "VACUUM ANALYZE;"
sudo -u postgres psql skyguard_db -c "REINDEX DATABASE skyguard_db;"
```

#### Problemas de Memoria GPS
```bash
# Verificar uso de memoria de servicios GPS
ps aux | grep -E "gps_servers|device_monitor" | grep -v grep

# Verificar límites de memoria
systemctl show skyguard-gps-servers.service | grep -i memory
systemctl show skyguard-device-monitor.service | grep -i memory

# Configurar límites de memoria si es necesario
sudo systemctl edit skyguard-gps-servers.service
# Agregar:
# [Service]
# MemoryLimit=512M
# MemoryMax=1G

sudo systemctl edit skyguard-device-monitor.service
# Agregar:
# [Service]
# MemoryLimit=256M
# MemoryMax=512M

sudo systemctl daemon-reload
sudo systemctl restart skyguard-gps-servers.service
sudo systemctl restart skyguard-device-monitor.service
```

## URLs de Acceso Final

Una vez completada la configuración:

- **Frontend**: `https://tu-dominio.com/` o `https://tu-ip-publica/`
- **API Backend**: `https://tu-dominio.com/api/` o `https://tu-ip-publica/api/`
- **Admin Django**: `https://tu-dominio.com/admin/` o `https://tu-ip-publica/admin/`

## Comandos Útiles de Mantenimiento

```bash
# Reiniciar todos los servicios
sudo systemctl restart skyguard-django nginx postgresql redis-server

# Ver logs en tiempo real
sudo journalctl -u skyguard-django -f

# Actualizar código
cd /var/www/skyguard
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
cd frontend && npm install && npm run build
sudo systemctl restart skyguard-django

# Verificar estado del sistema
sudo systemctl status skyguard-django nginx postgresql redis-server
```

# 9. Configuración de Servicios GPS

## 9.1 Scripts de Gestión GPS

### GPS Simulator (Desarrollo y Pruebas)
```bash
# Copiar el simulador GPS
cp gps_simulator.py /opt/skyguard/
chmod +x /opt/skyguard/gps_simulator.py

# Ejecutar simulador para pruebas
cd /opt/skyguard
python gps_simulator.py
```

### Monitor de Dispositivos GPS
```bash
# Monitor rápido de dispositivos (comando Django)
python manage.py quick_device_monitor --quiet

# Monitor continuo de dispositivos
python manage.py start_device_monitor --timeout 1 --interval 60 --verbose

# Verificar estado de dispositivos
python manage.py check_device_status --timeout 60 --verbose

# Script de monitoreo automático
cp start_gps_monitor.py /opt/skyguard/
chmod +x /opt/skyguard/start_gps_monitor.py

# Monitor de posiciones GPS en tiempo real
cp monitor_gps_positions.py /opt/skyguard/
chmod +x /opt/skyguard/monitor_gps_positions.py
```

### Gestión de Servidores GPS
```bash
# Comandos de gestión de servidores GPS
python manage.py gps_servers start --daemon
python manage.py gps_servers stop
python manage.py gps_servers restart
python manage.py gps_servers status
python manage.py gps_servers stats

# Iniciar servidor específico
python manage.py gps_servers start --server concox
python manage.py gps_servers start --server meiligao
python manage.py gps_servers start --server satellite

# Solo procesamiento de emails de registro
python manage.py gps_servers start --email-only
```

## 9.2 Configuración de Servicios Systemd

### Servicio Principal de Servidores GPS
```bash
sudo nano /etc/systemd/system/skyguard-gps-servers.service
```

```ini
[Unit]
Description=SkyGuard GPS Servers
After=network.target postgresql.service skyguard-django.service
Requires=postgresql.service

[Service]
Type=forking
User=skyguard
Group=skyguard
WorkingDirectory=/opt/skyguard
Environment=DJANGO_SETTINGS_MODULE=skyguard.settings.production
ExecStart=/opt/skyguard/venv/bin/python manage.py gps_servers start --daemon
ExecStop=/opt/skyguard/venv/bin/python manage.py gps_servers stop
ExecReload=/opt/skyguard/venv/bin/python manage.py gps_servers restart
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=skyguard-gps

[Install]
WantedBy=multi-user.target
```

### Servicio de Monitor de Dispositivos
```bash
sudo nano /etc/systemd/system/skyguard-device-monitor.service
```

```ini
[Unit]
Description=SkyGuard Device Monitor
After=network.target postgresql.service skyguard-gps-servers.service
Requires=postgresql.service

[Service]
Type=simple
User=skyguard
Group=skyguard
WorkingDirectory=/opt/skyguard
Environment=DJANGO_SETTINGS_MODULE=skyguard.settings.production
ExecStart=/opt/skyguard/venv/bin/python manage.py start_device_monitor --timeout 2 --interval 60
Restart=always
RestartSec=15
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=skyguard-monitor

[Install]
WantedBy=multi-user.target
```

### Servicio de Verificación de Estado de Dispositivos
```bash
sudo nano /etc/systemd/system/skyguard-device-check.service
```

```ini
[Unit]
Description=SkyGuard Device Status Check
Requires=postgresql.service

[Service]
Type=oneshot
User=skyguard
Group=skyguard
WorkingDirectory=/opt/skyguard
Environment=DJANGO_SETTINGS_MODULE=skyguard.settings.production
ExecStart=/opt/skyguard/venv/bin/python manage.py check_device_status --timeout 120
```

### Timer para Verificación Periódica
```bash
sudo nano /etc/systemd/system/skyguard-device-check.timer
```

```ini
[Unit]
Description=Run SkyGuard Device Check every 5 minutes
Requires=skyguard-device-check.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

## 9.3 Configuración de Puertos GPS

### Configuración de Firewall para Protocolos GPS
```bash
# Puertos para protocolos GPS
sudo ufw allow 55300/tcp comment "Concox GPS Protocol"
sudo ufw allow 62000/udp comment "Meiligao GPS Protocol"  
sudo ufw allow 15557/tcp comment "Satellite Communication Protocol"

# Puertos para protocolo Wialon
sudo ufw allow 20332/tcp comment "Wialon GPS Protocol Standard"
sudo ufw allow 55301/tcp comment "Wialon GPS Protocol Alternative"
sudo ufw allow 60001/udp comment "Wialon GPS Protocol Legacy"

# Verificar reglas
sudo ufw status numbered
```

### Configuración de Variables de Entorno GPS
```bash
# Agregar al archivo .env.production
cat >> /opt/skyguard/.env.production << 'EOF'

# GPS Server Configuration
GPS_CONCOX_PORT=55300
GPS_MEILIGAO_PORT=62000
GPS_SATELLITE_PORT=15557

# Wialon Protocol Configuration
GPS_WIALON_PORT=20332
GPS_WIALON_ALT_PORT=55301
GPS_WIALON_LEGACY_PORT=60001

# GPS Server Settings
GPS_HEARTBEAT_TIMEOUT=120
GPS_DEVICE_OFFLINE_TIMEOUT=300
GPS_EMAIL_PROCESSOR_INTERVAL=1800

# GPS Logging
GPS_LOG_LEVEL=INFO
GPS_LOG_FILE=/opt/skyguard/logs/gps.log
EOF
```

## 9.4 Activación y Verificación de Servicios

### Habilitar y Iniciar Servicios
```bash
# Recargar configuración systemd
sudo systemctl daemon-reload

# Habilitar servicios GPS
sudo systemctl enable skyguard-gps-servers.service
sudo systemctl enable skyguard-device-monitor.service
sudo systemctl enable skyguard-device-check.service
sudo systemctl enable skyguard-device-check.timer

# Iniciar servicios
sudo systemctl start skyguard-gps-servers.service
sudo systemctl start skyguard-device-monitor.service
sudo systemctl start skyguard-device-check.timer

# Verificar estado
sudo systemctl status skyguard-gps-servers.service
sudo systemctl status skyguard-device-monitor.service
sudo systemctl status skyguard-device-check.timer
```

### Verificación de Conectividad GPS
```bash
# Verificar puertos abiertos
sudo netstat -tlnp | grep -E "55300|62000|15557|20332|55301|60001"

# Probar conectividad de protocolos
telnet localhost 55300  # Concox
nc -u localhost 62000   # Meiligao (UDP)
telnet localhost 15557  # Satellite
telnet localhost 20332  # Wialon Standard
telnet localhost 55301  # Wialon Alternative
nc -u localhost 60001   # Wialon Legacy (UDP)

# Verificar logs de GPS
sudo journalctl -u skyguard-gps-servers.service -f
sudo journalctl -u skyguard-device-monitor.service -f
tail -f /opt/skyguard/logs/gps.log
```

## 9.5 Scripts de Utilidad GPS

### Comando Wialon Legacy (Puerto 60001 UDP)
```bash
# Ejecutar servidor Wialon legacy independiente
python manage.py run_wialon_server

# Crear servicio systemd para Wialon legacy
sudo nano /etc/systemd/system/skyguard-wialon-legacy.service
```

Contenido del servicio Wialon legacy:
```ini
[Unit]
Description=SkyGuard Wialon Legacy Server
After=network.target postgresql.service

[Service]
Type=simple
User=skyguard
Group=skyguard
WorkingDirectory=/opt/skyguard
Environment=DJANGO_SETTINGS_MODULE=skyguard.settings.production
ExecStart=/opt/skyguard/venv/bin/python manage.py run_wialon_server
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=skyguard-wialon-legacy

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar servicio Wialon legacy
sudo systemctl daemon-reload
sudo systemctl enable skyguard-wialon-legacy.service
sudo systemctl start skyguard-wialon-legacy.service
sudo systemctl status skyguard-wialon-legacy.service
```

### Comandos de Gestión de Usuarios
```bash
# Crear usuario administrador
python manage.py create_superuser --username admin --email admin@tudominio.com

# Crear usuario regular
python manage.py create_user --username user --email user@tudominio.com --password user123

# Crear configuración por defecto para GPS
python manage.py create_default_harness
```

### Protocolos GPS Soportados

#### **Protocolo Concox (Puerto 55300 TCP)**
- Dispositivos compatibles: GT06, TK103, TK110, etc.
- Formato: Binario con estructura específica
- Autenticación por IMEI

#### **Protocolo Meiligao (Puerto 62000 UDP)** 
- Dispositivos compatibles: MVT340, MVT380, etc.
- Formato: Binario con checksum
- Soporte para comandos bidireccionales

#### **Protocolo Satellite (Puerto 15557 TCP)**
- Comunicación satelital
- Protocolo propietario
- Alta confiabilidad

#### **Protocolo Wialon**
- **Puerto 20332 TCP**: Protocolo estándar integrado
- **Puerto 55301 TCP**: Puerto alternativo
- **Puerto 60001 UDP**: Servidor legacy independiente

**Formatos de paquetes Wialon:**
- Login: `#L#<IMEI>;<password>\r\n`
- Data: `#D#<date>;<time>;<lat1>;<lat2>;<lon1>;<lon2>;<speed>;<course>;<height>;<sats>;<hdop>;<inputs>;<outputs>;<adc>;<ibutton>;<params>\r\n`
- Respuestas: `#AL#1\r\n` (login OK), `#AD#1\r\n` (data OK)

### Script de Prueba de Conectividad GPS
```bash
cat > /opt/skyguard/test_gps_connectivity.sh << 'EOF'
#!/bin/bash
echo "=== Prueba de Conectividad GPS ==="

# Verificar servicios
echo "1. Estado de servicios:"
systemctl is-active skyguard-gps-servers.service
systemctl is-active skyguard-device-monitor.service
systemctl is-active skyguard-wialon-legacy.service

# Verificar puertos
echo "2. Puertos GPS abiertos:"
netstat -tlnp | grep -E "55300|62000|15557|20332|55301|60001" || echo "No hay puertos GPS abiertos"

# Verificar base de datos
echo "3. Dispositivos GPS registrados:"
cd /opt/skyguard
python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
print(f'Total dispositivos: {GPSDevice.objects.count()}')
print(f'Dispositivos online: {GPSDevice.objects.filter(connection_status=\"ONLINE\").count()}')
print(f'Dispositivos offline: {GPSDevice.objects.filter(connection_status=\"OFFLINE\").count()}')
"

# Verificar logs recientes
echo "4. Logs recientes de GPS:"
journalctl -u skyguard-gps-servers.service --since "5 minutes ago" --no-pager | tail -5

# Verificar protocolos específicos
echo "5. Prueba de protocolos:"
timeout 3 telnet localhost 55300 </dev/null && echo "Concox: OK" || echo "Concox: FAIL"
timeout 3 nc -u -w 1 localhost 62000 </dev/null && echo "Meiligao: OK" || echo "Meiligao: FAIL"
timeout 3 telnet localhost 15557 </dev/null && echo "Satellite: OK" || echo "Satellite: FAIL"
timeout 3 telnet localhost 20332 </dev/null && echo "Wialon Standard: OK" || echo "Wialon Standard: FAIL"
timeout 3 telnet localhost 55301 </dev/null && echo "Wialon Alt: OK" || echo "Wialon Alt: FAIL"
timeout 3 nc -u -w 1 localhost 60001 </dev/null && echo "Wialon Legacy: OK" || echo "Wialon Legacy: FAIL"

echo "=== Fin de la prueba ==="
EOF

chmod +x /opt/skyguard/test_gps_connectivity.sh
```

### Script de Monitoreo Avanzado GPS
```bash
cat > /opt/skyguard/monitor_gps_system.sh << 'EOF'
#!/bin/bash
echo "=== Monitor del Sistema GPS ==="

while true; do
    clear
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Estado del Sistema GPS"
    echo "=================================================="
    
    # Estado de servicios
    echo "Servicios:"
    echo "  GPS Servers: $(systemctl is-active skyguard-gps-servers.service)"
    echo "  Device Monitor: $(systemctl is-active skyguard-device-monitor.service)"
    echo "  Wialon Legacy: $(systemctl is-active skyguard-wialon-legacy.service)"
    
    # Estadísticas de dispositivos
    cd /opt/skyguard
    python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
from django.utils import timezone
from datetime import timedelta

total = GPSDevice.objects.count()
online = GPSDevice.objects.filter(connection_status='ONLINE').count()
offline = GPSDevice.objects.filter(connection_status='OFFLINE').count()

# Dispositivos activos en la última hora
active_hour = GPSDevice.objects.filter(
    last_heartbeat__gte=timezone.now() - timedelta(hours=1)
).count()

print(f'  Total: {total} | Online: {online} | Offline: {offline} | Activos (1h): {active_hour}')
"
    
    # Conexiones activas por protocolo
    echo "Conexiones GPS activas:"
    echo "  Concox (55300): $(netstat -tn | grep ':55300' | wc -l)"
    echo "  Meiligao (62000): $(netstat -un | grep ':62000' | wc -l)"
    echo "  Satellite (15557): $(netstat -tn | grep ':15557' | wc -l)"
    echo "  Wialon Std (20332): $(netstat -tn | grep ':20332' | wc -l)"
    echo "  Wialon Alt (55301): $(netstat -tn | grep ':55301' | wc -l)"
    echo "  Wialon Legacy (60001): $(netstat -un | grep ':60001' | wc -l)"
    
    sleep 10
done
EOF

chmod +x /opt/skyguard/monitor_gps_system.sh
```

## 9.6 Configuración de Logs GPS

### Configuración de Logrotate para GPS
```bash
sudo nano /etc/logrotate.d/skyguard-gps
```

```
/opt/skyguard/logs/gps.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 skyguard skyguard
    postrotate
        systemctl reload skyguard-gps-servers.service > /dev/null 2>&1 || true
    endscript
}

/var/log/skyguard-gps.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 syslog adm
}

/var/log/skyguard-monitor.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 syslog adm
}

/var/log/skyguard-wialon-legacy.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 syslog adm
}
```

### Configuración de Rsyslog para GPS
```bash
sudo nano /etc/rsyslog.d/50-skyguard-gps.conf
```

```
# SkyGuard GPS logging
:programname, isequal, "skyguard-gps" /var/log/skyguard-gps.log
:programname, isequal, "skyguard-monitor" /var/log/skyguard-monitor.log
:programname, isequal, "skyguard-wialon-legacy" /var/log/skyguard-wialon-legacy.log
& stop
```

```bash
sudo systemctl restart rsyslog
```

## 9.7 Comandos de Mantenimiento GPS

### Limpieza Automática de Datos GPS
```bash
# Script de limpieza diaria
cat > /opt/skyguard/cleanup_gps_data.sh << 'EOF'
#!/bin/bash
echo "$(date): Iniciando limpieza de datos GPS"

cd /opt/skyguard
source venv/bin/activate

# Limpiar posiciones antiguas (más de 90 días)
python manage.py shell -c "
from skyguard.apps.gps.models import GPSLocation
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
old_date = timezone.now() - timedelta(days=90)
deleted = GPSLocation.objects.filter(timestamp__lt=old_date).delete()
print(f'Eliminadas {deleted[0]} posiciones GPS antiguas')
logger.info(f'GPS cleanup: {deleted[0]} old locations deleted')
"

# Limpiar eventos antiguos (más de 180 días)
python manage.py shell -c "
from skyguard.apps.gps.models import GPSEvent
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
old_date = timezone.now() - timedelta(days=180)
deleted = GPSEvent.objects.filter(timestamp__lt=old_date).delete()
print(f'Eliminados {deleted[0]} eventos GPS antiguos')
logger.info(f'GPS cleanup: {deleted[0]} old events deleted')
"

# Optimizar tablas GPS
sudo -u postgres psql skyguard_db -c "
VACUUM ANALYZE skyguard_gps_gpslocation;
VACUUM ANALYZE skyguard_gps_gpsevent;
VACUUM ANALYZE skyguard_gps_gpsdevice;
"

echo "$(date): Limpieza de datos GPS completada"
EOF

chmod +x /opt/skyguard/cleanup_gps_data.sh

# Programar limpieza diaria a las 3 AM
echo "0 3 * * * /opt/skyguard/cleanup_gps_data.sh >> /opt/skyguard/logs/cleanup.log 2>&1" | sudo crontab -u skyguard -
```

#### Monitoreo Avanzado GPS
```bash
# Script de monitoreo de salud GPS
cat > /opt/skyguard/health_check_gps.sh << 'EOF'
#!/bin/bash
LOGFILE="/opt/skyguard/logs/gps_health.log"
ALERT_EMAIL="admin@tudominio.com"

echo "$(date): Verificación de salud GPS" >> $LOGFILE

cd /opt/skyguard
source venv/bin/activate

# Verificar servicios GPS
services=("skyguard-gps-servers" "skyguard-device-monitor" "skyguard-wialon-legacy")
for service in "${services[@]}"; do
    if ! systemctl is-active --quiet $service; then
        echo "ALERTA: Servicio $service no está activo" >> $LOGFILE
        echo "Servicio $service no está activo" | mail -s "ALERTA GPS SkyGuard" $ALERT_EMAIL
        systemctl restart $service.service
    fi
done

# Verificar puertos GPS
ports=("55300:Concox" "62000:Meiligao" "15557:Satellite" "20332:Wialon-Std" "55301:Wialon-Alt" "60001:Wialon-Legacy")
for port_info in "${ports[@]}"; do
    port=${port_info%:*}
    name=${port_info#*:}
    if ! netstat -tlnp | grep -q ":$port "; then
        echo "ALERTA: Puerto GPS $port ($name) no está abierto" >> $LOGFILE
        echo "Puerto GPS $port ($name) no está disponible" | mail -s "ALERTA GPS SkyGuard" $ALERT_EMAIL
    fi
done

# Verificar dispositivos activos
ACTIVE_DEVICES=$(python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
from django.utils import timezone
from datetime import timedelta
active = GPSDevice.objects.filter(
    last_heartbeat__gte=timezone.now() - timedelta(minutes=10)
).count()
print(active)
")

echo "Dispositivos activos (últimos 10 min): $ACTIVE_DEVICES" >> $LOGFILE

# Verificar uso de memoria de servicios GPS
for service in gps_servers device_monitor; do
    GPS_MEMORY=$(ps aux | grep "$service" | grep -v grep | awk '{sum+=$6} END {print sum/1024}')
    if [ ! -z "$GPS_MEMORY" ] && (( $(echo "$GPS_MEMORY > 1000" | bc -l) )); then
        echo "ALERTA: Alto uso de memoria en $service: ${GPS_MEMORY}MB" >> $LOGFILE
        echo "Alto uso de memoria en $service: ${GPS_MEMORY}MB" | mail -s "ALERTA GPS SkyGuard" $ALERT_EMAIL
    fi
done

echo "$(date): Verificación completada" >> $LOGFILE
EOF

chmod +x /opt/skyguard/health_check_gps.sh

# Programar verificación cada 15 minutos
echo "*/15 * * * * /opt/skyguard/health_check_gps.sh" | sudo crontab -u skyguard -
```

#### Backup Avanzado de Datos GPS
```bash
# Script de backup incremental GPS
cat > /opt/skyguard/backup_gps_incremental.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/skyguard/backups/gps"
DATE=$(date +%Y%m%d_%H%M%S)
LAST_BACKUP_FILE="$BACKUP_DIR/.last_backup"

mkdir -p $BACKUP_DIR

# Determinar fecha del último backup
if [ -f "$LAST_BACKUP_FILE" ]; then
    LAST_BACKUP=$(cat $LAST_BACKUP_FILE)
else
    LAST_BACKUP=$(date -d "7 days ago" '+%Y-%m-%d %H:%M:%S')
fi

echo "Backup incremental GPS desde: $LAST_BACKUP"

cd /opt/skyguard
source venv/bin/activate

# Backup de datos GPS incrementales
python manage.py shell -c "
import csv
from skyguard.apps.gps.models import GPSLocation, GPSEvent, GPSDevice
from django.utils import timezone
from datetime import datetime

last_backup = datetime.strptime('$LAST_BACKUP', '%Y-%m-%d %H:%M:%S')
last_backup = timezone.make_aware(last_backup)

# Backup de posiciones nuevas
locations = GPSLocation.objects.filter(timestamp__gte=last_backup)
with open('$BACKUP_DIR/locations_$DATE.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['device_imei', 'timestamp', 'latitude', 'longitude', 'speed', 'course'])
    for loc in locations:
        writer.writerow([
            loc.device.imei, loc.timestamp, 
            loc.position.y, loc.position.x, 
            loc.speed, loc.course
        ])

print(f'Exportadas {locations.count()} posiciones GPS')

# Backup de eventos nuevos
events = GPSEvent.objects.filter(timestamp__gte=last_backup)
with open('$BACKUP_DIR/events_$DATE.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['device_imei', 'timestamp', 'event_type', 'data'])
    for event in events:
        writer.writerow([
            event.device.imei, event.timestamp,
            event.event_type, str(event.data)
        ])

print(f'Exportados {events.count()} eventos GPS')
"

# Comprimir backups
gzip $BACKUP_DIR/locations_$DATE.csv 2>/dev/null || true
gzip $BACKUP_DIR/events_$DATE.csv 2>/dev/null || true

# Actualizar fecha del último backup
echo "$(date '+%Y-%m-%d %H:%M:%S')" > $LAST_BACKUP_FILE

echo "Backup incremental GPS completado: $DATE"

# Limpiar backups antiguos (más de 60 días)
find $BACKUP_DIR -name "*.csv.gz" -mtime +60 -delete
EOF

chmod +x /opt/skyguard/backup_gps_incremental.sh

# Programar backup incremental cada 6 horas
echo "0 */6 * * * /opt/skyguard/backup_gps_incremental.sh >> /opt/skyguard/logs/backup.log 2>&1" | sudo crontab -u skyguard -
```

#### Optimización de Rendimiento GPS
```bash
# Script de optimización GPS
cat > /opt/skyguard/optimize_gps_performance.sh << 'EOF'
#!/bin/bash
echo "$(date): Iniciando optimización GPS"

cd /opt/skyguard
source venv/bin/activate

# Crear índices adicionales para GPS si no existen
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()

# Índices para optimizar consultas GPS
indexes = [
    'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gps_location_timestamp ON skyguard_gps_gpslocation(timestamp);',
    'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gps_location_device_timestamp ON skyguard_gps_gpslocation(device_id, timestamp);',
    'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gps_event_timestamp ON skyguard_gps_gpsevent(timestamp);',
    'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gps_device_heartbeat ON skyguard_gps_gpsdevice(last_heartbeat);',
    'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gps_device_status ON skyguard_gps_gpsdevice(connection_status);'
]

for index_sql in indexes:
    try:
        cursor.execute(index_sql)
        print(f'Índice creado: {index_sql[:50]}...')
    except Exception as e:
        print(f'Error creando índice: {e}')
"

# Actualizar estadísticas de tablas GPS
sudo -u postgres psql skyguard_db -c "
ANALYZE skyguard_gps_gpslocation;
ANALYZE skyguard_gps_gpsevent;
ANALYZE skyguard_gps_gpsdevice;
"

# Verificar configuración de PostgreSQL para GPS
sudo -u postgres psql skyguard_db -c "
SELECT name, setting, unit FROM pg_settings 
WHERE name IN ('shared_buffers', 'work_mem', 'maintenance_work_mem', 'effective_cache_size');
"

echo "$(date): Optimización GPS completada"
EOF

chmod +x /opt/skyguard/optimize_gps_performance.sh

# Ejecutar optimización semanalmente
echo "0 4 * * 0 /opt/skyguard/optimize_gps_performance.sh >> /opt/skyguard/logs/optimization.log 2>&1" | sudo crontab -u skyguard -
```

## 9.8 Verificación Completa del Sistema GPS

### Script de Verificación Integral
```bash
cat > /opt/skyguard/gps_system_check.sh << 'EOF'
#!/bin/bash
echo "=== Verificación Integral del Sistema GPS SkyGuard ==="
echo "Fecha: $(date)"
echo "=========================================================="

# 1. Verificar servicios del sistema
echo "1. SERVICIOS DEL SISTEMA:"
services=("skyguard-gps-servers" "skyguard-device-monitor" "skyguard-wialon-legacy" "nginx" "postgresql" "redis-server")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "  ✓ $service: ACTIVO"
    else
        echo "  ✗ $service: INACTIVO"
    fi
done

# 2. Verificar puertos GPS
echo -e "\n2. PUERTOS GPS:"
ports=("55300:Concox" "62000:Meiligao" "15557:Satellite" "20332:Wialon-Std" "55301:Wialon-Alt" "60001:Wialon-Legacy")
for port_info in "${ports[@]}"; do
    port=${port_info%:*}
    name=${port_info#*:}
    if netstat -tlnp | grep -q ":$port "; then
        echo "  ✓ Puerto $port ($name): ABIERTO"
    else
        echo "  ✗ Puerto $port ($name): CERRADO"
    fi
done

# 3. Verificar conectividad de base de datos
echo -e "\n3. BASE DE DATOS:"
cd /opt/skyguard
if python manage.py shell -c "from django.db import connection; connection.cursor().execute('SELECT 1'); print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "  ✓ Conexión a PostgreSQL: OK"
    
    # Estadísticas de dispositivos
    python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
print(f'Total dispositivos: {GPSDevice.objects.count()}')
print(f'Dispositivos online: {GPSDevice.objects.filter(connection_status=\"ONLINE\").count()}')
print(f'Dispositivos offline: {GPSDevice.objects.filter(connection_status=\"OFFLINE\").count()}')
" 2>/dev/null || echo "  ✗ Error consultando dispositivos"
else
    echo "  ✗ Conexión a PostgreSQL: FALLO"
fi

# 4. Verificar Redis
echo -e "\n4. REDIS:"
if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo "  ✓ Redis: CONECTADO"
else
    echo "  ✗ Redis: DESCONECTADO"
fi

# 5. Verificar logs recientes
echo -e "\n5. LOGS RECIENTES (últimas 24 horas):"
journalctl -u skyguard-gps-servers.service --since "24 hours ago" --no-pager -q 2>/dev/null | tail -5

# 6. Verificar espacio en disco
echo -e "\n6. RECURSOS DEL SISTEMA:"
disk_usage=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
if [ $disk_usage -lt 80 ]; then
    echo "  ✓ Espacio en disco: ${disk_usage}% (OK)"
else
    echo "  ⚠ Advertencia: Espacio en disco alto ($disk_usage%)"
fi

mem_usage=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')
if [ $mem_usage -lt 80 ]; then
    echo "  ✓ Uso de memoria: ${mem_usage}% (OK)"
else
    echo "  ⚠ Advertencia: Uso de memoria alto ($mem_usage%)"
fi

echo -e "\n=== Verificación completada: $(date) ==="
EOF

chmod +x /opt/skyguard/gps_system_check.sh
```

### Comandos de Gestión Rápida
```bash
# Crear aliases útiles para administración
cat >> ~/.bashrc << 'EOF'

# SkyGuard GPS Aliases
alias gps-status='sudo systemctl status skyguard-gps-servers skyguard-device-monitor skyguard-wialon-legacy'
alias gps-start='sudo systemctl start skyguard-gps-servers skyguard-device-monitor skyguard-wialon-legacy'
alias gps-stop='sudo systemctl stop skyguard-gps-servers skyguard-device-monitor skyguard-wialon-legacy'
alias gps-logs='sudo journalctl -f -u skyguard-gps-servers -u skyguard-device-monitor'
alias skyguard-logs='sudo journalctl -f -u skyguard-django -u nginx'
EOF

source ~/.bashrc
```

### Configuración de Alertas por Email
```bash
# Instalar mailutils para notificaciones
sudo apt install -y mailutils

# Configurar postfix básico (seleccionar "Internet Site")
sudo dpkg-reconfigure postfix

# Script de notificación de errores críticos
cat > /opt/skyguard/critical_alert.sh << 'EOF'
#!/bin/bash
ALERT_EMAIL="admin@tudominio.com"
HOSTNAME=$(hostname)

# Función para enviar alerta
send_alert() {
    local subject="$1"
    local message="$2"
    echo "$message" | mail -s "ALERTA CRÍTICA SkyGuard - $HOSTNAME: $subject" $ALERT_EMAIL
}

# Verificar servicios críticos
critical_services=("skyguard-gps-servers" "skyguard-device-monitor" "skyguard-wialon-legacy")
for service in "${critical_services[@]}"; do
    if ! systemctl is-active --quiet $service.service; then
        send_alert "Servicio $service no está activo" "El servicio $service no está funcionando en $HOSTNAME. Verificar inmediatamente."
    fi
done

# Verificar puertos GPS
ports=("55300:Concox" "62000:Meiligao" "15557:Satellite" "20332:Wialon-Std" "55301:Wialon-Alt" "60001:Wialon-Legacy")
for port_info in "${ports[@]}"; do
    port=${port_info%:*}
    name=${port_info#*:}
    if ! netstat -tlnp | grep -q ":$port "; then
        send_alert "Puerto GPS $port ($name) no está abierto" "Puerto GPS $port ($name) no está disponible"
    fi
done

# Verificar dispositivos activos
ACTIVE_DEVICES=$(python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
from django.utils import timezone
from datetime import timedelta
active = GPSDevice.objects.filter(
    last_heartbeat__gte=timezone.now() - timedelta(minutes=10)
).count()
print(active)
")

echo "Dispositivos activos (últimos 10 min): $ACTIVE_DEVICES"

# Verificar uso de memoria de servicios GPS
for service in gps_servers device_monitor; do
    GPS_MEMORY=$(ps aux | grep "$service" | grep -v grep | awk '{sum+=$6} END {print sum/1024}')
    if [ ! -z "$GPS_MEMORY" ] && (( $(echo "$GPS_MEMORY > 1000" | bc -l) )); then
        send_alert "Alto uso de memoria en $service: ${GPS_MEMORY}MB" "Alto uso de memoria en $service: ${GPS_MEMORY}MB"
    fi
done

echo "$(date): Verificación completada"
EOF

chmod +x /opt/skyguard/critical_alert.sh

# Programar alertas críticas cada 5 minutos
echo "*/5 * * * * /opt/skyguard/critical_alert.sh" | sudo crontab -u skyguard -
```

### Comandos de Diagnóstico Avanzado
```bash
# Script de diagnóstico completo
cat > /opt/skyguard/diagnose_gps_issues.sh << 'EOF'
#!/bin/bash
echo "=== Diagnóstico Avanzado GPS SkyGuard ==="
echo "Iniciado: $(date)"

cd /opt/skyguard

# 1. Verificar configuración de Django
echo -e "\n1. CONFIGURACIÓN DJANGO:"
python manage.py check --deploy 2>/dev/null && echo "  ✓ Configuración Django: OK" || echo "  ✗ Configuración Django: ERRORES"

# 2. Verificar migraciones
echo -e "\n2. MIGRACIONES:"
python manage.py showmigrations --plan 2>/dev/null | grep -q "\[ \]" && echo "  ⚠ Hay migraciones pendientes" || echo "  ✓ Todas las migraciones aplicadas"

# 3. Análisis de logs de errores
echo -e "\n3. ANÁLISIS DE LOGS (últimas 24 horas):"
error_count=$(journalctl --since "24 hours ago" --no-pager -u skyguard-gps-servers -u skyguard-device-monitor | grep -i "error\|exception\|fail" | wc -l)
echo "  Errores encontrados en logs: $error_count"

if [ $error_count -gt 0 ]; then
    echo "  Últimos errores:"
    journalctl --since "24 hours ago" --no-pager -u skyguard-gps-servers -u skyguard-device-monitor | grep -i "error\|exception\|fail" | tail -5 | sed 's/^/    /'
fi

# 4. Verificar conectividad de dispositivos
echo -e "\n4. CONECTIVIDAD DE DISPOSITIVOS:"
python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
from django.utils import timezone
from datetime import timedelta

# Dispositivos por protocolo
protocols = GPSDevice.objects.values_list('protocol', flat=True).distinct()
for protocol in protocols:
    count = GPSDevice.objects.filter(protocol=protocol).count()
    online = GPSDevice.objects.filter(protocol=protocol, connection_status='ONLINE').count()
    print(f'  {protocol.upper()}: {online}/{count} online')

# Dispositivos con problemas de conexión
problem_devices = GPSDevice.objects.filter(
    last_heartbeat__lt=timezone.now() - timedelta(hours=1)
).exclude(connection_status='OFFLINE')[:5]

if problem_devices:
    echo "  Dispositivos con problemas de heartbeat:"
    for device in problem_devices:
        echo "    IMEI ${device.imei}: último heartbeat hace ${timezone.now() - device.last_heartbeat if device.last_heartbeat else "nunca"}"
else
    echo "  ✓ Dispositivos GPS: OK"
fi

# 5. Verificar performance de base de datos
echo -e "\n5. PERFORMANCE BASE DE DATOS:"
query_time=$(python manage.py shell -c "
import time
from django.db import connection
start = time.time()
cursor = connection.cursor()
cursor.execute('SELECT COUNT(*) FROM skyguard_gps_gpsdevice')
result = cursor.fetchone()
end = time.time()
print(f'{(end-start)*1000:.2f}')
" 2>/dev/null)

if [ ! -z "$query_time" ]; then
    echo "  Tiempo de consulta básica: ${query_time}ms"
    if (( $(echo "$query_time > 1000" | bc -l) )); then
        echo "  ⚠ Consultas lentas detectadas"
    fi
fi

# 6. Verificar archivos de log grandes
echo -e "\n6. TAMAÑO DE LOGS:"
log_files=("/opt/skyguard/logs/gps.log" "/var/log/skyguard-gps.log" "/var/log/skyguard-monitor.log")
for log_file in "${log_files[@]}"; do
    if [ -f "$log_file" ]; then
        size=$(du -h "$log_file" | cut -f1)
        echo "  $log_file: $size"
    fi
done

echo -e "\n=== Diagnóstico completado: $(date) ==="
EOF

chmod +x /opt/skyguard/diagnose_gps_issues.sh
```

### Comandos de Utilidad GPS
```bash
# Script de utilidades GPS
cat > /opt/skyguard/gps_utilities.sh << 'EOF'
#!/bin/bash

show_help() {
    echo "=== Utilidades GPS SkyGuard ==="
    echo "Uso: $0 [comando] [opciones]"
    echo ""
    echo "Comandos disponibles:"
    echo "  devices         - Mostrar estadísticas de dispositivos"
    echo "  protocols       - Mostrar protocolos activos"
    echo "  ports          - Verificar puertos GPS"
    echo "  logs           - Mostrar logs recientes"
    echo "  performance    - Mostrar métricas de rendimiento"
    echo "  cleanup        - Limpiar logs antiguos"
    echo "  reset-device   - Resetear dispositivo por IMEI"
    echo "  test-protocol  - Probar protocolo específico"
    echo "  backup         - Crear backup de datos GPS"
    echo "  help           - Mostrar esta ayuda"
}

show_devices() {
    cd /opt/skyguard
    echo "=== Estadísticas de Dispositivos GPS ==="
    python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
from django.utils import timezone
from datetime import timedelta

print('📊 RESUMEN GENERAL:')
total = GPSDevice.objects.count()
online = GPSDevice.objects.filter(connection_status='ONLINE').count()
offline = GPSDevice.objects.filter(connection_status='OFFLINE').count()
print(f'  Total: {total}')
print(f'  Online: {online}')
print(f'  Offline: {offline}')

print('\n📡 POR PROTOCOLO:')
protocols = GPSDevice.objects.values_list('protocol', flat=True).distinct()
for protocol in protocols:
    count = GPSDevice.objects.filter(protocol=protocol).count()
    online_count = GPSDevice.objects.filter(protocol=protocol, connection_status='ONLINE').count()
    print(f'  {protocol.upper()}: {online_count}/{count} activos')

print('\n⏰ ACTIVIDAD RECIENTE:')
recent = GPSDevice.objects.filter(
    last_heartbeat__gte=timezone.now() - timedelta(minutes=10)
).count()
print(f'  Activos últimos 10 min: {recent}')

stale = GPSDevice.objects.filter(
    last_heartbeat__lt=timezone.now() - timedelta(hours=1)
).exclude(connection_status='OFFLINE').count()
print(f'  Sin heartbeat > 1h: {stale}')
"
}

show_protocols() {
    echo "=== Protocolos GPS Activos ==="
    echo "Puerto | Protocolo | Estado | Conexiones"
    echo "-------|-----------|--------|------------"
    
    # Verificar puertos y conexiones
    ports=("55300:Concox:TCP" "62000:Meiligao:UDP" "15557:Satellite:TCP" "20332:Wialon-Std:TCP" "55301:Wialon-Alt:TCP" "60001:Wialon-Legacy:UDP")
    
    for port_info in "${ports[@]}"; do
        IFS=':' read -r port protocol type <<< "$port_info"
        
        if [ "$type" = "TCP" ]; then
            if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
                connections=$(netstat -tn 2>/dev/null | grep ":$port " | wc -l)
                echo "$port   | $protocol | ✓ Activo | $connections"
            else
                echo "$port   | $protocol | ✗ Inactivo | 0"
            fi
        else
            if netstat -ulnp 2>/dev/null | grep -q ":$port "; then
                echo "$port   | $protocol | ✓ Activo | N/A (UDP)"
            else
                echo "$port   | $protocol | ✗ Inactivo | 0"
            fi
        fi
    done
}

show_performance() {
    echo "=== Métricas de Rendimiento GPS ==="
    cd /opt/skyguard
    
    echo "🔄 SERVICIOS:"
    systemctl is-active skyguard-gps-servers && echo "  GPS Servers: ✓ Activo" || echo "  GPS Servers: ✗ Inactivo"
    systemctl is-active skyguard-device-monitor && echo "  Device Monitor: ✓ Activo" || echo "  Device Monitor: ✗ Inactivo"
    systemctl is-active skyguard-wialon-legacy && echo "  Wialon Legacy: ✓ Activo" || echo "  Wialon Legacy: ✗ Inactivo"
    
    echo -e "\n💾 MEMORIA:"
    ps aux | grep -E "(gps_servers|device_monitor|wialon)" | grep -v grep | awk '{print "  " $11 ": " $6/1024 " MB"}'
    
    echo -e "\n💽 BASE DE DATOS:"
    python manage.py shell -c "
import time
from django.db import connection
from skyguard.apps.gps.models import GPSDevice, GPSLocation

# Tiempo de consulta
start = time.time()
device_count = GPSDevice.objects.count()
end = time.time()
print(f'  Dispositivos: {device_count} (consulta: {(end-start)*1000:.2f}ms)')

start = time.time()
location_count = GPSLocation.objects.count()
end = time.time()
print(f'  Ubicaciones: {location_count} (consulta: {(end-start)*1000:.2f}ms)')
" 2>/dev/null
}

reset_device() {
    if [ -z "$2" ]; then
        echo "Uso: $0 reset-device <IMEI>"
        return 1
    fi
    
    local imei="$2"
    cd /opt/skyguard
    
    echo "Reseteando dispositivo IMEI: $imei"
    python manage.py shell -c "
from skyguard.apps.gps.models import GPSDevice
try:
    device = GPSDevice.objects.get(imei='$imei')
    device.connection_status = 'OFFLINE'
    device.last_heartbeat = None
    device.save()
    print(f'✓ Dispositivo {device.imei} reseteado correctamente')
except GPSDevice.DoesNotExist:
    print(f'✗ Dispositivo con IMEI $imei no encontrado')
except Exception as e:
    print(f'✗ Error: {e}')
"
}

test_protocol() {
    if [ -z "$2" ]; then
        echo "Protocolos disponibles: concox, meiligao, satellite, wialon"
        echo "Uso: $0 test-protocol <protocolo>"
        return 1
    fi
    
    local protocol="$2"
    
    case $protocol in
        "concox")
            echo "Probando protocolo Concox (puerto 55300)..."
            timeout 5 telnet localhost 55300 2>/dev/null && echo "✓ Concox: Conectado" || echo "✗ Concox: No disponible"
            ;;
        "meiligao")
            echo "Probando protocolo Meiligao (puerto 62000)..."
            timeout 5 nc -u -z localhost 62000 2>/dev/null && echo "✓ Meiligao: Disponible" || echo "✗ Meiligao: No disponible"
            ;;
        "satellite")
            echo "Probando protocolo Satellite (puerto 15557)..."
            timeout 5 telnet localhost 15557 2>/dev/null && echo "✓ Satellite: Conectado" || echo "✗ Satellite: No disponible"
            ;;
        "wialon")
            echo "Probando protocolo Wialon..."
            echo "  Puerto 20332 (Estándar):"
            timeout 5 telnet localhost 20332 2>/dev/null && echo "    ✓ Conectado" || echo "    ✗ No disponible"
            echo "  Puerto 55301 (Alternativo):"
            timeout 5 telnet localhost 55301 2>/dev/null && echo "    ✓ Conectado" || echo "    ✗ No disponible"
            echo "  Puerto 60001 (Legacy UDP):"
            timeout 5 nc -u -z localhost 60001 2>/dev/null && echo "    ✓ Disponible" || echo "    ✗ No disponible"
            ;;
        *)
            echo "Protocolo no reconocido: $protocol"
            echo "Protocolos disponibles: concox, meiligao, satellite, wialon"
            ;;
    esac
}

backup_gps_data() {
    echo "=== Backup de Datos GPS ==="
    BACKUP_DIR="/opt/skyguard/backups"
    DATE=$(date +%Y%m%d_%H%M%S)
    
    mkdir -p $BACKUP_DIR
    cd /opt/skyguard
    
    echo "Creando backup de base de datos GPS..."
    python manage.py dumpdata skyguard.gps --indent 2 > "$BACKUP_DIR/gps_data_$DATE.json"
    
    echo "Comprimiendo backup..."
    gzip "$BACKUP_DIR/gps_data_$DATE.json"
    
    echo "✓ Backup creado: $BACKUP_DIR/gps_data_$DATE.json.gz"
    
    # Limpiar backups antiguos (más de 30 días)
    find $BACKUP_DIR -name "gps_data_*.json.gz" -mtime +30 -delete
    echo "✓ Backups antiguos limpiados"
}

cleanup_logs() {
    echo "=== Limpieza de Logs GPS ==="
    
    # Rotar logs de journalctl
    sudo journalctl --vacuum-time=7d
    
    # Limpiar logs de aplicación
    log_files=("/opt/skyguard/logs/gps.log" "/var/log/skyguard-gps.log" "/var/log/skyguard-monitor.log")
    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            # Mantener solo las últimas 1000 líneas
            tail -1000 "$log_file" > "$log_file.tmp" && mv "$log_file.tmp" "$log_file"
            echo "✓ Limpiado: $log_file"
        fi
    done
    
    echo "✓ Limpieza de logs completada"
}

# Función principal
case "$1" in
    "devices")
        show_devices
        ;;
    "protocols")
        show_protocols
        ;;
    "ports")
        show_protocols
        ;;
    "logs")
        echo "=== Logs GPS Recientes ==="
        journalctl -u skyguard-gps-servers -u skyguard-device-monitor --since "1 hour ago" --no-pager | tail -20
        ;;
    "performance")
        show_performance
        ;;
    "cleanup")
        cleanup_logs
        ;;
    "reset-device")
        reset_device "$@"
        ;;
    "test-protocol")
        test_protocol "$@"
        ;;
    "backup")
        backup_gps_data
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "Comando no reconocido: $1"
        show_help
        ;;
esac
EOF

chmod +x /opt/skyguard/gps_utilities.sh

# Crear enlace simbólico para acceso fácil
sudo ln -sf /opt/skyguard/gps_utilities.sh /usr/local/bin/gps-util
```

## 10. Resumen Final y Verificación

### 10.1 Lista de Verificación Completa

```bash
# Script de verificación final
cat > /opt/skyguard/final_deployment_check.sh << 'EOF'
#!/bin/bash
echo "=== VERIFICACIÓN FINAL DE DESPLIEGUE GPS SKYGUARD ==="
echo "Fecha: $(date)"
echo "============================================================"

ERRORS=0
WARNINGS=0

check_item() {
    local description="$1"
    local command="$2"
    local is_critical="$3"
    
    echo -n "Verificando $description... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo "✓ OK"
    else
        if [ "$is_critical" = "true" ]; then
            echo "✗ ERROR"
            ((ERRORS++))
        else
            echo "⚠ ADVERTENCIA"
            ((WARNINGS++))
        fi
    fi
}

echo "1. SERVICIOS CRÍTICOS:"
check_item "Django (skyguard-django)" "systemctl is-active --quiet skyguard-django" true
check_item "GPS Servers (skyguard-gps-servers)" "systemctl is-active --quiet skyguard-gps-servers" true
check_item "Device Monitor (skyguard-device-monitor)" "systemctl is-active --quiet skyguard-device-monitor" true
check_item "PostgreSQL" "systemctl is-active --quiet postgresql" true
check_item "Redis" "systemctl is-active --quiet redis-server" true
check_item "Nginx" "systemctl is-active --quiet nginx" true

echo -e "\n2. SERVICIOS GPS OPCIONALES:"
check_item "Wialon Legacy (skyguard-wialon-legacy)" "systemctl is-active --quiet skyguard-wialon-legacy" false

echo -e "\n3. PUERTOS GPS:"
check_item "Puerto 55300 (Concox)" "netstat -tlnp | grep -q ':55300 '" true
check_item "Puerto 62000 (Meiligao)" "netstat -ulnp | grep -q ':62000 '" true
check_item "Puerto 15557 (Satellite)" "netstat -tlnp | grep -q ':15557 '" true
check_item "Puerto 20332 (Wialon Std)" "netstat -tlnp | grep -q ':20332 '" true
check_item "Puerto 55301 (Wialon Alt)" "netstat -tlnp | grep -q ':55301 '" false
check_item "Puerto 60001 (Wialon Legacy)" "netstat -ulnp | grep -q ':60001 '" false

echo -e "\n4. CONECTIVIDAD:"
check_item "Base de datos Django" "cd /opt/skyguard && python manage.py shell -c 'from django.db import connection; connection.cursor().execute(\"SELECT 1\")'" true
check_item "Redis conectividad" "redis-cli ping | grep -q PONG" true
check_item "Nginx respondiendo" "curl -s -o /dev/null -w '%{http_code}' http://localhost | grep -q 200" true

echo -e "\n5. ARCHIVOS DE CONFIGURACIÓN:"
check_item "Archivo .env.production" "[ -f /opt/skyguard/.env.production ]" true
check_item "Configuración Nginx" "[ -f /etc/nginx/sites-enabled/skyguard ]" true
check_item "Servicio GPS Servers" "[ -f /etc/systemd/system/skyguard-gps-servers.service ]" true
check_item "Servicio Device Monitor" "[ -f /etc/systemd/system/skyguard-device-monitor.service ]" true

echo -e "\n6. SCRIPTS DE MANTENIMIENTO:"
check_item "Script de verificación GPS" "[ -x /opt/skyguard/gps_system_check.sh ]" false
check_item "Script de utilidades GPS" "[ -x /opt/skyguard/gps_utilities.sh ]" false
check_item "Script de monitoreo" "[ -x /opt/skyguard/monitor_gps_system.sh ]" false
check_item "Script de limpieza" "[ -x /opt/skyguard/cleanup_gps_data.sh ]" false
check_item "Script de backup" "[ -x /opt/skyguard/backup_gps_incremental.sh ]" false

echo -e "\n7. PERMISOS Y DIRECTORIOS:"
check_item "Directorio de logs" "[ -d /opt/skyguard/logs ]" false
check_item "Directorio de backups" "[ -d /opt/skyguard/backups ]" false
check_item "Usuario skyguard" "id skyguard > /dev/null 2>&1" true

echo -e "\n8. FUNCIONALIDAD BÁSICA:"
cd /opt/skyguard
check_item "Comando gps_servers disponible" "python manage.py help gps_servers > /dev/null 2>&1" true
check_item "Comando device_monitor disponible" "python manage.py help start_device_monitor > /dev/null 2>&1" true
check_item "Modelos GPS cargados" "python manage.py shell -c 'from skyguard.apps.gps.models import GPSDevice; print(GPSDevice.objects.count())' > /dev/null 2>&1" true

echo -e "\n============================================================"
echo "RESUMEN DE VERIFICACIÓN:"
echo "  ✓ Elementos correctos: $(($(echo "1. SERVICIOS CRÍTICOS:" | wc -l) + $(echo "2. SERVICIOS GPS OPCIONALES:" | wc -l) + $(echo "3. PUERTOS GPS:" | wc -l) + $(echo "4. CONECTIVIDAD:" | wc -l) + $(echo "5. ARCHIVOS DE CONFIGURACIÓN:" | wc -l) + $(echo "6. SCRIPTS DE MANTENIMIENTO:" | wc -l) + $(echo "7. PERMISOS Y DIRECTORIOS:" | wc -l) + $(echo "8. FUNCIONALIDAD BÁSICA:" | wc -l) - $ERRORS - $WARNINGS))"
echo "  ⚠ Advertencias: $WARNINGS"
echo "  ✗ Errores críticos: $ERRORS"

if [ $ERRORS -eq 0 ]; then
    echo -e "\n🎉 ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!"
    echo "El sistema GPS SkyGuard está listo para producción."
    echo ""
    echo "Comandos útiles:"
    echo "  gps-util devices    # Ver estadísticas de dispositivos"
    echo "  gps-util protocols  # Ver protocolos activos"
    echo "  gps-util performance # Ver métricas de rendimiento"
    echo "  gps-check          # Verificación completa del sistema"
    echo "  gps-monitor        # Monitoreo en tiempo real"
else
    echo -e "\n❌ DESPLIEGUE INCOMPLETO"
    echo "Se encontraron $ERRORS errores críticos que deben resolverse."
    echo "Ejecute los comandos de diagnóstico para más detalles:"
    echo "  /opt/skyguard/diagnose_gps_issues.sh"
fi

echo "============================================================"
EOF

chmod +x /opt/skyguard/final_deployment_check.sh

# Crear enlaces simbólicos para comandos rápidos
sudo ln -sf /opt/skyguard/gps_system_check.sh /usr/local/bin/gps-check
sudo ln -sf /opt/skyguard/monitor_gps_system.sh /usr/local/bin/gps-monitor
sudo ln -sf /opt/skyguard/diagnose_gps_issues.sh /usr/local/bin/gps-diagnose
sudo ln -sf /opt/skyguard/final_deployment_check.sh /usr/local/bin/gps-deploy-check
```

### 10.2 Comandos de Gestión Unificados

```bash
# Crear script maestro de gestión
cat > /opt/skyguard/skyguard_manager.sh << 'EOF'
#!/bin/bash

show_help() {
    echo "=== SkyGuard GPS Manager ==="
    echo "Sistema de gestión unificado para SkyGuard GPS"
    echo ""
    echo "Uso: skyguard [comando] [opciones]"
    echo ""
    echo "COMANDOS PRINCIPALES:"
    echo "  start          - Iniciar todos los servicios GPS"
    echo "  stop           - Detener todos los servicios GPS"
    echo "  restart        - Reiniciar todos los servicios GPS"
    echo "  status         - Estado de todos los servicios"
    echo "  logs           - Ver logs en tiempo real"
    echo ""
    echo "COMANDOS DE INFORMACIÓN:"
    echo "  check          - Verificación completa del sistema"
    echo "  devices        - Estadísticas de dispositivos"
    echo "  protocols      - Estado de protocolos GPS"
    echo "  performance    - Métricas de rendimiento"
    echo "  monitor        - Monitoreo en tiempo real"
    echo ""
    echo "COMANDOS DE MANTENIMIENTO:"
    echo "  backup         - Crear backup de datos GPS"
    echo "  cleanup        - Limpiar logs y datos antiguos"
    echo "  optimize       - Optimizar base de datos"
    echo "  diagnose       - Diagnóstico avanzado"
    echo ""
    echo "COMANDOS DE UTILIDAD:"
    echo "  test-protocol <protocolo>  - Probar protocolo específico"
    echo "  reset-device <imei>        - Resetear dispositivo"
    echo "  create-user                - Crear usuario administrador"
    echo "  deploy-check               - Verificación de despliegue"
    echo ""
    echo "Ejemplos:"
    echo "  skyguard start"
    echo "  skyguard devices"
    echo "  skyguard test-protocol wialon"
    echo "  skyguard reset-device 123456789012345"
}

case "$1" in
    "start")
        echo "🚀 Iniciando servicios GPS SkyGuard..."
        sudo systemctl start skyguard-gps-servers skyguard-device-monitor skyguard-wialon-legacy
        echo "✓ Servicios iniciados"
        ;;
    "stop")
        echo "🛑 Deteniendo servicios GPS SkyGuard..."
        sudo systemctl stop skyguard-gps-servers skyguard-device-monitor skyguard-wialon-legacy
        echo "✓ Servicios detenidos"
        ;;
    "restart")
        echo "🔄 Reiniciando servicios GPS SkyGuard..."
        sudo systemctl restart skyguard-gps-servers skyguard-device-monitor skyguard-wialon-legacy
        echo "✓ Servicios reiniciados"
        ;;
    "status")
        echo "📊 Estado de servicios GPS SkyGuard:"
        systemctl status skyguard-gps-servers skyguard-device-monitor skyguard-wialon-legacy --no-pager -l
        ;;
    "logs")
        echo "📋 Logs en tiempo real (Ctrl+C para salir):"
        sudo journalctl -f -u skyguard-gps-servers -u skyguard-device-monitor -u skyguard-wialon-legacy
        ;;
    "check")
        /opt/skyguard/gps_system_check.sh
        ;;
    "devices")
        /opt/skyguard/gps_utilities.sh devices
        ;;
    "protocols")
        /opt/skyguard/gps_utilities.sh protocols
        ;;
    "performance")
        /opt/skyguard/gps_utilities.sh performance
        ;;
    "monitor")
        /opt/skyguard/monitor_gps_system.sh
        ;;
    "backup")
        /opt/skyguard/gps_utilities.sh backup
        ;;
    "cleanup")
        /opt/skyguard/cleanup_gps_data.sh
        ;;
    "optimize")
        /opt/skyguard/optimize_gps_performance.sh
        ;;
    "diagnose")
        /opt/skyguard/diagnose_gps_issues.sh
        ;;
    "test-protocol")
        /opt/skyguard/gps_utilities.sh test-protocol "$2"
        ;;
    "reset-device")
        /opt/skyguard/gps_utilities.sh reset-device "$2"
        ;;
    "create-user")
        cd /opt/skyguard && python manage.py create_user
        ;;
    "deploy-check")
        /opt/skyguard/final_deployment_check.sh
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ Comando no reconocido: $1"
        echo "Usa 'skyguard help' para ver los comandos disponibles"
        ;;
esac
EOF

chmod +x /opt/skyguard/skyguard_manager.sh
sudo ln -sf /opt/skyguard/skyguard_manager.sh /usr/local/bin/skyguard
```

### 10.3 Información Final del Sistema

```bash
echo "=== INFORMACIÓN DEL SISTEMA GPS SKYGUARD ==="
echo "Versión: 1.0"
echo "Fecha de despliegue: $(date)"
echo ""
echo "🌐 ACCESO WEB:"
echo "  URL: http://$(curl -s ifconfig.me):80"
echo "  Admin: http://$(curl -s ifconfig.me):80/admin/"
echo ""
echo "📡 PUERTOS GPS CONFIGURADOS:"
echo "  55300/tcp  - Concox GPS Protocol"
echo "  62000/udp  - Meiligao GPS Protocol"
echo "  15557/tcp  - Satellite Communication Protocol"
echo "  20332/tcp  - Wialon GPS Protocol (Estándar)"
echo "  55301/tcp  - Wialon GPS Protocol (Alternativo)"
echo "  60001/udp  - Wialon GPS Protocol (Legacy)"
echo ""
echo "🔧 COMANDOS PRINCIPALES:"
echo "  skyguard start     - Iniciar sistema GPS"
echo "  skyguard status    - Ver estado del sistema"
echo "  skyguard devices   - Ver dispositivos conectados"
echo "  skyguard monitor   - Monitoreo en tiempo real"
echo "  skyguard help      - Ayuda completa"
echo ""
echo "📁 ARCHIVOS IMPORTANTES:"
echo "  Configuración: /opt/skyguard/.env.production"
echo "  Logs: /opt/skyguard/logs/"
echo "  Backups: /opt/skyguard/backups/"
echo "  Scripts: /opt/skyguard/"
echo ""
echo "✅ SISTEMA LISTO PARA PRODUCCIÓN"
echo "============================================="
```

## Verificación Final

Ejecutar la verificación completa del despliegue:

```bash
# Verificar que todo esté funcionando correctamente
/opt/skyguard/final_deployment_check.sh

# Si todo está OK, iniciar el sistema completo
skyguard start

# Verificar estado
skyguard status

# Ver dispositivos (si hay alguno conectado)
skyguard devices
```

¡El sistema GPS SkyGuard está ahora completamente documentado y listo para producción! 🎉

