#!/usr/bin/env python3
"""
Servidor GPS Wialon Simple para recibir datos de celulares
"""
import socket
import threading
import time
from datetime import datetime

def handle_client(client_socket, address):
    """Manejar conexión de cliente GPS"""
    print(f"📱 Nueva conexión desde: {address}")
    
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            message = data.decode('ascii', errors='ignore').strip()
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📩 Recibido de {address}: {message}")
            
            if message.startswith('#L#'):
                # Paquete de login: #L#IMEI;PASSWORD
                parts = message.split(';')
                if len(parts) >= 2:
                    imei = parts[0][3:]  # Quitar #L#
                    print(f"✅ Login exitoso para IMEI: {imei}")
                    response = b'#AL#1\r\n'  # Login OK
                else:
                    print("❌ Login fallido - formato incorrecto")
                    response = b'#AL#0\r\n'  # Login failed
                client_socket.send(response)
                
            elif message.startswith('#D#'):
                # Paquete de datos: #D#fecha;lat;lon;speed;course;sats
                print("📍 Datos GPS recibidos")
                response = b'#AD#1\r\n'  # Data acknowledged
                client_socket.send(response)
                
            elif message.startswith('#P#'):
                # Ping packet
                print("💗 Ping recibido")
                response = b'#AP#\r\n'  # Ping response
                client_socket.send(response)
                
    except Exception as e:
        print(f"❌ Error manejando cliente {address}: {e}")
    finally:
        client_socket.close()
        print(f"🔴 Desconectado: {address}")

def start_wialon_server(host='0.0.0.0', port=20332):
    """Iniciar servidor GPS Wialon"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"🟢 Servidor GPS Wialon iniciado en {host}:{port}")
        print("📱 Esperando conexiones de dispositivos GPS...")
        print("🔄 Presiona Ctrl+C para detener el servidor")
        print("-" * 50)
        
        while True:
            client_socket, address = server.accept()
            
            # Crear hilo para manejar cada cliente
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor GPS...")
    except Exception as e:
        print(f"❌ Error del servidor: {e}")
    finally:
        server.close()
        print("✅ Servidor GPS detenido")

if __name__ == "__main__":
    start_wialon_server() 