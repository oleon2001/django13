# 🚀 Guía de Despliegue - SkyGuard GPS Tracking System

## 📋 Índice

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Configuración Rápida](#configuración-rápida)
3. [Configuración de Desarrollo](#configuración-de-desarrollo)
4. [Configuración de Producción](#configuración-de-producción)
5. [Migración de Datos](#migración-de-datos)
6. [Mantenimiento](#mantenimiento)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos del Sistema

### Mínimos
- **Sistema Operativo**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Python**: 3.8+
- **PostgreSQL**: 12+ con PostGIS
- **Redis**: 6.0+
- **RAM**: 2GB mínimo (4GB recomendado)
- **Almacenamiento**: 10GB mínimo

### Para Producción
- **RAM**: 8GB+ recomendado
- **CPU**: 4 cores+
- **Almacenamiento**: SSD 50GB+
- **Nginx**: 1.18+
- **Certificado SSL**: Let's Encrypt

---

## ⚡ Configuración Rápida

### 1. Clonar y Configurar

```bash
# Clonar repositorio
git clone <your-repo-url> skyguard
cd skyguard

# Hacer ejecutable el configurador
chmod +x backend_setup.py

# Configuración de desarrollo
python3 backend_setup.py --environment development

# O configuración de producción
python3 backend_setup.py --environment production
```

### 2. Configurar Base de Datos

```bash
# Instalar PostgreSQL y PostGIS
sudo apt update
sudo apt install postgresql postgresql-contrib postgis

# Crear usuario y base de datos
sudo -u postgres psql
CREATE USER skyguard WITH PASSWORD 'skyguard123';
CREATE DATABASE skyguard OWNER skyguard;
GRANT ALL PRIVILEGES ON DATABASE skyguard TO skyguard;
\c skyguard
CREATE EXTENSION postgis;
\q
```

### 3. Iniciar Sistema

```bash
# Desarrollo
./start_dev.sh

# Producción
./start_prod.sh
```

---

## 🛠️ Configuración de Desarrollo

### Instalación Automática

```bash
# Ejecutar configurador
python3 backend_setup.py --environment development
```

### Configuración Manual

1. **Crear Entorno Virtual**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configurar Variables de Entorno**
```bash
cp .env.development.example .env.development
# Editar .env.development con tus valores
```

3. **Configurar Base de Datos**
```bash
export DJANGO_SETTINGS_MODULE=skyguard.settings.development
python manage.py migrate
python manage.py createsuperuser
```

4. **Iniciar Servidor**
```bash
python manage.py runserver 0.0.0.0:8000
```

### Configuración de Desarrollo Típica

```env
# .env.development
DJANGO_ENVIRONMENT=development
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DB_NAME=skyguard
DB_USER=skyguard
DB_PASSWORD=skyguard123
DB_HOST=localhost
DB_PORT=5432
```

---

## 🏭 Configuración de Producción

### 1. Preparación del Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib postgis \
    redis-server nginx supervisor \
    git curl wget unzip

# Instalar certbot para SSL
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Configuración Automática

```bash
# Ejecutar configurador para producción
python3 backend_setup.py --environment production
```

### 3. Configuración Manual de Producción

#### A. Configurar PostgreSQL

```bash
# Configurar PostgreSQL
sudo -u postgres psql
CREATE USER skyguard WITH PASSWORD 'tu-password-seguro';
CREATE DATABASE skyguard OWNER skyguard;
GRANT ALL PRIVILEGES ON DATABASE skyguard TO skyguard;
\c skyguard
CREATE EXTENSION postgis;
\q

# Configurar autenticación
sudo nano /etc/postgresql/14/main/pg_hba.conf
# Agregar: local   skyguard    skyguard                                md5
sudo systemctl restart postgresql
```

#### B. Configurar Redis

```bash
# Configurar Redis
sudo nano /etc/redis/redis.conf
# Descomentar y configurar:
# requirepass tu-password-redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

#### C. Configurar Variables de Entorno

```bash
# Editar archivo de producción
nano .env.production
```

```env
# .env.production
DJANGO_ENVIRONMENT=production
DJANGO_SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
DEBUG=False
DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Database
DB_NAME=skyguard
DB_USER=skyguard
DB_PASSWORD=tu-password-seguro
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://:tu-password-redis@localhost:6379/1

# Email (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-email@gmail.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Static Files
STATIC_ROOT=/var/www/skyguard/static
MEDIA_ROOT=/var/www/skyguard/media
```

#### D. Configurar Nginx

```bash
# Copiar configuración
sudo cp nginx_skyguard.conf /etc/nginx/sites-available/skyguard
sudo ln -s /etc/nginx/sites-available/skyguard /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Crear directorios
sudo mkdir -p /var/www/skyguard/static
sudo mkdir -p /var/www/skyguard/media
sudo chown -R www-data:www-data /var/www/skyguard

# Verificar configuración
sudo nginx -t
sudo systemctl reload nginx
```

#### E. Configurar SSL

```bash
# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

#### F. Configurar Systemd

```bash
# Copiar servicio
sudo cp skyguard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable skyguard
sudo systemctl start skyguard

# Verificar estado
sudo systemctl status skyguard
```

### 4. Configuración de Logs

```bash
# Crear directorios de logs
sudo mkdir -p /var/log/django
sudo mkdir -p /var/log/gunicorn
sudo mkdir -p /run/skyguard

# Configurar permisos
sudo chown -R www-data:www-data /var/log/django
sudo chown -R www-data:www-data /var/log/gunicorn
sudo chown -R www-data:www-data /run/skyguard
```

---

## 📊 Migración de Datos

### 1. Preparación

```bash
cd migration_scripts

# Verificar scripts disponibles
ls -la *.py

# Verificar conexiones
python data_analysis.py --check-connections
```

### 2. Análisis Previo

```bash
# Ejecutar análisis completo
python data_analysis.py --full-analysis

# Revisar reporte
cat data_analysis_report.log
```

### 3. Migración en Modo Prueba

```bash
# Ejecutar migración completa en modo dry-run
python run_migration.py --dry-run

# Revisar logs
tail -f master_migration.log
```

### 4. Migración Real

```bash
# ⚠️ IMPORTANTE: Hacer backup de la base de datos
pg_dump skyguard > backup_pre_migration.sql

# Ejecutar migración real
python run_migration.py --execute

# Verificar resultados
python validate_migration.py
```

### 5. Migración Selectiva

```bash
# Solo datos core
python run_migration.py --execute --skip-historical

# Solo datos históricos
python migrate_historical_logs.py --execute

# Con filtro de fechas
python migrate_historical_logs.py --execute --days-back 30
```

---

## 🔧 Mantenimiento

### Comandos Útiles

```bash
# Ver logs en tiempo real
tail -f /var/log/django/skyguard.log
tail -f /var/log/gunicorn/skyguard-error.log

# Reiniciar servicios
sudo systemctl restart skyguard
sudo systemctl reload nginx

# Backup de base de datos
pg_dump skyguard > backup_$(date +%Y%m%d_%H%M%S).sql

# Limpiar logs antiguos
sudo find /var/log -name "*.log" -mtime +30 -delete

# Actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Aplicar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### Monitoreo

```bash
# Estado de servicios
sudo systemctl status skyguard
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis

# Uso de recursos
htop
df -h
free -h

# Conexiones de base de datos
sudo -u postgres psql skyguard -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos

```bash
# Verificar que PostgreSQL esté ejecutándose
sudo systemctl status postgresql

# Verificar conexión
psql -h localhost -U skyguard -d skyguard

# Revisar logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### 2. Error 502 Bad Gateway

```bash
# Verificar que Gunicorn esté ejecutándose
sudo systemctl status skyguard

# Verificar socket
ls -la /run/skyguard/

# Revisar logs de Nginx
sudo tail -f /var/log/nginx/skyguard_error.log
```

#### 3. Problemas de Permisos

```bash
# Corregir permisos de archivos estáticos
sudo chown -R www-data:www-data /var/www/skyguard/
sudo chmod -R 755 /var/www/skyguard/

# Corregir permisos de logs
sudo chown -R www-data:www-data /var/log/django/
sudo chown -R www-data:www-data /var/log/gunicorn/
```

#### 4. Error de Memoria en Migración

```bash
# Usar migración por lotes más pequeños
python migrate_historical_logs.py --execute --batch-size 1000

# Aumentar memoria swap temporal
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 5. Problemas de SSL

```bash
# Renovar certificado
sudo certbot renew

# Verificar configuración SSL
sudo nginx -t
openssl s_client -connect tu-dominio.com:443
```

### Logs Importantes

```bash
# Logs de aplicación Django
/var/log/django/skyguard.log

# Logs de Gunicorn
/var/log/gunicorn/skyguard-access.log
/var/log/gunicorn/skyguard-error.log

# Logs de Nginx
/var/log/nginx/skyguard_access.log
/var/log/nginx/skyguard_error.log

# Logs de migración
migration_scripts/master_migration.log
migration_scripts/data_analysis_report.log
migration_scripts/validation_report.log
```

---

## 📞 Soporte

### Información del Sistema

```bash
# Generar reporte de sistema
./generate_system_report.sh
```

### Contacto

Para soporte técnico, incluir:
1. Logs relevantes
2. Configuración de entorno
3. Pasos para reproducir el problema
4. Versión del sistema

---

## 🔄 Actualizaciones

### Actualización de Código

```bash
# Hacer backup
pg_dump skyguard > backup_pre_update.sql

# Actualizar código
git pull origin main

# Actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Aplicar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Reiniciar servicios
sudo systemctl restart skyguard
sudo systemctl reload nginx
```

---

**⚠️ Importante**: Siempre hacer backup antes de cambios en producción.

**✅ Recomendación**: Probar todos los cambios en un entorno de desarrollo primero. 