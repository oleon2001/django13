# 🚀 SkyGuard GPS Enhanced Deployment Guide

## 📊 **Overview**

This guide covers the deployment of SkyGuard GPS Enhanced - a professional-grade GPS tracking system with real-time WebSocket communication, advanced analytics, enhanced security, and mobile-ready APIs.

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Hardware      │
│   React/TS      │◄──►│   Django        │◄──►│   GPS Devices   │
│                 │    │   + WebSockets  │    │                 │
│   - WebSocket   │    │   + Analytics   │    │   - Concox      │
│   - Real-time   │    │   + Security    │    │   - Meiligao    │
│   - Mobile      │    │   + ML/AI       │    │   - Satellite   │
│   - Analytics   │    │                 │    │   - Wialon      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ **Prerequisites**

### System Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **CPU**: 8+ cores (16+ recommended for production)
- **RAM**: 16GB+ (32GB+ recommended)
- **Storage**: 500GB+ SSD (1TB+ recommended)
- **Network**: 1Gbps+ connection

### Software Stack
- **Python**: 3.9+
- **Node.js**: 16+ 
- **PostgreSQL**: 13+ with PostGIS
- **Redis**: 6+
- **Nginx**: 1.18+
- **Docker**: 20.10+ (optional but recommended)

## 📦 **Installation Steps**

### 1. **System Preparation**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3.9-venv python3.9-dev \
    postgresql-13 postgresql-13-postgis-3 \
    redis-server nginx git curl build-essential \
    libpq-dev gdal-bin

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# Create system user
sudo useradd -m -s /bin/bash skyguard
sudo usermod -aG sudo skyguard
```

### 2. **Database Setup**

```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE skyguard_prod;
CREATE USER skyguard WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE skyguard_prod TO skyguard;

-- Enable PostGIS extension
\c skyguard_prod;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

\q
```

### 3. **Redis Configuration**

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Add/modify these settings:
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 4. **Backend Deployment**

```bash
# Switch to skyguard user
sudo -u skyguard -i

# Clone repository
git clone https://github.com/your-org/skyguard-gps.git
cd skyguard-gps

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Additional ML dependencies
pip install scikit-learn==1.3.0 pandas==1.5.3 numpy==1.24.3
pip install channels-redis==4.1.0 django-redis==5.3.0
pip install cryptography==41.0.3 celery==5.3.1
```

### 5. **Environment Configuration**

```bash
# Create environment file
cat > .env << EOF
# Database
DB_NAME=skyguard_prod
DB_USER=skyguard
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your_very_long_secret_key_here
GPS_COMMAND_SECRET_KEY=your_gps_command_secret_key_here

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@domain.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@your-domain.com

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Push Notifications
FCM_SERVER_KEY=your_fcm_server_key

# External APIs
GOOGLE_MAPS_API_KEY=your_google_maps_key
WEATHER_API_KEY=your_weather_api_key

# Production settings
DJANGO_SETTINGS_MODULE=skyguard.settings.production
DEBUG=False
EOF
```

### 6. **Database Migration**

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py create_superuser

# Load initial data (if any)
python manage.py loaddata initial_data.json
```

### 7. **Frontend Deployment**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build production version
npm run build

# Copy build files to static directory
sudo cp -r build/* /var/www/skyguard/static/
```

### 8. **Celery Setup**

```bash
# Create Celery service files
sudo tee /etc/systemd/system/skyguard-celery.service << EOF
[Unit]
Description=SkyGuard Celery Worker
After=network.target

[Service]
Type=forking
User=skyguard
Group=skyguard
EnvironmentFile=/home/skyguard/skyguard-gps/.env
WorkingDirectory=/home/skyguard/skyguard-gps
ExecStart=/home/skyguard/skyguard-gps/venv/bin/celery multi start worker1 \
    -A skyguard \
    --pidfile=/var/run/celery/%%n.pid \
    --logfile=/var/log/celery/%%n%%I.log \
    --loglevel=INFO \
    --concurrency=8 \
    --queues=default,gps_processing,notifications,analytics

ExecStop=/home/skyguard/skyguard-gps/venv/bin/celery multi stopwait worker1 \
    --pidfile=/var/run/celery/%%n.pid

ExecReload=/home/skyguard/skyguard-gps/venv/bin/celery multi restart worker1 \
    -A skyguard \
    --pidfile=/var/run/celery/%%n.pid \
    --logfile=/var/log/celery/%%n%%I.log \
    --loglevel=INFO \
    --concurrency=8 \
    --queues=default,gps_processing,notifications,analytics

Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create Celery Beat service
sudo tee /etc/systemd/system/skyguard-celerybeat.service << EOF
[Unit]
Description=SkyGuard Celery Beat
After=network.target

[Service]
Type=simple
User=skyguard
Group=skyguard
EnvironmentFile=/home/skyguard/skyguard-gps/.env
WorkingDirectory=/home/skyguard/skyguard-gps
ExecStart=/home/skyguard/skyguard-gps/venv/bin/celery -A skyguard beat \
    --loglevel=INFO \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create directories and start services
sudo mkdir -p /var/run/celery /var/log/celery
sudo chown skyguard:skyguard /var/run/celery /var/log/celery

sudo systemctl daemon-reload
sudo systemctl enable skyguard-celery skyguard-celerybeat
sudo systemctl start skyguard-celery skyguard-celerybeat
```

### 9. **Gunicorn & ASGI Setup**

```bash
# Create Gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
EOF

# Create Daphne (ASGI) configuration for WebSockets
sudo tee /etc/systemd/system/skyguard-daphne.service << EOF
[Unit]
Description=SkyGuard Daphne WebSocket Server
After=network.target

[Service]
Type=simple
User=skyguard
Group=skyguard
EnvironmentFile=/home/skyguard/skyguard-gps/.env
WorkingDirectory=/home/skyguard/skyguard-gps
ExecStart=/home/skyguard/skyguard-gps/venv/bin/daphne \
    -b 127.0.0.1 -p 8001 \
    skyguard.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create Gunicorn service
sudo tee /etc/systemd/system/skyguard-gunicorn.service << EOF
[Unit]
Description=SkyGuard Gunicorn WSGI Server
After=network.target

[Service]
Type=simple
User=skyguard
Group=skyguard
EnvironmentFile=/home/skyguard/skyguard-gps/.env
WorkingDirectory=/home/skyguard/skyguard-gps
ExecStart=/home/skyguard/skyguard-gps/venv/bin/gunicorn \
    --config gunicorn.conf.py \
    skyguard.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start services
sudo systemctl daemon-reload
sudo systemctl enable skyguard-gunicorn skyguard-daphne
sudo systemctl start skyguard-gunicorn skyguard-daphne
```

### 10. **Nginx Configuration**

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/skyguard << EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=websocket:10m rate=5r/s;

# Upstream servers
upstream skyguard_wsgi {
    server 127.0.0.1:8000;
}

upstream skyguard_asgi {
    server 127.0.0.1:8001;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name your-domain.com api.your-domain.com ws.your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

# Main application server
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/skyguard.crt;
    ssl_certificate_key /etc/ssl/private/skyguard.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Gzip compression
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # Static files
    location /static/ {
        alias /var/www/skyguard/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/skyguard/skyguard-gps/media/;
        expires 1y;
    }
    
    # API endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://skyguard_wsgi;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Admin interface
    location /admin/ {
        proxy_pass http://skyguard_wsgi;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Frontend application
    location / {
        try_files \$uri \$uri/ /index.html;
        root /var/www/skyguard/static;
    }
}

# WebSocket server
server {
    listen 443 ssl http2;
    server_name ws.your-domain.com;
    
    # SSL Configuration (same as above)
    ssl_certificate /etc/ssl/certs/skyguard.crt;
    ssl_certificate_key /etc/ssl/private/skyguard.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # WebSocket configuration
    location /ws/ {
        limit_req zone=websocket burst=10 nodelay;
        proxy_pass http://skyguard_asgi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 86400s;  # 24 hours for WebSocket
    }
}

# API server (for mobile apps and external integrations)
server {
    listen 443 ssl http2;
    server_name api.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/skyguard.crt;
    ssl_certificate_key /etc/ssl/private/skyguard.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # CORS headers for mobile apps
    add_header Access-Control-Allow-Origin "https://your-domain.com" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Device-ID, X-App-Version" always;
    add_header Access-Control-Allow-Credentials true always;
    
    # Handle preflight requests
    location ~* \.(OPTIONS) {
        add_header Access-Control-Allow-Origin "https://your-domain.com";
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Device-ID, X-App-Version";
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Type "text/plain charset=UTF-8";
        add_header Content-Length 0;
        return 204;
    }
    
    location / {
        limit_req zone=api burst=30 nodelay;
        proxy_pass http://skyguard_wsgi;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/skyguard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 11. **GPS Server Services**

```bash
# Create GPS server service
sudo tee /etc/systemd/system/skyguard-gps-servers.service << EOF
[Unit]
Description=SkyGuard GPS Servers
After=network.target

[Service]
Type=simple
User=skyguard
Group=skyguard
EnvironmentFile=/home/skyguard/skyguard-gps/.env
WorkingDirectory=/home/skyguard/skyguard-gps
ExecStart=/home/skyguard/skyguard-gps/venv/bin/python manage.py start_gps_servers
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable skyguard-gps-servers
sudo systemctl start skyguard-gps-servers
```

## 🔧 **Configuration**

### WebSocket Configuration
```python
# In frontend/src/services/websocket.ts
const wsUrl = process.env.REACT_APP_WS_URL || 'wss://ws.your-domain.com/ws/gps/realtime/';
```

### Analytics Configuration
```python
# In Django settings
ANALYTICS_SETTINGS = {
    'enable_real_time': True,
    'enable_ml_analytics': True,
    'cache_metrics_duration': 300,
    'anomaly_detection_threshold': 0.1,
}
```

## 📊 **Monitoring & Health Checks**

### 1. **System Monitoring**

```bash
# Create health check script
cat > /home/skyguard/health_check.py << EOF
#!/usr/bin/env python3
import psutil
import redis
import requests
import json
from datetime import datetime

def check_system_health():
    health = {
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy',
        'services': {}
    }
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    health['services']['cpu'] = {
        'status': 'healthy' if cpu_percent < 80 else 'warning',
        'usage_percent': cpu_percent
    }
    
    # Check memory usage
    memory = psutil.virtual_memory()
    health['services']['memory'] = {
        'status': 'healthy' if memory.percent < 85 else 'warning',
        'usage_percent': memory.percent,
        'available_mb': memory.available // 1024 // 1024
    }
    
    # Check Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        health['services']['redis'] = {'status': 'healthy'}
    except:
        health['services']['redis'] = {'status': 'error'}
        health['status'] = 'degraded'
    
    # Check Web services
    try:
        response = requests.get('http://127.0.0.1:8000/admin/', timeout=5)
        health['services']['wsgi'] = {
            'status': 'healthy' if response.status_code == 200 else 'warning'
        }
    except:
        health['services']['wsgi'] = {'status': 'error'}
        health['status'] = 'degraded'
    
    return health

if __name__ == '__main__':
    print(json.dumps(check_system_health(), indent=2))
EOF

chmod +x /home/skyguard/health_check.py

# Create cron job for health checks
echo "*/5 * * * * /home/skyguard/health_check.py >> /var/log/skyguard/health.log" | sudo crontab -u skyguard -
```

### 2. **Log Monitoring**

```bash
# Create log rotation
sudo tee /etc/logrotate.d/skyguard << EOF
/var/log/skyguard/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 skyguard skyguard
    postrotate
        systemctl reload skyguard-gunicorn
        systemctl reload skyguard-daphne
    endscript
}
EOF
```

## 🔒 **Security Hardening**

### 1. **Firewall Configuration**

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (change port if needed)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow GPS server ports
sudo ufw allow 55300/tcp  # Concox
sudo ufw allow 62000/udp  # Meiligao
sudo ufw allow 15557/tcp  # Satellite
sudo ufw allow 20332/tcp  # Wialon

# Block other ports
sudo ufw deny 5432/tcp    # PostgreSQL (only local)
sudo ufw deny 6379/tcp    # Redis (only local)
```

### 2. **SSL Certificate Setup**

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com -d ws.your-domain.com

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## 📱 **Mobile App Configuration**

### React Native Configuration
```javascript
// config/api.js
export const API_CONFIG = {
  BASE_URL: 'https://api.your-domain.com',
  WS_URL: 'wss://ws.your-domain.com/ws/gps/realtime/',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3
};
```

### Flutter Configuration
```dart
// lib/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'https://api.your-domain.com';
  static const String wsUrl = 'wss://ws.your-domain.com/ws/gps/realtime/';
  static const Duration timeout = Duration(seconds: 30);
}
```

## 🚀 **Performance Optimization**

### 1. **Database Optimization**

```sql
-- Create indexes for GPS data
CREATE INDEX CONCURRENTLY idx_gps_location_device_timestamp 
ON gps_location(device_id, timestamp DESC);

CREATE INDEX CONCURRENTLY idx_gps_location_position 
ON gps_location USING GIST(position);

CREATE INDEX CONCURRENTLY idx_gps_device_status 
ON gps_device(connection_status) WHERE connection_status = 'ONLINE';

-- Partition large tables by date
CREATE TABLE gps_location_y2024m01 PARTITION OF gps_location
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 2. **Redis Optimization**

```bash
# Add to /etc/redis/redis.conf
save 900 1
save 300 10
save 60 10000
maxmemory-policy allkeys-lru
tcp-keepalive 300
timeout 0
```

## 🔄 **Backup & Recovery**

### 1. **Automated Backups**

```bash
# Create backup script
cat > /home/skyguard/backup.sh << EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/skyguard"

# Create backup directory
mkdir -p \$BACKUP_DIR

# Database backup
pg_dump skyguard_prod | gzip > \$BACKUP_DIR/db_\$DATE.sql.gz

# Media files backup
tar -czf \$BACKUP_DIR/media_\$DATE.tar.gz /home/skyguard/skyguard-gps/media/

# Configuration backup
tar -czf \$BACKUP_DIR/config_\$DATE.tar.gz /home/skyguard/skyguard-gps/.env /etc/nginx/sites-available/skyguard

# Cleanup old backups (keep 30 days)
find \$BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: \$DATE"
EOF

chmod +x /home/skyguard/backup.sh

# Schedule daily backups
echo "0 2 * * * /home/skyguard/backup.sh >> /var/log/skyguard/backup.log 2>&1" | sudo crontab -u skyguard -
```

## 📈 **Scaling Considerations**

### Horizontal Scaling
- Use load balancers (HAProxy/Nginx) for multiple application servers
- Implement Redis Cluster for cache distribution
- Use PostgreSQL replication for read scaling
- Separate GPS processing servers for heavy workloads

### Performance Monitoring
- Implement Prometheus + Grafana for metrics
- Use ELK Stack (Elasticsearch, Logstash, Kibana) for log analysis
- Monitor WebSocket connections and GPS data throughput

## 🔧 **Troubleshooting**

### Common Issues

1. **WebSocket Connection Failed**
   ```bash
   # Check Daphne service
   sudo systemctl status skyguard-daphne
   
   # Check WebSocket logs
   sudo journalctl -u skyguard-daphne -f
   ```

2. **GPS Data Not Processing**
   ```bash
   # Check GPS server status
   sudo systemctl status skyguard-gps-servers
   
   # Check Celery workers
   sudo systemctl status skyguard-celery
   ```

3. **High Memory Usage**
   ```bash
   # Monitor processes
   htop
   
   # Check Redis memory
   redis-cli info memory
   ```

## 📞 **Support & Maintenance**

### Regular Maintenance Tasks
- Weekly: Review system logs and performance metrics
- Monthly: Update dependencies and security patches
- Quarterly: Database optimization and cleanup
- Annually: SSL certificate renewal and security audit

### Contact Information
- **Technical Support**: support@your-domain.com
- **Emergency Contact**: +1-XXX-XXX-XXXX
- **Documentation**: https://docs.your-domain.com

---

**🎉 Congratulations!** Your SkyGuard GPS Enhanced system is now deployed with:
- ✅ Real-time WebSocket communication
- ✅ Advanced analytics with ML
- ✅ Enhanced security features
- ✅ Professional notification system
- ✅ Mobile-ready APIs
- ✅ Scalable architecture 