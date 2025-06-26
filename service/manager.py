#!/usr/bin/env python3
"""Script de administración para el servicio Tabula Cloud Sync."""

import argparse
import os
import platform
import sys


def get_service_class():
    """Obtiene la clase de servicio apropiada para la plataforma."""
    system = platform.system().lower()

    if system == "windows":
        from service.windows_service import TabulaCloudWindowsService

        return TabulaCloudWindowsService
    elif system in ["linux", "darwin", "unix"]:
        from service.daemon import TabulaCloudDaemon

        return TabulaCloudDaemon
    else:
        raise RuntimeError(f"Plataforma no soportada: {system}")


def install_service(config_file=None):
    """Instala el servicio en el sistema."""
    system = platform.system().lower()

    if system == "windows":
        service_class = get_service_class()
        service_class.install_service()

    elif system in ["linux", "darwin", "unix"]:
        # Para Linux, crear un archivo systemd
        create_systemd_service(config_file or "config.ini")

    else:
        print(f"Instalación automática no soportada en {system}")
        return False

    return True


def remove_service():
    """Desinstala el servicio del sistema."""
    system = platform.system().lower()

    if system == "windows":
        service_class = get_service_class()
        service_class.remove_service()

    elif system in ["linux", "darwin", "unix"]:
        remove_systemd_service()

    else:
        print(f"Desinstalación automática no soportada en {system}")
        return False

    return True


def create_systemd_service(config_file):
    """Crea un archivo de servicio systemd para Linux."""
    service_content = f"""[Unit]
Description=Tabula Cloud Sync Service
After=network.target

[Service]
Type=forking
User=root
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} -m service.daemon start
ExecStop={sys.executable} -m service.daemon stop
Restart=always
RestartSec=10
Environment=PYTHONPATH={os.getcwd()}
Environment=CONFIG_FILE={config_file}

[Install]
WantedBy=multi-user.target
"""

    service_file = "/etc/systemd/system/tabula-cloud-sync.service"

    try:
        with open(service_file, "w") as f:
            f.write(service_content)

        os.system("systemctl daemon-reload")
        os.system("systemctl enable tabula-cloud-sync.service")

        print(f"Servicio systemd creado en {service_file}")
        print(
            "Para iniciar el servicio: sudo systemctl start tabula-cloud-sync"
        )
        print("Para ver el estado: sudo systemctl status tabula-cloud-sync")

    except PermissionError:
        print(
            "Error: Se requieren permisos de administrador para instalar el servicio"
        )
        print("Ejecute como root o use sudo")
        return False

    return True


def remove_systemd_service():
    """Elimina el archivo de servicio systemd."""
    service_file = "/etc/systemd/system/tabula-cloud-sync.service"

    try:
        os.system("systemctl stop tabula-cloud-sync.service")
        os.system("systemctl disable tabula-cloud-sync.service")

        if os.path.exists(service_file):
            os.remove(service_file)

        os.system("systemctl daemon-reload")

        print("Servicio systemd eliminado")

    except PermissionError:
        print("Error: Se requieren permisos de administrador")
        return False

    return True


def start_service(config_file=None):
    """Inicia el servicio."""
    system = platform.system().lower()

    if system == "windows":
        os.system("net start TabulaCloudSync")

    elif system in ["linux", "darwin", "unix"]:
        config_file = config_file or "config.ini"
        service_class = get_service_class()
        daemon = service_class(config_file=config_file)
        daemon.start()

    else:
        print(f"Inicio automático no soportado en {system}")
        return False

    return True


def stop_service():
    """Detiene el servicio."""
    system = platform.system().lower()

    if system == "windows":
        os.system("net stop TabulaCloudSync")

    elif system in ["linux", "darwin", "unix"]:
        service_class = get_service_class()
        daemon = service_class()
        daemon.stop()

    else:
        print(f"Detención automática no soportada en {system}")
        return False

    return True


def restart_service(config_file=None):
    """Reinicia el servicio."""
    system = platform.system().lower()

    if system == "windows":
        os.system("net stop TabulaCloudSync")
        os.system("net start TabulaCloudSync")

    elif system in ["linux", "darwin", "unix"]:
        config_file = config_file or "config.ini"
        service_class = get_service_class()
        daemon = service_class(config_file=config_file)
        daemon.restart()

    else:
        print(f"Reinicio automático no soportado en {system}")
        return False

    return True


def status_service():
    """Muestra el estado del servicio."""
    system = platform.system().lower()

    if system == "windows":
        os.system("sc query TabulaCloudSync")

    elif system in ["linux", "darwin", "unix"]:
        service_class = get_service_class()
        daemon = service_class()
        daemon.status()

    else:
        print(f"Estado no disponible en {system}")
        return False

    return True


def main():
    """Función principal del script de administración."""
    parser = argparse.ArgumentParser(
        description="Administrador del servicio Tabula Cloud Sync"
    )

    parser.add_argument(
        "command",
        choices=["install", "remove", "start", "stop", "restart", "status"],
        help="Comando a ejecutar",
    )

    parser.add_argument(
        "--config",
        default="config.ini",
        help="Archivo de configuración a usar (default: config.ini)",
    )

    args = parser.parse_args()

    try:
        if args.command == "install":
            if install_service(args.config):
                print("Servicio instalado correctamente")
            else:
                sys.exit(1)

        elif args.command == "remove":
            if remove_service():
                print("Servicio desinstalado correctamente")
            else:
                sys.exit(1)

        elif args.command == "start":
            if start_service(args.config):
                print("Servicio iniciado")
            else:
                sys.exit(1)

        elif args.command == "stop":
            if stop_service():
                print("Servicio detenido")
            else:
                sys.exit(1)

        elif args.command == "restart":
            if restart_service(args.config):
                print("Servicio reiniciado")
            else:
                sys.exit(1)

        elif args.command == "status":
            status_service()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
