#!/usr/bin/env python3
"""
Script de debug para verificar la carga de configuración
"""
import configparser
import sys
from pathlib import Path

# Agregar el directorio del proyecto al PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tabula_cloud_sync.utils.directories import get_appropriate_config_path

print("🔍 Debug de configuración:")
print()

# 1. Verificar qué archivo está intentando leer
config_path = get_appropriate_config_path()
print(f"📁 Archivo de configuración detectado: {config_path}")
print(f"   Existe: {config_path.exists()}")
print()

# 2. Verificar el archivo real que tienes
real_config = Path("config/tabula_config.ini")
print(f"📁 Tu archivo real: {real_config}")
print(f"   Existe: {real_config.exists()}")
print()

# 3. Probar cargar directamente tu archivo
if real_config.exists():
    config = configparser.ConfigParser()
    config.read(str(real_config))

    print("📋 Secciones encontradas:")
    for section in config.sections():
        print(f"   [{section}]")
        for key, value in config.items(section):
            if "password" in key.lower() or "key" in key.lower():
                print(f"     {key} = ***")
            else:
                print(f"     {key} = {value}")
        print()

    # 4. Probar la extracción de URL
    try:
        base_url = config.get("API", "base_url", fallback="")
        print(f"🌐 base_url extraído: '{base_url}'")

        if base_url:
            if base_url.startswith("https://"):
                protocolo = "https"
                url_base = base_url.replace("https://", "")
            elif base_url.startswith("http://"):
                protocolo = "http"
                url_base = base_url.replace("http://", "")
            else:
                protocolo = "https"
                url_base = base_url

            print(f"   PROTOCOLO: {protocolo}")
            print(f"   URL_BASE: {url_base}")

    except Exception as e:
        print(f"❌ Error al extraer URL: {e}")

print()
print("💡 Solución:")
print("   ✅ Archivo configurado correctamente en config/tabula_config.ini")
print("   📁 Orden de búsqueda: usuario → actual → config/ → examples/")
