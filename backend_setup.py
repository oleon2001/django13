#!/usr/bin/env python3
"""
Script de configuración completa del nuevo backend SkyGuard.
Configura el entorno, instala dependencias y prepara el sistema para producción.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class BackendConfigurator:
    """Configurador completo del backend SkyGuard."""
    
    def __init__(self, environment='development'):
        self.environment = environment
        self.base_dir = Path(__file__).resolve().parent
        self.venv_path = self.base_dir / 'venv'
        self.log_file = self.base_dir / f'setup_{environment}.log'
        
    def log(self, message, level='INFO'):
        """Log con timestamp."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')
    
    def run_command(self, command, check=True):
        """Ejecuta comando y maneja errores."""
        self.log(f"Ejecutando: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                check=check
            )
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Error ejecutando comando: {e}", 'ERROR')
            if e.stderr:
                self.log(f"Error output: {e.stderr}", 'ERROR')
            raise
    
    def check_system_requirements(self):
        """Verifica requisitos del sistema."""
        self.log("🔍 Verificando requisitos del sistema...")
        
        # Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            raise RuntimeError(f"Python 3.8+ requerido, encontrado {python_version}")
        self.log(f"✅ Python {python_version.major}.{python_version.minor}")
        
        # PostgreSQL
        try:
            result = self.run_command("psql --version", check=False)
            if result.returncode == 0:
                self.log("✅ PostgreSQL disponible")
            else:
                self.log("⚠️  PostgreSQL no encontrado, instalar manualmente", 'WARNING')
        except:
            self.log("⚠️  PostgreSQL no encontrado", 'WARNING')
        
        # Redis
        try:
            result = self.run_command("redis-server --version", check=False)
            if result.returncode == 0:
                self.log("✅ Redis disponible")
            else:
                self.log("⚠️  Redis no encontrado, instalar manualmente", 'WARNING')
        except:
            self.log("⚠️  Redis no encontrado", 'WARNING')
    
    def create_virtual_environment(self):
        """Crea entorno virtual."""
        self.log("🐍 Configurando entorno virtual...")
        
        if self.venv_path.exists():
            self.log("Entorno virtual ya existe, recreando...")
            self.run_command(f"rm -rf {self.venv_path}")
        
        self.run_command(f"python3 -m venv {self.venv_path}")
        self.log("✅ Entorno virtual creado")
    
    def install_dependencies(self):
        """Instala dependencias Python."""
        self.log("📦 Instalando dependencias...")
        
        pip_path = self.venv_path / 'bin' / 'pip'
        
        # Actualizar pip
        self.run_command(f"{pip_path} install --upgrade pip setuptools wheel")
        
        # Instalar dependencias principales
        if (self.base_dir / 'requirements.txt').exists():
            self.run_command(f"{pip_path} install -r requirements.txt")
        else:
            # Dependencias básicas si no hay requirements.txt
            basic_deps = [
                'Django>=4.2.0,<5.0.0',
                'djangorestframework>=3.14.0',
                'djangorestframework-simplejwt>=5.5.0',
                'django-cors-headers>=4.3.0',
                'psycopg2-binary>=2.9.9',
                'django-environ>=0.11.2',
                'python-dotenv>=1.0.0',
                'gunicorn>=21.2.0',
                'whitenoise>=6.6.0',
                'redis>=5.0.1',
                'django-redis>=5.4.0',
                'Pillow>=10.0.0',
                'requests>=2.31.0'
            ]
            
            for dep in basic_deps:
                self.run_command(f"{pip_path} install '{dep}'")
        
        # Dependencias adicionales para producción
        if self.environment == 'production':
            prod_deps = [
                'django-storages>=1.14.2',
                'boto3>=1.34.0',
                'django-axes>=6.3.0',
                'django-ratelimit>=4.1.0',
                'celery>=5.3.6'
            ]
            
            for dep in prod_deps:
                self.run_command(f"{pip_path} install '{dep}'")
        
        self.log("✅ Dependencias instaladas")
    
    def create_environment_file(self):
        """Crea archivo de configuración de entorno."""
        self.log("⚙️  Creando archivo de configuración...")
        
        env_file = self.base_dir / f'.env.{self.environment}'
        
        if env_file.exists():
            self.log(f"Archivo {env_file.name} ya existe, respaldando...")
            backup_file = self.base_dir / f'.env.{self.environment}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            env_file.rename(backup_file)
        
        env_content = self._get_env_template()
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        self.log(f"✅ Archivo {env_file.name} creado")
        self.log(f"⚠️  IMPORTANTE: Editar {env_file.name} con valores reales", 'WARNING')
    
    def _get_env_template(self):
        """Template del archivo de entorno."""
        if self.environment == 'production':
            return """# SkyGuard Production Environment Configuration
DJANGO_ENVIRONMENT=production
DJANGO_SECRET_KEY=your-super-secret-key-here-change-this-in-production
DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Configuration
DB_NAME=skyguard
DB_USER=skyguard
DB_PASSWORD=skyguard123
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/1

# Email Configuration (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# GPS Device Settings
GPS_DEVICE_TOKEN=your-secure-gps-token-here
GPS_UPDATE_INTERVAL=60
GPS_MAX_RETRIES=3
GPS_TIMEOUT=30

# Static Files (Production)
STATIC_ROOT=/var/www/skyguard/static
MEDIA_ROOT=/var/www/skyguard/media

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/django/skyguard.log

# Optional: AWS S3 Configuration
# AWS_ACCESS_KEY_ID=your-aws-access-key
# AWS_SECRET_ACCESS_KEY=your-aws-secret-key
# AWS_STORAGE_BUCKET_NAME=your-bucket-name
# AWS_S3_REGION_NAME=us-east-1
"""
        else:
            return """# SkyGuard Development Environment Configuration
DJANGO_ENVIRONMENT=development
DJANGO_SECRET_KEY=django-insecure-development-key
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DB_NAME=skyguard
DB_USER=skyguard
DB_PASSWORD=skyguard123
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration (opcional en desarrollo)
REDIS_URL=redis://localhost:6379/1

# Email Configuration (desarrollo - usa console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# GPS Device Settings
GPS_DEVICE_TOKEN=dev-token-123
GPS_UPDATE_INTERVAL=30
GPS_MAX_RETRIES=3
GPS_TIMEOUT=15

# Logging
LOG_LEVEL=DEBUG
"""
    
    def setup_database(self):
        """Configura la base de datos."""
        self.log("🗄️  Configurando base de datos...")
        
        python_path = self.venv_path / 'bin' / 'python'
        
        # Verificar conexión a PostgreSQL
        try:
            self.run_command("psql -c 'SELECT version();' postgres", check=False)
        except:
            self.log("⚠️  No se pudo conectar a PostgreSQL", 'WARNING')
            self.log("Asegúrate de que PostgreSQL esté instalado y ejecutándose", 'WARNING')
            return
        
        # Crear base de datos si no existe
        db_name = 'skyguard'
        self.run_command(f"createdb {db_name} 2>/dev/null || true", check=False)
        
        # Ejecutar migraciones
        os.environ['DJANGO_SETTINGS_MODULE'] = f'skyguard.settings.{self.environment}'
        
        try:
            self.run_command(f"{python_path} manage.py migrate")
            self.log("✅ Migraciones ejecutadas")
        except Exception as e:
            self.log(f"Error ejecutando migraciones: {e}", 'ERROR')
            self.log("Ejecutar manualmente: python manage.py migrate", 'WARNING')
    
    def collect_static_files(self):
        """Recolecta archivos estáticos."""
        if self.environment == 'production':
            self.log("📁 Recolectando archivos estáticos...")
            
            python_path = self.venv_path / 'bin' / 'python'
            os.environ['DJANGO_SETTINGS_MODULE'] = f'skyguard.settings.{self.environment}'
            
            try:
                self.run_command(f"{python_path} manage.py collectstatic --noinput")
                self.log("✅ Archivos estáticos recolectados")
            except Exception as e:
                self.log(f"Error recolectando archivos estáticos: {e}", 'ERROR')
    
    def create_superuser_script(self):
        """Crea script para crear superusuario."""
        self.log("👤 Creando script de superusuario...")
        
        script_content = f"""#!/bin/bash
# Script para crear superusuario en SkyGuard
source {self.venv_path}/bin/activate
export DJANGO_SETTINGS_MODULE=skyguard.settings.{self.environment}

echo "Creando superusuario para SkyGuard..."
python manage.py createsuperuser
"""
        
        script_path = self.base_dir / 'create_superuser.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        self.log(f"✅ Script creado: {script_path}")
    
    def create_startup_scripts(self):
        """Crea scripts de inicio."""
        self.log("🚀 Creando scripts de inicio...")
        
        # Script de desarrollo
        dev_script = f"""#!/bin/bash
# Script de inicio para desarrollo
source {self.venv_path}/bin/activate
export DJANGO_SETTINGS_MODULE=skyguard.settings.development

echo "Iniciando servidor de desarrollo SkyGuard..."
python manage.py runserver 0.0.0.0:8000
"""
        
        dev_path = self.base_dir / 'start_dev.sh'
        with open(dev_path, 'w') as f:
            f.write(dev_script)
        os.chmod(dev_path, 0o755)
        
        # Script de producción
        if self.environment == 'production':
            prod_script = f"""#!/bin/bash
# Script de inicio para producción
source {self.venv_path}/bin/activate
export DJANGO_SETTINGS_MODULE=skyguard.settings.production

echo "Iniciando servidor de producción SkyGuard..."
gunicorn skyguard.wsgi:application \\
    --bind 0.0.0.0:8000 \\
    --workers 4 \\
    --timeout 120 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --preload \\
    --access-logfile /var/log/gunicorn/access.log \\
    --error-logfile /var/log/gunicorn/error.log \\
    --log-level info
"""
            
            prod_path = self.base_dir / 'start_prod.sh'
            with open(prod_path, 'w') as f:
                f.write(prod_script)
            os.chmod(prod_path, 0o755)
        
        self.log("✅ Scripts de inicio creados")
    
    def create_systemd_service(self):
        """Crea servicio systemd para producción."""
        if self.environment != 'production':
            return
        
        self.log("⚙️  Creando servicio systemd...")
        
        service_content = f"""[Unit]
Description=SkyGuard GPS Tracking System
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={self.base_dir}
Environment=DJANGO_SETTINGS_MODULE=skyguard.settings.production
ExecStart={self.venv_path}/bin/gunicorn skyguard.wsgi:application \\
    --bind unix:/run/skyguard/skyguard.sock \\
    --workers 4 \\
    --timeout 120 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --preload \\
    --access-logfile /var/log/gunicorn/skyguard-access.log \\
    --error-logfile /var/log/gunicorn/skyguard-error.log \\
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        
        service_path = self.base_dir / 'skyguard.service'
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        self.log(f"✅ Servicio systemd creado: {service_path}")
        self.log("Para instalar: sudo cp skyguard.service /etc/systemd/system/", 'INFO')
    
    def create_nginx_config(self):
        """Crea configuración de Nginx."""
        if self.environment != 'production':
            return
        
        self.log("🌐 Creando configuración de Nginx...")
        
        nginx_config = """server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Static files
    location /static/ {
        alias /var/www/skyguard/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/skyguard/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://unix:/run/skyguard/skyguard.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Frontend (React)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Security
    location ~ /\\.ht {
        deny all;
    }
    
    # Logs
    access_log /var/log/nginx/skyguard_access.log;
    error_log /var/log/nginx/skyguard_error.log;
}
"""
        
        nginx_path = self.base_dir / 'nginx_skyguard.conf'
        with open(nginx_path, 'w') as f:
            f.write(nginx_config)
        
        self.log(f"✅ Configuración Nginx creada: {nginx_path}")
        self.log("Para instalar: sudo cp nginx_skyguard.conf /etc/nginx/sites-available/skyguard", 'INFO')
    
    def run_full_setup(self):
        """Ejecuta configuración completa."""
        self.log(f"🚀 INICIANDO CONFIGURACIÓN COMPLETA - ENTORNO: {self.environment.upper()}")
        
        try:
            self.check_system_requirements()
            self.create_virtual_environment()
            self.install_dependencies()
            self.create_environment_file()
            self.setup_database()
            self.collect_static_files()
            self.create_superuser_script()
            self.create_startup_scripts()
            self.create_systemd_service()
            self.create_nginx_config()
            
            self.log("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
            self._print_next_steps()
            
        except Exception as e:
            self.log(f"❌ Error durante la configuración: {e}", 'ERROR')
            return False
        
        return True
    
    def _print_next_steps(self):
        """Imprime pasos siguientes."""
        self.log("\n" + "="*60)
        self.log("📋 PRÓXIMOS PASOS:")
        self.log("="*60)
        
        env_file = f'.env.{self.environment}'
        self.log(f"1. Editar {env_file} con valores reales")
        self.log("2. Configurar PostgreSQL y crear usuario/base de datos")
        
        if self.environment == 'production':
            self.log("3. Instalar certificado SSL: sudo certbot --nginx")
            self.log("4. Copiar archivos de configuración:")
            self.log("   sudo cp skyguard.service /etc/systemd/system/")
            self.log("   sudo cp nginx_skyguard.conf /etc/nginx/sites-available/skyguard")
            self.log("   sudo ln -s /etc/nginx/sites-available/skyguard /etc/nginx/sites-enabled/")
            self.log("5. Iniciar servicios:")
            self.log("   sudo systemctl enable skyguard")
            self.log("   sudo systemctl start skyguard")
            self.log("   sudo systemctl reload nginx")
            self.log("6. Crear superusuario: ./create_superuser.sh")
        else:
            self.log("3. Crear superusuario: ./create_superuser.sh")
            self.log("4. Iniciar servidor: ./start_dev.sh")
        
        self.log("\n📊 PARA MIGRAR DATOS:")
        self.log("1. cd migration_scripts")
        self.log("2. python run_migration.py --dry-run")
        self.log("3. python run_migration.py --execute")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Configurar backend SkyGuard')
    parser.add_argument('--environment', choices=['development', 'production'], 
                       default='development', help='Entorno de configuración')
    parser.add_argument('--force', action='store_true', 
                       help='Forzar reconfiguración')
    
    args = parser.parse_args()
    
    configurator = BackendConfigurator(args.environment)
    
    if configurator.run_full_setup():
        print("\n🎉 ¡Configuración completada exitosamente!")
        sys.exit(0)
    else:
        print("\n💥 Configuración falló")
        sys.exit(1)


if __name__ == '__main__':
    main() 