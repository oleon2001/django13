# 🚀 GUÍA RÁPIDA: Sistema GPS SkyGuard

## 🎯 Inicio Rápido (La forma más fácil)

### Opción 1: Script Automático para Windows PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File start_gps_windows.ps1
```
Este script abrirá 4 ventanas de PowerShell con todos los servicios.

### Opción 2: Script Automático para WSL/Linux
```bash
chmod +x start_gps_linux.sh
./start_gps_linux.sh
```

### Opción 3: Script Python Todo-en-Uno
```bash
python start_pc_as_gps.py
```

## 🔧 Inicio Manual (Si prefieres control total)

Abre 4 terminales/ventanas PowerShell y ejecuta en cada una:

**Terminal 1 - Backend Django:**
```bash
# Windows PowerShell
cd C:\Users\oswaldo\Desktop\django13
venv\Scripts\activate
python manage.py runserver

# WSL/Linux
cd /mnt/c/Users/oswaldo/Desktop/django13
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Servidor GPS (¡IMPORTANTE: Usa el correcto!):**
```bash
# Windows PowerShell
venv\Scripts\activate
python start_django_gps_server.py

# O alternativamente:
python manage.py runserver_gps --servers=wialon
```

**Terminal 3 - Simulador GPS:**
```bash
# Windows PowerShell
venv\Scripts\activate
python pc_gps_simulator.py
```

**Terminal 4 - Frontend React:**
```bash
# Windows PowerShell
cd frontend
npm start
```

## 🔍 Verificación

1. **Verificar dispositivo en BD:**
   ```bash
   python check_pc_device.py
   ```

2. **Abrir el Dashboard:**
   - http://localhost:3000/dashboard
   - Deberías ver el dispositivo "PC-DESKTOP-5V9VDBR" en el mapa

## ⚠️ Errores Comunes y Soluciones

### El dispositivo no aparece en el frontend
- **Causa:** Estás usando el servidor GPS incorrecto
- **Solución:** Usa `start_django_gps_server.py` NO `start_gps_server.py`

### Error "value too long for type character varying(4)"
- **Causa:** Campo software_version muy largo
- **Solución:** Ya corregido en `register_pc_device.py`

### Puerto 20332 en uso
```bash
# Windows - Ver qué usa el puerto
netstat -ano | findstr :20332

# Matar proceso por PID
taskkill /PID <numero_pid> /F
```

### Frontend muestra warnings de CSS
- Son solo warnings de autoprefixer, no afectan funcionalidad

## 📊 Diferencia Crítica entre Servidores

| ❌ NO USES | ✅ USA ESTE |
|------------|------------|
| `start_gps_server.py` | `start_django_gps_server.py` |
| Solo recibe datos | Recibe Y guarda en BD |
| NO aparece en frontend | SÍ aparece en frontend |

## 🎉 ¡Listo!

Una vez iniciados los servicios correctamente:
1. Ve a http://localhost:3000/dashboard
2. Verás tu PC como dispositivo GPS
3. La ubicación se actualiza cada 15 segundos

## 🛑 Para Detener Todo

- **Si usaste script automático:** Cierra todas las ventanas
- **Si usaste inicio manual:** Ctrl+C en cada terminal
- **Si usaste tmux:** `tmux kill-session -t skyguard` 