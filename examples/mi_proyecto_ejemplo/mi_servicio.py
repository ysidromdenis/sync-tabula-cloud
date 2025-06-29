"""
Servicio personalizado para Mi Distribuidor Tabula.

Este archivo muestra cómo implementar un servicio específico para tu proyecto
que utiliza la librería tabula-cloud-sync como base.
"""

import os
import platform
import sys
import time
from datetime import datetime

# Agregar la librería base al path (si no está instalada como paquete)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from models.mi_modelo import MiModelo  # Tu modelo personalizado
from service.base_service import TabulaCloudService
from service.daemon import TabulaCloudDaemon


class MiDistribuidorService(TabulaCloudService):
    """Servicio personalizado para Mi Distribuidor."""

    def __init__(self, config_file="config.ini"):
        """Inicializa el servicio personalizado."""
        super().__init__(config_file)

        # Configuraciones específicas del proyecto
        self.productos_sincronizados = 0
        self.clientes_actualizados = 0
        self.ultimo_error = None

        # Base de datos local (ejemplo)
        self.db_local = None

    def on_start(self):
        """Callback ejecutado al iniciar el servicio."""
        self.logger.info("=== Iniciando Mi Distribuidor Tabula Service ===")

        # Conectar a base de datos local
        self._conectar_db_local()

        # Validar configuraciones específicas
        self._validar_configuracion_distribuidor()

        self.logger.info("Servicio de distribuidor iniciado correctamente")

    def on_stop(self):
        """Callback ejecutado al detener el servicio."""
        self.logger.info("Deteniendo servicio de distribuidor...")

        # Cerrar conexiones de base de datos
        if self.db_local:
            self.db_local.close()

        self.logger.info("Servicio de distribuidor detenido")

    def perform_sync(self):
        """Lógica principal de sincronización del distribuidor."""
        try:
            self.logger.info("=== Iniciando ciclo de sincronización ===")

            # 1. Sincronizar productos desde Tabula Cloud
            self._sincronizar_productos()

            # 2. Actualizar información de clientes
            self._actualizar_clientes()

            # 3. Procesar pedidos pendientes
            self._procesar_pedidos_pendientes()

            # 4. Generar reportes si es necesario
            self._generar_reportes_diarios()

            # 5. Limpiar datos antiguos
            self._limpiar_datos_antiguos()

            # Marcar sincronización exitosa
            self._last_sync = datetime.now().isoformat()
            self.ultimo_error = None

            self.logger.info(
                f"Sincronización completada. "
                f"Productos: {self.productos_sincronizados}, "
                f"Clientes: {self.clientes_actualizados}"
            )

        except Exception as e:
            self.ultimo_error = str(e)
            self.logger.error(f"Error en sincronización: {e}")
            self._manejar_error_sincronizacion(e)

    def _conectar_db_local(self):
        """Conecta a la base de datos local del distribuidor."""
        try:
            # Ejemplo de conexión a MySQL local
            if "mysql" in self.config:
                mysql_config = self.config["mysql"]
                self.logger.info(f"Conectando a DB local: {mysql_config.get('host')}")

                # Aquí conectarías a tu base de datos
                # self.db_local = mysql.connector.connect(**mysql_config)

            self.logger.info("Conexión a DB local establecida")

        except Exception as e:
            self.logger.error(f"Error conectando a DB local: {e}")
            raise

    def _validar_configuracion_distribuidor(self):
        """Valida configuraciones específicas del distribuidor."""
        if "distribuidor" not in self.config:
            raise ValueError("Configuración de distribuidor no encontrada")

        dist_config = self.config["distribuidor"]
        required_fields = ["codigo_distribuidor", "zona", "sucursal"]

        for field in required_fields:
            if not dist_config.get(field):
                raise ValueError(f"Campo requerido no configurado: {field}")

        self.logger.info(
            f"Distribuidor configurado: "
            f"{dist_config.get('codigo_distribuidor')} - "
            f"Zona {dist_config.get('zona')}"
        )

    def _sincronizar_productos(self):
        """Sincroniza productos desde Tabula Cloud."""
        self.logger.info("Sincronizando productos...")

        try:
            # Obtener productos desde la API
            response = self.session.get("api/items/v1/items/")

            if response.status_code == 200:
                productos = response.json()
                self.logger.info(f"Obtenidos {len(productos)} productos de Tabula")

                count = 0
                for producto in productos:
                    if self._procesar_producto(producto):
                        count += 1

                self.productos_sincronizados = count
                self.logger.info(f"Sincronizados {count} productos")

            else:
                self.logger.warning(
                    f"Error obteniendo productos: {response.status_code}"
                )

        except Exception as e:
            self.logger.error(f"Error sincronizando productos: {e}")
            raise

    def _procesar_producto(self, producto_data):
        """Procesa un producto individual."""
        try:
            producto_id = producto_data.get("id")
            codigo = producto_data.get("codigo")

            self.logger.debug(f"Procesando producto {codigo} (ID: {producto_id})")

            # Crear o actualizar en modelo local
            modelo = MiModelo()
            modelo.actualizar_producto(producto_data)

            return True

        except Exception as e:
            self.logger.error(
                f"Error procesando producto {producto_data.get('codigo')}: {e}"
            )
            return False

    def _actualizar_clientes(self):
        """Actualiza información de clientes."""
        self.logger.info("Actualizando clientes...")

        try:
            response = self.session.get("api/contacts/v1/contacts/")

            if response.status_code == 200:
                clientes = response.json()
                self.logger.info(f"Obtenidos {len(clientes)} clientes")

                count = 0
                for cliente in clientes:
                    if self._procesar_cliente(cliente):
                        count += 1

                self.clientes_actualizados = count

            else:
                self.logger.warning(
                    f"Error obteniendo clientes: {response.status_code}"
                )

        except Exception as e:
            self.logger.error(f"Error actualizando clientes: {e}")
            raise

    def _procesar_cliente(self, cliente_data):
        """Procesa un cliente individual."""
        try:
            cliente_id = cliente_data.get("id")
            documento = cliente_data.get("documento")

            self.logger.debug(f"Procesando cliente {documento} (ID: {cliente_id})")

            # Actualizar en base de datos local
            # Aquí iría tu lógica específica

            return True

        except Exception as e:
            self.logger.error(
                f"Error procesando cliente {cliente_data.get('documento')}: {e}"
            )
            return False

    def _procesar_pedidos_pendientes(self):
        """Procesa pedidos pendientes en la cola local."""
        self.logger.info("Procesando pedidos pendientes...")

        # Aquí procesarías pedidos que están en tu sistema local
        # y necesitan ser enviados a Tabula Cloud
        pass

    def _generar_reportes_diarios(self):
        """Genera reportes diarios si es necesario."""
        now = datetime.now()

        # Generar reporte solo una vez al día
        if now.hour == 23 and now.minute < (self.sync_interval / 60):
            self.logger.info("Generando reportes diarios...")
            # Lógica de reportes aquí

    def _limpiar_datos_antiguos(self):
        """Limpia datos antiguos del sistema."""
        # Ejecutar limpieza cada cierto tiempo
        pass

    def _manejar_error_sincronizacion(self, error):
        """Maneja errores de sincronización."""
        self.logger.error(f"Manejando error de sincronización: {error}")

        # Aquí podrías implementar:
        # - Reintentos automáticos
        # - Notificaciones por email
        # - Alertas al sistema de monitoreo
        # - Respaldos de emergencia

    def get_status(self):
        """Obtiene el estado extendido del servicio."""
        base_status = super().get_status()

        # Agregar información específica del distribuidor
        base_status.update(
            {
                "productos_sincronizados": self.productos_sincronizados,
                "clientes_actualizados": self.clientes_actualizados,
                "ultimo_error": self.ultimo_error,
                "db_local_conectada": self.db_local is not None,
            }
        )

        return base_status


class MiDistribuidorDaemon(TabulaCloudDaemon):
    """Daemon personalizado para el distribuidor."""

    def __init__(
        self,
        pidfile="/var/run/mi_distribuidor_tabula.pid",
        config_file="config.ini",
    ):
        super().__init__(pidfile, config_file)
        # Reemplazar el servicio base con nuestro servicio personalizado
        self.distribuidor_service = MiDistribuidorService(config_file)

    def perform_sync(self):
        """Delega la sincronización al servicio del distribuidor."""
        if hasattr(self, "distribuidor_service"):
            self.distribuidor_service.perform_sync()
        else:
            super().perform_sync()

    def run(self):
        """Ejecuta el daemon con el servicio personalizado."""
        import signal

        def signal_handler(signum, frame):
            self.logger.info(f"Recibida señal {signum}, terminando...")
            if hasattr(self, "distribuidor_service"):
                self.distribuidor_service.stop_service()
            self.running = False

        # Configurar manejadores de señales
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        try:
            # Iniciar el servicio personalizado en lugar del base
            self.distribuidor_service.start_service()
            self.running = True

            # Mantener el daemon ejecutándose
            while self.running:
                time.sleep(1)

        except Exception as e:
            self.logger.error(f"Error en el daemon: {e}")
        finally:
            if hasattr(self, "distribuidor_service"):
                self.distribuidor_service.stop_service()


def main():
    """Función principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Mi Distribuidor Tabula Service")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["start", "stop", "restart", "status"],
        help="Comando a ejecutar",
    )
    parser.add_argument(
        "--foreground", action="store_true", help="Ejecutar en primer plano"
    )
    parser.add_argument(
        "--config", default="config.ini", help="Archivo de configuración"
    )

    args = parser.parse_args()

    if args.foreground:
        # Ejecutar en primer plano para desarrollo
        print("Ejecutando Mi Distribuidor Service en primer plano...")
        print("Presiona Ctrl+C para detener")

        service = MiDistribuidorService(args.config)

        try:
            service.start_service()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeteniendo servicio...")
            service.stop_service()
            print("Servicio detenido")

    elif args.command:
        # Ejecutar como daemon
        system = platform.system().lower()

        if system in ["linux", "darwin"]:
            daemon = MiDistribuidorDaemon(config_file=args.config)

            if args.command == "start":
                daemon.start()
            elif args.command == "stop":
                daemon.stop()
            elif args.command == "restart":
                daemon.restart()
            elif args.command == "status":
                daemon.status()
        else:
            print(f"Daemon no soportado en {system}")
            print("Use --foreground para ejecutar en primer plano")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
