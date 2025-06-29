# 🔧 SOLUCIÓN: Dispositivo GPS no aparece en el Frontend

## 🚨 El Problema

El servidor GPS simple (`start_gps_server.py`) **solo recibe datos pero NO los guarda en la base de datos**. Por eso el frontend no puede mostrar el dispositivo.

## ✅ La Solución

Usa el servidor GPS de Django que SÍ guarda los datos en la base de datos.

## 📝 Pasos para solucionarlo:

### 1️⃣ Detén todos los servicios actuales
```bash
# Presiona Ctrl+C en todas las terminales donde tengas servicios corriendo
```

### 2️⃣ Inicia los servicios en el orden correcto

**Terminal 1 - Backend Django:**
```bash
cd /c/Users/oswaldo/Desktop/django13
source venv/bin/activate  # o venv\Scripts\activate en Windows
python manage.py runserver
```

**Terminal 2 - Servidor GPS con Django (¡IMPORTANTE!):**
```bash
cd /c/Users/oswaldo/Desktop/django13
source venv/bin/activate
python start_django_gps_server.py
```
⚠️ **NO uses** `python start_gps_server.py` - ese es el servidor simple sin BD

**Terminal 3 - Simulador GPS:**
```bash
cd /c/Users/oswaldo/Desktop/django13
source venv/bin/activate
python pc_gps_simulator.py
```

**Terminal 4 - Frontend React:**
```bash
cd /c/Users/oswaldo/Desktop/django13/frontend
npm start
```

### 3️⃣ Verifica que funcione

1. Abre http://localhost:3000/dashboard
2. Deberías ver el dispositivo "PC-DESKTOP-5V9VDBR" en el mapa
3. El dispositivo debería mostrar su ubicación y actualizarse cada 15 segundos

## 🔍 Comandos útiles para verificar:

**Verificar dispositivo en BD:**
```bash
python check_pc_device.py
```

**Ver todos los dispositivos:**
```bash
python manage.py shell
>>> from skyguard.apps.gps.models import GPSDevice
>>> GPSDevice.objects.all()
```

## 🎯 Alternativa: Usar el comando Django directamente

En lugar de `start_django_gps_server.py`, también puedes usar:
```bash
python manage.py runserver_gps --servers=wialon
```

## ⚡ Script todo-en-uno actualizado

Si prefieres usar el script automatizado:
```bash
python start_pc_as_gps.py
```
Este script ya fue actualizado para usar el servidor GPS correcto.

## 🛠️ Si algo falla:

1. **Error "value too long for type character varying(4)":**
   - Ya está corregido en `register_pc_device.py`
   
2. **El dispositivo no aparece:**
   - Ejecuta `python check_pc_device.py` para verificar
   - Asegúrate de usar `start_django_gps_server.py` NO `start_gps_server.py`

3. **Error de conexión:**
   - Verifica que el puerto 20332 esté libre
   - Verifica que PostgreSQL esté corriendo

## 📊 Diferencias entre servidores:

| Servidor | Archivo | ¿Guarda en BD? | ¿Aparece en Frontend? |
|----------|---------|----------------|----------------------|
| Simple | `start_gps_server.py` | ❌ NO | ❌ NO |
| Django | `start_django_gps_server.py` | ✅ SÍ | ✅ SÍ |
| Django CMD | `manage.py runserver_gps` | ✅ SÍ | ✅ SÍ |

## 🎉 ¡Listo!

Con estos cambios, tu dispositivo GPS debería aparecer correctamente en el frontend. 