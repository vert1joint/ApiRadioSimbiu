#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para renovar el token de autenticación de la API de Simbiu
Ejecutar cuando el token expire o necesite ser actualizado
"""

import requests
import json
import os
from datetime import datetime

# configuración
API_LOGIN_URL = "https://api.simbiu.es/api/Account/login"
EMAIL = "gqueupan@nexnews.cl"
PASSWORD = "S3gu1m13nto"

# archivo donde se guardará el token
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "token_simbiu.txt")

def renovar_token():
    """solicita un nuevo token a la API de Simbiu y lo guarda en archivo"""
    print("\n" + "="*80)
    print("🔑 RENOVADOR DE TOKEN - API SIMBIU")
    print("="*80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # preparar datos de login
    data = {
        'email': EMAIL,
        'password': PASSWORD
    }
    
    headers = {
        'x-version': '1',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔄 Solicitando nuevo token...")
        print(f"   URL: {API_LOGIN_URL}")
        print(f"   Email: {EMAIL}")
        print()
        
        # hacer request
        json_data = json.dumps(data)
        response = requests.post(API_LOGIN_URL, data=json_data, headers=headers)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login exitoso!")
            
            # extraer token de la respuesta
            respuesta_token = response.json()
            token = respuesta_token['token']
            
            print(f"\n📝 Token obtenido:")
            print(f"   {token[:50]}...{token[-20:]}")
            print()
            
            # guardar token en archivo
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(token)
            
            print(f"💾 Token guardado en: {TOKEN_FILE}")
            print()
            print("="*80)
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
            print("="*80)
            print()
            print("El token ha sido actualizado y está listo para usar.")
            print("Puedes ejecutar InterfaceApi.py normalmente.")
            print()
            return True
            
        else:
            print(f"❌ Error al renovar token: {response.status_code}")
            print(f"\n📄 Respuesta del servidor:")
            print(response.text)
            print()
            print("="*80)
            print("❌ PROCESO FALLIDO")
            print("="*80)
            print()
            print("Posibles causas:")
            print("  - Credenciales incorrectas")
            print("  - API no disponible")
            print("  - Problemas de conexión")
            print()
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión")
        print()
        print("No se pudo conectar a la API de Simbiu.")
        print("Verifica tu conexión a Internet.")
        print()
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print()
        import traceback
        print("Detalles del error:")
        print(traceback.format_exc())
        print()
        return False

def verificar_token_actual():
    """verifica si existe un token guardado"""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                token_actual = f.read().strip()
                if token_actual:
                    print("📋 Token actual encontrado:")
                    print(f"   {token_actual[:50]}...{token_actual[-20:]}")
                    print(f"   Archivo: {TOKEN_FILE}")
                    print()
                    return True
        except Exception as e:
            print(f"⚠️ Error al leer token actual: {e}")
            print()
    else:
        print("⚠️ No se encontró archivo de token")
        print(f"   Se creará en: {TOKEN_FILE}")
        print()
    return False

def main():
    """función principal"""
    print()
    
    # verificar token actual
    existe_token = verificar_token_actual()
    
    if existe_token:
        respuesta = input("¿Deseas renovar el token? (s/n): ").lower().strip()
        if respuesta != 's':
            print("\nOperación cancelada.")
            print()
            return
        print()
    
    # renovar token
    exitoso = renovar_token()
    
    # pausa al final
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()

