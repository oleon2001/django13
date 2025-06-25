#!/usr/bin/env python3
"""
Aplicación Web para controlar el simulador GPS desde móvil
"""

from flask import Flask, render_template_string, request, jsonify
import subprocess
import threading
import time
import json
import os
import signal

app = Flask(__name__)

# Estado global del simulador
simulator_process = None
simulator_status = {
    'running': False,
    'imei': None,
    'latitude': 19.4326,
    'longitude': -99.1332,
    'speed': 0,
    'course': 0
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 GPS Móvil - SkyGuard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .status {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
        }
        
        .status.running {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.stopped {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 10px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        
        .location-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .location-info h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .location-info p {
            margin: 5px 0;
            color: #666;
        }
        
        .quick-locations {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .quick-btn {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            text-align: center;
            font-size: 12px;
            transition: all 0.3s;
        }
        
        .quick-btn:hover {
            background: #f0f0f0;
            border-color: #667eea;
        }
        
        .geolocation-btn {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 GPS Móvil SkyGuard</h1>
            <p>Convierte tu teléfono en un dispositivo GPS</p>
        </div>
        
        <div id="status" class="status stopped">
            🔴 Simulador Detenido
        </div>
        
        <div class="form-group">
            <label for="imei">📟 IMEI (15 dígitos):</label>
            <input type="text" id="imei" placeholder="123456789012345" maxlength="15" pattern="[0-9]{15}">
        </div>
        
        <div class="form-group">
            <label for="server">🌐 Servidor GPS:</label>
            <input type="text" id="server" value="localhost" placeholder="localhost o IP del servidor">
        </div>
        
        <div class="form-group">
            <label for="protocol">📡 Protocolo:</label>
            <select id="protocol">
                <option value="concox">Concox (Puerto 55300)</option>
                <option value="wialon">Wialon (Puerto 20332)</option>
                <option value="meiligao">Meiligao (Puerto 62000)</option>
            </select>
        </div>
        
        <button class="btn geolocation-btn" onclick="getCurrentLocation()">
            📍 Usar Mi Ubicación Actual
        </button>
        
        <div class="quick-locations">
            <button class="quick-btn" onclick="setLocation(19.4326, -99.1332)">
                🏙️ Ciudad de México
            </button>
            <button class="quick-btn" onclick="setLocation(20.6597, -103.3496)">
                🌮 Guadalajara
            </button>
            <button class="quick-btn" onclick="setLocation(25.6866, -100.3161)">
                🏭 Monterrey
            </button>
            <button class="quick-btn" onclick="setLocation(21.1619, -86.8515)">
                🏖️ Cancún
            </button>
        </div>
        
        <div class="location-info">
            <h3>📍 Ubicación Actual</h3>
            <p><strong>Latitud:</strong> <span id="current-lat">19.4326</span></p>
            <p><strong>Longitud:</strong> <span id="current-lon">-99.1332</span></p>
            <p><strong>Velocidad:</strong> <span id="current-speed">0</span> km/h</p>
        </div>
        
        <div class="form-group">
            <label for="latitude">🌍 Latitud:</label>
            <input type="number" id="latitude" value="19.4326" step="0.000001" placeholder="19.4326">
        </div>
        
        <div class="form-group">
            <label for="longitude">🗺️ Longitud:</label>
            <input type="number" id="longitude" value="-99.1332" step="0.000001" placeholder="-99.1332">
        </div>
        
        <div class="form-group">
            <label for="speed">🚗 Velocidad (km/h):</label>
            <input type="number" id="speed" value="0" min="0" max="200" placeholder="0">
        </div>
        
        <button id="start-btn" class="btn btn-primary" onclick="startSimulator()">
            🚀 Iniciar Simulador GPS
        </button>
        
        <button id="stop-btn" class="btn btn-danger" onclick="stopSimulator()" style="display: none;">
            🛑 Detener Simulador
        </button>
        
        <button class="btn btn-secondary" onclick="updateLocation()">
            📍 Actualizar Ubicación
        </button>
    </div>

    <script>
        let statusInterval;
        
        function getCurrentLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        setLocation(lat, lon);
                        alert(`✅ Ubicación obtenida: ${lat.toFixed(6)}, ${lon.toFixed(6)}`);
                    },
                    function(error) {
                        alert(`❌ Error obteniendo ubicación: ${error.message}`);
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 60000
                    }
                );
            } else {
                alert("❌ Geolocalización no soportada en este navegador");
            }
        }
        
        function setLocation(lat, lon) {
            document.getElementById('latitude').value = lat.toFixed(6);
            document.getElementById('longitude').value = lon.toFixed(6);
            document.getElementById('current-lat').textContent = lat.toFixed(6);
            document.getElementById('current-lon').textContent = lon.toFixed(6);
        }
        
        function startSimulator() {
            const imei = document.getElementById('imei').value;
            const server = document.getElementById('server').value;
            const protocol = document.getElementById('protocol').value;
            const latitude = document.getElementById('latitude').value;
            const longitude = document.getElementById('longitude').value;
            const speed = document.getElementById('speed').value;
            
            if (!imei || imei.length !== 15 || !/^\d{15}$/.test(imei)) {
                alert('❌ Por favor ingresa un IMEI válido de 15 dígitos');
                return;
            }
            
            fetch('/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    imei: imei,
                    server: server,
                    protocol: protocol,
                    latitude: parseFloat(latitude),
                    longitude: parseFloat(longitude),
                    speed: parseFloat(speed)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('status').className = 'status running';
                    document.getElementById('status').textContent = '🟢 Simulador Activo';
                    document.getElementById('start-btn').style.display = 'none';
                    document.getElementById('stop-btn').style.display = 'block';
                    
                    // Iniciar monitoreo de estado
                    statusInterval = setInterval(checkStatus, 2000);
                } else {
                    alert(`❌ Error: ${data.message}`);
                }
            })
            .catch(error => {
                alert(`❌ Error de conexión: ${error}`);
            });
        }
        
        function stopSimulator() {
            fetch('/stop', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').className = 'status stopped';
                document.getElementById('status').textContent = '🔴 Simulador Detenido';
                document.getElementById('start-btn').style.display = 'block';
                document.getElementById('stop-btn').style.display = 'none';
                
                if (statusInterval) {
                    clearInterval(statusInterval);
                }
            });
        }
        
        function updateLocation() {
            const latitude = document.getElementById('latitude').value;
            const longitude = document.getElementById('longitude').value;
            const speed = document.getElementById('speed').value;
            
            fetch('/update_location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: parseFloat(latitude),
                    longitude: parseFloat(longitude),
                    speed: parseFloat(speed)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('current-lat').textContent = latitude;
                    document.getElementById('current-lon').textContent = longitude;
                    document.getElementById('current-speed').textContent = speed;
                    alert('✅ Ubicación actualizada');
                }
            });
        }
        
        function checkStatus() {
            fetch('/status')
            .then(response => response.json())
            .then(data => {
                if (data.running) {
                    document.getElementById('current-lat').textContent = data.latitude.toFixed(6);
                    document.getElementById('current-lon').textContent = data.longitude.toFixed(6);
                    document.getElementById('current-speed').textContent = data.speed;
                } else {
                    if (statusInterval) {
                        clearInterval(statusInterval);
                    }
                    stopSimulator();
                }
            });
        }
        
        // Generar IMEI aleatorio si está vacío
        window.onload = function() {
            const imeiField = document.getElementById('imei');
            if (!imeiField.value) {
                const randomImei = '35' + Math.random().toString().substr(2, 13);
                imeiField.value = randomImei.substr(0, 15);
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start', methods=['POST'])
def start_simulator():
    global simulator_process, simulator_status
    
    try:
        data = request.json
        imei = data['imei']
        server = data['server']
        protocol = data['protocol']
        latitude = data['latitude']
        longitude = data['longitude']
        speed = data['speed']
        
        # Detener simulador anterior si existe
        if simulator_process:
            simulator_process.terminate()
            simulator_process = None
        
        # Iniciar nuevo simulador
        cmd = [
            'python3', 'mobile_gps_simulator.py',
            '--imei', imei,
            '--server', server,
            '--protocol', protocol,
            '--lat', str(latitude),
            '--lon', str(longitude)
        ]
        
        simulator_process = subprocess.Popen(cmd, 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE)
        
        simulator_status.update({
            'running': True,
            'imei': imei,
            'latitude': latitude,
            'longitude': longitude,
            'speed': speed,
            'course': 0
        })
        
        return jsonify({'success': True, 'message': 'Simulador iniciado correctamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/stop', methods=['POST'])
def stop_simulator():
    global simulator_process, simulator_status
    
    try:
        if simulator_process:
            simulator_process.terminate()
            simulator_process = None
        
        simulator_status['running'] = False
        
        return jsonify({'success': True, 'message': 'Simulador detenido'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/update_location', methods=['POST'])
def update_location():
    global simulator_status
    
    try:
        data = request.json
        simulator_status.update({
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'speed': data['speed']
        })
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/status')
def get_status():
    return jsonify(simulator_status)

if __name__ == '__main__':
    print("🌐 Iniciando servidor web para control GPS móvil...")
    print("📱 Abre tu navegador en: http://localhost:5000")
    print("🔗 Desde tu teléfono: http://[IP-DE-TU-PC]:5000")
    print("⏹️  Presiona Ctrl+C para detener")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
