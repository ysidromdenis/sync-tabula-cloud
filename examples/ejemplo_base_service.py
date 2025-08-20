#!/usr/bin/env python3
"""
Ejemplo de uso del módulo base_service.py
"""

import time

from tabula_cloud_sync.service.base_service import TabulaCloudService


# 1. Crear un servicio heredando de TabulaCloudService
class ServicioSyncRemisiones(TabulaCloudService):
    """Servicio específico para sincronizar remisiones"""

    def __init__(self, config_file="config.ini"):
        super().__init__(config_file)

        # Configuración específica
        self.sync_interval = 60  # cada minuto
        self.api_endpoint = "/api/remisiones"

        # Agregar hooks personalizados
        self.add_pre_sync_hook(self._validar_conexion)
        self.add_post_sync_hook(self._actualizar_cache)
        self.add_error_hook(self._manejar_error)

    def perform_sync(self):
        """Implementación obligatoria - sincroniza remisiones"""
        self.logger.info("🔄 Iniciando sincronización de remisiones...")

        try:
            # Simular obtención de datos locales
            remisiones_locales = self._obtener_remisiones_locales()

            # Enviar a Tabula Cloud
            self._enviar_a_tabula_cloud(remisiones_locales)

            self.logger.info(
                f"✅ Sincronizadas {len(remisiones_locales)} remisiones"
            )

            return {
                "status": "success",
                "remisiones_sincronizadas": len(remisiones_locales),
                "timestamp": time.time(),
            }

        except Exception as e:
            self.logger.error(f"❌ Error en sincronización: {e}")
            raise

    def _obtener_remisiones_locales(self):
        """Simula obtener remisiones de base de datos local"""
        # Aquí conectarías a tu BD local
        return [
            {"id": 1, "numero": "REM-001", "cliente": "Cliente A"},
            {"id": 2, "numero": "REM-002", "cliente": "Cliente B"},
        ]

    def _enviar_a_tabula_cloud(self, remisiones):
        """Envía remisiones a Tabula Cloud"""
        if not self.session:
            raise Exception("Sesión no inicializada")

        # Simular envío a API
        self.logger.info(
            f"📤 Enviando {len(remisiones)} remisiones a Tabula Cloud"
        )
        time.sleep(0.5)  # Simular latencia de red
        return {"uploaded": len(remisiones)}

    # Hooks personalizados
    def _validar_conexion(self, service):
        """Hook pre-sincronización: valida conexión"""
        self.logger.info("🔍 Validando conexión antes de sincronizar...")

    def _actualizar_cache(self, service, resultado):
        """Hook post-sincronización: actualiza cache local"""
        self.logger.info("💾 Actualizando cache local...")

    def _manejar_error(self, service, error):
        """Hook de error: manejo personalizado"""
        self.logger.error(f"🚨 Error capturado por hook: {error}")
        # Aquí podrías enviar notificaciones, etc.


# 2. Crear otro servicio para documentos
class ServicioSyncDocumentos(TabulaCloudService):
    """Servicio específico para sincronizar documentos"""

    def __init__(self, config_file="config.ini"):
        super().__init__(config_file)
        self.sync_interval = 300  # cada 5 minutos

    def perform_sync(self):
        """Sincroniza documentos"""
        self.logger.info("📄 Sincronizando documentos...")

        # Lógica específica para documentos
        documentos = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

        return {
            "status": "success",
            "documentos_sincronizados": len(documentos),
        }


# 3. Ejemplos de uso directo (sin daemon)
def ejemplo_uso_directo():
    """Ejemplo de usar el servicio directamente (no como daemon)"""
    print("=== USO DIRECTO DEL SERVICIO ===")

    # Crear servicio
    servicio = ServicioSyncRemisiones("config.ini")

    try:
        # Iniciar servicio (correrá en hilo separado)
        servicio.start()

        # Dejar correr por 30 segundos
        print("⏱️  Servicio ejecutándose por 30 segundos...")
        time.sleep(30)

        # Verificar estado
        estado = servicio.get_status()
        print(f"📊 Estado: {estado}")

        # Obtener métricas
        metricas = servicio.get_metrics()
        print(f"📈 Métricas: {metricas}")

        # Forzar sincronización
        print("🔄 Forzando sincronización...")
        resultado = servicio.force_sync()
        print(f"✅ Resultado: {resultado}")

    finally:
        # Detener servicio
        servicio.stop()
        print("🛑 Servicio detenido")


def ejemplo_uso_con_daemon():
    """Ejemplo de usar el servicio CON daemon"""
    print("=== USO CON DAEMON ===")
    print("Para usar con daemon, ejecuta:")
    print("python ejemplo_daemon.py start")
    print("python ejemplo_daemon.py status")
    print("python ejemplo_daemon.py stop")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        ejemplo_uso_con_daemon()
    else:
        ejemplo_uso_directo()
