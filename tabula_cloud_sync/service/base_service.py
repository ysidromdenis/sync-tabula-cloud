"""
Servicio base mejorado para Tabula Cloud Sync.

Esta versión incluye características avanzadas como auto-configuración,
logging mejorado, manejo de errores robusto, y hooks extensibles.
"""

import abc
import configparser
import logging
import logging.config
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List

import yaml

from ..core.session import Session
from ..core.urls import URL_BASE
from ..utils.commons import ensure_directory


class TabulaCloudService(abc.ABC):
    """
    Clase base abstracta mejorada para servicios de Tabula Cloud.

    Proporciona funcionalidad base para sincronización con auto-configuración,
    logging avanzado, manejo de errores robusto y hooks extensibles.
    """

    def __init__(self, config_file: str = "config.ini"):
        """
        Inicializa el servicio base.

        Args:
            config_file: Ruta al archivo de configuración
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.running = False
        self.paused = False
        self.session = None
        self.sync_thread = None
        self.sync_interval = 300  # 5 minutos por defecto
        self.retry_attempts = 3
        self.retry_delay = 10
        self.last_sync_time = None
        self.sync_count = 0
        self.error_count = 0
        self.max_errors = 10

        # Hooks personalizables
        self.pre_sync_hooks: List[Callable] = []
        self.post_sync_hooks: List[Callable] = []
        self.error_hooks: List[Callable] = []

        # Configurar logging
        self._setup_logging()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _setup_logging(self) -> None:
        """Configura el sistema de logging avanzado."""
        # Buscar configuración de logging personalizada
        logging_config_file = (
            Path(self.config_file).parent / "logging_config.yaml"
        )

        if logging_config_file.exists():
            try:
                with open(logging_config_file, "r") as f:
                    config = yaml.safe_load(f)
                logging.config.dictConfig(config)
                return
            except Exception:
                pass

        # Configuración de logging por defecto
        log_dir = Path("logs")
        ensure_directory(str(log_dir))

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "tabula_service.log"),
                logging.StreamHandler(),
            ],
        )

    def load_config(self) -> None:
        """Carga la configuración desde el archivo."""
        if not os.path.exists(self.config_file):
            # Intentar auto-configuración si no existe el archivo
            self._auto_configure()

        self.config.read(self.config_file)

        # Cargar configuración de sincronización
        if "SYNC" in self.config:
            sync_config = self.config["SYNC"]
            self.sync_interval = sync_config.getint("interval", 300)
            self.retry_attempts = sync_config.getint("retry_attempts", 3)
            self.retry_delay = sync_config.getint("retry_delay", 10)

        # Cargar configuración de API
        if "API" not in self.config:
            raise ValueError("Configuración de API no encontrada")

        self.logger.info(f"Configuración cargada desde {self.config_file}")

    def _auto_configure(self) -> None:
        """Auto-configura el servicio si no existe configuración."""
        self.logger.warning(
            "Archivo de configuración no encontrado. Auto-configurando..."
        )

        try:
            from ..build_tools.post_install import PostInstallHooks

            PostInstallHooks.run_post_install()
            self.logger.info("Auto-configuración completada")
        except Exception as e:
            self.logger.error(f"Error en auto-configuración: {e}")
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {self.config_file}"
            )

    def initialize_session(self) -> None:
        """Inicializa la sesión con Tabula Cloud."""
        if "API" not in self.config:
            raise ValueError("Configuración de API no encontrada")

        api_config = self.config["API"]
        api_key = api_config.get("api_key")
        base_url = api_config.get("base_url", "https://api.tabula.com.py")

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError(
                "API key no configurada. Edita el archivo de configuración."
            )

        self.session = Session(
            api_key=api_key,
            base_url=base_url,
            timeout=api_config.getint("timeout", 30),
        )
        self.logger.info("Sesión con Tabula Cloud inicializada")

    def start(self) -> None:
        """Inicia el servicio de sincronización."""
        try:
            self.logger.info(f"=== Iniciando {self.__class__.__name__} ===")

            # Cargar configuración
            self.load_config()

            # Inicializar sesión
            self.initialize_session()

            # Marcar como ejecutándose
            self.running = True
            self.paused = False

            # Ejecutar hook de inicio
            self.on_start()

            # Iniciar hilo de sincronización
            self.sync_thread = threading.Thread(
                target=self._sync_loop,
                daemon=True,
                name=f"{self.__class__.__name__}SyncThread",
            )
            self.sync_thread.start()

            self.logger.info("Servicio iniciado correctamente")

        except Exception as e:
            self.logger.error(f"Error al iniciar el servicio: {e}")
            self.running = False
            raise

    def stop(self) -> None:
        """Detiene el servicio de sincronización."""
        self.logger.info(f"=== Deteniendo {self.__class__.__name__} ===")

        self.running = False

        if self.sync_thread and self.sync_thread.is_alive():
            self.logger.info(
                "Esperando a que termine el hilo de sincronización..."
            )
            self.sync_thread.join(timeout=30)

            if self.sync_thread.is_alive():
                self.logger.warning(
                    "El hilo de sincronización no terminó en tiempo"
                )

        # Ejecutar hook de parada
        self.on_stop()

        self.logger.info("Servicio detenido correctamente")

    def pause(self) -> None:
        """Pausa la sincronización sin detener el servicio."""
        self.paused = True
        self.logger.info("Servicio pausado")

    def resume(self) -> None:
        """Reanuda la sincronización."""
        self.paused = False
        self.logger.info("Servicio reanudado")

    def _sync_loop(self) -> None:
        """Bucle principal de sincronización."""
        while self.running:
            try:
                if not self.paused:
                    self._execute_sync_with_hooks()

                time.sleep(self.sync_interval)

            except Exception as e:
                self.logger.error(
                    f"Error crítico en bucle de sincronización: {e}"
                )
                self.error_count += 1

                if self.error_count >= self.max_errors:
                    self.logger.critical(
                        "Máximo número de errores alcanzado. Deteniendo servicio."
                    )
                    self.running = False
                    break

                time.sleep(self.retry_delay)

    def _execute_sync_with_hooks(self) -> None:
        """Ejecuta la sincronización con hooks pre/post."""
        start_time = datetime.now()

        try:
            # Ejecutar hooks pre-sincronización
            for hook in self.pre_sync_hooks:
                try:
                    hook(self)
                except Exception as e:
                    self.logger.warning(f"Error en pre-sync hook: {e}")

            # Ejecutar sincronización con reintentos
            for attempt in range(self.retry_attempts):
                try:
                    result = self.perform_sync()

                    # Actualizar estadísticas
                    self.last_sync_time = datetime.now()
                    self.sync_count += 1
                    self.error_count = 0  # Reset error count on success

                    self.logger.info(
                        f"Sincronización completada en intento {attempt + 1}"
                    )
                    break

                except Exception as e:
                    self.logger.warning(f"Intento {attempt + 1} falló: {e}")
                    if attempt == self.retry_attempts - 1:
                        raise  # Re-raise on final attempt
                    time.sleep(self.retry_delay)

            # Ejecutar hooks post-sincronización
            for hook in self.post_sync_hooks:
                try:
                    hook(self, result)
                except Exception as e:
                    self.logger.warning(f"Error en post-sync hook: {e}")

        except Exception as e:
            self.logger.error(f"Error en sincronización: {e}")
            self.error_count += 1

            # Ejecutar hooks de error
            for hook in self.error_hooks:
                try:
                    hook(self, e)
                except Exception as hook_error:
                    self.logger.warning(f"Error en error hook: {hook_error}")

    @abc.abstractmethod
    def perform_sync(self) -> Dict[str, Any]:
        """
        Realiza la sincronización con Tabula Cloud.

        Este método debe ser implementado por las clases derivadas.

        Returns:
            Dict con resultados de la sincronización
        """
        pass

    def on_start(self) -> None:
        """Callback llamado cuando el servicio se inicia."""
        pass

    def on_stop(self) -> None:
        """Callback llamado cuando el servicio se detiene."""
        pass

    def add_pre_sync_hook(self, hook: Callable) -> None:
        """Agrega un hook que se ejecuta antes de cada sincronización."""
        self.pre_sync_hooks.append(hook)

    def add_post_sync_hook(self, hook: Callable) -> None:
        """Agrega un hook que se ejecuta después de cada sincronización."""
        self.post_sync_hooks.append(hook)

    def add_error_hook(self, hook: Callable) -> None:
        """Agrega un hook que se ejecuta cuando ocurre un error."""
        self.error_hooks.append(hook)

    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del servicio.

        Returns:
            Diccionario con información del estado
        """
        return {
            "running": self.running,
            "paused": self.paused,
            "config_file": self.config_file,
            "sync_interval": self.sync_interval,
            "session_active": self.session is not None,
            "last_sync_time": (
                self.last_sync_time.isoformat()
                if self.last_sync_time
                else None
            ),
            "sync_count": self.sync_count,
            "error_count": self.error_count,
            "thread_alive": (
                self.sync_thread.is_alive() if self.sync_thread else False
            ),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas detalladas del servicio.

        Returns:
            Diccionario con métricas de rendimiento
        """
        return {
            "total_syncs": self.sync_count,
            "total_errors": self.error_count,
            "uptime_seconds": (
                (datetime.now() - self.last_sync_time).total_seconds()
                if self.last_sync_time
                else 0
            ),
            "success_rate": (
                self.sync_count / max(self.sync_count + self.error_count, 1)
            )
            * 100,
            "average_interval": self.sync_interval,
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

            if self.error_count >= self.max_errors:
                return False

            # Verificar que el hilo esté vivo
            if self.sync_thread and not self.sync_thread.is_alive():
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error en health check: {e}")
            return False

    def force_sync(self) -> Dict[str, Any]:
        """
        Fuerza una sincronización inmediata.

        Returns:
            Resultado de la sincronización
        """
        self.logger.info("Forzando sincronización inmediata...")
        return self.perform_sync()

    def reload_config(self) -> None:
        """Recarga la configuración sin reiniciar el servicio."""
        self.logger.info("Recargando configuración...")
        old_interval = self.sync_interval

        self.load_config()

        if old_interval != self.sync_interval:
            self.logger.info(
                f"Intervalo de sincronización cambiado de {old_interval} a {self.sync_interval}"
            )
