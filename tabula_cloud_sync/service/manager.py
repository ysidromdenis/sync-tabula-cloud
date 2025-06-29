"""
Manager de servicios para Tabula Cloud Sync.

Proporciona funcionalidad para gestionar servicios como daemon,
incluyendo start, stop, restart, status y monitoreo.
"""

import argparse
import sys
from pathlib import Path

from ..utils.commons import safe_read_file
from .base_service import TabulaCloudService
from .daemon import TabulaCloudDaemon


def create_default_service():
    """Crea un servicio por defecto para testing."""

    class DefaultTabulaService(TabulaCloudService):
        def perform_sync(self):
            self.logger.info("Ejecutando sincronización por defecto...")
            return {
                "status": "success",
                "message": "Sincronización por defecto completada",
                "timestamp": str(self.last_sync_time),
            }

    return DefaultTabulaService


def load_service_class(config_file: str = "config/tabula_config.ini"):
    """
    Carga la clase de servicio desde configuración o usa la por defecto.

    Args:
        config_file: Archivo de configuración

    Returns:
        Clase del servicio a usar
    """
    # Intentar cargar configuración para encontrar la clase de servicio
    config_content = safe_read_file(config_file)

    if config_content and "[SERVICE]" in config_content:
        # TODO: Implementar carga de clase personalizada desde config
        pass

    # Por ahora, usar servicio por defecto
    return create_default_service()


def main():
    """Función principal del manager de servicios."""
    parser = argparse.ArgumentParser(
        description="Manager de servicios Tabula Cloud Sync",
        prog="tabula-service",
    )

    parser.add_argument(
        "action",
        choices=["start", "stop", "restart", "status", "test"],
        help="Acción a realizar",
    )

    parser.add_argument(
        "--config",
        default="config/tabula_config.ini",
        help="Archivo de configuración (default: config/tabula_config.ini)",
    )

    parser.add_argument("--pidfile", help="Archivo PID personalizado")

    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Ejecutar como daemon (default en Linux/Unix)",
    )

    parser.add_argument(
        "--foreground",
        action="store_true",
        help="Ejecutar en primer plano (no como daemon)",
    )

    args = parser.parse_args()

    try:
        if args.action == "test":
            # Modo de prueba - ejecutar sin daemon
            print("🧪 Modo de prueba - Ejecutando servicio en primer plano...")
            service_class = load_service_class(args.config)
            service = service_class(args.config)

            print("▶️  Iniciando servicio...")
            service.start()

            try:
                # Ejecutar por un tiempo limitado en modo prueba
                import time

                print("⏱️  Ejecutando por 30 segundos...")
                time.sleep(30)
            except KeyboardInterrupt:
                print("\n🛑 Interrumpido por el usuario")
            finally:
                print("⏹️  Deteniendo servicio...")
                service.stop()
                print("✅ Prueba completada")

        elif args.foreground:
            # Ejecutar en primer plano
            print(f"▶️  Ejecutando servicio en primer plano...")
            service_class = load_service_class(args.config)
            service = service_class(args.config)

            try:
                service.start()

                # Mantener ejecutándose hasta interrupción
                import time

                while service.running:
                    time.sleep(1)

            except KeyboardInterrupt:
                print("\n🛑 Interrumpido por el usuario")
            finally:
                service.stop()

        else:
            # Usar daemon
            service_class = load_service_class(args.config)

            daemon = TabulaCloudDaemon(
                service_class=service_class,
                config_file=args.config,
                pidfile=args.pidfile,
            )

            if args.action == "start":
                daemon.start()
            elif args.action == "stop":
                daemon.stop()
            elif args.action == "restart":
                daemon.restart()
            elif args.action == "status":
                daemon.status()

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
