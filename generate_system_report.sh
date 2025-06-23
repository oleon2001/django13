#!/bin/bash

# Script para generar reporte completo del sistema SkyGuard
# Útil para diagnóstico y soporte técnico

REPORT_FILE="skyguard_system_report_$(date +%Y%m%d_%H%M%S).txt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Generando reporte del sistema SkyGuard..."
echo "Archivo de reporte: $REPORT_FILE"

# Función para agregar separador
add_separator() {
    echo "=================================================================" >> "$REPORT_FILE"
    echo "$1" >> "$REPORT_FILE"
    echo "=================================================================" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# Función para ejecutar comando y capturar salida
run_command() {
    local cmd="$1"
    local description="$2"
    
    echo "📋 $description"
    add_separator "$description"
    
    echo "Comando: $cmd" >> "$REPORT_FILE"
    echo "Fecha: $(date)" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    if eval "$cmd" >> "$REPORT_FILE" 2>&1; then
        echo "✅ $description - OK"
    else
        echo "❌ $description - ERROR"
        echo "ERROR: Comando falló" >> "$REPORT_FILE"
    fi
    
    echo "" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# Inicializar reporte
echo "REPORTE DEL SISTEMA SKYGUARD GPS TRACKING" > "$REPORT_FILE"
echo "Generado: $(date)" >> "$REPORT_FILE"
echo "Servidor: $(hostname)" >> "$REPORT_FILE"
echo "Usuario: $(whoami)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 1. Información del Sistema
run_command "uname -a" "INFORMACIÓN DEL SISTEMA OPERATIVO"
run_command "lsb_release -a" "DISTRIBUCIÓN LINUX"
run_command "uptime" "TIEMPO DE FUNCIONAMIENTO"
run_command "date" "FECHA Y HORA ACTUAL"

# 2. Recursos del Sistema
run_command "free -h" "MEMORIA RAM"
run_command "df -h" "ESPACIO EN DISCO"
run_command "lscpu" "INFORMACIÓN DEL CPU"
run_command "ps aux --sort=-%mem | head -20" "PROCESOS QUE MÁS MEMORIA USAN"
run_command "ps aux --sort=-%cpu | head -20" "PROCESOS QUE MÁS CPU USAN"

# 3. Red
run_command "ip addr show" "CONFIGURACIÓN DE RED"
run_command "netstat -tlnp" "PUERTOS ABIERTOS"
run_command "ss -tlnp" "CONEXIONES DE RED (SS)"

# 4. Servicios del Sistema
run_command "systemctl status skyguard" "ESTADO SERVICIO SKYGUARD"
run_command "systemctl status nginx" "ESTADO SERVICIO NGINX"
run_command "systemctl status postgresql" "ESTADO SERVICIO POSTGRESQL"
run_command "systemctl status redis" "ESTADO SERVICIO REDIS"

# 5. Logs de Servicios (últimas 50 líneas)
run_command "journalctl -u skyguard --no-pager -n 50" "LOGS SYSTEMD SKYGUARD"
run_command "journalctl -u nginx --no-pager -n 50" "LOGS SYSTEMD NGINX"
run_command "journalctl -u postgresql --no-pager -n 50" "LOGS SYSTEMD POSTGRESQL"

# 6. Configuración de Nginx
if [ -f "/etc/nginx/sites-available/skyguard" ]; then
    run_command "cat /etc/nginx/sites-available/skyguard" "CONFIGURACIÓN NGINX SKYGUARD"
fi

run_command "nginx -t" "VERIFICACIÓN CONFIGURACIÓN NGINX"

# 7. Base de Datos PostgreSQL
run_command "sudo -u postgres psql -c 'SELECT version();'" "VERSIÓN POSTGRESQL"
run_command "sudo -u postgres psql -c '\\l'" "BASES DE DATOS DISPONIBLES"

if sudo -u postgres psql skyguard -c '\dt' >/dev/null 2>&1; then
    run_command "sudo -u postgres psql skyguard -c '\\dt'" "TABLAS EN BASE DE DATOS SKYGUARD"
    run_command "sudo -u postgres psql skyguard -c 'SELECT count(*) FROM pg_stat_activity;'" "CONEXIONES ACTIVAS"
    run_command "sudo -u postgres psql skyguard -c 'SELECT schemaname,tablename,n_tup_ins,n_tup_upd,n_tup_del FROM pg_stat_user_tables ORDER BY n_tup_ins DESC LIMIT 10;'" "ESTADÍSTICAS DE TABLAS"
fi

# 8. Redis
run_command "redis-cli ping" "CONEXIÓN A REDIS"
run_command "redis-cli info server" "INFORMACIÓN SERVIDOR REDIS"
run_command "redis-cli info memory" "USO DE MEMORIA REDIS"

# 9. Python y Dependencias
if [ -d "$SCRIPT_DIR/venv" ]; then
    run_command "source $SCRIPT_DIR/venv/bin/activate && python --version" "VERSIÓN PYTHON (VENV)"
    run_command "source $SCRIPT_DIR/venv/bin/activate && pip list" "PAQUETES PYTHON INSTALADOS"
fi

run_command "python3 --version" "VERSIÓN PYTHON SISTEMA"

# 10. Archivos de Configuración Django
if [ -f "$SCRIPT_DIR/.env.development" ]; then
    add_separator "ARCHIVO .ENV.DEVELOPMENT (SIN PASSWORDS)"
    echo "Archivo encontrado: .env.development" >> "$REPORT_FILE"
    grep -v -i "password\|secret\|key" "$SCRIPT_DIR/.env.development" >> "$REPORT_FILE" 2>/dev/null || echo "Error leyendo archivo" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

if [ -f "$SCRIPT_DIR/.env.production" ]; then
    add_separator "ARCHIVO .ENV.PRODUCTION (SIN PASSWORDS)"
    echo "Archivo encontrado: .env.production" >> "$REPORT_FILE"
    grep -v -i "password\|secret\|key" "$SCRIPT_DIR/.env.production" >> "$REPORT_FILE" 2>/dev/null || echo "Error leyendo archivo" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# 11. Logs de la Aplicación (últimas 100 líneas)
if [ -f "/var/log/django/skyguard.log" ]; then
    run_command "tail -100 /var/log/django/skyguard.log" "LOGS DJANGO SKYGUARD"
fi

if [ -f "/var/log/gunicorn/skyguard-error.log" ]; then
    run_command "tail -100 /var/log/gunicorn/skyguard-error.log" "LOGS ERROR GUNICORN"
fi

if [ -f "/var/log/nginx/skyguard_error.log" ]; then
    run_command "tail -100 /var/log/nginx/skyguard_error.log" "LOGS ERROR NGINX SKYGUARD"
fi

# 12. Certificados SSL
run_command "certbot certificates" "CERTIFICADOS SSL"

# 13. Estructura de Archivos del Proyecto
run_command "find $SCRIPT_DIR -maxdepth 3 -type f -name '*.py' | head -20" "ARCHIVOS PYTHON DEL PROYECTO"
run_command "ls -la $SCRIPT_DIR" "CONTENIDO DIRECTORIO PRINCIPAL"

if [ -d "$SCRIPT_DIR/skyguard" ]; then
    run_command "ls -la $SCRIPT_DIR/skyguard" "CONTENIDO DIRECTORIO SKYGUARD"
fi

if [ -d "$SCRIPT_DIR/migration_scripts" ]; then
    run_command "ls -la $SCRIPT_DIR/migration_scripts" "SCRIPTS DE MIGRACIÓN"
fi

# 14. Verificación de Conectividad
run_command "curl -I http://localhost:8000" "CONECTIVIDAD HTTP LOCAL"
run_command "curl -I https://localhost" "CONECTIVIDAD HTTPS LOCAL"

# 15. Variables de Entorno
add_separator "VARIABLES DE ENTORNO RELEVANTES"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-'No configurado'}" >> "$REPORT_FILE"
echo "DJANGO_ENVIRONMENT: ${DJANGO_ENVIRONMENT:-'No configurado'}" >> "$REPORT_FILE"
echo "PATH: $PATH" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 16. Información de Migración (si existe)
if [ -f "$SCRIPT_DIR/migration_scripts/master_migration.log" ]; then
    run_command "tail -50 $SCRIPT_DIR/migration_scripts/master_migration.log" "ÚLTIMOS LOGS DE MIGRACIÓN"
fi

# 17. Resumen Final
add_separator "RESUMEN DEL SISTEMA"
{
    echo "✅ SERVICIOS ACTIVOS:"
    systemctl is-active skyguard >/dev/null 2>&1 && echo "  - SkyGuard: ACTIVO" || echo "  - SkyGuard: INACTIVO"
    systemctl is-active nginx >/dev/null 2>&1 && echo "  - Nginx: ACTIVO" || echo "  - Nginx: INACTIVO"
    systemctl is-active postgresql >/dev/null 2>&1 && echo "  - PostgreSQL: ACTIVO" || echo "  - PostgreSQL: INACTIVO"
    systemctl is-active redis >/dev/null 2>&1 && echo "  - Redis: ACTIVO" || echo "  - Redis: INACTIVO"
    
    echo ""
    echo "💾 RECURSOS:"
    echo "  - Memoria disponible: $(free -h | grep '^Mem:' | awk '{print $7}')"
    echo "  - Espacio disco /: $(df -h / | tail -1 | awk '{print $4}')"
    
    echo ""
    echo "🌐 CONECTIVIDAD:"
    if curl -s http://localhost:8000 >/dev/null 2>&1; then
        echo "  - HTTP localhost:8000: OK"
    else
        echo "  - HTTP localhost:8000: ERROR"
    fi
    
    echo ""
    echo "📊 BASE DE DATOS:"
    if sudo -u postgres psql skyguard -c 'SELECT 1;' >/dev/null 2>&1; then
        echo "  - Conexión PostgreSQL: OK"
        echo "  - Conexiones activas: $(sudo -u postgres psql skyguard -t -c 'SELECT count(*) FROM pg_stat_activity;' 2>/dev/null | xargs)"
    else
        echo "  - Conexión PostgreSQL: ERROR"
    fi
    
    echo ""
    echo "🔧 CONFIGURACIÓN:"
    echo "  - Entorno Django: ${DJANGO_ENVIRONMENT:-'No configurado'}"
    echo "  - Configuración Nginx: $(nginx -t 2>&1 | grep -q 'successful' && echo 'OK' || echo 'ERROR')"
    
} >> "$REPORT_FILE"

# Finalizar
echo "" >> "$REPORT_FILE"
echo "=================================================================" >> "$REPORT_FILE"
echo "FIN DEL REPORTE - $(date)" >> "$REPORT_FILE"
echo "=================================================================" >> "$REPORT_FILE"

echo ""
echo "✅ Reporte generado exitosamente: $REPORT_FILE"
echo ""
echo "📋 RESUMEN RÁPIDO:"
echo "  - Servicios activos: $(systemctl is-active skyguard nginx postgresql redis 2>/dev/null | grep -c active)"
echo "  - Memoria libre: $(free -h | grep '^Mem:' | awk '{print $7}')"
echo "  - Espacio disco: $(df -h / | tail -1 | awk '{print $4}')"
echo ""
echo "Para ver el reporte completo:"
echo "  cat $REPORT_FILE"
echo ""
echo "Para enviar por email:"
echo "  mail -s 'Reporte Sistema SkyGuard' admin@example.com < $REPORT_FILE" 