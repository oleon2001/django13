#!/bin/bash
# Script para iniciar el sistema GPS en Linux/WSL

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Función para iniciar servicio en nueva terminal
start_service() {
    title=$1
    command=$2
    
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$title" -- bash -c "$command; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -title "$title" -e "$command; bash" &
    else
        # Si no hay terminal gráfica, usar tmux
        tmux new-window -n "$title" "$command"
    fi
}

clear
print_color $CYAN "============================================"
print_color $YELLOW "    INICIANDO SISTEMA GPS SKYGUARD"
print_color $CYAN "============================================"

# Cambiar al directorio del proyecto
cd /mnt/c/Users/oswaldo/Desktop/django13 || exit 1

print_color $GREEN "\n[1/5] Verificando entorno virtual..."
if [ -f "venv/bin/activate" ]; then
    print_color $GREEN "✓ Entorno virtual encontrado"
else
    print_color $RED "✗ Entorno virtual no encontrado. Creándolo..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

print_color $GREEN "\n[2/5] Registrando dispositivo PC..."
python register_pc_device.py

print_color $GREEN "\n[3/5] Iniciando servicios..."

# Verificar si hay tmux disponible
if command -v tmux &> /dev/null; then
    # Crear nueva sesión tmux si no existe
    tmux has-session -t skyguard 2>/dev/null || tmux new-session -d -s skyguard
    
    # Backend Django
    print_color $CYAN "  → Iniciando Backend Django..."
    tmux new-window -t skyguard -n "Django" "cd $(pwd) && source venv/bin/activate && python manage.py runserver"
    sleep 3
    
    # Servidor GPS Django
    print_color $CYAN "  → Iniciando Servidor GPS Django..."
    tmux new-window -t skyguard -n "GPS-Server" "cd $(pwd) && source venv/bin/activate && python start_django_gps_server.py"
    sleep 3
    
    # Simulador GPS
    print_color $CYAN "  → Iniciando Simulador GPS..."
    tmux new-window -t skyguard -n "GPS-Sim" "cd $(pwd) && source venv/bin/activate && python pc_gps_simulator.py"
    sleep 2
    
    # Frontend React
    print_color $CYAN "  → Iniciando Frontend React..."
    tmux new-window -t skyguard -n "React" "cd $(pwd)/frontend && npm start"
    
    print_color $YELLOW "\n💡 Usa 'tmux attach -t skyguard' para ver los servicios"
    print_color $YELLOW "   Navega entre ventanas con Ctrl+B y luego número (0-4)"
else
    # Sin tmux, ejecutar en background
    print_color $CYAN "  → Iniciando Backend Django..."
    python manage.py runserver > logs/django.log 2>&1 &
    DJANGO_PID=$!
    sleep 3
    
    print_color $CYAN "  → Iniciando Servidor GPS Django..."
    python start_django_gps_server.py > logs/gps_server.log 2>&1 &
    GPS_PID=$!
    sleep 3
    
    print_color $CYAN "  → Iniciando Simulador GPS..."
    python pc_gps_simulator.py > logs/gps_sim.log 2>&1 &
    SIM_PID=$!
    sleep 2
    
    print_color $CYAN "  → Iniciando Frontend React..."
    cd frontend && npm start > ../logs/react.log 2>&1 &
    REACT_PID=$!
    cd ..
    
    print_color $GREEN "\nPIDs de los procesos:"
    echo "  Django: $DJANGO_PID"
    echo "  GPS Server: $GPS_PID"
    echo "  GPS Simulator: $SIM_PID"
    echo "  React: $REACT_PID"
fi

print_color $GREEN "\n[4/5] Esperando que los servicios estén listos..."
sleep 10

print_color $GREEN "\n[5/5] Verificando dispositivo en BD..."
python check_pc_device.py

print_color $CYAN "\n============================================"
print_color $GREEN "✓ SISTEMA INICIADO CORRECTAMENTE"
print_color $CYAN "============================================"
print_color $YELLOW "\nURLs disponibles:"
echo -e "  • Frontend: ${CYAN}http://localhost:3000${NC}"
echo -e "  • Dashboard: ${CYAN}http://localhost:3000/dashboard${NC}"
echo -e "  • Backend API: ${CYAN}http://localhost:8000${NC}"
echo -e "  • Django Admin: ${CYAN}http://localhost:8000/admin${NC}"

if command -v tmux &> /dev/null; then
    print_color $YELLOW "\nPara ver los servicios:"
    echo "  tmux attach -t skyguard"
    print_color $YELLOW "\nPara detener todos los servicios:"
    echo "  tmux kill-session -t skyguard"
else
    print_color $YELLOW "\nPara detener todos los servicios:"
    echo "  kill $DJANGO_PID $GPS_PID $SIM_PID $REACT_PID"
fi

echo
read -p "Presiona Enter para salir..." 