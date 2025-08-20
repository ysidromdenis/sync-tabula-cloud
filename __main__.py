#!/usr/bin/env python3
"""Punto de entrada principal para el servicio Tabula Cloud Sync."""

import argparse
import platform
import sys
from pathlib import Path

# Importar utilidades de directorio
try:
    from tabula_cloud_sync.utils.directories import get_appropriate_config_path
except ImportError:
    # Fallback si no se puede importar
    def get_appropriate_config_path(local_config=None):
        if local_config:
            return Path(local_config)
        return Path.cwd() / "config.ini"


def main():
    """Función principal para ejecutar el servicio."""
    parser = argparse.ArgumentParser(
        description="Tabula Cloud Sync Service", prog="tabula-cloud-sync"
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=["start", "stop", "restart", "status", "install", "remove"],
        help="Comando a ejecutar",
    )

    parser.add_argument(
        "--config",
        default="config.ini",
        help="Archivo de configuración (default: config.ini)",
    )

    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Ejecutar como daemon (solo Linux/Unix)",
    )

    parser.add_argument(
        "--foreground",
        action="store_true",
        help="Ejecutar en primer plano para debugging",
    )

    args = parser.parse_args()

    # Resolver ruta de configuración usando platformdirs
    config_path = get_appropriate_config_path(args.config)

    system = platform.system().lower()

    # Si no se especifica comando, mostrar ayuda
    if not args.command:
        if args.foreground:
            # Ejecutar en modo foreground para debugging
            run_foreground(str(config_path))
        else:
            parser.print_help()
            return

    # Ejecutar comando específico
    try:
        if system == "windows":
            handle_windows_command(args, str(config_path))
        elif system in ["linux", "darwin"]:
            handle_unix_command(args, str(config_path))
        else:
            print(f"Sistema no soportado: {system}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_foreground(config_file):
    """Ejecuta el servicio en primer plano."""
    import time

    from service.base_service import TabulaCloudService

    class SimpleService(TabulaCloudService):
        def perform_sync(self):
            self.logger.info("Ejecutando sincronización de ejemplo...")
            # Aquí iría la lógica de sincronización por defecto
            import datetime

            self._last_sync = datetime.datetime.now().isoformat()

    print("Iniciando servicio en modo foreground...")
    print("Presiona Ctrl+C para detener")

    service = SimpleService(config_file)

    try:
        service.start_service()

        # Mantener ejecutándose hasta Ctrl+C
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDeteniendo servicio...")
        service.stop_service()
        print("Servicio detenido")


def handle_windows_command(args, config_path):
    """Maneja comandos en Windows."""
    try:
        from service.windows_service import TabulaCloudWindowsService

        if args.command == "install":
            TabulaCloudWindowsService.install_service()
        elif args.command == "remove":
            TabulaCloudWindowsService.remove_service()
        elif args.command in ["start", "stop", "restart", "status"]:
            import os

            if args.command == "start":
                os.system("net start TabulaCloudSync")
            elif args.command == "stop":
                os.system("net stop TabulaCloudSync")
            elif args.command == "restart":
                os.system("net stop TabulaCloudSync")
                os.system("net start TabulaCloudSync")
            elif args.command == "status":
                os.system("sc query TabulaCloudSync")

    except ImportError:
        print("Error: Dependencias de Windows no disponibles")
        print("Instale pywin32: pip install pywin32")
        sys.exit(1)


def handle_unix_command(args, config_path):
    """Maneja comandos en Linux/Unix."""
    from service.daemon import TabulaCloudDaemon

    # Determinar archivo PID usando nombre de configuración
    config_name = Path(config_path).stem
    pidfile = f"/var/run/tabula_cloud_{config_name}.pid"

    daemon = TabulaCloudDaemon(pidfile=pidfile, config_file=config_path)

    if args.command == "start":
        daemon.start()
    elif args.command == "stop":
        daemon.stop()
    elif args.command == "restart":
        daemon.restart()
    elif args.command == "status":
        daemon.status()
    elif args.command == "install":
        # Para Linux, usar el manager
        from service.manager import install_service

        install_service(args.config)
    elif args.command == "remove":
        from service.manager import remove_service

        remove_service()


if __name__ == "__main__":
    main()
