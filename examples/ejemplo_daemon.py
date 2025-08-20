#!/usr/bin/env python3
"""
Ejemplo de uso del módulo daemon.py
"""

from tabula_cloud_sync.service.base_service import TabulaCloudService
from tabula_cloud_sync.service.daemon import TabulaCloudDaemon


# 1. Primero necesitas un servicio que herede de TabulaCloudService
class MiServicioSync(TabulaCloudService):
    """Servicio de ejemplo que sincroniza datos cada 30 segundos"""

    def __init__(self, config_file="config.ini"):
        super().__init__(config_file)
        self.sync_interval = 30  # cada 30 segundos

    def perform_sync(self):
        """Implementación obligatoria del método abstracto"""
        self.logger.info("Realizando sincronización de datos...")
        # Aquí iría tu lógica de sincronización
        return {"status": "success", "synced_items": 10}


# 2. Crear el daemon con tu servicio
def main():
    # Crear daemon que manejará tu servicio
    daemon = TabulaCloudDaemon(
        service_class=MiServicioSync,
        pidfile="/tmp/mi_servicio_daemon.pid",
        config_file="config/mi_config.ini",
        name="MiServicioTabula",
    )

    import sys

    if len(sys.argv) == 2:
        comando = sys.argv[1]

        if comando == "start":
            print("🚀 Iniciando daemon...")
            daemon.start()

        elif comando == "stop":
            print("🛑 Deteniendo daemon...")
            daemon.stop()

        elif comando == "restart":
            print("🔄 Reiniciando daemon...")
            daemon.restart()

        elif comando == "status":
            print("📊 Estado del daemon:")
            daemon.status()

        else:
            print("❌ Comando no válido")
            print("Uso: python ejemplo_daemon.py {start|stop|restart|status}")
    else:
        print("Uso: python ejemplo_daemon.py {start|stop|restart|status}")


if __name__ == "__main__":
    main()
