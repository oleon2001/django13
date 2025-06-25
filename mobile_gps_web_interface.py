#!/usr/bin/env python3
"""
Interfaz web para controlar GPS móvil desde celular
Permite enviar coordenadas GPS reales desde el navegador del celular
"""

from flask import Flask, render_template_string, request, jsonify
import socket
import struct
import threading
import time
import json
from datetime import datetime
import os

app = Flask(__name__)

class MobileGPSController:
    """Controlador de GPS móvil que recibe coordenadas del navegador."""
    
    def __init__(self, server_host: str = 'localhost', server_port: int = 50100):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.session_id = None
        self.imei = 123456789012345
        self.running = False
        self.last_position = None
        self.connected = False
        
        # Constantes del protocolo
        self.PKTID_LOGIN = 0x01
        self.PKTID_PING = 0x02
        
    def connect_to_server(self) -> bool:
        """Conectar al servidor SkyGuard."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            
            # Enviar login
            login_packet = self.create_login_packet()
            self.socket.sendto(login_packet, (self.server_host, self.server_port))
            
            # Recibir respuesta
            response, addr = self.socket.recvfrom(1024)
            if len(response) >= 5:
                self.session_id = struct.unpack("<I", response[1:5])[0]
                self.connected = True
                print(f"Conectado al servidor SkyGuard. Session ID: {self.session_id}")
                return True
            else:
                print("Respuesta de login inválida")
                return False
                
        except Exception as e:
            print(f"Error al conectar: {e}")
            return False
    
    def create_login_packet(self) -> bytes:
        """Crear paquete de login."""
        imei_bytes = struct.pack("<Q", self.imei)
        mac_bytes = b'\x00\x11\x22\x33\x44\x55'
        return struct.pack("B", self.PKTID_LOGIN) + imei_bytes + mac_bytes
    
    def send_position(self, lat: float, lon: float, speed: float = 0.0, course: float = 0.0):
        """Enviar posición al servidor."""
        if not self.connected or not self.session_id:
            print("No conectado al servidor")
            return False
        
        try:
            # Crear datos de posición
            timestamp = int(time.time())
            lat_int = int(lat * 10000000)
            lon_int = int(lon * 10000000)
            speed_int = int(speed * 10)
            course_int = int(course * 10)
            
            # Paquete de ping: PKTID_PING + timestamp + lat + lon + speed + course + inputs
            inputs = 0x01  # Ignición encendida
            ping_data = struct.pack("<IiiBB", timestamp, lat_int, lon_int, speed_int, inputs)
            ping_packet = struct.pack("B", self.PKTID_PING) + ping_data
            
            self.socket.sendto(ping_packet, (self.server_host, self.server_port))
            
            # Recibir respuesta
            try:
                response, addr = self.socket.recvfrom(1024)
                print(f"Posición enviada: {lat:.6f}, {lon:.6f} - Respuesta: {len(response)} bytes")
                self.last_position = (lat, lon, speed, course, datetime.now())
                return True
            except socket.timeout:
                print("Timeout en respuesta del ping")
                return False
                
        except Exception as e:
            print(f"Error enviando posición: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del servidor."""
        self.connected = False
        if self.socket:
            self.socket.close()
            self.socket = None
        print("Desconectado del servidor")

# Instancia global del controlador
gps_controller = MobileGPSController()

# HTML template para la interfaz móvil
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
        
        input[type="number"], input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="number"]:focus, input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .btn {
            padding: 15px 20px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
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
        
        .location-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .location-info h3 {
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
        
        .auto-send {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            text-align: center;
        }
        
        .auto-send label {
            display: inline-flex;
            align-items: center;
            cursor: pointer;
        }
        
        .auto-send input[type="checkbox"] {
            margin-right: 10px;
            transform: scale(1.2);
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
            
            <div class="button-group">
                <button class="btn btn-primary" onclick="connectToServer()">Conectar</button>
                <button class="btn btn-danger" onclick="disconnectFromServer()">Desconectar</button>
            </div>
            
            <button class="btn btn-success" style="width: 100%;" onclick="sendPosition()" id="sendBtn" disabled>
                📡 Enviar Posición
            </button>
            
            <button class="btn btn-primary" style="width: 100%; margin-top: 10px;" onclick="getCurrentLocation()">
                📍 Obtener Ubicación Actual
            </button>
            
            <div class="auto-send">
                <label>
                    <input type="checkbox" id="autoSend" onchange="toggleAutoSend()">
                    Envío automático cada 30 segundos
                </label>
            </div>
            
            <div class="location-info">
                <h3>📊 Información de Ubicación</h3>
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
        let autoSendInterval = null;
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
                positionStatus.textContent = 'Conectado al servidor';
            } else {
                statusText.textContent = 'Desconectado';
                statusDiv.className = 'status disconnected';
                sendBtn.disabled = true;
                positionStatus.textContent = 'Desconectado';
            }
        }
        
        async function connectToServer() {
            try {
                log('Conectando al servidor SkyGuard...', 'info');
                const response = await fetch('/connect', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    updateStatus(true);
                    log('Conectado exitosamente al servidor', 'success');
                } else {
                    log('Error al conectar: ' + data.error, 'error');
                }
            } catch (error) {
                log('Error de conexión: ' + error.message, 'error');
            }
        }
        
        async function disconnectFromServer() {
            try {
                log('Desconectando del servidor...', 'info');
                const response = await fetch('/disconnect', { method: 'POST' });
                const data = await response.json();
                
                updateStatus(false);
                log('Desconectado del servidor', 'info');
                
                if (autoSendInterval) {
                    clearInterval(autoSendInterval);
                    autoSendInterval = null;
                }
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
        
        function toggleAutoSend() {
            const autoSend = document.getElementById('autoSend').checked;
            
            if (autoSend && isConnected) {
                log('Activando envío automático cada 30 segundos', 'info');
                autoSendInterval = setInterval(sendPosition, 30000);
            } else if (autoSendInterval) {
                log('Desactivando envío automático', 'info');
                clearInterval(autoSendInterval);
                autoSendInterval = null;
            }
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
    """Conectar al servidor SkyGuard."""
    try:
        success = gps_controller.connect_to_server()
        return jsonify({'success': success, 'error': None if success else 'Error de conexión'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    """Desconectar del servidor SkyGuard."""
    try:
        gps_controller.disconnect()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/send_position', methods=['POST'])
def send_position():
    """Enviar posición al servidor SkyGuard."""
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

def main():
    """Función principal."""
    print("=== Interfaz Web GPS Móvil SkyGuard ===")
    print("Iniciando servidor web en http://0.0.0.0:5000")
    print("Abre esta URL en tu celular para controlar el GPS")
    
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main() 