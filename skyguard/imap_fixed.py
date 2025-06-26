#!/usr/bin/env python3
"""
Script mejorado para IMAP con soporte SSL moderno.
"""
import ssl
import imaplib
from imapclient import IMAPClient

def create_secure_context():
    """Crear contexto SSL seguro."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

def test_imap_connection():
    """Probar conexión IMAP con SSL moderno."""
    HOST = 'imap.zoho.com'
    USERNAME = 'admin@ensambles.net'
    PASSWORD = 'l6moSa5mgCpg'
    
    try:
        # Método 1: IMAPClient con contexto SSL personalizado
        context = create_secure_context()
        server = IMAPClient(HOST, use_uid=True, ssl=True, ssl_context=context)
        server.login(USERNAME, PASSWORD)
        
        select_info = server.select_folder('INBOX')
        print(f'✅ Conexión IMAP exitosa: {select_info["EXISTS"]} mensajes en INBOX')
        server.logout()
        return True
        
    except Exception as e:
        print(f"❌ Error conexión IMAP: {e}")
        
        try:
            # Método 2: imaplib directo
            context = create_secure_context()
            mail = imaplib.IMAP4_SSL(HOST, 993, ssl_context=context)
            mail.login(USERNAME, PASSWORD)
            mail.select('inbox')
            
            typ, data = mail.search(None, 'ALL')
            print(f'✅ Conexión IMAP alternativa exitosa: {len(data[0].split())} mensajes')
            mail.close()
            mail.logout()
            return True
            
        except Exception as e2:
            print(f"❌ Error conexión IMAP alternativa: {e2}")
            return False

if __name__ == "__main__":
    test_imap_connection()
