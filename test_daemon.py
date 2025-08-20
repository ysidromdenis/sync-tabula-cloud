#!/usr/bin/env python3
"""
Script de prueba para TabulaCloudDaemon.

Prueba la funcionalidad del daemon con DRamoSoftService.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from services.dramosoft_service import DRamoSoftService  # noqa: E402

# Imports después de modificar sys.path
from tabula_cloud_sync.service.daemon import TabulaCloudDaemon  # noqa: E402


def main():
    """Función principal para probar el daemon."""

    # Crear daemon para el servicio DRamoSoft
    daemon = TabulaCloudDaemon(
        service_class=DRamoSoftService,
        pidfile="/tmp/dramosoft_daemon.pid",
        config_file="config.ini",
        name="DRamoSoftDaemon",
    )

    if len(sys.argv) == 1:
        print("Uso: python test_daemon.py {start|stop|restart|status|test}")
        print("\nComandos disponibles:")
        print("  start   - Inicia el daemon")
        print("  stop    - Detiene el daemon")
        print("  restart - Reinicia el daemon")
        print("  status  - Muestra el estado del daemon")
        print("  test    - Prueba el servicio sin daemon")
        return

    command = sys.argv[1].lower()

    try:
        if command == "start":
            daemon.start()
        elif command == "stop":
            daemon.stop()
        elif command == "restart":
            daemon.restart()
        elif command == "status":
            daemon.status()
        elif command == "test":
            # Probar el servicio directamente sin daemon
            print("🧪 Probando el servicio DRamoSoft directamente...")
            service = DRamoSoftService("config.ini")
            print(f"Estado inicial: {service.get_status()}")

            # Probar sincronización
            result = service.perform_sync()
            print(f"Resultado de sync: {result}")

        else:
            print(f"Comando desconocido: {command}")
            print("Comandos válidos: start, stop, restart, status, test")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Interrumpido por el usuario")
        if command == "start":
            print("Deteniendo daemon...")
            daemon.stop()
    except Exception as e:
        print(f"❌ Error ejecutando comando '{command}': {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
