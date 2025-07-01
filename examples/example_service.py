"""
Ejemplo de cómo usar el servicio Tabula Cloud Sync en tu proyecto.

Este archivo muestra cómo extender el servicio base para implementar
lógica de sincronización específica de tu proyecto.
"""

import datetime
import time

from models.documentos import Documento  # Ejemplo de importar modelos
from service.base_service import TabulaCloudService


class MiProyectoTabulaService(TabulaCloudService):
    """
    Servicio personalizado que extiende TabulaCloudService.

    Esta clase implementa la lógica específica de sincronización
    para tu proyecto.
    """

    def __init__(self, config_file="config.ini"):
        """Inicializa tu servicio personalizado."""
        super().__init__(config_file)

        # Agregar configuraciones específicas de tu proyecto
        self.last_document_sync = None
        self.sync_errors = []

    def perform_sync(self):
        """
        Implementa la lógica de sincronización específica de tu proyecto.

        Este método se llama automáticamente cada `sync_interval` segundos.
        """
        try:
            self.logger.info("Iniciando sincronización personalizada...")

            # Ejemplo 1: Sincronizar documentos
            self._sync_documents()

            # Ejemplo 2: Sincronizar contactos
            self._sync_contacts()

            # Ejemplo 3: Procesar elementos pendientes
            self._process_pending_items()

            # Marcar tiempo de última sincronización exitosa
            self._last_sync = datetime.datetime.now().isoformat()
            self.last_document_sync = self._last_sync

            self.logger.info("Sincronización completada exitosamente")

        except Exception as e:
            error_msg = f"Error en sincronización personalizada: {e}"
            self.logger.error(error_msg)
            self.sync_errors.append(
                {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "error": str(e),
                }
            )

            # Mantener solo los últimos 10 errores
            if len(self.sync_errors) > 10:
                self.sync_errors = self.sync_errors[-10:]

    def _sync_documents(self):
        """Sincroniza documentos con Tabula Cloud."""
        self.logger.info("Sincronizando documentos...")

        try:
            # Ejemplo de uso de la sesión para obtener documentos
            response = self.session.get("api/documents/v1/documentos/")

            if response.status_code == 200:
                documents = response.json()
                self.logger.info(f"Obtenidos {len(documents)} documentos")

                # Procesar cada documento
                for doc_data in documents:
                    self._process_document(doc_data)

            else:
                self.logger.warning(
                    f"Error al obtener documentos: {response.status_code}"
                )

        except Exception as e:
            self.logger.error(f"Error sincronizando documentos: {e}")
            raise

    def _sync_contacts(self):
        """Sincroniza contactos con Tabula Cloud."""
        self.logger.info("Sincronizando contactos...")

        try:
            response = self.session.get("api/contacts/v1/contacts/")

            if response.status_code == 200:
                contacts = response.json()
                self.logger.info(f"Obtenidos {len(contacts)} contactos")

                # Aquí implementarías la lógica específica para contactos

            else:
                self.logger.warning(
                    f"Error al obtener contactos: {response.status_code}"
                )

        except Exception as e:
            self.logger.error(f"Error sincronizando contactos: {e}")
            raise

    def _process_pending_items(self):
        """Procesa elementos pendientes en la cola."""
        self.logger.info("Procesando elementos pendientes...")

        try:
            # Ejemplo de procesamiento de items pendientes
            response = self.session.get("api/items/v1/items/")

            if response.status_code == 200:
                items = response.json()
                pending_items = [
                    item for item in items if item.get("status") == "pending"
                ]

                self.logger.info(f"Procesando {len(pending_items)} items pendientes")

                for item in pending_items:
                    self._process_item(item)

        except Exception as e:
            self.logger.error(f"Error procesando items pendientes: {e}")
            raise

    def _process_document(self, doc_data):
        """Procesa un documento individual."""
        # Ejemplo de procesamiento de documento
        doc_id = doc_data.get("id")
        self.logger.debug(f"Procesando documento {doc_id}")

        # Aquí implementarías tu lógica específica
        # Por ejemplo: validar, transformar, guardar en base de datos local, etc.
        pass

    def _process_item(self, item_data):
        """Procesa un item individual."""
        item_id = item_data.get("id")
        self.logger.debug(f"Procesando item {item_id}")

        # Aquí implementarías tu lógica específica para items
        pass

    def on_start(self):
        """Callback ejecutado cuando el servicio se inicia."""
        self.logger.info("Mi servicio personalizado iniciado")

        # Realizar configuraciones adicionales si es necesario
        self._validate_custom_config()

    def on_stop(self):
        """Callback ejecutado cuando el servicio se detiene."""
        self.logger.info("Mi servicio personalizado detenido")

        # Realizar limpieza si es necesario
        self._cleanup_resources()

    def _validate_custom_config(self):
        """Valida configuraciones específicas del proyecto."""
        # Validar configuraciones adicionales aquí
        if "mi_proyecto" in self.config:
            project_config = self.config["mi_proyecto"]
            # Validar configuraciones específicas
            pass

    def _cleanup_resources(self):
        """Limpia recursos específicos del proyecto."""
        # Realizar limpieza de recursos aquí
        pass

    def get_status(self):
        """Obtiene el estado extendido del servicio."""
        base_status = super().get_status()

        # Agregar información específica del proyecto
        base_status.update(
            {
                "last_document_sync": self.last_document_sync,
                "sync_errors_count": len(self.sync_errors),
                "recent_errors": (self.sync_errors[-3:] if self.sync_errors else []),
            }
        )

        return base_status


# Ejemplo de cómo usar el servicio personalizado
if __name__ == "__main__":
    import platform
    import sys

    # Crear instancia del servicio personalizado
    service = MiProyectoTabulaService("config.ini")

    # Determinar el tipo de ejecución según la plataforma
    system = platform.system().lower()

    if system == "windows":
        # En Windows, usar el servicio de Windows
        
        from service.windows_service import TabulaCloudWindowsService

        # Aquí deberías crear una clase que herede de TabulaCloudWindowsService
        # y use tu MiProyectoTabulaService internamente

    elif system in ["linux", "darwin", "unix"]:
        # En Linux/Unix, usar el daemon
        from service.daemon import TabulaCloudDaemon

        class MiProyectoDaemon(TabulaCloudDaemon):
            """Daemon personalizado para mi proyecto."""

            def __init__(
                self,
                pidfile="/var/run/mi_proyecto_tabula.pid",
                config_file="config.ini",
            ):
                super().__init__(pidfile, config_file)
                self.custom_service = MiProyectoTabulaService(config_file)

            def perform_sync(self):
                """Delega la sincronización al servicio personalizado."""
                self.custom_service.perform_sync()

        # Usar el daemon personalizado
        if len(sys.argv) >= 2:
            daemon = MiProyectoDaemon()

            if sys.argv[1] == "start":
                daemon.start()
            elif sys.argv[1] == "stop":
                daemon.stop()
            elif sys.argv[1] == "restart":
                daemon.restart()
            elif sys.argv[1] == "status":
                daemon.status()
            else:
                print("Uso: python example_service.py {start|stop|restart|status}")
                sys.exit(2)
        else:
            print("Uso: python example_service.py {start|stop|restart|status}")

    else:
        # Ejecución directa para desarrollo/testing
        try:
            service.start_service()
            print("Servicio iniciado. Presiona Ctrl+C para detener.")

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nDeteniendo servicio...")
            service.stop_service()
            print("Servicio detenido.")
