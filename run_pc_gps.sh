#!/bin/bash
# Script para ejecutar PC como dispositivo GPS en WSL

echo "🚀 PC GPS SYSTEM - SkyGuard"
echo "🌍 Iniciando PC como dispositivo GPS"
echo "============================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "pc_gps_config.json" ]; then
    echo "❌ Error: No se encuentra pc_gps_config.json"
    echo "💡 Ejecuta desde el directorio del proyecto"
    exit 1
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Verificar IMEI
echo "🔍 Verificando IMEI..."
python verify_imei.py
if [ $? -ne 0 ]; then
    echo "❌ IMEI inválido"
    exit 1
fi

# Registrar dispositivo
echo "🔧 Registrando dispositivo PC..."
python register_pc_device.py

# Preguntar si iniciar sistema completo
echo ""
echo "¿Cómo quieres iniciar el sistema?"
echo "1) Sistema completo automático"
echo "2) Solo servidor GPS"
echo "3) Solo simulador PC"
echo "4) Manual (paso a paso)"
read -p "Selecciona una opción (1-4): " option

case $option in
    1)
        echo "🚀 Iniciando sistema completo..."
        python start_pc_as_gps.py
        ;;
    2)
        echo "🌐 Iniciando solo servidor GPS..."
        python start_gps_server.py
        ;;
    3)
        echo "🖥️ Iniciando solo simulador PC..."
        python pc_gps_simulator.py
        ;;
    4)
        echo "📋 COMANDOS MANUALES:"
        echo ""
        echo "Terminal 1 - Servidor GPS:"
        echo "  python start_gps_server.py"
        echo ""
        echo "Terminal 2 - Simulador PC:"
        echo "  python pc_gps_simulator.py"
        echo ""
        echo "Terminal 3 - Frontend:"
        echo "  cd frontend && npm start"
        echo ""
        echo "URLs importantes:"
        echo "  • Frontend: http://localhost:3000"
        echo "  • Backend: http://localhost:8000"
        echo "  • Admin: http://localhost:8000/admin"
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo "✅ Script completado" 