#!/bin/bash

# Script para manejar el proyecto Falkun
# Uso: ./manage_falkun.sh [comando]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKYGUARD_DIR="$PROJECT_DIR/skyguard"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log() {
    echo -e "${GREEN}[FALKUN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Función para verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado. Por favor instala Docker primero."
        exit 1
    fi
    
    # Intentar usar docker compose (nueva versión) primero, luego docker-compose
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
        exit 1
    fi
}

# Función para verificar si Python está instalado
check_python() {
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        error "Python no está instalado. Por favor instala Python primero."
        exit 1
    fi
}

# Función para levantar la base de datos
start_db() {
    log "Levantando base de datos PostgreSQL con PostGIS..."
    cd "$PROJECT_DIR"
    $DOCKER_COMPOSE_CMD up -d db
    log "Base de datos iniciada en puerto 5433"
    log "Credenciales:"
    log "  Base de datos: falkun"
    log "  Usuario: falkun_user"
    log "  Contraseña: falkun_password"
    log "  Puerto: 5433"
}

# Función para detener la base de datos
stop_db() {
    log "Deteniendo base de datos..."
    cd "$PROJECT_DIR"
    $DOCKER_COMPOSE_CMD down
    log "Base de datos detenida"
}

# Función para crear entorno virtual
create_venv() {
    log "Creando entorno virtual..."
    cd "$PROJECT_DIR"
    python3 -m venv venv_falkun
    log "Entorno virtual creado en venv_falkun/"
}

# Función para activar entorno virtual
activate_venv() {
    log "Activando entorno virtual..."
    source "$PROJECT_DIR/venv_falkun/bin/activate"
    log "Entorno virtual activado"
}

# Función para instalar dependencias
install_deps() {
    log "Instalando dependencias..."
    cd "$PROJECT_DIR"
    source venv_falkun/bin/activate
    
    # Intentar con requirements modernos primero
    if [ -f "requirements_modern.txt" ]; then
        log "Usando dependencias modernas..."
        pip install -r requirements_modern.txt
    else
        log "Usando dependencias originales..."
        pip install -r requirements.txt
    fi
    
    log "Dependencias instaladas"
}

# Función para ejecutar migraciones
run_migrations() {
    log "Ejecutando migraciones..."
    cd "$SKYGUARD_DIR"
    source "$PROJECT_DIR/venv_falkun/bin/activate"
    export DJANGO_SETTINGS_MODULE=sites.www.settings_docker
    python manage.py migrate
    log "Migraciones completadas"
}

# Función para crear superusuario
create_superuser() {
    log "Creando superusuario..."
    cd "$SKYGUARD_DIR"
    source "$PROJECT_DIR/venv_falkun/bin/activate"
    export DJANGO_SETTINGS_MODULE=sites.www.settings_docker
    python manage.py createsuperuser
    log "Superusuario creado"
}

# Función para ejecutar el servidor de desarrollo
run_server() {
    log "Iniciando servidor de desarrollo..."
    cd "$SKYGUARD_DIR"
    source "$PROJECT_DIR/venv_falkun/bin/activate"
    export DJANGO_SETTINGS_MODULE=sites.www.settings_docker
    python manage.py runserver 0.0.0.0:8000
}

# Función para mostrar estado
status() {
    log "Estado del proyecto Falkun:"
    echo
    
    # Verificar Docker
    if docker ps | grep -q falkun_db; then
        info "✓ Base de datos PostgreSQL ejecutándose"
    else
        warn "✗ Base de datos PostgreSQL no está ejecutándose"
    fi
    
    # Verificar entorno virtual
    if [ -d "$PROJECT_DIR/venv_falkun" ]; then
        info "✓ Entorno virtual creado"
    else
        warn "✗ Entorno virtual no creado"
    fi
    
    # Verificar dependencias
    if [ -f "$PROJECT_DIR/venv_falkun/bin/activate" ]; then
        source "$PROJECT_DIR/venv_falkun/bin/activate"
        if python -c "import django" 2>/dev/null; then
            info "✓ Django instalado"
        else
            warn "✗ Django no instalado"
        fi
    fi
}

# Función para mostrar ayuda
show_help() {
    echo "Script de manejo para el proyecto Falkun"
    echo
    echo "Uso: $0 [comando]"
    echo
    echo "Comandos disponibles:"
    echo "  start-db      - Levantar base de datos PostgreSQL con PostGIS"
    echo "  stop-db       - Detener base de datos"
    echo "  setup         - Configurar todo el entorno (DB + venv + deps)"
    echo "  create-venv   - Crear entorno virtual"
    echo "  install-deps  - Instalar dependencias"
    echo "  migrate       - Ejecutar migraciones de Django"
    echo "  superuser     - Crear superusuario"
    echo "  runserver     - Ejecutar servidor de desarrollo"
    echo "  status        - Mostrar estado del proyecto"
    echo "  help          - Mostrar esta ayuda"
    echo
    echo "Ejemplos:"
    echo "  $0 setup      # Configurar todo el entorno"
    echo "  $0 start-db   # Solo levantar base de datos"
    echo "  $0 runserver  # Solo ejecutar servidor"
}

# Función para configuración completa
setup() {
    log "Configurando entorno completo de Falkun..."
    
    check_docker
    check_python
    
    start_db
    create_venv
    install_deps
    
    log "Esperando que la base de datos esté lista..."
    sleep 10
    
    run_migrations
    
    log "Configuración completada!"
    log "Para iniciar el servidor: $0 runserver"
    log "Para crear superusuario: $0 superuser"
}

# Manejo de comandos
case "${1:-help}" in
    start-db)
        check_docker
        start_db
        ;;
    stop-db)
        stop_db
        ;;
    setup)
        setup
        ;;
    create-venv)
        create_venv
        ;;
    install-deps)
        install_deps
        ;;
    migrate)
        run_migrations
        ;;
    superuser)
        create_superuser
        ;;
    runserver)
        run_server
        ;;
    status)
        status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Comando desconocido: $1"
        echo
        show_help
        exit 1
        ;;
esac 