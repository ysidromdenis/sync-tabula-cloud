"""Servicio base para Tabula Cloud Sync."""

import abc
import configparser
import json
import logging
import os
import threading
import time
from typing import Any, Dict, Optional

from core.session import Session
from utils.logger import logging as tabula_logger


class TabulaCloudService(abc.ABC):
    """Clase base abstracta para el servicio de Tabula Cloud."""

    def __init__(self, config_file: str = "config.ini"):
        """
        Inicializa el servicio base.

        Args:
            config_file: Ruta al archivo de configuración
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.running = False
        self.session = None
        self.sync_thread = None
        self.sync_interval = 30  # segundos por defecto
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("tabula_service.log"),
                logging.StreamHandler(),
            ],
        )

    def load_config(self) -> None:
        """Carga la configuración desde el archivo."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {self.config_file}"
            )

        self.config.read(self.config_file)

        # Obtener configuración del sincronizador
        if "sincronizador" in self.config:
            sync_config = self.config["sincronizador"]
            self.sync_interval = sync_config.getint("interval", 30)

        self.logger.info(f"Configuración cargada desde {self.config_file}")

    def initialize_session(self) -> None:
        """Inicializa la sesión con Tabula Cloud."""
        if "sincronizador" not in self.config:
            raise ValueError("Configuración de sincronizador no encontrada")

        token = self.config["sincronizador"].get("token")
        if not token:
            raise ValueError("Token no configurado")

        self.session = Session(token)
        self.logger.info("Sesión con Tabula Cloud inicializada")

    def start_service(self) -> None:
        """Inicia el servicio de sincronización."""
        try:
            self.load_config()
            self.initialize_session()

            self.running = True
            self.sync_thread = threading.Thread(
                target=self._sync_loop, daemon=True
            )
            self.sync_thread.start()

            self.logger.info("Servicio de Tabula Cloud iniciado")
            self.on_start()

        except Exception as e:
            self.logger.error(f"Error al iniciar el servicio: {e}")
            raise

    def stop_service(self) -> None:
        """Detiene el servicio de sincronización."""
        self.running = False

        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=10)

        self.logger.info("Servicio de Tabula Cloud detenido")
        self.on_stop()

    def _sync_loop(self) -> None:
        """Bucle principal de sincronización."""
        while self.running:
            try:
                self.perform_sync()
                time.sleep(self.sync_interval)
            except Exception as e:
                self.logger.error(f"Error en la sincronización: {e}")
                time.sleep(self.sync_interval)

    @abc.abstractmethod
    def perform_sync(self) -> None:
        """
        Realiza la sincronización con Tabula Cloud.
        Este método debe ser implementado por las clases derivadas.
        """
        pass

    def on_start(self) -> None:
        """Callback llamado cuando el servicio se inicia."""
        pass

    def on_stop(self) -> None:
        """Callback llamado cuando el servicio se detiene."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del servicio.

        Returns:
            Diccionario con información del estado
        """
        return {
            "running": self.running,
            "config_file": self.config_file,
            "sync_interval": self.sync_interval,
            "session_active": self.session is not None,
            "last_sync": getattr(self, "_last_sync", None),
        }

    def health_check(self) -> bool:
        """
        Realiza una verificación de salud del servicio.

        Returns:
            True si el servicio está funcionando correctamente
        """
        try:
            if not self.running:
                return False

            if not self.session:
                return False

            # Aquí podrías agregar más verificaciones específicas
            return True

        except Exception as e:
            self.logger.error(f"Error en health check: {e}")
            return False
