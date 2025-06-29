#!/usr/bin/env python3
"""
Verificar que el IMEI sea válido (15 dígitos)
"""
import json

def verify_imei():
    print("🔍 Verificando IMEI...")
    
    # Leer configuración
    try:
        with open('pc_gps_config.json', 'r') as f:
            config = json.load(f)
        
        imei = config.get('imei', '')
        print(f"IMEI encontrado: {imei}")
        print(f"Longitud: {len(imei)} caracteres")
        
        # Verificar que sea numérico
        if not imei.isdigit():
            print("❌ Error: IMEI debe contener solo números")
            return False
        
        # Verificar longitud
        if len(imei) != 15:
            print(f"❌ Error: IMEI debe tener exactamente 15 dígitos, tiene {len(imei)}")
            return False
        
        print("✅ IMEI válido!")
        print(f"   IMEI: {imei}")
        print(f"   Formato: {imei[:3]}-{imei[3:5]}-{imei[5:11]}-{imei[11:14]}-{imei[14]}")
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: Archivo pc_gps_config.json no encontrado")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    verify_imei() 