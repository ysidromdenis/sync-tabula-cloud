#!/usr/bin/env python3
"""
Script para probar TabulaCloudDaemon con un servicio que se mantiene ejecutándose.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.dramosoft_service import DRamoSoftService  # noqa: E402
from tabula_cloud_sync.service.daemon import TabulaCloudDaemon  # noqa: E402


def test_daemon_background():
    """Prueba el daemon iniciándolo en background."""
    print("🧪 Probando daemon en background...")

    daemon = TabulaCloudDaemon(
        service_class=DRamoSoftService,
        pidfile="/tmp/dramosoft_daemon.pid",
        config_file="config.ini",
        name="DRamoSoftDaemon",
    )

    try:
        print("🚀 Iniciando daemon...")

        # Crear instancia del servicio y configurarlo para que se mantenga ejecutándose
        service = DRamoSoftService("config.ini")
        service.load_config()

        try:
            service.initialize_session()
        except ValueError as e:
            print(f"⚠️ API key no configurada, continuando en modo demo: {e}")

        # Iniciar el servicio manualmente
        service.start()

        print(f"✅ Servicio iniciado. Estado: {service.get_status()}")
        print("⏱️ Servicio ejecutándose por 10 segundos...")

        # Mantener ejecutándose por un tiempo para probar
        start_time = time.time()
        while time.time() - start_time < 10 and service.running:
            time.sleep(1)
            if int(time.time() - start_time) % 3 == 0:
                status = service.get_status()
                running_status = status["running"]
                sync_count = status["sync_count"]
                print(
                    f"📊 Estado: running={running_status}, syncs={sync_count}"
                )

        print("🛑 Deteniendo servicio...")
        service.stop()

        print(f"📈 Estado final: {service.get_status()}")

    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_daemon_background()
