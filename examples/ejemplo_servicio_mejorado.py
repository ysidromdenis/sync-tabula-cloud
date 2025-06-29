"""
Ejemplo de uso de la librería Tabula Cloud Sync.

Este ejemplo muestra cómo crear un servicio personalizado que utiliza
la librería como base para sincronización con Tabula Cloud.
"""

import json
from datetime import datetime

from tabula_cloud_sync import TabulaCloudService


class EjemploServicio(TabulaCloudService):
    """
    Ejemplo de servicio personalizado que hereda de TabulaCloudService.

    Este servicio implementa lógica específica para sincronizar
    datos de ejemplo con Tabula Cloud.
    """

    def __init__(self, config_file="config/tabula_config.ini"):
        """Inicializa el servicio de ejemplo."""
        super().__init__(config_file)

        # Variables específicas del servicio
        self.productos_sincronizados = 0
        self.clientes_procesados = 0
        self.datos_ejemplo = []

    def on_start(self):
        """Se ejecuta al iniciar el servicio."""
        self.logger.info("=== Iniciando Servicio de Ejemplo ===")

        # Inicialización personalizada
        self._cargar_datos_ejemplo()
        self._configurar_hooks()

        self.logger.info("Servicio de ejemplo iniciado correctamente")

    def on_stop(self):
        """Se ejecuta al detener el servicio."""
        self.logger.info("=== Deteniendo Servicio de Ejemplo ===")

        # Limpieza de recursos
        self._guardar_estadisticas()

        self.logger.info("Servicio de ejemplo detenido correctamente")

    def perform_sync(self):
        """
        Implementa la lógica de sincronización personalizada.

        Returns:
            Dict con resultados de la sincronización
        """
        self.logger.info("Iniciando sincronización de ejemplo...")

        try:
            # Simular sincronización de productos
            productos_sync = self._sincronizar_productos()

            # Simular sincronización de clientes
            clientes_sync = self._sincronizar_clientes()

            # Actualizar estadísticas
            self.productos_sincronizados += productos_sync
            self.clientes_procesados += clientes_sync

            resultado = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "productos_sincronizados": productos_sync,
                "clientes_procesados": clientes_sync,
                "total_productos": self.productos_sincronizados,
                "total_clientes": self.clientes_procesados,
            }

            self.logger.info(
                f"Sincronización completada: {json.dumps(resultado, indent=2)}"
            )
            return resultado

        except Exception as e:
            self.logger.error(f"Error en sincronización: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _cargar_datos_ejemplo(self):
        """Carga datos de ejemplo para el servicio."""
        self.datos_ejemplo = [
            {"id": 1, "nombre": "Producto A", "precio": 100.0},
            {"id": 2, "nombre": "Producto B", "precio": 200.0},
            {"id": 3, "nombre": "Producto C", "precio": 300.0},
        ]
        self.logger.info(
            f"Cargados {len(self.datos_ejemplo)} productos de ejemplo"
        )

    def _configurar_hooks(self):
        """Configura hooks personalizados."""

        # Hook pre-sincronización
        def pre_sync_hook(service):
            service.logger.debug(
                "Ejecutando preparación pre-sincronización..."
            )

        # Hook post-sincronización
        def post_sync_hook(service, result):
            service.logger.debug(
                f"Sincronización completada con resultado: {result['status']}"
            )

        # Hook de error
        def error_hook(service, error):
            service.logger.warning(f"Hook de error ejecutado: {error}")

        self.add_pre_sync_hook(pre_sync_hook)
        self.add_post_sync_hook(post_sync_hook)
        self.add_error_hook(error_hook)

    def _sincronizar_productos(self):
        """
        Simula sincronización de productos con Tabula Cloud.

        Returns:
            Número de productos sincronizados
        """
        if not self.session:
            self.logger.warning(
                "Sesión no disponible para sincronización de productos"
            )
            return 0

        try:
            # Simular llamada a API de Tabula Cloud
            # En implementación real, aquí irían las llamadas reales a la API

            productos_a_sincronizar = len(self.datos_ejemplo)

            for producto in self.datos_ejemplo:
                # Simular envío a Tabula Cloud
                self.logger.debug(
                    f"Sincronizando producto: {producto['nombre']}"
                )

                # Aquí iría la lógica real:
                # response = self.session.post('productos', json_data=producto)

            return productos_a_sincronizar

        except Exception as e:
            self.logger.error(f"Error sincronizando productos: {e}")
            return 0

    def _sincronizar_clientes(self):
        """
        Simula sincronización de clientes con Tabula Cloud.

        Returns:
            Número de clientes procesados
        """
        if not self.session:
            self.logger.warning(
                "Sesión no disponible para sincronización de clientes"
            )
            return 0

        try:
            # Simular procesamiento de clientes
            clientes_ejemplo = 5  # Simular 5 clientes

            for i in range(clientes_ejemplo):
                self.logger.debug(f"Procesando cliente {i+1}")

                # Aquí iría la lógica real:
                # cliente_data = obtener_cliente(i)
                # response = self.session.post('clientes', json_data=cliente_data)

            return clientes_ejemplo

        except Exception as e:
            self.logger.error(f"Error sincronizando clientes: {e}")
            return 0

    def _guardar_estadisticas(self):
        """Guarda estadísticas finales del servicio."""
        estadisticas = {
            "productos_sincronizados": self.productos_sincronizados,
            "clientes_procesados": self.clientes_procesados,
            "tiempo_finalizacion": datetime.now().isoformat(),
        }

        try:
            with open("logs/estadisticas_ejemplo.json", "w") as f:
                json.dump(estadisticas, f, indent=2)
            self.logger.info(
                "Estadísticas guardadas en logs/estadisticas_ejemplo.json"
            )
        except Exception as e:
            self.logger.warning(f"No se pudieron guardar estadísticas: {e}")

    def obtener_resumen(self):
        """
        Obtiene un resumen del estado actual del servicio.

        Returns:
            Dict con resumen del servicio
        """
        return {
            "nombre_servicio": self.__class__.__name__,
            "estado": "ejecutando" if self.running else "detenido",
            "productos_sincronizados": self.productos_sincronizados,
            "clientes_procesados": self.clientes_procesados,
            "ultima_sincronizacion": (
                self.last_sync_time.isoformat()
                if self.last_sync_time
                else None
            ),
            "errores_totales": self.error_count,
            "sincronizaciones_completadas": self.sync_count,
        }


def main():
    """Función principal para ejecutar el servicio de ejemplo."""
    print("🚀 Iniciando servicio de ejemplo de Tabula Cloud Sync...")

    # Crear instancia del servicio
    servicio = EjemploServicio()

    try:
        # Iniciar el servicio
        servicio.start()

        print("✅ Servicio iniciado. Presiona Ctrl+C para detener.")

        # Mantener ejecutándose
        import time

        while servicio.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Recibida señal de interrupción...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Detener el servicio
        servicio.stop()
        print("👋 Servicio detenido")


if __name__ == "__main__":
    main()
