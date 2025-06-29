"""
Daemon personalizado para Cli.

Este archivo fue generado automáticamente por Tabula Cloud Sync.
"""

import sys
import signal
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tabula_cloud_sync.service.daemon import TabulaCloudDaemon
from .test_tabula_projectservice import testtabulaprojectService


class CliDaemon(TabulaCloudDaemon):
    """Daemon personalizado para Cli."""

    def __init__(self):
        super().__init__(
            service_class=testtabulaprojectService, pidfile="/tmp/cli_daemon.pid"
        )


def signal_handler(signum, frame):
    """Manejador de señales para cerrar el daemon correctamente."""
    print(f"\nRecibida señal {signum}. Cerrando daemon...")
    daemon.stop()
    sys.exit(0)


if __name__ == "__main__":
    daemon = CliDaemon()

    # Configurar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if len(sys.argv) == 2:
        if "start" == sys.argv[1]:
            daemon.start()
        elif "stop" == sys.argv[1]:
            daemon.stop()
        elif "restart" == sys.argv[1]:
            daemon.restart()
        elif "status" == sys.argv[1]:
            daemon.status()
        else:
            print(f"Comando desconocido: {sys.argv[1]}")
            sys.exit(2)
        sys.exit(0)
    else:
        print(f"Uso: {sys.argv[0]} start|stop|restart|status")
        sys.exit(2)
