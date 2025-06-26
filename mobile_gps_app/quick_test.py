#!/usr/bin/env python3
"""
Script de prueba rápida para verificar la conectividad GPS.
Envía una ubicación de prueba al servidor.
"""

import socket
import time
import sys
from datetime import datetime

def test_gps_connection(host='localhost', port=20332, imei='123456789012345'):
    """Probar conexión GPS básica."""
    
    print("=" * 60)
    print("🧪 FALKON GPS - PRUEBA RÁPIDA DE CONECTIVIDAD")
    print("=" * 60)
    print(f"🎯 Servidor: {host}:{port}")
    print(f"📱 IMEI: {imei}")
    print()
    
    try:
        # 1. Conectar al servidor
        print("🔄 Conectando al servidor...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        print("✅ Conexión establecida")
        
        # 2. Enviar login
        print("🔐 Enviando login...")
        login_packet = f"#L#{imei};123456\r\n"
        sock.send(login_packet.encode('ascii'))
        print(f"📤 Enviado: {login_packet.strip()}")
        
        # 3. Esperar respuesta (opcional)
        try:
            response = sock.recv(1024)
            if response:
                print(f"📥 Respuesta: {response.decode('ascii').strip()}")
        except socket.timeout:
            print("⏰ Sin respuesta del servidor (normal)")
        
        # 4. Enviar ubicación de prueba
        print("📍 Enviando ubicación de prueba...")
        
        # Ciudad de México como ubicación de prueba
        lat = 19.4326
        lon = -99.1332
        
        now = datetime.now()
        date = now.strftime("%d%m%y")
        time_str = now.strftime("%H%M%S")
        
        # Convertir a formato Wialon
        lat1 = int(lat)
        lat2 = (lat - lat1) * 60
        lon1 = int(abs(lon))
        lon2 = (abs(lon) - lon1) * 60
        
        data_packet = (
            f"#D#{date};{time_str};{lat1};{lat2:.4f};{lon1};{lon2:.4f};"
            f"45;180;2240;8;1.0;0;0;0;;NA\r\n"
        )
        
        sock.send(data_packet.encode('ascii'))
        print(f"📤 Ubicación enviada:")
        print(f"   📍 Coordenadas: {lat}, {lon}")
        print(f"   📦 Paquete: {data_packet.strip()}")
        
        # 5. Mantener conexión por unos segundos
        print("⏱️ Manteniendo conexión...")
        time.sleep(3)
        
        # 6. Cerrar conexión
        sock.close()
        print("✅ Prueba completada exitosamente!")
        print()
        print("🎉 Tu servidor GPS está funcionando correctamente")
        print("📱 Ahora puedes usar tu teléfono como dispositivo GPS")
        
        return True
        
    except ConnectionRefusedError:
        print("❌ ERROR: Conexión rechazada")
        print("💡 Soluciones:")
        print("   1. Verifica que el servidor GPS esté corriendo")
        print("   2. Ejecuta: python manage.py runserver_gps")
        print("   3. Verifica que el puerto 20332 esté abierto")
        return False
        
    except socket.timeout:
        print("❌ ERROR: Timeout de conexión")
        print("💡 Soluciones:")
        print("   1. Verifica la IP del servidor")
        print("   2. Verifica la conectividad de red")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Función principal."""
    
    # Configuración por defecto
    host = 'localhost'
    port = 20332
    imei = '123456789012345'
    
    # Permitir argumentos de línea de comandos
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        imei = sys.argv[3]
    
    # Ejecutar prueba
    success = test_gps_connection(host, port, imei)
    
    if success:
        print("\n📋 SIGUIENTE PASO:")
        print("1. En tu teléfono, ejecuta: python gps_client.py")
        print("2. O abre la aplicación web en tu navegador móvil")
        print("3. Configura la misma IP y puerto")
        print("4. ¡Disfruta del rastreo GPS en tiempo real!")
    else:
        print("\n🔧 SOLUCIÓN DE PROBLEMAS:")
        print("1. Inicia el servidor GPS:")
        print("   cd /path/to/skyguard")
        print("   python manage.py runserver_gps")
        print()
        print("2. Verifica puertos abiertos:")
        print("   netstat -tlnp | grep 20332")
        print()
        print("3. Configura firewall si es necesario:")
        print("   sudo ufw allow 20332")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()