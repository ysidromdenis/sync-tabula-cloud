#!/usr/bin/env python3
"""
Script de prueba para verificar la carga de configuración de URLs
"""
import sys
import os
from pathlib import Path

# Agregar el directorio del proyecto al PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from tabula_cloud_sync.core.urls import PROTOCOLO, URL_BASE, PORT
    
    print("🔧 Configuración de URLs cargada exitosamente:")
    print(f"   PROTOCOLO: {PROTOCOLO}")
    print(f"   URL_BASE: {URL_BASE}")
    print(f"   PORT: {PORT}")
    print()
    
    # Construir URL de ejemplo
    if URL_BASE:
        if PORT in ("80", "443"):
            example_url = f"{PROTOCOLO}://{URL_BASE}/api/accounts/v1/login/"
        else:
            example_url = f"{PROTOCOLO}://{URL_BASE}:{PORT}/api/accounts/v1/login/"
        
        print(f"🌐 URL de ejemplo: {example_url}")
    else:
        print("⚠️  URL_BASE está vacía - verifica tu configuración")
        
except ImportError as e:
    print(f"❌ Error al importar: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
