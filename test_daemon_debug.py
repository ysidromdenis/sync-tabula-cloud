#!/usr/bin/env python3
"""
Script simplificado para probar TabulaCloudDaemon en modo debug.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.dramosoft_service import DRamoSoftService  # noqa: E402
from tabula_cloud_sync.service.daemon import TabulaCloudDaemon  # noqa: E402


def test_daemon_direct():
    """Prueba el daemon directamente sin fork para debug."""
    print("🧪 Probando daemon en modo debug...")

    daemon = TabulaCloudDaemon(
        service_class=DRamoSoftService,
        pidfile="/tmp/dramosoft_debug.pid",
        config_file="config.ini",
        name="DRamoSoftDebug",
    )

    try:
        print("📝 Creando instancia del servicio...")
        daemon.service_instance = daemon.service_class(daemon.config_file)

        print("🔧 Cargando configuración...")
        daemon.service_instance.load_config()

        print("🌐 Inicializando sesión...")
        try:
            daemon.service_instance.initialize_session()
        except ValueError as e:
            print(f"⚠️ Advertencia de sesión: {e}")
            print("Continuando sin sesión (modo demo)...")

        print("📊 Estado del servicio:")
        status = daemon.service_instance.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")

        print("🔄 Ejecutando sincronización de prueba...")
        sync_result = daemon.service_instance.perform_sync()
        print(f"Resultado: {sync_result}")

        print("✅ Prueba de daemon completada exitosamente")

    except Exception as e:
        print(f"❌ Error en prueba de daemon: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_daemon_direct()
