#!/usr/bin/env python3
"""
Sistema GPS Móvil Simplificado para SkyGuard
Versión simplificada que funciona con la infraestructura existente
"""

import os
import sys
import time
import threading
import socket
import struct
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyguard.settings')
import django
django.setup()

# Importar modelos de Django
from skyguard.apps.gps.models.device import GPSDevice
from skyguard.apps.gps.models.protocols import UDPSession
from django.contrib.gis.geos import Point

app = Flask(__name__)

class SimpleGPSController:
    """Controlador GPS simplificado que se integra directamente con Django."""
    
    def __init__(self):
        self.imei = 123456789012345
        self.device = None
        self.connected = False
        self.last_position = None
        
    def connect_to_system(self) -> bool:
        """Conectar al sistema SkyGuard creando/actualizando el dispositivo."""
        try:
            # Buscar o crear el dispositivo GPS
            self.device, created = GPSDevice.objects.get_or_create(
                imei=self.imei,
                defaults={
                    'name': f'GPS Móvil {self.imei}',
                    'protocol': 'bluetooth',
                    'connection_status': 'ONLINE',
                    'current_ip': '127.0.0.1',
                    'current_port': 5000,
                    'first_connection': datetime.now(),
                    'last_connection': datetime.now(),
                    'last_heartbeat': datetime.now(),
                    'total_connections': 1
                }
            )
            
            if not created:
                # Actualizar dispositivo existente
                self.device.connection_status = 'ONLINE'
                self.device.current_ip = '127.0.0.1'
                self.device.current_port = 5000
                self.device.last_connection = datetime.now()
                self.device.last_heartbeat = datetime.now()
                self.device.total_connections += 1
                self.device.save()
            
            self.connected = True
            print(f"✅ Dispositivo GPS conectado: {self.device.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error conectando dispositivo: {e}")
            return False
    
    def send_position(self, lat: float, lon: float, speed: float = 0.0, course: float = 0.0):
        """Enviar posición al sistema SkyGuard."""
        if not self.connected or not self.device:
            print("❌ No conectado al sistema")
            return False
        
        try:
            # Crear punto geográfico
            position = Point(lon, lat)
            
            # Actualizar dispositivo
            self.device.position = position
            self.device.speed = speed
            self.device.course = course
            self.device.last_seen = datetime.now()
            self.device.last_heartbeat = datetime.now()
            self.device.connection_status = 'ONLINE'
            self.device.save()
            
            # Guardar posición
            self.last_position = (lat, lon, speed, course, datetime.now())
            
            print(f"✅ Posición enviada: {lat:.6f}, {lon:.6f} - Velocidad: {speed} km/h")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando posición: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del sistema."""
        if self.device:
            self.device.connection_status = 'OFFLINE'
            self.device.save()
        
        self.connected = False
        print("✅ Dispositivo GPS desconectado")

# Instancia global del controlador
gps_controller = SimpleGPSController()

# HTML template simplificado
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPS Móvil SkyGuard</title>
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
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }
        
        .status.connected {
            background: rgba(76, 175, 80, 0.2);
            color: #4CAF50;
        }
        
        .status.disconnected {
            background: rgba(244, 67, 54, 0.2);
            color: #F44336;
        }
        
        .content {
            padding: 30px 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input[type="number"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            width: 100%;
            padding: 15px 20px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 10px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(76, 175, 80, 0.3);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #F44336 0%, #d32f2f 100%);
            color: white;
        }
        
        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(244, 67, 54, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .info h3 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-label {
            font-weight: 600;
            color: #666;
        }
        
        .info-value {
            color: #333;
        }
        
        .log {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }
        
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-radius: 5px;
        }
        
        .log-entry.success {
            background: #e8f5e8;
            color: #2e7d32;
        }
        
        .log-entry.error {
            background: #ffebee;
            color: #c62828;
        }
        
        .log-entry.info {
            background: #e3f2fd;
            color: #1565c0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 GPS Móvil SkyGuard</h1>
            <div class="status" id="connectionStatus">
                <span id="statusText">Desconectado</span>
            </div>
        </div>
        
        <div class="content">
            <div class="form-group">
                <label for="latitude">Latitud:</label>
                <input type="number" id="latitude" step="0.000001" placeholder="19.4326" value="19.4326">
            </div>
            
            <div class="form-group">
                <label for="longitude">Longitud:</label>
                <input type="number" id="longitude" step="0.000001" placeholder="-99.1332" value="-99.1332">
            </div>
            
            <div class="form-group">
                <label for="speed">Velocidad (km/h):</label>
                <input type="number" id="speed" step="0.1" placeholder="0" value="0">
            </div>
            
            <div class="form-group">
                <label for="course">Dirección (grados):</label>
                <input type="number" id="course" step="0.1" placeholder="0" value="0">
            </div>
            
            <button class="btn btn-primary" onclick="connectToSystem()">Conectar</button>
            <button class="btn btn-danger" onclick="disconnectFromSystem()">Desconectar</button>
            
            <button class="btn btn-success" onclick="sendPosition()" id="sendBtn" disabled>
                📡 Enviar Posición
            </button>
            
            <button class="btn btn-primary" onclick="getCurrentLocation()">
                📍 Obtener Ubicación Actual
            </button>
            
            <div class="info">
                <h3>📊 Información del Dispositivo</h3>
                <div class="info-item">
                    <span class="info-label">IMEI:</span>
                    <span class="info-value">123456789012345</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Última posición:</span>
                    <span class="info-value" id="lastPosition">No enviada</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Estado:</span>
                    <span class="info-value" id="positionStatus">Desconectado</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Último envío:</span>
                    <span class="info-value" id="lastSent">Nunca</span>
                </div>
            </div>
            
            <div class="log" id="log">
                <div class="log-entry info">Sistema iniciado. Listo para conectar.</div>
            </div>
        </div>
    </div>

    <script>
        let isConnected = false;
        
        function log(message, type = 'info') {
            const logDiv = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        function updateStatus(connected) {
            isConnected = connected;
            const statusText = document.getElementById('statusText');
            const statusDiv = document.getElementById('connectionStatus');
            const sendBtn = document.getElementById('sendBtn');
            const positionStatus = document.getElementById('positionStatus');
            
            if (connected) {
                statusText.textContent = 'Conectado';
                statusDiv.className = 'status connected';
                sendBtn.disabled = false;
                positionStatus.textContent = 'Conectado al sistema';
            } else {
                statusText.textContent = 'Desconectado';
                statusDiv.className = 'status disconnected';
                sendBtn.disabled = true;
                positionStatus.textContent = 'Desconectado';
            }
        }
        
        async function connectToSystem() {
            try {
                log('Conectando al sistema SkyGuard...', 'info');
                const response = await fetch('/connect', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    updateStatus(true);
                    log('Conectado exitosamente al sistema', 'success');
                } else {
                    log('Error al conectar: ' + data.error, 'error');
                }
            } catch (error) {
                log('Error de conexión: ' + error.message, 'error');
            }
        }
        
        async function disconnectFromSystem() {
            try {
                log('Desconectando del sistema...', 'info');
                const response = await fetch('/disconnect', { method: 'POST' });
                const data = await response.json();
                
                updateStatus(false);
                log('Desconectado del sistema', 'info');
            } catch (error) {
                log('Error al desconectar: ' + error.message, 'error');
            }
        }
        
        async function sendPosition() {
            const lat = parseFloat(document.getElementById('latitude').value);
            const lon = parseFloat(document.getElementById('longitude').value);
            const speed = parseFloat(document.getElementById('speed').value);
            const course = parseFloat(document.getElementById('course').value);
            
            if (isNaN(lat) || isNaN(lon)) {
                log('Error: Coordenadas inválidas', 'error');
                return;
            }
            
            try {
                const response = await fetch('/send_position', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        latitude: lat,
                        longitude: lon,
                        speed: speed,
                        course: course
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('lastPosition').textContent = `${lat.toFixed(6)}, ${lon.toFixed(6)}`;
                    document.getElementById('lastSent').textContent = new Date().toLocaleTimeString();
                    log(`Posición enviada: ${lat.toFixed(6)}, ${lon.toFixed(6)}`, 'success');
                } else {
                    log('Error al enviar posición: ' + data.error, 'error');
                }
            } catch (error) {
                log('Error de envío: ' + error.message, 'error');
            }
        }
        
        function getCurrentLocation() {
            if (!navigator.geolocation) {
                log('Geolocalización no soportada en este navegador', 'error');
                return;
            }
            
            log('Obteniendo ubicación actual...', 'info');
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    document.getElementById('latitude').value = lat.toFixed(6);
                    document.getElementById('longitude').value = lon.toFixed(6);
                    
                    log(`Ubicación obtenida: ${lat.toFixed(6)}, ${lon.toFixed(6)}`, 'success');
                },
                function(error) {
                    log('Error obteniendo ubicación: ' + error.message, 'error');
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                }
            );
        }
        
        // Verificar estado inicial
        updateStatus(false);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal de la interfaz web."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/connect', methods=['POST'])
def connect():
    """Conectar al sistema SkyGuard."""
    try:
        success = gps_controller.connect_to_system()
        return jsonify({'success': success, 'error': None if success else 'Error de conexión'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    """Desconectar del sistema SkyGuard."""
    try:
        gps_controller.disconnect()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/send_position', methods=['POST'])
def send_position():
    """Enviar posición al sistema SkyGuard."""
    try:
        data = request.get_json()
        lat = data.get('latitude')
        lon = data.get('longitude')
        speed = data.get('speed', 0.0)
        course = data.get('course', 0.0)
        
        if lat is None or lon is None:
            return jsonify({'success': False, 'error': 'Coordenadas requeridas'})
        
        success = gps_controller.send_position(lat, lon, speed, course)
        return jsonify({'success': success, 'error': None if success else 'Error al enviar posición'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status')
def status():
    """Obtener estado del controlador."""
    return jsonify({
        'connected': gps_controller.connected,
        'last_position': gps_controller.last_position
    })

def get_local_ip():
    """Obtener la IP local del sistema."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def main():
    """Función principal."""
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🚗 GPS MÓVIL SKYGUARD - SISTEMA SIMPLIFICADO")
    print("=" * 60)
    print("Este sistema permite usar tu celular como GPS")
    print("y conectarlo directamente a SkyGuard.")
    print("=" * 60)
    print(f"🌐 Interfaz web disponible en: http://{local_ip}:5000")
    print("📱 Abre esta URL en tu celular para controlar el GPS")
    print("=" * 60)
    print("📋 Instrucciones:")
    print("1. Abre la URL en tu celular")
    print("2. Haz clic en 'Conectar'")
    print("3. Usa 'Obtener Ubicación Actual' para GPS real")
    print("4. Haz clic en 'Enviar Posición'")
    print("5. Verifica en SkyGuard (dispositivo IMEI: 123456789012345)")
    print("=" * 60)
    
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main() 